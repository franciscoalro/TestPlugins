# Capturar logs PlayerEmbedAPI v222

Write-Host "=== CAPTURA LOGS PLAYEREMBEDAPI V222 ===" -ForegroundColor Cyan
Write-Host ""

cd C:\Users\KYTHOURS\Desktop\platform-tools

# Limpar logs antigos
Write-Host "1. Limpando logs..." -ForegroundColor Yellow
.\adb.exe logcat -c
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "2. AGORA NO CELULAR:" -ForegroundColor Cyan
Write-Host "   a) Abrir um FILME no MaxSeries" -ForegroundColor White
Write-Host "   b) Clicar em PlayerEmbedAPI" -ForegroundColor White
Write-Host "   c) Aguardar carregar ou dar erro" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando terminar..." -ForegroundColor Yellow
Read-Host

# Capturar logs filtrados
Write-Host ""
Write-Host "3. Capturando logs..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "playerembedapi_v222_$timestamp.txt"

# Filtrar apenas logs relevantes
.\adb.exe logcat -d | Select-String -Pattern "MaxSeries|PlayerEmbedAPI|MegaEmbed|EXTRACT|loadLinks|WebView|Video|URL|Captured|Error|Exception" > $logfile

Write-Host "Logs salvos: $logfile" -ForegroundColor Green
Write-Host ""

# Mostrar resumo
Write-Host "4. RESUMO:" -ForegroundColor Cyan
$content = Get-Content $logfile -Raw

if ($content -match "v222") {
    Write-Host "[OK] v222 detectada" -ForegroundColor Green
} else {
    Write-Host "[AVISO] v222 nao encontrada nos logs" -ForegroundColor Yellow
}

if ($content -match "PLAYEREMBEDAPI DETECTADO") {
    Write-Host "[OK] PlayerEmbedAPI detectado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] PlayerEmbedAPI NAO detectado" -ForegroundColor Red
}

if ($content -match "EXTRACT CHAMADO") {
    Write-Host "[OK] Extract foi chamado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Extract NAO foi chamado" -ForegroundColor Red
}

if ($content -match "Seguindo redirect") {
    Write-Host "[OK] Redirect sendo seguido" -ForegroundColor Green
}

if ($content -match "URL final:") {
    Write-Host "[OK] URL final capturada" -ForegroundColor Green
}

if ($content -match "googleapis") {
    Write-Host "[OK] URL do Google Storage encontrada" -ForegroundColor Green
}

if ($content -match "ERROR|Error|error") {
    Write-Host "[AVISO] Erros encontrados nos logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Arquivo completo: $logfile" -ForegroundColor White
Write-Host ""
Write-Host "Cole o conteudo do arquivo aqui para analise" -ForegroundColor Cyan
