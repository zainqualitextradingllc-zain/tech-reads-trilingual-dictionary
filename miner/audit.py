"""
Audio & Data Quality Audit for the trilingual dictionary.
Read-only: never modifies the DB.

The app speaks:
  - English  : entry.english            (en-US)
  - Japanese : entry.japanese_kana || entry.japanese_kanji  (ja-JP)
  - Urdu     : entry.urdu_script        (ur-PK)
So these three fields are what the audit focuses on for audio.
"""
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent
DB = ROOT.parent / "data" / "dictionary.db"
OUT_JSON = ROOT.parent / "data" / "audit_report.json"

# ---------- character classes ----------
URDU_OK = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u200c\u200d\s\.\,\-\(\)\/،۔؟!:]")
LATIN = re.compile(r"[A-Za-z]")
CYRILLIC = re.compile(r"[\u0400-\u04FF]")
JP_ANY = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")
KANJI = re.compile(r"[\u4E00-\u9FFF]")
KANA_OK = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u30FC\u30FB\s・ー（）\(\)/、]")
# Arabic-only letters that Urdu normally writes differently (TTS mispronounces)
ARABIC_NOT_URDU = {"ة": "ta marbuta (Arabic) - Urdu uses ہ/ت",
                   "ي": "Arabic yeh - Urdu uses ی",
                   "ك": "Arabic kaf - Urdu uses ک",
                   "ى": "alef maksura - Urdu uses ی",
                   "ە": "Kurdish ae"}
# Common Persian (not Urdu) words seen in LLM output
PERSIAN_WORDS = ["پزشکی", "بین‌المللی", "دارو", "طراحی", "امنیت", "شکستن", "جابجایی", "جابجایگی", "مكافآت", "راحة"]

# ---------- simple kana -> romaji (Hepburn-ish) ----------
K2R = {}
_base = ("あa いi うu えe おo かka きki くku けke こko さsa しshi すsu せse そso たta ちchi つtsu てte とto "
         "なna にni ぬnu ねne のno はha ひhi ふfu へhe ほho まma みmi むmu めme もmo やya ゆyu よyo "
         "らra りri るru れre ろro わwa をo んn がga ぎgi ぐgu げge ごgo ざza じji ずzu ぜze ぞzo "
         "だda ぢji づzu でde どdo ばba びbi ぶbu べbe ぼbo ぱpa ぴpi ぷpu ぺpe ぽpo ゔvu")
for tok in _base.split():
    K2R[tok[0]] = tok[1:]
_yoon = {"ゃ": "ya", "ゅ": "yu", "ょ": "yo"}

def kata_to_hira(s):
    return "".join(chr(ord(c) - 0x60) if "\u30A1" <= c <= "\u30F6" else c for c in s)

def kana_to_romaji(s):
    s = kata_to_hira(s)
    out, i = [], 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if c == "っ":
            # double next consonant
            if nxt in K2R and K2R[nxt]:
                out.append(K2R[nxt][0])
            i += 1
            continue
        if c == "ー":
            if out and out[-1]:
                out.append(out[-1][-1])
            i += 1
            continue
        if c in K2R:
            r = K2R[c]
            if nxt in _yoon:
                base = r[:-1]
                if base in ("sh", "ch", "j"):
                    r = base + _yoon[nxt][1:]
                else:
                    r = base + _yoon[nxt]
                i += 1
            elif nxt in "ぁぃぅぇぉ" and nxt:
                r = r[:-1] + {"ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o"}[nxt]
                i += 1
            out.append(r)
        elif c.isspace() or c in "・/":
            out.append(" ")
        i += 1
    return "".join(out)

def norm_romaji(s):
    s = s.lower()
    for a, b in (("ā", "aa"), ("ī", "ii"), ("ū", "uu"), ("ē", "ee"), ("ō", "ou"),
                 ("ô", "ou"), ("â", "aa"), ("û", "uu"), ("'", ""), ("-", ""), ("’", "")):
        s = s.replace(a, b)
    s = s.replace("oo", "ou")
    return re.sub(r"[^a-z]", "", s)

def similarity(a, b):
    # bigram Dice coefficient
    if not a or not b:
        return 0.0
    A = Counter(a[i:i + 2] for i in range(len(a) - 1))
    B = Counter(b[i:i + 2] for i in range(len(b) - 1))
    inter = sum((A & B).values())
    tot = sum(A.values()) + sum(B.values())
    return 2 * inter / tot if tot else 0.0

# ---------- audit ----------
def audit_row(r, urdu_counter, kanji_counter):
    issues = []  # (severity, field, message)
    eng, kanji, kana, romaji, ur, ur_rom = (r[k] or "" for k in
        ("english", "japanese_kanji", "japanese_kana", "japanese_romaji", "urdu_script", "urdu_roman"))

    # ===== URDU AUDIO (urdu_script is spoken by ur-PK voice) =====
    if not re.search(r"[\u0600-\u06FF]", ur):
        issues.append(("CRITICAL", "urdu_audio", "No Urdu script at all - Urdu voice will say nothing/garbage"))
    bad = [c for c in ur if not URDU_OK.match(c)]
    if CYRILLIC.search(ur):
        issues.append(("CRITICAL", "urdu_audio", f"Cyrillic letters inside Urdu: {''.join(set(CYRILLIC.findall(ur)))}"))
    if JP_ANY.search(ur):
        issues.append(("CRITICAL", "urdu_audio", "Japanese characters inside Urdu text"))
    if LATIN.search(ur):
        issues.append(("HIGH", "urdu_audio", f"Latin letters inside Urdu text (voice switches language / spells letters): {''.join(LATIN.findall(ur))[:30]}"))
    other = [c for c in bad if not LATIN.match(c) and not CYRILLIC.match(c) and not JP_ANY.match(c)]
    if other:
        issues.append(("MEDIUM", "urdu_audio", f"Unexpected symbols in Urdu: {''.join(set(other))}"))
    for ch, why in ARABIC_NOT_URDU.items():
        if ch in ur:
            issues.append(("MEDIUM", "urdu_audio", f"Arabic letter '{ch}' ({why})"))
    for w in PERSIAN_WORDS:
        if w in ur:
            issues.append(("HIGH", "urdu_meaning", f"Persian/Arabic word '{w}' - not natural Urdu"))
    toks = ur.replace("/", " ").split()
    if len(toks) >= 3:
        c = Counter(toks)
        rep = [t for t, n in c.items() if n >= 3 and len(t) > 1]
        if rep:
            issues.append(("HIGH", "urdu_meaning", f"Repetitive/looping Urdu words: {rep}"))
    halves = [h.strip() for h in ur.split("/")]
    if len(halves) == 2 and halves[0] == halves[1]:
        issues.append(("LOW", "urdu_audio", "Same Urdu text repeated on both sides of '/' - spoken twice"))
    if "/" in ur:
        issues.append(("LOW", "urdu_audio", "Contains '/' alternatives - voice reads both variants back-to-back"))
    if "(" in ur:
        issues.append(("LOW", "urdu_audio", "Contains parentheses - extra text spoken"))
    if len(ur) > 45:
        issues.append(("LOW", "urdu_audio", f"Very long for a headword ({len(ur)} chars) - likely a sentence, not a term"))
    if urdu_counter[ur.strip()] > 1:
        issues.append(("HIGH", "urdu_meaning", f"Same Urdu text used by {urdu_counter[ur.strip()]} different entries"))

    # ===== JAPANESE AUDIO (kana is spoken, fallback kanji) =====
    if not kana.strip():
        issues.append(("HIGH", "ja_audio", "Empty kana - app falls back to kanji field"))
    else:
        if KANJI.search(kana):
            issues.append(("MEDIUM", "ja_audio", "Kana reading contains kanji - reading guide is not a reading"))
        if LATIN.search(kana):
            issues.append(("HIGH", "ja_audio", f"Latin letters in kana reading: {''.join(LATIN.findall(kana))[:30]}"))
        if not JP_ANY.search(kana):
            issues.append(("CRITICAL", "ja_audio", "Kana field has no Japanese at all - Japanese voice will mispronounce"))
    if not JP_ANY.search(kanji):
        issues.append(("HIGH", "ja_text", "Headword has no Japanese characters"))
    if "/" in kanji:
        issues.append(("LOW", "ja_text", "Kanji field has '/' alternatives"))
    if kanji_counter[kanji.strip()] > 1:
        issues.append(("MEDIUM", "ja_meaning", f"Same Japanese headword used by {kanji_counter[kanji.strip()]} entries"))

    # kana <-> romaji consistency (does the reading match the romanization?)
    if kana and romaji and not KANJI.search(kana) and not LATIN.search(kana):
        first_kana = kana.split("/")[0]
        first_rom = romaji.split("/")[0]
        k = norm_romaji(kana_to_romaji(first_kana))
        rr = norm_romaji(first_rom)
        sim = similarity(k, rr)
        if sim < 0.45:
            issues.append(("HIGH", "ja_audio", f"Kana reading and romaji disagree (kana->'{k}' vs romaji '{rr}', sim={sim:.2f})"))
        elif sim < 0.7:
            issues.append(("LOW", "ja_audio", f"Kana/romaji partial mismatch (kana->'{k}' vs '{rr}', sim={sim:.2f})"))

    # kanji field reading vs kana when kanji is pure katakana
    head = kanji.split("/")[0].split("（")[0].split("(")[0].strip()
    if head and re.fullmatch(r"[\u30A0-\u30FF\u30FC・\s]+", head) and kana and not KANJI.search(kana):
        if norm_romaji(kana_to_romaji(head)) and similarity(norm_romaji(kana_to_romaji(head)),
                                                           norm_romaji(kana_to_romaji(kana.split('/')[0]))) < 0.5:
            issues.append(("HIGH", "ja_audio", "Katakana headword and kana reading don't match"))

    # ===== ENGLISH =====
    if not eng.strip():
        issues.append(("CRITICAL", "en_audio", "Empty English"))

    # ===== EXAMPLES =====
    for f, rx in (("example_ja", JP_ANY), ("example_ur", re.compile(r"[\u0600-\u06FF]"))):
        if not rx.search(r[f] or ""):
            issues.append(("MEDIUM", f, "Example sentence missing correct script"))

    return issues

def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=30)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM entries ORDER BY id")]
    urdu_counter = Counter((r["urdu_script"] or "").strip() for r in rows)
    kanji_counter = Counter((r["japanese_kanji"] or "").strip() for r in rows)

    sev_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    report, by_sev, by_field, by_model = [], Counter(), Counter(), defaultdict(Counter)
    for r in rows:
        iss = audit_row(r, urdu_counter, kanji_counter)
        worst = max((sev_rank[s] for s, _, _ in iss), default=0)
        grade = {4: "FAIL", 3: "FAIL", 2: "WARN", 1: "OK*", 0: "PASS"}[worst]
        by_model[r.get("model") or "?"][grade] += 1
        for s, f, _ in iss:
            by_sev[s] += 1
            by_field[f] += 1
        report.append({"id": r["id"], "category": r["category"], "english": r["english"],
                       "japanese_kanji": r["japanese_kanji"], "japanese_kana": r["japanese_kana"],
                       "japanese_romaji": r["japanese_romaji"], "urdu_script": r["urdu_script"],
                       "urdu_roman": r["urdu_roman"], "model": r.get("model"),
                       "grade": grade, "issues": [{"severity": s, "field": f, "msg": m} for s, f, m in iss]})

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    grades = Counter(x["grade"] for x in report)
    print(f"TOTAL ENTRIES: {len(rows)}")
    print("GRADES:", dict(grades))
    print("ISSUES BY SEVERITY:", dict(by_sev))
    print("ISSUES BY FIELD:", dict(by_field))
    print("GRADES BY MODEL:")
    for m, c in by_model.items():
        print(f"   {m:<18} {dict(c)}")
    print("\nGRADES BY CATEGORY:")
    cat = defaultdict(Counter)
    for x in report:
        cat[x["category"]][x["grade"]] += 1
    for k, v in cat.items():
        print(f"   {k:<12} {dict(v)}")
    print(f"\nFull report: {OUT_JSON}")

if __name__ == "__main__":
    main()
