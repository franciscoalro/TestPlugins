$adb = "D:\Android\platform-tools\adb.exe"

Write-Host "`n=== MaxSeries v121 - Verificação ===" -ForegroundColor Cyan

# 1. Device
Write-Host "`n[Dispositivo]" -ForegroundColor Yellow
& $adb devices

# 2. CloudStream version
Write-Host "`n[CloudStream]" -ForegroundColor Yellow
& $adb shell pm dump com.lagradost.cloudstream3 | Select-String "versionName" | Select-Object -First 1

# 3. Check if MaxSeries is loaded
Write-Host "`n[Logs recentes do MaxSeries]" -ForegroundColor Yellow
& $adb logcat -d | Select-String "MaxSeries" | Select-Object -Last 10

Write-Host "`n=== Instruções ===" -ForegroundColor Green
Write-Host "1. No CloudStream, vá em: Configurações → Extensões"
Write-Host "2. Encontre 'MaxSeries' e clique nos 3 pontinhos"
Write-Host "3. Clique em 'Atualizar' ou 'Update'"
Write-Host "4. Aguarde o download da v121"
Write-Host "5. Teste uma série qualquer"
Write-Host "`nPara monitorar logs em tempo real, execute:"
Write-Host "  D:\Android\platform-tools\adb.exe logcat | Select-String MaxSeries" -ForegroundColor Cyan
