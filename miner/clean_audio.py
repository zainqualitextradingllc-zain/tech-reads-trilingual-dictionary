import sqlite3
import json
import re

DB_PATH = 'data/dictionary.db'
ASSET_JSON_PATH = 'app/assets/dictionary.json'

KANA_REPAIRS = {
    5: {
        'japanese_kanji': 'オイル交換',
        'japanese_kana': 'オイルこうかん',
        'japanese_romaji': 'oiru kōkan'
    },
    34: {
        'japanese_kanji': '税金',
        'japanese_kana': 'ぜいきん',
        'japanese_romaji': 'zeikin'
    },
    35: {
        'japanese_kanji': '住宅ローン / 抵当権',
        'japanese_kana': 'じゅうたくローン / ていとうけん',
        'japanese_romaji': 'jūtaku rōn / teitōken'
    },
    50: {
        'japanese_kanji': '見積書',
        'japanese_kana': 'みつもりしょ',
        'japanese_romaji': 'mitsumorisho'
    },
    69: {
        'japanese_kanji': 'ソースコード',
        'japanese_kana': 'ソースコード',
        'japanese_romaji': 'sōsu kōdo'
    },
    106: {
        'japanese_kanji': '触媒コンバーター / 排気浄化装置',
        'japanese_kana': 'しょくばいコンバーター / はいきじょうかそうち',
        'japanese_romaji': 'shokubai konbātā / haiki jōka sōchi'
    },
    109: {
        'japanese_kanji': 'ホイールアライメント / 車輪調整',
        'japanese_kana': 'ホイールアライメント / しゃりんちょうせい',
        'japanese_romaji': 'hoīru araimento / sharin chōsei'
    },
    118: {
        'japanese_kanji': '船荷証券',
        'japanese_kana': 'ふなづみしょうけん',
        'japanese_romaji': 'funazumi shōken'
    },
    120: {
        'japanese_kanji': 'デビットカード',
        'japanese_kana': 'デビットカード',
        'japanese_romaji': 'debitto kādo'
    },
    121: {
        'japanese_kanji': 'ATM引き出し / 現金引き出し',
        'japanese_kana': 'エーティーエムひきだし / げんきんひきだし',
        'japanese_romaji': 'ētīemu hikidashi / genkin hikidashi'
    },
    123: {
        'japanese_kanji': '定期預金',
        'japanese_kana': 'ていきよきん',
        'japanese_romaji': 'teiki yokin'
    },
    142: {
        'japanese_kanji': 'サプライチェーン / 供給網',
        'japanese_kana': 'サプライチェーン / きょうきゅうもう',
        'japanese_romaji': 'sapurai chēn / kyōkyūmō'
    },
    146: {
        'japanese_kanji': '通関手続き',
        'japanese_kana': 'つうかんてつづき',
        'japanese_romaji': 'tsūkan tetsuzuki'
    },
    155: {
        'japanese_kanji': '実現可能性調査',
        'japanese_kana': 'じつげんかのうせいちょうさ',
        'japanese_romaji': 'jitsugen kanōsei chōsa'
    },
    160: {
        'japanese_kanji': 'APIエンドポイント',
        'japanese_kana': 'エーピーアイエンドポイント',
        'japanese_romaji': 'ēpīai endopointo'
    },
    162: {
        'japanese_kanji': '暗号化',
        'japanese_kana': 'あんごうか',
        'japanese_romaji': 'angōka'
    },
    165: {
        'japanese_kanji': 'プルリクエスト',
        'japanese_kana': 'プルリクエスト',
        'japanese_romaji': 'puru rikuesuto'
    },
    171: {
        'japanese_kanji': 'コードレビュー',
        'japanese_kana': 'コードレビュー',
        'japanese_romaji': 'kōdo rebyū'
    },
    177: {
        'japanese_kanji': 'SSL証明書',
        'japanese_kana': 'エスエスエルしょうめいしょ',
        'japanese_romaji': 'esu-esu-eru shōmeisho'
    },
    180: {
        'japanese_kanji': '年間賞与 / ボーナス',
        'japanese_kana': 'ねんかんしょうよ / ボーナス',
        'japanese_romaji': 'nenkan shōyo / bōnasu'
    },
    194: {
        'japanese_kanji': '行動規範',
        'japanese_kana': 'こうどうきはん',
        'japanese_romaji': 'kōdō kihan'
    },
    195: {
        'japanese_kanji': '労働安全',
        'japanese_kana': 'ろうどうあんぜん',
        'japanese_romaji': 'rōdō anzen'
    },
    238: {
        'japanese_kanji': 'サスペンションアーム',
        'japanese_kana': 'サスペンションアーム',
        'japanese_romaji': 'sasupenshon āmu'
    },
    244: {
        'japanese_kanji': 'ヘッドガスケット',
        'japanese_kana': 'ヘッドガスケット',
        'japanese_romaji': 'heddo gasuketto'
    },
    247: {
        'japanese_kanji': 'クランクシャフト',
        'japanese_kana': 'クランクシャフト',
        'japanese_romaji': 'kuranku shafuto'
    },
    249: {
        'japanese_kanji': 'オイルフィルター',
        'japanese_kana': 'オイルフィルター',
        'japanese_romaji': 'oiru firutā'
    },
    255: {
        'japanese_kanji': '継続的デプロイ',
        'japanese_kana': 'けいぞくてきデプロイ',
        'japanese_romaji': 'keizokuteki depuroi'
    },
    266: {
        'japanese_kanji': 'リレーショナルデータベース',
        'japanese_kana': 'リレーショナルデータベース',
        'japanese_romaji': 'rirēshonaru dētabēsu'
    },
    288: {
        'japanese_kanji': '買掛金 / 未払金',
        'japanese_kana': 'かいかけきん / みばらいきん',
        'japanese_romaji': 'kaikakekin / mibaraikin'
    },
    306: {
        'japanese_kanji': '通関業者',
        'japanese_kana': 'つうかんぎょうしゃ',
        'japanese_romaji': 'tsūkan gyōsha'
    },
    339: {
        'japanese_kanji': '在留資格認定証明書',
        'japanese_kana': 'ざいりゅうしかくにんていしょうめいしょ',
        'japanese_romaji': 'zairyū shikaku nintei shōmeisho'
    },
    344: {
        'japanese_kanji': '知的財産',
        'japanese_kana': 'ちてきざいさん',
        'japanese_romaji': 'chiteki zaisan'
    },
    347: {
        'japanese_kanji': '著作権侵害',
        'japanese_kana': 'ちょさくけんしんがい',
        'japanese_romaji': 'chosakuken shingai'
    },
    349: {
        'japanese_kanji': 'コンプライアンス監査',
        'japanese_kana': 'コンプライアンスかんさ',
        'japanese_romaji': 'konpuraiansu kansa'
    },
    353: {
        'japanese_kanji': '和解合意書 / 示談書',
        'japanese_kana': 'わかいごういしょ / じだんしょ',
        'japanese_romaji': 'wakai gōisho / jidansho'
    }
}

URDU_REPAIRS = {
    54: {
        'urdu_script': 'معاہدہ',
        'urdu_roman': 'muahida'
    },
    78: {
        'urdu_script': 'ڈویلپر',
        'urdu_roman': 'developer / taraqqi dahinda'
    },
    121: {
        'urdu_script': 'اے ٹی ایم سے رقم نکلوانا',
        'urdu_roman': 'ATM se raqam nikalwana'
    },
    124: {
        'urdu_script': 'کریڈٹ اسکور',
        'urdu_roman': 'credit score'
    },
    128: {
        'urdu_script': 'براہ راست رقم کی منتقلی',
        'urdu_roman': 'barah-e-raast raqam ki muntaqili'
    },
    141: {
        'urdu_script': 'یادداشت مفاہمت',
        'urdu_roman': 'yaddasht-e-mufahimat'
    },
    156: {
        'urdu_script': 'کاروباری منصوبہ / بزنس پلان',
        'urdu_roman': 'karobari mansooba / business plan'
    },
    160: {
        'urdu_script': 'اے پی آئی اینڈ پوائنٹ',
        'urdu_roman': 'API endpoint'
    },
    177: {
        'urdu_script': 'ایس ایس ایل سرٹیفکیٹ',
        'urdu_roman': 'SSL certificate'
    },
    178: {
        'urdu_script': 'ریسپانسو ڈیزائن',
        'urdu_roman': 'responsive design'
    },
    181: {
        'urdu_script': 'آمد و رفت کا الاؤنس',
        'urdu_roman': 'aamad-o-raft ka allowance'
    },
    233: {
        'urdu_script': 'ڈرائیو شافٹ',
        'urdu_roman': 'drive shaft'
    },
    277: {
        'urdu_script': 'کریڈٹ کی حد / کریڈٹ لمیٹ',
        'urdu_roman': 'credit ki hadd / credit limit'
    },
    281: {
        'urdu_script': 'مالیاتی پالیسی',
        'urdu_roman': 'malyati policy'
    },
    303: {
        'urdu_script': 'سامان کی فہرست / کارگو مینی فیسٹ',
        'urdu_roman': 'saman ki fehrist / cargo manifest'
    },
    337: {
        'urdu_script': 'قیام کی حیثیت',
        'urdu_roman': 'qayam ki haisiat'
    },
    345: {
        'urdu_script': 'ٹریڈ مارک رجسٹریشن',
        'urdu_roman': 'trademark registration'
    }
}

def clean_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 60000;")
    cur = conn.cursor()

    updated_kana = 0
    for id_val, rep in KANA_REPAIRS.items():
        cur.execute("""
            UPDATE entries 
            SET japanese_kanji = ?, japanese_kana = ?, japanese_romaji = ?
            WHERE id = ?
        """, (rep['japanese_kanji'], rep['japanese_kana'], rep['japanese_romaji'], id_val))
        updated_kana += cur.rowcount

    updated_urdu = 0
    for id_val, rep in URDU_REPAIRS.items():
        cur.execute("""
            UPDATE entries 
            SET urdu_script = ?, urdu_roman = ?
            WHERE id = ?
        """, (rep['urdu_script'], rep['urdu_roman'], id_val))
        updated_urdu += cur.rowcount

    conn.commit()
    print(f"Applied {updated_kana} Japanese Kana repairs.")
    print(f"Applied {updated_urdu} Urdu script repairs.")

    # Re-export all entries to app/assets/dictionary.json
    conn.row_factory = sqlite3.Row
    all_entries = [dict(row) for row in conn.execute("SELECT * FROM entries ORDER BY id").fetchall()]
    conn.close()

    with open(ASSET_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(all_entries)} cleaned entries to {ASSET_JSON_PATH}")

if __name__ == '__main__':
    clean_database()
