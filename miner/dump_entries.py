import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
rep = json.loads((Path(__file__).resolve().parent.parent / "data" / "audit_report.json").read_text(encoding="utf-8"))
out = []
for r in rep:
    out.append(f"{r['id']}|{r['category'][:4]}|{r['grade']}|{r['english']}|{r['japanese_kanji']}|{r['japanese_kana']}|{r['japanese_romaji']}|{r['urdu_script']}|{r['urdu_roman']}")
Path(__file__).resolve().parent.parent.joinpath("data", "audit_dump.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out))
