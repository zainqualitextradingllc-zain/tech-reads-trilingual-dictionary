import sqlite3
import json

con = sqlite3.connect('data/dictionary.db')
con.execute("PRAGMA journal_mode=WAL;")
con.execute("PRAGMA busy_timeout=60000;")

PATCHES = {
    365: {
        'japanese_kanji': 'イベント駆動型アーキテクチャ',
        'japanese_kana': 'イベントくどうがたアーキテクチャ',
        'japanese_romaji': 'ibento kudōgata ākitekucha',
        'urdu_script': 'ایونٹ ڈریون فن تعمیر',
        'urdu_roman': 'event-driven architecture'
    },
    368: {
        'japanese_kanji': 'メモリリーク',
        'japanese_kana': 'メモリリーク',
        'japanese_romaji': 'memorī rīku',
        'urdu_script': 'میموری لیک',
        'urdu_roman': 'memory leak'
    },
    397: {
        'japanese_kanji': 'ハイブリッドワークモデル',
        'japanese_kana': 'ハイブリッドワークモデル',
        'japanese_romaji': 'haibriddo wāku moderu',
        'urdu_script': 'ہائبرڈ ورک ماڈل',
        'urdu_roman': 'hybrid work model'
    },
    417: {
        'japanese_kanji': '超音波検査 / エコー検査',
        'japanese_kana': 'ちょうおんぱけんさ / エコーけんさ',
        'japanese_romaji': 'chōonpa kensa / ekō kensa',
        'urdu_script': 'الٹراساؤنڈ اسکین',
        'urdu_roman': 'ultrasound scan'
    }
}

for id_val, patch in PATCHES.items():
    con.execute("""
        UPDATE entries
        SET japanese_kanji = ?, japanese_kana = ?, japanese_romaji = ?,
            urdu_script = ?, urdu_roman = ?
        WHERE id = ?
    """, (
        patch['japanese_kanji'], patch['japanese_kana'], patch['japanese_romaji'],
        patch['urdu_script'], patch['urdu_roman'], id_val
    ))

con.commit()

con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute("SELECT * FROM entries ORDER BY id").fetchall()]
con.close()

with open('app/assets/dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f"Patched 4 entries and synced {len(rows)} entries to dictionary.json")
