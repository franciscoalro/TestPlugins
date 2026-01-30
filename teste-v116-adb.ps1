# Script de Teste ADB - MaxSeries v116
# Uso: .\teste-v116-adb.ps1

Write-Host "🔍 MaxSeries v116 - Monitor ADB" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar conexão ADB
Write-Host "📱 Verificando dispositivo..." -ForegroundColor Yellow
cd C:\Users\KYTHOURS\Desktop\platform-tools
$devices = .\adb devices
Write-Host $devices
Write-Host ""

# Limpar logs antigos
Write-Host "🧹 Limpando logs antigos..." -ForegroundColor Yellow
.\adb logcat -c
Write-Host "✅ Logs limpos" -ForegroundColor Green
Write-Host ""

# Iniciar monitoramento
Write-Host "🎬 Iniciando monitoramento..." -ForegroundColor Yellow
Write-Host "Aguardando logs do MegaEmbed..." -ForegroundColor Gray
Write-Host ""
Write-Host "📋 INSTRUÇÕES:" -ForegroundColor Cyan
Write-Host "1. Abra o Cloudstream no celular" -ForegroundColor White
Write-Host "2. Verifique se MaxSeries está em v116" -ForegroundColor White
Write-Host "3. Abra uma série e selecione um episódio" -ForegroundColor White
Write-Host "4. Aguarde as fontes carregarem" -ForegroundColor White
Write-Host "5. Clique em MegaEmbed" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Logs aparecerão abaixo:" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Monitorar logs
.\adb logcat | Select-String "MegaEmbed|MaxSeriesProvider"
