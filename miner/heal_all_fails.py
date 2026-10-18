import sqlite3
import json

DB_PATH = 'data/dictionary.db'
ASSET_JSON_PATH = 'app/assets/dictionary.json'

FAILS_HEALING = {
    7: {
        'japanese_kanji': 'データベース',
        'japanese_kana': 'データベース',
        'japanese_romaji': 'dētabēsu',
        'urdu_script': 'ڈیٹا بیس',
        'urdu_roman': 'data base'
    },
    15: {
        'japanese_kanji': '輸出証明書',
        'japanese_kana': 'ゆしゅつしょうめいしょ',
        'japanese_romaji': 'yushutsu shōmeisho',
        'urdu_script': 'برآمدی سرٹیفکیٹ',
        'urdu_roman': 'baramadi certificate'
    },
    25: {
        'japanese_kanji': '引き出し',
        'japanese_kana': 'ひきだし',
        'japanese_romaji': 'hikidashi',
        'urdu_script': 'رقم نکلوانا / رقم کی واپسی',
        'urdu_roman': 'raqam nikalwana'
    },
    28: {
        'japanese_kanji': 'ローン / 融資',
        'japanese_kana': 'ローン / ゆうし',
        'japanese_romaji': 'rōn / yūshi',
        'urdu_script': 'قرضہ',
        'urdu_roman': 'qarzah'
    },
    49: {
        'japanese_kanji': 'サプライヤー / 供給業者',
        'japanese_kana': 'サプライヤー / きょうきゅうぎょうしゃ',
        'japanese_romaji': 'sapuraiyā / kyōkyū gyōsha',
        'urdu_script': 'سپلائر / مال فراہم کنندہ',
        'urdu_roman': 'supplier / faraham kunandah'
    },
    72: {
        'japanese_kanji': 'バックアップ',
        'japanese_kana': 'バックアップ',
        'japanese_romaji': 'bakkuappu',
        'urdu_script': 'بیک اپ',
        'urdu_roman': 'backup'
    },
    79: {
        'japanese_kanji': '機能',
        'japanese_kana': 'きのう',
        'japanese_romaji': 'kinō',
        'urdu_script': 'خصوصیت',
        'urdu_roman': 'khasoosiyat'
    },
    95: {
        'japanese_kanji': '出張',
        'japanese_kana': 'しゅっちょう',
        'japanese_romaji': 'shucchō',
        'urdu_script': 'کاروباری دورہ / دفتری سفر',
        'urdu_roman': 'karobari daura / daftari safar'
    },
    100: {
        'japanese_kanji': 'フィードバック',
        'japanese_kana': 'フィードバック',
        'japanese_romaji': 'fīdobakku',
        'urdu_script': 'فیڈ بیک / رائے',
        'urdu_roman': 'feedback / raye'
    },
    104: {
        'japanese_kanji': 'タイミングベルト',
        'japanese_kana': 'タイミングベルト',
        'japanese_romaji': 'taimingu beruto',
        'urdu_script': 'ٹائمنگ بیلٹ',
        'urdu_roman': 'timing belt'
    },
    110: {
        'japanese_kanji': 'ヘッドライト',
        'japanese_kana': 'ヘッドライト',
        'japanese_romaji': 'heddoraito',
        'urdu_script': 'ہیڈ لائٹ',
        'urdu_roman': 'headlight'
    },
    131: {
        'japanese_kanji': '資本利得',
        'japanese_kana': 'しほんりとく',
        'japanese_romaji': 'shihon ritoku',
        'urdu_script': 'سرمایہ دارانہ منافع',
        'urdu_roman': 'sarmaya darana munafa'
    },
    155: {
        'japanese_kanji': '実現可能性調査',
        'japanese_kana': 'じつげんかのうせいちょうさ',
        'japanese_romaji': 'jitsugen kanōsei chōsa',
        'urdu_script': 'امکانی مطالعہ / فزیبلٹی رپورٹ',
        'urdu_roman': 'imkani mutala\'a / feasibility report'
    },
    162: {
        'japanese_kanji': '暗号化',
        'japanese_kana': 'あんごうか',
        'japanese_romaji': 'angōka',
        'urdu_script': 'انکرپشن / رمز نگاری',
        'urdu_roman': 'encryption / ramz nigari'
    },
    169: {
        'japanese_kanji': 'マイクロサービス',
        'japanese_kana': 'マイクロサービス',
        'japanese_romaji': 'maikurosābisu',
        'urdu_script': 'مائیکرو سروسز',
        'urdu_roman': 'microservices'
    },
    180: {
        'japanese_kanji': '年間賞与 / ボーナス',
        'japanese_kana': 'ねんかんしょうよ / ボーナス',
        'japanese_romaji': 'nenkan shōyo / bōnasu',
        'urdu_script': 'سالانہ بونس',
        'urdu_roman': 'salahna bonus'
    },
    182: {
        'japanese_kanji': '病気休暇 / 病欠',
        'japanese_kana': 'びょうききゅうか / びょうけつ',
        'japanese_romaji': 'byōki kyūka / byōketsu',
        'urdu_script': 'بیماری کی رخصت',
        'urdu_roman': 'beemari ki rukhsat'
    },
    183: {
        'japanese_kanji': '産休 / 出産休暇',
        'japanese_kana': 'さんきゅう / しゅっさんきゅうか',
        'japanese_romaji': 'sankyū / shussan kyūka',
        'urdu_script': 'زچگی کی رخصت',
        'urdu_roman': 'zachgi ki rukhsat'
    },
    184: {
        'japanese_kanji': '育休 / 育児休暇',
        'japanese_kana': 'いくきゅう / いくじきゅうか',
        'japanese_romaji': 'ikukyū / ikuji kyūka',
        'urdu_script': 'پدرانہ رخصت',
        'urdu_roman': 'pidarana rukhsat'
    },
    192: {
        'japanese_kanji': '人事',
        'japanese_kana': 'じんじ',
        'japanese_romaji': 'jinji',
        'urdu_script': 'انسانی وسائل / ایچ آر',
        'urdu_roman': 'insani wasail / HR'
    },
    195: {
        'japanese_kanji': '労働安全',
        'japanese_kana': 'ろうどうあんぜん',
        'japanese_romaji': 'rōdō anzen',
        'urdu_script': 'پیشہ ورانہ تحفظ',
        'urdu_roman': 'peshawarana tahaffuz'
    },
    220: {
        'japanese_kanji': 'REST API（レストエーピーアイ）',
        'japanese_kana': 'レストエーピーアイ',
        'japanese_romaji': 'resuto ēpīai',
        'urdu_script': 'ریسٹ اے پی آئی',
        'urdu_roman': 'REST API'
    },
    236: {
        'japanese_kanji': 'アンチロック・ブレーキ・システム',
        'japanese_kana': 'アンチロック・ブレーキ・システム',
        'japanese_romaji': 'anchirokku burēki shisutemu',
        'urdu_script': 'اینٹی لاک بریکنگ سسٹم',
        'urdu_roman': 'anti-lock braking system'
    },
    248: {
        'japanese_kanji': 'タイミングチェーン',
        'japanese_kana': 'タイミングチェーン',
        'japanese_romaji': 'taimingu chēn',
        'urdu_script': 'ٹائمنگ چین',
        'urdu_roman': 'timing chain'
    },
    252: {
        'japanese_kanji': '燃料フィルター',
        'japanese_kana': 'ねんりょうフィルター',
        'japanese_romaji': 'nenryō firutā',
        'urdu_script': 'فیول فلٹر',
        'urdu_roman': 'fuel filter'
    },
    269: {
        'japanese_kanji': 'データウェアハウス',
        'japanese_kana': 'データウェアハウス',
        'japanese_romaji': 'dēta weahausu',
        'urdu_script': 'ڈیٹا ویئر ہاؤس',
        'urdu_roman': 'data warehouse'
    },
    270: {
        'japanese_kanji': 'スキーマ移行',
        'japanese_kana': 'スキーマいこう',
        'japanese_romaji': 'sukīma ikō',
        'urdu_script': 'اسکیما مائیگریشن',
        'urdu_roman': 'schema migration'
    },
    279: {
        'japanese_kanji': 'デフォルト率',
        'japanese_kana': 'デフォルトりつ',
        'japanese_romaji': 'deforuto ritsu',
        'urdu_script': 'ڈیفالٹ کی شرح',
        'urdu_roman': 'default ki sharah'
    },
    292: {
        'japanese_kanji': '年次有給休暇手当',
        'japanese_kana': 'ねんじゆうきゅうきゅうかてあて',
        'japanese_romaji': 'nenji yūkyū kyūka teate',
        'urdu_script': 'سالانہ رخصت کا الاؤنس',
        'urdu_roman': 'salahna rukhsat ka allowance'
    },
    305: {
        'japanese_kanji': '複合一貫輸送',
        'japanese_kana': 'ふくごういっかんゆそう',
        'japanese_romaji': 'fukugō ikkan yusō',
        'urdu_script': 'کثیر ذرائع مواصلات',
        'urdu_roman': 'kaseer zaraye mwasilat'
    },
    317: {
        'japanese_kanji': '診療所 / クリニック',
        'japanese_kana': 'しんりょうじょ / クリニック',
        'japanese_romaji': 'shinryōjo / kurinikku',
        'urdu_script': 'طبی کلینک',
        'urdu_roman': 'tibbi clinic'
    },
    318: {
        'japanese_kanji': '健康保険証',
        'japanese_kana': 'けんこうほけんしょう',
        'japanese_romaji': 'kenkō hoken shō',
        'urdu_script': 'صحت کارڈ / ہیلتھ انشورنس کارڈ',
        'urdu_roman': 'sehat card / health insurance card'
    },
    321: {
        'japanese_kanji': '重要業績評価指標',
        'japanese_kana': 'じゅうようぎょうせきひょうかしひょう',
        'japanese_romaji': 'jūyō gyōseki hyōka shihyō',
        'urdu_script': 'اہم کارکردگی کے اشاریے',
        'urdu_roman': 'aham karkardagi ke isharay'
    },
    322: {
        'japanese_kanji': '薬局',
        'japanese_kana': 'やっきょく',
        'japanese_romaji': 'yakkyoku',
        'urdu_script': 'فارمیسی / میڈیکل اسٹور',
        'urdu_roman': 'pharmacy / medical store'
    },
    323: {
        'japanese_kanji': '診断書 / 医療証明書',
        'japanese_kana': 'しんだんしょ / いりょうしょうめいしょ',
        'japanese_romaji': 'shindansho / iryō shōmeisho',
        'urdu_script': 'طبی سرٹیفکیٹ / میڈیکل سرٹیفکیٹ',
        'urdu_roman': 'tibbi certificate'
    },
    327: {
        'japanese_kanji': '外来',
        'japanese_kana': 'がいらい',
        'japanese_romaji': 'gairai',
        'urdu_script': 'او پی ڈی / بیرونی مریضوں کا شعبہ',
        'urdu_roman': 'OPD / bairooni mareezon ka shoba'
    },
    333: {
        'japanese_kanji': '専門医',
        'japanese_kana': 'せんもんい',
        'japanese_romaji': "senmon'i",
        'urdu_script': 'ماہر معالج / اسپیشلسٹ ڈاکٹر',
        'urdu_roman': 'mahir-e-mualij / specialist doctor'
    },
    343: {
        'japanese_kanji': '仲裁条項',
        'japanese_kana': 'ちゅうさいじょうこう',
        'japanese_romaji': 'chūsai jōkō',
        'urdu_script': 'ثالثی کی شق',
        'urdu_roman': 'salisi ki shaq'
    }
}

def heal():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 60000;")
    cur = conn.cursor()

    count = 0
    for id_val, rep in FAILS_HEALING.items():
        cur.execute("""
            UPDATE entries 
            SET japanese_kanji = ?, japanese_kana = ?, japanese_romaji = ?,
                urdu_script = ?, urdu_roman = ?
            WHERE id = ?
        """, (
            rep['japanese_kanji'], rep['japanese_kana'], rep['japanese_romaji'],
            rep['urdu_script'], rep['urdu_roman'], id_val
        ))
        count += cur.rowcount

    conn.commit()
    print(f"Healed {count} entries in {DB_PATH}.")

    conn.row_factory = sqlite3.Row
    all_entries = [dict(row) for row in conn.execute("SELECT * FROM entries ORDER BY id").fetchall()]
    conn.close()

    with open(ASSET_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(all_entries)} pristine entries to {ASSET_JSON_PATH}.")

if __name__ == '__main__':
    heal()
