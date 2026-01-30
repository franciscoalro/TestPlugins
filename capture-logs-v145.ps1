# Capturar logs do MegaEmbed v145
$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "=== Captura de Logs v145 ===" -ForegroundColor Cyan
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c

Write-Host "`nAguardando logs do MegaEmbed..." -ForegroundColor Yellow
Write-Host "Abra um video no MaxSeries agora!" -ForegroundColor Green
Write-Host "`nPressione Ctrl+C para parar`n" -ForegroundColor Yellow

# Capturar logs filtrados
& $adb logcat | Select-String -Pattern "MegaEmbedV7|MaxSeries|WebView"
