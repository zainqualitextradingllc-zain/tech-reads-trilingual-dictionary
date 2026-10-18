# Start Trilingual Dictionary Mobile App
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Trilingual Dictionary (English • Japanese • Urdu)" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Options to view your app:" -ForegroundColor Green
Write-Host "1. Scan the QR code using 'Expo Go' app on your Android or iPhone" -ForegroundColor White
Write-Host "2. Press 'w' in terminal to open in Chrome / Edge browser immediately" -ForegroundColor White
Write-Host "3. Press 'a' to open in Android Emulator (if installed)" -ForegroundColor White
Write-Host ""

if (Test-Path "$PSScriptRoot\app") {
    Set-Location "$PSScriptRoot\app"
} elseif (Test-Path "$PSScriptRoot\..\app") {
    Set-Location "$PSScriptRoot\..\app"
}

npx expo start
