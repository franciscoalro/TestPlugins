# Release v124 - PlayerEmbedAPI SSSRR.ORG CDN Fix
# Data: 18/01/2026

Write-Host "=== RELEASE v124 - PlayerEmbedAPI SSSRR.ORG CDN Fix ===" -ForegroundColor Cyan
Write-Host ""

# 1. Build
Write-Host "1. Building MaxSeries v124..." -ForegroundColor Yellow
$env:ANDROID_HOME="D:\Android"
.\gradlew.bat MaxSeries:make
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# 2. Verificar arquivo
$cs3File = "MaxSeries\build\MaxSeries.cs3"
if (!(Test-Path $cs3File)) {
    Write-Host "MaxSeries.cs3 not found!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $cs3File).Length
Write-Host "MaxSeries.cs3 size: $fileSize bytes" -ForegroundColor Green
Write-Host ""

# 3. Git add e commit
Write-Host "2. Git commit..." -ForegroundColor Yellow
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt
git add MaxSeries/build.gradle.kts
git add plugins.json
git add release-notes-v124.md
git add PLAYEREMBEDAPI_BURP_ANALYSIS_V123.md
git add burp_video_urls.txt

git commit -m "v124: PlayerEmbedAPI SSSRR.ORG CDN Fix

- Corrigido regex: googleapis.com -> sssrr.org (CDN real)
- Baseado em analise Burp Suite (1352 requisicoes)
- Padroes identificados: sora API, direct file, future endpoint
- Timeout mantido em 30s
- Filtro .js mantido
- PlayerEmbedAPIExtractor v3.3"

# 4. Tag
Write-Host "3. Creating tag v124.0..." -ForegroundColor Yellow
git tag -a v124.0 -m "v124: PlayerEmbedAPI SSSRR.ORG CDN Fix"

# 5. Push
Write-Host "4. Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
git push origin v124.0

# 6. Atualizar plugins.json
Write-Host "5. Updating plugins.json..." -ForegroundColor Yellow
$pluginsJson = Get-Content "plugins.json" -Raw | ConvertFrom-Json
$pluginsJson[0].version = 124
$pluginsJson[0].status = 1
$pluginsJson[0].changelog = "v124: PlayerEmbedAPI SSSRR.ORG CDN Fix - Regex corrigido para CDN real"
$pluginsJson | ConvertTo-Json -Depth 10 | Set-Content "plugins.json"

git add plugins.json
git commit -m "Update plugins.json to v124"
git push origin main

Write-Host ""
Write-Host "=== RELEASE v124 COMPLETED ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create GitHub release at: https://github.com/franciscoalro/brcloudstream/releases/new?tag=v124.0"
Write-Host "2. Upload MaxSeries.cs3"
Write-Host "3. Test with ADB: .\monitor-maxseries-v122.ps1"
Write-Host ""
