# Live Miner Daemon Output Streamer
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$primaryLog = "C:\Users\zain_\.gemini\antigravity-ide\brain\2c790f0f-2539-457c-9ce2-d4d5e0062328\.system_generated\tasks\task-501.log"

if (Test-Path $primaryLog) {
    $targetLog = $primaryLog
} else {
    $targetLog = (Get-ChildItem "C:\Users\zain_\.gemini\antigravity-ide\brain\*\.system_generated\tasks\task-*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -gt 50000 } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1).FullName
}

if (-not $targetLog -or -not (Test-Path $targetLog)) {
    Write-Host "❌ Could not find active miner daemon log file." -ForegroundColor Red
    Write-Host "You can start a new miner with: .\Start-Miner.ps1" -ForegroundColor Yellow
    Exit 1
}

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🤖 Tech Reads™ Live Miner Daemon Stream" -ForegroundColor Yellow
Write-Host "   Press [Ctrl + C] anytime to exit" -ForegroundColor DarkGray
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Streaming from: $targetLog" -ForegroundColor DarkGray
Write-Host ""

Get-Content -Path $targetLog -Wait -Tail 25
