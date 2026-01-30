# Script para testar MaxSeries v219 - PlayerEmbedAPI WebView
# Execute este script DEPOIS de conectar o dispositivo

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host ""
Write-Host "🔧 MaxSeries v219 - Test Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar dispositivos
Write-Host "📱 Verificando dispositivos conectados..." -ForegroundColor Yellow
& $adb devices
Write-Host ""

$devices = & $adb devices | Select-String -Pattern "device$"
if ($devices.Count -eq 0) {
    Write-Host "❌ Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para conectar via WiFi:" -ForegroundColor Yellow
    Write-Host "  1. No celular, ativar 'Depuração sem fio' nas Opções do Desenvolvedor" -ForegroundColor White
    Write-Host "  2. Anotar IP e porta (ex: 192.168.0.184:34307)" -ForegroundColor White
    Write-Host "  3. Executar: $adb connect IP:PORTA" -ForegroundColor White
    Write-Host ""
    Write-Host "Para conectar via USB:" -ForegroundColor Yellow
    Write-Host "  1. Conectar cabo USB" -ForegroundColor White
    Write-Host "  2. Ativar 'Depuração USB' no celular" -ForegroundColor White
    Write-Host "  3. Aceitar permissão no celular" -ForegroundColor White
    Write-Host ""
    exit
}

Write-Host "✅ Dispositivo conectado!" -ForegroundColor Green
Write-Host ""

# Limpar logs
Write-Host "🧹 Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c
Start-Sleep -Seconds 1
Write-Host ""

# Instruções
Write-Host "📋 INSTRUÇÕES:" -ForegroundColor Cyan
Write-Host "1. Abra o Cloudstream no celular" -ForegroundColor White
Write-Host "2. Vá em Configurações → Extensões" -ForegroundColor White
Write-Host "3. Verifique se MaxSeries está na versão 219" -ForegroundColor White
Write-Host "4. Se não estiver, clique em 'Atualizar'" -ForegroundColor White
Write-Host "5. Reinicie o Cloudstream" -ForegroundColor White
Write-Host "6. Busque 'Gerente da Noite'" -ForegroundColor White
Write-Host "7. Selecione qualquer episódio" -ForegroundColor White
Write-Host "8. Aguarde carregar os players" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando estiver pronto para capturar logs..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "📡 Capturando logs... (Pressione Ctrl+C para parar)" -ForegroundColor Green
Write-Host ""
Write-Host "Procurando por:" -ForegroundColor Cyan
Write-Host "  🌐 PLAYEREMBEDAPI DETECTADO" -ForegroundColor White
Write-Host "  🚀 EXTRACT CHAMADO" -ForegroundColor White
Write-Host "  🎯 Captured URLs" -ForegroundColor White
Write-Host "  ✅ links via WebView" -ForegroundColor White
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v219_$timestamp.txt"

& $adb logcat | Select-String -Pattern "MaxSeries|PlayerEmbedAPI|WebView|PLAYEREMBEDAPI|EXTRACT|Captured|sssrr\.org|googleapis\.com" | ForEach-Object {
    $line = $_.Line
    
    # Destacar linhas importantes
    if ($line -match "PLAYEREMBEDAPI DETECTADO") {
        Write-Host $line -ForegroundColor Green
    }
    elseif ($line -match "EXTRACT CHAMADO") {
        Write-Host $line -ForegroundColor Cyan
    }
    elseif ($line -match "Captured|sssrr\.org|googleapis\.com") {
        Write-Host $line -ForegroundColor Yellow
    }
    elseif ($line -match "links via WebView") {
        Write-Host $line -ForegroundColor Magenta
    }
    elseif ($line -match "❌|Erro|Error|Failed|Timeout") {
        Write-Host $line -ForegroundColor Red
    }
    else {
        Write-Host $line
    }
    
    # Salvar em arquivo
    Add-Content -Path $logFile -Value $line
}

Write-Host ""
Write-Host "📝 Logs salvos em: $logFile" -ForegroundColor Green
