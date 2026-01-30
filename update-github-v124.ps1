# Update GitHub for v124
# Data: 18/01/2026

Write-Host "=== UPDATING GITHUB FOR v124 ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se MaxSeries.cs3 existe
$cs3File = "MaxSeries\build\MaxSeries.cs3"
if (!(Test-Path $cs3File)) {
    Write-Host "ERROR: MaxSeries.cs3 not found! Run build first." -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $cs3File).Length
Write-Host "MaxSeries.cs3 size: $fileSize bytes" -ForegroundColor Green
Write-Host ""

# 2. Git add e commit JSONs
Write-Host "1. Committing JSON updates..." -ForegroundColor Yellow
git add plugins.json
git add repo.json

git commit -m "Update plugins.json to v124 - SSSRR.ORG CDN Fix"

if ($LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit or commit failed" -ForegroundColor Yellow
}

# 3. Push
Write-Host "2. Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== GITHUB UPDATED SUCCESSFULLY ===" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub Release: https://github.com/franciscoalro/TestPlugins/releases/tag/v124.0" -ForegroundColor Cyan
Write-Host "Raw plugins.json: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "Users can now update to v124 from the app!" -ForegroundColor Green
Write-Host ""
