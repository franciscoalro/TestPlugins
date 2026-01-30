Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE v157 - LOGS ADB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs limpos!" -ForegroundColor Green
Write-Host ""
Write-Host "INSTRUCOES:" -ForegroundColor Yellow
Write-Host "1. CERTIFIQUE-SE que MaxSeries v157 esta instalado" -ForegroundColor White
Write-Host "   (Settings -> Extensions -> MaxSeries -> Version: 157)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Escolha UM episodio no CloudStream" -ForegroundColor White
Write-Host ""
Write-Host "3. Clique em REPRODUZIR" -ForegroundColor White
Write-Host ""
Write-Host "4. AGUARDE ate:" -ForegroundColor White
Write-Host "   - Player iniciar OU" -ForegroundColor Gray
Write-Host "   - Aparecer erro" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Pressione ENTER aqui quando terminar" -ForegroundColor White
Write-Host ""
Write-Host "Aguardando teste..." -ForegroundColor Cyan
Read-Host "Pressione ENTER apos testar"

Write-Host ""
Write-Host "Capturando logs..." -ForegroundColor Yellow

$logFile = "teste_v157_$(Get-Date -Format 'HHmmss').txt"
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -d > $logFile

Write-Host "OK Logs salvos: $logFile" -ForegroundColor Green
Write-Host ""

# Análise
Write-Host "Analisando..." -ForegroundColor Yellow
Write-Host ""

# Verificar versão
$versao = Select-String -Path $logFile -Pattern "v157|v156|v129" | Select-Object -First 5
Write-Host "=== VERSAO ===" -ForegroundColor Cyan
$versao | ForEach-Object { Write-Host $_.Line -ForegroundColor Cyan }

# MegaEmbed logs
$megaembed = Select-String -Path $logFile -Pattern "MegaEmbedV8" | Select-Object -Last 20
Write-Host ""
Write-Host "=== MEGAEMBED V8 ===" -ForegroundColor Green
$megaembed | ForEach-Object { 
    if ($_.Line -match "SUCESSO|OK|✅|válida") {
        Write-Host $_.Line -ForegroundColor Green
    }
    elseif ($_.Line -match "cancelled|Erro|Failed|❌") {
        Write-Host $_.Line -ForegroundColor Red
    }
    else {
        Write-Host $_.Line -ForegroundColor White
    }
}

# Erros
$erros = Select-String -Path $logFile -Pattern "Job was cancelled|Erro:|Failed|Exception" | Select-Object -Last 10
if ($erros) {
    Write-Host ""
    Write-Host "=== ERROS ===" -ForegroundColor Red
    $erros | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
} else {
    Write-Host ""
    Write-Host "OK Nenhum erro 'Job was cancelled' encontrado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Arquivo completo: $logFile" -ForegroundColor Cyan
