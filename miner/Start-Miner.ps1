# Start Trilingual AI Data Miner via PowerShell & Ollama
param(
    [string]$Model = "qwen2.5:7b",
    [string]$Category = "",
    [switch]$All = $true,
    [int]$Limit = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Trilingual Data Miner Worker (PowerShell + Ollama)" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Ollama is running
try {
    $models = (Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 3).models.name
    Write-Host "[Ollama] Connected. Active model: $Model" -ForegroundColor Green
} catch {
    Write-Host "[Ollama] Starting local Ollama service in background..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Minimized
    Start-Sleep -Seconds 4
}

# Resolve miner directory accurately whether run from root or miner folder
if (Test-Path "$PSScriptRoot\miner.py") {
    Set-Location $PSScriptRoot
} elseif (Test-Path "$PSScriptRoot\miner\miner.py") {
    Set-Location "$PSScriptRoot\miner"
}

$argsList = @("miner.py", "--model", $Model)
if ($All) {
    $argsList += "--all"
} elseif ($Category) {
    $argsList += "--category", $Category
}
if ($Limit -gt 0) {
    $argsList += "--limit", $Limit
}

Write-Host "Running: python $($argsList -join ' ')" -ForegroundColor Cyan
python -u @argsList
