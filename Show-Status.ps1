# Show Trilingual Dictionary & Miner Status
$d = "$PSScriptRoot"
if (Test-Path "$d\..\data\dictionary.db") {
    $dbPath = "$d\..\data\dictionary.db"
    $appJson = "$d\..\app\assets\dictionary.json"
} else {
    $dbPath = "$d\data\dictionary.db"
    $appJson = "$d\app\assets\dictionary.json"
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Trilingual Dictionary & Miner Live Status" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

python -c "
import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect(r'$dbPath')
cur = con.cursor()
total = cur.execute('SELECT count(*) FROM entries').fetchone()[0]
print(f'\n📊 Total Verified Words in DB: {total}')
print('\n📁 Breakdown by Domain:')
for cat, cnt in cur.execute('SELECT category, count(*) FROM entries GROUP BY category ORDER BY count(*) DESC'):
    print(f'   • {cat:<15}: {cnt} words')

print('\n🕒 Last 5 Mined Words:')
for r in cur.execute('SELECT category, english, japanese_kanji, urdu_script FROM entries ORDER BY id DESC LIMIT 5'):
    print(f'   [{r[0]}] {r[1]} -> {r[2]} | {r[3]}')
"

Write-Host ""
Write-Host "Ollama Worker Status:" -ForegroundColor Cyan
try {
    $ps = ollama ps 2>$null
    if ($ps) { $ps } else { Write-Host "No active model in VRAM right now." -ForegroundColor DarkGray }
} catch {
    Write-Host "Ollama status unavailable." -ForegroundColor DarkGray
}
Write-Host "==========================================================" -ForegroundColor Cyan
