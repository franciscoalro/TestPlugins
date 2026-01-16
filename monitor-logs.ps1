# MaxSeries v97 - ADB Log Monitor
# Monitora logs do MaxSeries em tempo real

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MaxSeries v97 - Log Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar dispositivo conectado
Write-Host "Verificando dispositivos..." -ForegroundColor Yellow
$devices = & $adb devices
Write-Host $devices
Write-Host ""

if ($devices -match "device$") {
    Write-Host "✅ Dispositivo conectado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando monitoramento de logs..." -ForegroundColor Yellow
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Monitorar logs do MaxSeries
    & $adb logcat | Select-String "MaxSeries"
} else {
    Write-Host "❌ Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Conecte seu Android via USB" -ForegroundColor White
    Write-Host "2. Ative 'Depuração USB' nas opções de desenvolvedor" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    
    Read-Host "Pressione Enter para sair"
}