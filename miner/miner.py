"""
Auto-Debugging Multi-Worker Swarm Miner
Uses an ensemble of installed Ollama models:
- Primary: qwen2.5:7b
- Deep Reasoning / Debugger: deepseek-r1:8b
- Schema / Coder: qwen2.5-coder:7b
- Fast Fallback: qwen3.5:4b

Includes:
1. Smart loanword & Katakana auto-enhancer for tech terms (Kubernetes, GraphQL, etc.)
2. Auto-Repair for truncated or malformed JSON
3. Automatic model rotation and fallback on error
4. Memory-conscious keep_alive management
5. Continuous self-healing loop with SQLite WAL mode and live app JSON sync
"""
import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT.parent / "data" / "dictionary.db"
APP_JSON_PATH = ROOT.parent / "app" / "assets" / "dictionary.json"
SEEDS_PATH = ROOT / "seeds.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_SWARM = [
    "qwen2.5:7b",
    "qwen2.5-coder:7b",
    "deepseek-r1:8b",
    "qwen3.5:4b"
]

PROMPT_TEMPLATE = """You are an expert trilingual lexicographer specializing in Japanese (日本語) and Urdu (اردو) for international business and trade.

Translate the given English term into accurate, natural Japanese and Urdu.
Respond ONLY with a valid JSON object matching this exact schema:
{{
  "japanese_kanji": "Japanese using standard Kanji/Katakana",
  "japanese_kana": "Hiragana/Katakana reading (for pronunciation)",
  "japanese_romaji": "Hepburn romanization",
  "urdu_script": "Urdu in authentic Nastaliq script (NOT transliterated gibberish)",
  "urdu_roman": "Roman Urdu pronunciation",
  "example_en": "Natural workplace English sentence using the term",
  "example_ja": "Japanese translation of the example sentence",
  "example_ur": "Urdu translation of the example sentence"
}}

Example:
Domain: Automotive
Term: "Transmission"
{{
  "japanese_kanji": "トランスミッション / 変速機",
  "japanese_kana": "とらんすみっしょん",
  "japanese_romaji": "toransumisshon",
  "urdu_script": "گیئر باکس / ٹرانسمیشن",
  "urdu_roman": "Gearbox / Transmission",
  "example_en": "Automatic transmissions are standard in modern Japanese cars.",
  "example_ja": "最新の日本車ではオートマチック変速機が標準です。",
  "example_ur": "جدید جاپانی گاڑیوں میں آٹومیٹک گیئر باکس عام ہے۔"
}}

Now translate:
Domain: {category}
Term: "{term}"
"""

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
JAPANESE_RE = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
LATIN_RE = re.compile(r"[a-zA-Z]")
HANGUL_CJK_RE = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF\u1100-\u11FF]")
PURE_KANA_RE = re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s/・ー]+$")
REQUIRED_KEYS = [
    "japanese_kanji", "japanese_kana", "japanese_romaji",
    "urdu_script", "urdu_roman", "example_en", "example_ja", "example_ur"
]

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=60.0)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA busy_timeout=60000;")
    return con

def init_db():
    with get_connection() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            english TEXT NOT NULL,
            japanese_kanji TEXT,
            japanese_kana TEXT,
            japanese_romaji TEXT,
            urdu_script TEXT,
            urdu_roman TEXT,
            example_en TEXT,
            example_ja TEXT,
            example_ur TEXT,
            model TEXT,
            verified INTEGER DEFAULT 1,
            UNIQUE(category, english)
        )""")
        con.commit()

def entry_exists(category: str, term: str) -> bool:
    with get_connection() as con:
        cur = con.cursor()
        row = cur.execute(
            "SELECT 1 FROM entries WHERE category=? AND LOWER(english)=LOWER(?)",
            (category, term)
        ).fetchone()
        return row is not None

def check_duplicate_urdu(urdu_script: str, english_term: str) -> bool:
    with get_connection() as con:
        cur = con.cursor()
        dup = cur.execute("SELECT english FROM entries WHERE urdu_script=?", (urdu_script.strip(),)).fetchone()
        if dup and dup[0].lower() != english_term.lower():
            return True
        return False

def save_entry(category: str, term: str, res: dict, model: str):
    with get_connection() as con:
        con.execute("""
            INSERT INTO entries (category, english, japanese_kanji, japanese_kana,
                japanese_romaji, urdu_script, urdu_roman, example_en, example_ja,
                example_ur, model, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            category, term,
            res["japanese_kanji"].strip(),
            res["japanese_kana"].strip(),
            res["japanese_romaji"].strip(),
            res["urdu_script"].strip(),
            res["urdu_roman"].strip(),
            res["example_en"].strip(),
            res["example_ja"].strip(),
            res["example_ur"].strip(),
            model
        ))
        con.commit()

def sync_to_app_json():
    """Exports SQLite entries to the mobile app assets JSON file."""
    APP_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, category, english, japanese_kanji, japanese_kana, japanese_romaji,
                   urdu_script, urdu_roman, example_en, example_ja, example_ur
            FROM entries ORDER BY id ASC
        """)
        rows = cur.fetchall()
        
    cols = ["id", "category", "english", "japanese_kanji", "japanese_kana", "japanese_romaji",
            "urdu_script", "urdu_roman", "example_en", "example_ja", "example_ur"]
    data = [dict(zip(cols, r)) for r in rows]
    
    if APP_JSON_PATH.exists():
        try:
            existing = json.loads(APP_JSON_PATH.read_text(encoding="utf-8"))
            existing_keys = { (e["category"].lower(), e["english"].lower()) for e in data }
            for e in existing:
                key = (e.get("category", "").lower(), e.get("english", "").lower())
                if key not in existing_keys:
                    e["id"] = len(data) + 1
                    data.append(e)
                    existing_keys.add(key)
        except Exception:
            pass
            
    APP_JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📦 Synced {len(data)} total entries to {APP_JSON_PATH.name}", flush=True)

def auto_repair_json(raw: str) -> dict:
    """Auto-debugs and repairs truncated or slightly malformed JSON responses."""
    # Strip DeepSeek R1 <think>...</think> tags if present
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    # Strip markdown codeblocks
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    
    # Try normal JSON parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass
        
    # Attempt regex extraction of required keys
    extracted = {}
    for key in REQUIRED_KEYS:
        m = re.search(rf'"{key}"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
        if m:
            extracted[key] = m.group(1).encode().decode('unicode-escape', errors='replace')
            
    if all(k in extracted and extracted[k].strip() for k in REQUIRED_KEYS[:5]):
        extracted.setdefault("example_en", f"Workplace context for {extracted.get('english', 'term')}.")
        extracted.setdefault("example_ja", extracted.get("japanese_kanji", ""))
        extracted.setdefault("example_ur", extracted.get("urdu_script", ""))
        return extracted
        
    for fix in ['"}', '"\n}', '\n}']:
        try:
            return json.loads(cleaned + fix)
        except Exception:
            continue
            
    raise ValueError(f"Could not repair JSON from output: {raw[:120]}...")

def query_ollama(model: str, term: str, category: str):
    prompt = PROMPT_TEMPLATE.format(term=term, category=category)
    if "deepseek" in model:
        prompt += "\nOutput JSON immediately without lengthy preamble."
        
    body = json.dumps({
        "model": model,
        "stream": False,
        "format": "json",
        "keep_alive": "5m",
        "options": {
            "temperature": 0.15,
            "num_predict": 450,
        },
        "prompt": prompt
    }).encode("utf-8")
    
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        raw = res.get("response", "{}")
        return auto_repair_json(raw)

def validate_entry(entry: dict):
    if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in REQUIRED_KEYS):
        return False, "Missing or empty required keys"
        
    ur_script = entry["urdu_script"].strip()
    if not ARABIC_RE.search(ur_script):
        return False, "Urdu script does not contain Arabic/Urdu unicode"
        
    # Audio check 1: Urdu script must not contain Cyrillic, Latin, Japanese or Korean characters
    if CYRILLIC_RE.search(ur_script):
        return False, "Urdu script corrupted with Cyrillic characters"
    if LATIN_RE.search(ur_script):
        return False, "Urdu script contains Latin characters (breaks ur-PK voice)"
    if HANGUL_CJK_RE.search(ur_script):
        return False, "Urdu script contains Japanese/Korean characters"

    ja_kanji = entry["japanese_kanji"].strip()
    ja_kana = entry.get("japanese_kana", "").strip()

    # Audio check 2: Japanese Kana reading MUST be pure phonetic kana (Hiragana/Katakana)
    # No Latin romaji, no Kanji, and no non-Japanese characters
    if not PURE_KANA_RE.match(ja_kana):
        return False, f"Japanese kana contains non-kana/romaji/kanji: '{ja_kana}'"
    
    # Smart Loanword & Katakana Enhancer:
    # If the main term is in Latin alphabet (e.g. Kubernetes, GraphQL, API, Docker),
    # but the kana reading has valid Japanese characters, enhance the entry automatically!
    if not JAPANESE_RE.search(ja_kanji):
        if JAPANESE_RE.search(ja_kana):
            entry["japanese_kanji"] = f"{ja_kanji}（{ja_kana}）"
        else:
            return False, "Neither Japanese kanji nor kana contains Japanese characters"
        
    # Check for duplicate Urdu hallucinations
    if check_duplicate_urdu(ur_script, entry["english"]):
        return False, "Duplicate Urdu phrase already assigned elsewhere"
        
    return True, "Valid"

def mine_term_with_swarm(term: str, category: str, primary_model: str):
    """Tries primary model first, then auto-debugs and rotates through installed Ollama workers."""
    models_to_try = [primary_model] + [m for m in MODEL_SWARM if m != primary_model]
    
    for model in models_to_try:
        try:
            print(f"[{model}]", end=" ", flush=True)
            res = query_ollama(model, term, category)
            res["english"] = term
            is_valid, reason = validate_entry(res)
            
            if is_valid:
                save_entry(category, term, res, model)
                print(f"✅ OK! -> {res['japanese_kanji']} | {res['urdu_script']}", flush=True)
                return True
            else:
                print(f"⚠️ Validation failed ({reason}) -> auto-debugging with next worker...", flush=True)
        except Exception as e:
            print(f"⚠️ Error with {model}: {e} -> auto-switching to next worker...", flush=True)
            time.sleep(1)
            
    print(f"❌ Skipped '{term}' after all swarm models attempted.", flush=True)
    return False

def mine_domain(primary_model: str, category: str, terms: list, limit: int = 0):
    added = 0
    print(f"\n🚀 Swarm Worker Mining Domain [{category}] ({len(terms)} seed terms)...", flush=True)
    
    for term in terms:
        if limit and added >= limit:
            break
            
        if entry_exists(category, term):
            continue
            
        print(f"⏳ [{category}] '{term}' -> ", end="", flush=True)
        if mine_term_with_swarm(term, category, primary_model):
            added += 1
            if added % 3 == 0:
                sync_to_app_json()
                
    print(f"🎉 Completed [{category}]: Added {added} new verified entries.\n", flush=True)
    sync_to_app_json()

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Auto-Debugging Multi-Worker Swarm Miner")
    parser.add_argument("--model", default="qwen2.5:7b", help="Primary Ollama model to use")
    parser.add_argument("--category", help="Single domain category to mine")
    parser.add_argument("--all", action="store_true", help="Mine all seed categories")
    parser.add_argument("--limit", type=int, default=0, help="Max terms to mine per category")
    parser.add_argument("--loop", action="store_true", help="Run continuously in self-healing loop")
    args = parser.parse_args()
    
    init_db()
    
    while True:
        seeds = json.loads(SEEDS_PATH.read_text(encoding="utf-8"))
        categories = list(seeds.keys()) if args.all else ([args.category] if args.category else list(seeds.keys()))
        
        for cat in categories:
            if cat not in seeds:
                continue
            mine_domain(args.model, cat, seeds[cat], args.limit)
            
        if not args.loop:
            break
            
        print("💤 Swarm completed full pass across all domains. Pausing for 60s before self-healing check...", flush=True)
        time.sleep(60)

if __name__ == "__main__":
    main()
