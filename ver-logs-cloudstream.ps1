# Ver logs do Cloudstream em tempo real

Write-Host "=== LOGS CLOUDSTREAM AO VIVO ===" -ForegroundColor Cyan
Write-Host ""

cd C:\Users\KYTHOURS\Desktop\platform-tools

Write-Host "Mostrando logs do Cloudstream..." -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Gray

# Filtrar apenas logs do Cloudstream
.\adb.exe logcat | Select-String -Pattern "cloudstream|MaxSeries|PlayerEmbedAPI|MegaEmbed"
