# Script para INSTALAR e TESTAR o MaxSeries v159 localmente via ADB

$ADB_PATH = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"
if (-not (Test-Path $ADB_PATH)) {
    Write-Host "❌ ADB não encontrado em $ADB_PATH" -ForegroundColor Red
    exit
}

$PluginPath = "MaxSeries\build\MaxSeries.cs3"
if (-not (Test-Path $PluginPath)) {
    Write-Host "❌ Arquivo compilado $PluginPath não encontrado. Rode o build primeiro." -ForegroundColor Red
    exit
}

Write-Host "📱 Verificando dispositivo..." -ForegroundColor Cyan
& $ADB_PATH devices

Write-Host "`n📦 Enviando v159 para o celular (/sdcard/Download/)..." -ForegroundColor Yellow
& $ADB_PATH push $PluginPath /sdcard/Download/MaxSeries_v159.cs3

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Arquivo enviado com sucesso!" -ForegroundColor Green
    
    Write-Host "`n🚀 Tentando iniciar instalação..." -ForegroundColor Yellow
    Write-Host "⚠️  Se o CloudStream não abrir, vá em:" -ForegroundColor White
    Write-Host "   Configurações > Extensões > Instalar Plugin (no rodapé) > Selecione MaxSeries_v159.cs3" -ForegroundColor White
    
    # Tenta abrir o arquivo com o CloudStream (intent genérica)
    & $ADB_PATH shell am start -a android.intent.action.VIEW -d "file:///sdcard/Download/MaxSeries_v159.cs3" -t "*/*"
    
    Write-Host "`n👀 Monitorando logs (Ctrl+C para parar)..." -ForegroundColor Cyan
    Write-Host "   Procurando por 'MegaEmbed' e 'MaxSeries'..." -ForegroundColor Gray
    
    # Limpa logs antigos
    & $ADB_PATH logcat -c
    
    # Monitora
    & $ADB_PATH logcat -v time | Select-String "MegaEmbed|MaxSeries|WebView"
} else {
    Write-Host "❌ Erro ao enviar arquivo. Verifique a conexão USB." -ForegroundColor Red
}
