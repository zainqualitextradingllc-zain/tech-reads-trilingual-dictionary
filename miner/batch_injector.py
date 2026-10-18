"""
High-Speed Verified Domain Batch Injector
Injects verified trilingual terms into SQLite (data/dictionary.db) and syncs to app/assets/dictionary.json
"""
import sqlite3
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT.parent / "data" / "dictionary.db"
APP_JSON_PATH = ROOT.parent / "app" / "assets" / "dictionary.json"

BATCH_ENTRIES = [
  # --- LOGISTICS & TRADE ---
  {
    "category": "Logistics",
    "english": "Bill of Lading (B/L)",
    "japanese_kanji": "船荷証券（B/L）",
    "japanese_kana": "ふなにしょうけん",
    "japanese_romaji": "funani shōken",
    "urdu_script": "بل آف لیڈنگ (بار برداری کا پروانہ)",
    "urdu_roman": "Bill of Lading / Bar-bardari ka parwana",
    "example_en": "The original Bill of Lading is required to release the cargo at the port.",
    "example_ja": "港で貨物を引き取るには船荷証券原本が必要です。",
    "example_ur": "بندرگاہ سے سامان چھڑوانے کے لیے اصل بل آف لیڈنگ درکار ہوتا ہے۔"
  },
  {
    "category": "Logistics",
    "english": "Customs Clearance",
    "japanese_kanji": "通関手続き",
    "japanese_kana": "つうかんてつづき",
    "japanese_romaji": "tsūkan tetsuzuki",
    "urdu_script": "کسٹمز کلیئرنس",
    "urdu_roman": "Customs clearance",
    "example_en": "Customs clearance took three days due to strict inspections.",
    "example_ja": "厳格な検査のため通関手続きに3日かかりました。",
    "example_ur": "سخت جانچ پڑتال کی وجہ سے کسٹمز کلیئرنس میں تین دن لگے۔"
  },
  {
    "category": "Logistics",
    "english": "Container Freight",
    "japanese_kanji": "コンテナ貨物",
    "japanese_kana": "こんてなかもつ",
    "japanese_romaji": "kontena kamotsu",
    "urdu_script": "کنٹینر سامان / کارگو",
    "urdu_roman": "Container samaan / cargo",
    "example_en": "The container freight arrived at Yokohama port safely.",
    "example_ja": "コンテナ貨物は無事に横浜港に到着しました。",
    "example_ur": "کنٹینر کارگو بحفاظت یوکوہاما بندرگاہ پر پہنچ گیا۔"
  },
  {
    "category": "Logistics",
    "english": "Freight Forwarder",
    "japanese_kanji": "利用運送事業者 / フォワーダー",
    "japanese_kana": "ふぉわーだー",
    "japanese_romaji": "fowādā",
    "urdu_script": "فریٹ فارورڈر (سامان ترسیل ایجنٹ)",
    "urdu_roman": "Freight forwarder",
    "example_en": "Contact the freight forwarder to track the ocean shipment.",
    "example_ja": "海上貨物の追跡はフォワーダーに問い合わせてください。",
    "example_ur": "بحری مال برداری کی معلومات کے لیے فریٹ فارورڈر سے رابطہ کریں۔"
  },
  {
    "category": "Logistics",
    "english": "Certificate of Origin",
    "japanese_kanji": "原産地証明書",
    "japanese_kana": "げんさんちしょうめいしょ",
    "japanese_romaji": "gensanchi shōmeisho",
    "urdu_script": "سرٹیفکیٹ آف اوریجن (پیداواری ملک کی سند)",
    "urdu_roman": "Certificate of origin",
    "example_en": "A Certificate of Origin proves that the machinery was manufactured in Japan.",
    "example_ja": "原産地証明書は機械が日本で製造されたことを証明します。",
    "example_ur": "سرٹیفکیٹ آف اوریجن یہ ثابت کرتا ہے کہ مشینری جاپان میں تیار ہوئی تھی۔"
  },
  {
    "category": "Logistics",
    "english": "Bonded Warehouse",
    "japanese_kanji": "保税倉庫",
    "japanese_kana": "ほぜいそうこ",
    "japanese_romaji": "hozei sōko",
    "urdu_script": "بانڈڈ گودام (کسٹمز گودام)",
    "urdu_roman": "Bonded godaam",
    "example_en": "Imported goods are held in the bonded warehouse prior to duty payment.",
    "example_ja": "輸入品は関税支払い前は保税倉庫に保管されます。",
    "example_ur": "درآمد شدہ مال کسٹمز ڈیوٹی کی ادائیگی سے پہلے بانڈڈ گودام میں رکھا جاتا ہے۔"
  },
  {
    "category": "Logistics",
    "english": "Demurrage",
    "japanese_kanji": "超過保管料 / デマレージ",
    "japanese_kana": "でまれーじ",
    "japanese_romaji": "demarēji",
    "urdu_script": "ڈیمریج (اضافی تاخیری ہرجانہ)",
    "urdu_roman": "Demurrage",
    "example_en": "Clear the containers quickly to avoid demurrage charges.",
    "example_ja": "デマレージ料金の発生を避けるためコンテナを速やかに引き取ってください。",
    "example_ur": "ڈیمریج چارجز سے بچنے کے لیے کنٹینرز فوری طور پر چھڑوائیں۔"
  },

  # --- MEDICAL & HEALTHCARE ---
  {
    "category": "Medical",
    "english": "Medical Prescription",
    "japanese_kanji": "処方箋",
    "japanese_kana": "しょほうせん",
    "japanese_romaji": "shohōsen",
    "urdu_script": "ڈاکٹری نسخہ (نسخہ ادویات)",
    "urdu_roman": "Daktari nuskha",
    "example_en": "Take this medical prescription to the dispensing pharmacy.",
    "example_ja": "この処方箋を調剤薬局にお持ちください。",
    "example_ur": "یہ نسخہ قریبی میڈیکل اسٹور پر لے جائیں۔"
  },
  {
    "category": "Medical",
    "english": "Doctor Consultation",
    "japanese_kanji": "医師の診察",
    "japanese_kana": "いしのしんさつ",
    "japanese_romaji": "ishi no shinsatsu",
    "urdu_script": "ڈاکٹر سے معائنہ / مشاورت",
    "urdu_roman": "Doctor se muaina / mashawarat",
    "example_en": "An appointment is required for specialist doctor consultation.",
    "example_ja": "専門医の診察を受けるには事前予約が必要です。",
    "example_ur": "ماہر ڈاکٹر سے معائنے کے لیے پیشگی وقت لینا ضروری ہے۔"
  },
  {
    "category": "Medical",
    "english": "Emergency Room (ER)",
    "japanese_kanji": "救急診療室 / 救急外来",
    "japanese_kana": "きゅうきゅうがいらい",
    "japanese_romaji": "kyūkyū gairai",
    "urdu_script": "شعبہ ایمرجنسی / ہنگامی طبی امداد",
    "urdu_roman": "Shoba-e-emergency",
    "example_en": "He was rushed to the hospital emergency room after the accident.",
    "example_ja": "彼は事故の後すぐに病院の救急外来へ搬送されました。",
    "example_ur": "حادثے کے بعد اسے فوری طور پر ہسپتال کے ایمرجنسی روم لے جایا گیا۔"
  },
  {
    "category": "Medical",
    "english": "Blood Pressure",
    "japanese_kanji": "血圧",
    "japanese_kana": "けつあつ",
    "japanese_romaji": "ketsuatsu",
    "urdu_script": "بلڈ پریشر / فشارِ خون",
    "urdu_roman": "Blood pressure / Fishar-e-khoon",
    "example_en": "The nurse measured the patient's blood pressure and pulse.",
    "example_ja": "看護師は患者の血圧と脈拍を測定しました。",
    "example_ur": "نرس نے مریض کا بلڈ پریشر اور نبض چیک کی۔"
  },
  {
    "category": "Medical",
    "english": "Medication Side Effects",
    "japanese_kanji": "副作用",
    "japanese_kana": "ふくさよう",
    "japanese_romaji": "fukusayō",
    "urdu_script": "دوا کے منفی اثرات (سائیڈ ایفیکٹس)",
    "urdu_roman": "Dawa ke manfi asraat (Side effects)",
    "example_en": "Inform the doctor immediately if you experience side effects.",
    "example_ja": "副作用が現れた場合は速やかに医師にご相談ください。",
    "example_ur": "اگر دوا کے منفی اثرات ظاہر ہوں تو فوری ڈاکٹر سے رجوع کریں۔"
  },

  # --- LEGAL & IMMIGRATION ---
  {
    "category": "Legal",
    "english": "Certificate of Eligibility (COE)",
    "japanese_kanji": "在留資格認定証明書",
    "japanese_kana": "ざいりゅうしかくにんていしょうめいしょ",
    "japanese_romaji": "zairyū shikaku nintei shōmeisho",
    "urdu_script": "اہلیت کی سند (سی او ای - ویزا منظوری)",
    "urdu_roman": "Ahliyat ki sanad (COE)",
    "example_en": "You need the Certificate of Eligibility to apply for a Japanese work visa.",
    "example_ja": "日本の就業ビザを申請するには在留資格認定証明書が必要です。",
    "example_ur": "جاپان کے ورک ویزا کی درخواست دینے کے لیے اہلیت کی سند (سی او ای) درکار ہوتی ہے۔"
  },
  {
    "category": "Legal",
    "english": "Immigration Bureau",
    "japanese_kanji": "出入国在留管理局（入管）",
    "japanese_kana": "しゅつにゅうこくざいりゅうかんりきょく",
    "japanese_romaji": "shutsu nyūkoku zairyū kanrikyoku (Nyūkan)",
    "urdu_script": "امیگریشن بیورو / دفترِ پاسپورٹ و ویزا",
    "urdu_roman": "Immigration bureau (Nyukan)",
    "example_en": "Submit your visa extension documents to the Immigration Bureau.",
    "example_ja": "ビザ更新書類を入国管理局に提出してください。",
    "example_ur": "ویزے میں توسیع کی دستاویزات امیگریشن بیورو میں جمع کروائیں۔"
  },
  {
    "category": "Legal",
    "english": "Permanent Residency",
    "japanese_kanji": "永住権 / 永住許可",
    "japanese_kana": "えいじゅうきょか",
    "japanese_romaji": "eijū kyoka",
    "urdu_script": "مستقل رہائش (پی آر)",
    "urdu_roman": "Mustaqil rihaish (Permanent Residency)",
    "example_en": "He applied for Japanese permanent residency after living there for ten years.",
    "example_ja": "彼は10年間日本に居住した後、永住許可を申請しました。",
    "example_ur": "اس نے جاپان میں دس سال رہنے کے بعد مستقل رہائش کی درخواست دی۔"
  },
  {
    "category": "Legal",
    "english": "Power of Attorney",
    "japanese_kanji": "委任状",
    "japanese_kana": "いにんじょう",
    "japanese_romaji": "ininjō",
    "urdu_script": "مختار نامہ (پاور آف اٹارنی)",
    "urdu_roman": "Mukhtar nama (Power of Attorney)",
    "example_en": "Sign this power of attorney so the lawyer can represent your firm.",
    "example_ja": "弁護士が貴社を代理できるよう委任状に署名してください。",
    "example_ur": "اس مختار نامے پر دستخط کریں تاکہ وکیل آپ کی کمپنی کی نمائندگی کر سکے۔"
  },
  {
    "category": "Legal",
    "english": "Non-Disclosure Agreement (NDA)",
    "japanese_kanji": "秘密保持契約（NDA）",
    "japanese_kana": "ひみつほじけいやく",
    "japanese_romaji": "himitsu hoji keiyaku",
    "urdu_script": "رازداری کا معاہدہ (این ڈی اے)",
    "urdu_roman": "Razdari ka muahida (NDA)",
    "example_en": "Both companies executed a Non-Disclosure Agreement before discussing trade secrets.",
    "example_ja": "両社は企業秘密を議論する前に秘密保持契約を締結しました。",
    "example_ur": "کاروباری رازوں پر بات کرنے سے پہلے دونوں کمپنیوں نے رازداری کے معاہدے پر دستخط کیے۔"
  },

  # --- ADVANCED AUTOMOTIVE ---
  {
    "category": "Automotive",
    "english": "Hybrid Battery Pack",
    "japanese_kanji": "ハイブリッド駆動用バッテリー",
    "japanese_kana": "はいぶりっどくどうようばってりー",
    "japanese_romaji": "haiburiddo kudō-yō batterī",
    "urdu_script": "ہائبرڈ بیٹری پیک",
    "urdu_roman": "Hybrid battery pack",
    "example_en": "The Prius hybrid battery pack comes with a five-year factory warranty.",
    "example_ja": "プリウスのハイブリッドバッテリーには5年間のメーカー保証が付いています。",
    "example_ur": "پریئس ہائبرڈ بیٹری پیک کے ساتھ پانچ سال کی فیکٹری وارنٹی ہوتی ہے۔"
  },
  {
    "category": "Automotive",
    "english": "Alternator",
    "japanese_kanji": "オルタネーター / 発電機",
    "japanese_kana": "おるたねーたー",
    "japanese_romaji": "orutanētā",
    "urdu_script": "الٹرنیٹر (گاڑی کا جنریٹر)",
    "urdu_roman": "Alternator / Generator",
    "example_en": "A faulty alternator will fail to charge the 12V battery while driving.",
    "example_ja": "故障したオルタネーターは走行中にバッテリーを充電できません。",
    "example_ur": "خراب الٹرنیٹر ڈرائیونگ کے دوران بیٹری کو چارج نہیں کر پاتا۔"
  },
  {
    "category": "Automotive",
    "english": "Timing Belt",
    "japanese_kanji": "タイミングベルト",
    "japanese_kana": "たいみんぐべると",
    "japanese_romaji": "taimingu beruto",
    "urdu_script": "ٹائمنگ بیلٹ",
    "urdu_roman": "Timing belt",
    "example_en": "Replace the timing belt every 100,000 kilometers to prevent engine damage.",
    "example_ja": "エンジンの破損を防ぐため10万キロごとにタイミングベルトを交換します。",
    "example_ur": "انجن کے نقصان سے بچنے کے لیے ہر ایک لاکھ کلومیٹر پر ٹائمنگ بیلٹ تبدیل کریں۔"
  },
  {
    "category": "Automotive",
    "english": "Catalytic Converter",
    "japanese_kanji": "触媒コンバーター",
    "japanese_kana": "しょくばいこんばーたー",
    "japanese_romaji": "shokubai konbātā",
    "urdu_script": "کیٹلیٹک کنورٹر (دھواں فلٹر)",
    "urdu_roman": "Catalytic converter",
    "example_en": "The catalytic converter reduces toxic emissions in exhaust gases.",
    "example_ja": "触媒コンバーターは排気ガス中の有害物質を低減します。",
    "example_ur": "کیٹلیٹک کنورٹر ایگزاسٹ گیسوں میں سے زہریلے اثرات کو کم کرتا ہے۔"
  },
  {
    "category": "Automotive",
    "english": "Anti-lock Braking System (ABS)",
    "japanese_kanji": "アンチロック・ブレーキ・システム（ABS）",
    "japanese_kana": "あんちろっくぶれーきしすてむ",
    "japanese_romaji": "anchirokku burēki shisutemu",
    "urdu_script": "اے بی ایس بریک سسٹم",
    "urdu_roman": "ABS brake system",
    "example_en": "ABS prevents wheels from locking up during emergency braking.",
    "example_ja": "ABSは急ブレーキ時に車輪がロックするのを防ぎます。",
    "example_ur": "اے بی ایس ہنگامی بریک کے دوران پہیوں کو جام ہونے سے بچاتا ہے۔"
  },

  # --- ADVANCED SOFTWARE & CLOUD ---
  {
    "category": "Software",
    "english": "Microservices Architecture",
    "japanese_kanji": "マイクロサービスアーキテクチャ",
    "japanese_kana": "まいくろさーびすあーきてくちゃ",
    "japanese_romaji": "maikurosābisu ākitekucha",
    "urdu_script": "مائیکرو سروسز آرکیٹیکچر",
    "urdu_roman": "Microservices architecture",
    "example_en": "We decoupled the monolithic application into scalable microservices.",
    "example_ja": "モノリシックなアプリケーションを拡張性の高いマイクロサービスに分割しました。",
    "example_ur": "ہم نے پرانی ایپ کو آزاد اور جدید مائیکرو سروسز میں تقسیم کیا۔"
  },
  {
    "category": "Software",
    "english": "Continuous Integration (CI)",
    "japanese_kanji": "継続的インテグレーション（CI）",
    "japanese_kana": "けいぞくてきいんてぐれーしょん",
    "japanese_romaji": "keizokuteki integurēshon",
    "urdu_script": "مسلسل انضمام (سی آئی)",
    "urdu_roman": "Musalsal inzimam (CI)",
    "example_en": "Automated unit tests run on every pull request using CI pipelines.",
    "example_ja": "CIパイプラインにより各プルリクエストで自動テストが実行されます。",
    "example_ur": "سی آئی پائپ لائن کے ذریعے ہر پل ریکویسٹ پر آٹومیٹک ٹیسٹ چلتے ہیں۔"
  },
  {
    "category": "Software",
    "english": "REST API",
    "japanese_kanji": "RESTful API",
    "japanese_kana": "れすとえーぴーあい",
    "japanese_romaji": "resuto ēpīai",
    "urdu_script": "ریسٹ اے پی آئی",
    "urdu_roman": "REST API",
    "example_en": "The mobile app communicates with backend services via a REST API.",
    "example_ja": "モバイルアプリはREST APIを介してバックエンドサービスと通信します。",
    "example_ur": "موبائل ایپ ریسٹ اے پی آئی کے ذریعے بیک اینڈ سے رابطہ کرتی ہے۔"
  },

  # --- ADVANCED BANKING & FINANCE ---
  {
    "category": "Banking",
    "english": "Letter of Credit (L/C)",
    "japanese_kanji": "信用状（L/C）",
    "japanese_kana": "しんようじょう",
    "japanese_romaji": "shin'yōjō",
    "urdu_script": "لیٹر آف کریڈٹ (ایل سی - مالی ضمانت نامہ)",
    "urdu_roman": "Letter of Credit (L/C)",
    "example_en": "The bank issued an irrevocable Letter of Credit to guarantee international payment.",
    "example_ja": "銀行は国際決済を保証するため取消不能信用状を発行しました。",
    "example_ur": "بینک نے بین الاقوامی ادائیگی کی ضمانت کے لیے غیر منسوخ شدہ ایل سی جاری کی۔"
  },
  {
    "category": "Banking",
    "english": "Fixed Deposit (FD)",
    "japanese_kanji": "定期預金",
    "japanese_kana": "ていきよきん",
    "japanese_romaji": "teiki yokin",
    "urdu_script": "فکسڈ ڈپازٹ (میعادی کھاتہ)",
    "urdu_roman": "Fixed deposit / Meyadi khata",
    "example_en": "Fixed deposits offer a higher interest rate than standard savings accounts.",
    "example_ja": "定期預金は通常の普通預金よりも高い金利を提供します。",
    "example_ur": "فکسڈ ڈپازٹ پر عام سیونگ اکاؤنٹ سے زیادہ منافع ملتا ہے۔"
  },
  {
    "category": "Banking",
    "english": "Direct Debit / Auto-Pay",
    "japanese_kanji": "口座振替 / 自動引き落とし",
    "japanese_kana": "こうざふりかえ",
    "japanese_romaji": "kōza furikae",
    "urdu_script": "خودکار کٹوتی / آٹو پے",
    "urdu_roman": "Khudkar katoti (Auto-pay)",
    "example_en": "Monthly electricity bills are paid automatically via direct debit.",
    "example_ja": "毎月の電気料金は口座振替で自動的に支払われます。",
    "example_ur": "بجلی کے ماہانہ بل خودکار کٹوتی کے ذریعے ادا ہوتے ہیں۔"
  }
]

def run():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=60.0)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA busy_timeout=60000;")
    
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
    
    inserted = 0
    for e in BATCH_ENTRIES:
        exists = con.execute(
            "SELECT 1 FROM entries WHERE category=? AND LOWER(english)=LOWER(?)",
            (e["category"], e["english"])
        ).fetchone()
        
        if not exists:
            con.execute("""
                INSERT INTO entries (category, english, japanese_kanji, japanese_kana,
                    japanese_romaji, urdu_script, urdu_roman, example_en, example_ja,
                    example_ur, model, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'agent-verified', 1)
            """, (
                e["category"], e["english"], e["japanese_kanji"], e["japanese_kana"],
                e["japanese_romaji"], e["urdu_script"], e["urdu_roman"],
                e["example_en"], e["example_ja"], e["example_ur"]
            ))
            inserted += 1
            print(f"✅ Injected [{e['category']}] {e['english']}")
            
    con.commit()
    print(f"\n🎉 Successfully added {inserted} new verified entries to SQLite!")
    
    # Sync to JSON
    cur = con.cursor()
    cur.execute("""
        SELECT id, category, english, japanese_kanji, japanese_kana, japanese_romaji,
               urdu_script, urdu_roman, example_en, example_ja, example_ur
        FROM entries ORDER BY id ASC
    """)
    rows = cur.fetchall()
    cols = ["id", "category", "english", "japanese_kanji", "japanese_kana", "japanese_romaji",
            "urdu_script", "urdu_roman", "example_en", "example_ja", "example_ur"]
    all_data = [dict(zip(cols, r)) for r in rows]
    
    APP_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    APP_JSON_PATH.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📦 Synchronized {len(all_data)} total entries to {APP_JSON_PATH.name}!")
    con.close()

if __name__ == "__main__":
    run()
