# Live Debugger for Trilingual Dictionary Miner
$logPath = "C:\Users\zain_\.gemini\antigravity-ide\brain\2c790f0f-2539-457c-9ce2-d4d5e0062328\.system_generated\tasks\task-325.log"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Trilingual Miner Live Stream & Auto-Debugger" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Streaming live logs from background Ollama swarm..." -ForegroundColor Green
Write-Host "Press Ctrl + C anytime to exit the stream." -ForegroundColor DarkGray
Write-Host ""

if (Test-Path $logPath) {
    Get-Content -Path $logPath -Tail 25 -Wait -Encoding UTF8
} else {
    Write-Host "Log file not found at $logPath" -ForegroundColor Red
}
