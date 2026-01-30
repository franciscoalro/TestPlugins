# Script para capturar erro do PlayerEmbedAPI
# MaxSeries v220 - 28 Jan 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Captura de Logs - PlayerEmbedAPI Error" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Conectar ADB
Write-Host "1. Conectando ADB..." -ForegroundColor Yellow
$adbPath = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "Digite o IP:PORTA do dispositivo (ex: 100.124.161.4:42685):" -ForegroundColor Yellow
$device = Read-Host

Write-Host "Tentando conectar em $device..." -ForegroundColor Yellow
& $adbPath connect $device

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao conectar. Verifique:" -ForegroundColor Red
    Write-Host "  1. IP e porta corretos" -ForegroundColor White
    Write-Host "  2. Dispositivo na mesma rede" -ForegroundColor White
    Write-Host "  3. Depuracao USB/WiFi habilitada" -ForegroundColor White
    exit
}

Write-Host "Conectado!" -ForegroundColor Green
Write-Host ""

# Limpar logs
Write-Host "2. Limpando logs antigos..." -ForegroundColor Yellow
& $adbPath logcat -c
Write-Host "Logs limpos!" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTRUCOES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Agora faca o seguinte no Cloudstream:" -ForegroundColor Yellow
Write-Host "  1. Abra o filme" -ForegroundColor White
Write-Host "  2. Clique em 'Fontes'" -ForegroundColor White
Write-Host "  3. Clique em 'PlayerEmbedAPI HD'" -ForegroundColor White
Write-Host "  4. Aguarde o erro aparecer" -ForegroundColor White
Write-Host "  5. Pressione ENTER aqui" -ForegroundColor White
Write-Host ""
Read-Host "Pressione ENTER quando o erro aparecer"

# Capturar logs
Write-Host ""
Write-Host "3. Capturando logs..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "playerembedapi_error_$timestamp.txt"

& $adbPath logcat -d | Select-String -Pattern "PlayerEmbedAPI|WebView|ERROR|Captured|IMDB|Extract|Context|Loading|timeout" | Out-File -FilePath $logFile

Write-Host "Logs salvos em: $logFile" -ForegroundColor Green
Write-Host ""

# Analisar logs
Write-Host "4. Analisando logs..." -ForegroundColor Yellow
Write-Host ""

$content = Get-Content $logFile -Raw

# Verificar se PlayerEmbedAPI foi chamado
if ($content -match "EXTRACT CHAMADO") {
    Write-Host "[OK] PlayerEmbedAPI extract() foi chamado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] PlayerEmbedAPI extract() NAO foi chamado" -ForegroundColor Red
}

# Verificar IMDB ID
if ($content -match "IMDB ID extraido: (tt\d+)") {
    $imdbId = $matches[1]
    Write-Host "[OK] IMDB ID extraido: $imdbId" -ForegroundColor Green
} else {
    Write-Host "[ERRO] IMDB ID NAO foi extraido" -ForegroundColor Red
}

# Verificar Context
if ($content -match "Context obtido") {
    Write-Host "[OK] Context do Android obtido" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Context NAO foi obtido" -ForegroundColor Red
}

# Verificar Loading
if ($content -match "Loading: (https://[^\s]+)") {
    $url = $matches[1]
    Write-Host "[OK] WebView carregando: $url" -ForegroundColor Green
} else {
    Write-Host "[ERRO] WebView NAO carregou URL" -ForegroundColor Red
}

# Verificar URLs capturadas
$capturedCount = ($content | Select-String -Pattern "Captured:" -AllMatches).Matches.Count
if ($capturedCount -gt 0) {
    Write-Host "[OK] URLs capturadas: $capturedCount" -ForegroundColor Green
    
    # Mostrar URLs
    $content | Select-String -Pattern "Captured: (https://[^\s]+)" -AllMatches | ForEach-Object {
        $_.Matches | ForEach-Object {
            Write-Host "  - $($_.Groups[1].Value)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "[ERRO] Nenhuma URL capturada" -ForegroundColor Red
}

# Verificar timeout
if ($content -match "timeout|Timeout") {
    Write-Host "[AVISO] Timeout detectado" -ForegroundColor Yellow
}

# Verificar erros
$errors = $content | Select-String -Pattern "ERROR|Error|erro|Erro" -AllMatches
if ($errors.Matches.Count -gt 0) {
    Write-Host ""
    Write-Host "[ERROS ENCONTRADOS]" -ForegroundColor Red
    $errors | Select-Object -First 10 | ForEach-Object {
        Write-Host "  $($_.Line)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs completos salvos em: $logFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Analise o arquivo $logFile" -ForegroundColor White
Write-Host "  2. Procure por linhas com 'PlayerEmbedAPI'" -ForegroundColor White
Write-Host "  3. Verifique se URLs foram capturadas" -ForegroundColor White
Write-Host "  4. Compartilhe o arquivo para analise" -ForegroundColor White
Write-Host ""
