# Captura logs MaxSeries v125
# Salva em arquivo para analise

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v125_$timestamp.txt"

Write-Host "=== CAPTURA LOGS V125 ===" -ForegroundColor Cyan
Write-Host "Arquivo: $logFile" -ForegroundColor Green
Write-Host "Dispositivo: Y9YP4XI7799P9LZT" -ForegroundColor Yellow
Write-Host ""
Write-Host "Instrucoes:" -ForegroundColor White
Write-Host "1. Abra CloudStream no celular" -ForegroundColor Gray
Write-Host "2. Va em Configuracoes > Extensoes" -ForegroundColor Gray
Write-Host "3. Atualize para MaxSeries v125" -ForegroundColor Gray
Write-Host "4. Abra Terra de Pecados" -ForegroundColor Gray
Write-Host "5. Teste Player #1 (PlayerEmbedAPI)" -ForegroundColor Gray
Write-Host "6. Teste Player #2 (MegaEmbed)" -ForegroundColor Gray
Write-Host ""
Write-Host "Pressione ENTER quando terminar de testar..." -ForegroundColor Yellow
Write-Host ""

$env:Path += ";D:\Android\platform-tools"

# Limpar logs antigos
adb logcat -c

# Iniciar captura em background
$job = Start-Job -ScriptBlock {
    param($logPath)
    $env:Path += ";D:\Android\platform-tools"
    adb logcat | Select-String -Pattern "PlayerEmbedAPI|MegaEmbed|MaxSeries|Direct API|WebViewResolver|ExtractorLink|MaxSeries-Extraction" | Out-File -FilePath $logPath -Append
} -ArgumentList (Join-Path $PSScriptRoot $logFile)

Write-Host "Capturando logs..." -ForegroundColor Green
Write-Host "Pressione ENTER para parar e ver os resultados" -ForegroundColor Yellow

# Aguardar usuario
Read-Host

# Parar captura
Stop-Job $job
Remove-Job $job

Write-Host ""
Write-Host "=== CAPTURA FINALIZADA ===" -ForegroundColor Cyan
Write-Host "Logs salvos em: $logFile" -ForegroundColor Green
Write-Host ""

# Mostrar resumo
if (Test-Path $logFile) {
    $content = Get-Content $logFile
    $lineCount = $content.Count
    
    Write-Host "Total de linhas capturadas: $lineCount" -ForegroundColor Yellow
    Write-Host ""
    
    if ($lineCount -gt 0) {
        Write-Host "=== ULTIMAS 30 LINHAS ===" -ForegroundColor Cyan
        $content | Select-Object -Last 30 | ForEach-Object {
            if ($_ -match "Direct API") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "SUCESSO|capturou") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "FALHA|erro|timeout") {
                Write-Host $_ -ForegroundColor Red
            } else {
                Write-Host $_ -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "AVISO: Nenhum log capturado!" -ForegroundColor Red
        Write-Host "Verifique se:" -ForegroundColor Yellow
        Write-Host "  - CloudStream esta rodando" -ForegroundColor Gray
        Write-Host "  - MaxSeries v125 esta instalado" -ForegroundColor Gray
        Write-Host "  - Voce testou os players" -ForegroundColor Gray
    }
} else {
    Write-Host "ERRO: Arquivo de log nao foi criado!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
