# TESTE PLAYEREMBEDAPI V222 - EXECUTAR AGORA

$adbPath = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TESTE PLAYEREMBEDAPI V222 - MAXSERIES             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar dispositivo
Write-Host "[1/4] Verificando dispositivo..." -ForegroundColor Yellow
& $adbPath devices
Write-Host ""

# 2. Limpar logs
Write-Host "[2/4] Limpando logs..." -ForegroundColor Yellow
& $adbPath logcat -c
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# 3. Instruções
Write-Host "[3/4] TESTE NO CELULAR:" -ForegroundColor Cyan
Write-Host ""
Write-Host "      1. Abrir Cloudstream" -ForegroundColor White
Write-Host "      2. Ir em MaxSeries" -ForegroundColor White
Write-Host "      3. Abrir um FILME (nao serie)" -ForegroundColor White
Write-Host "      4. Clicar em 'Assistir'" -ForegroundColor White
Write-Host "      5. Clicar em 'PlayerEmbedAPI'" -ForegroundColor White
Write-Host "      6. Aguardar carregar (10-20s)" -ForegroundColor White
Write-Host "      7. Ver se reproduz ou da erro" -ForegroundColor White
Write-Host ""
Write-Host "      Pressione ENTER quando terminar..." -ForegroundColor Yellow
Read-Host

# 4. Capturar logs
Write-Host ""
Write-Host "[4/4] Capturando logs..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "teste_v222_$timestamp.txt"

& $adbPath logcat -d > $logfile

Write-Host "      Logs salvos: $logfile" -ForegroundColor Green
Write-Host ""

# Análise rápida
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    ANALISE RAPIDA                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$content = Get-Content $logfile -Raw

# Verificar versão
if ($content -match "v222") {
    Write-Host "✓ Versao v222 detectada" -ForegroundColor Green
} elseif ($content -match "v221") {
    Write-Host "✗ Ainda esta na v221 (precisa atualizar)" -ForegroundColor Red
} elseif ($content -match "v220") {
    Write-Host "✗ Ainda esta na v220 (precisa atualizar)" -ForegroundColor Red
} else {
    Write-Host "? Versao nao detectada nos logs" -ForegroundColor Yellow
}

# Verificar se MaxSeries foi carregado
if ($content -match "MAXSERIES PROVIDER.*CARREGADO") {
    Write-Host "✓ MaxSeries carregado" -ForegroundColor Green
} else {
    Write-Host "✗ MaxSeries nao carregado" -ForegroundColor Red
}

# Verificar se PlayerEmbedAPI foi detectado
if ($content -match "PLAYEREMBEDAPI DETECTADO") {
    Write-Host "✓ PlayerEmbedAPI detectado" -ForegroundColor Green
} else {
    Write-Host "✗ PlayerEmbedAPI nao detectado" -ForegroundColor Red
}

# Verificar se extract foi chamado
if ($content -match "EXTRACT CHAMADO") {
    Write-Host "✓ Extract foi chamado" -ForegroundColor Green
} else {
    Write-Host "✗ Extract nao foi chamado" -ForegroundColor Red
}

# Verificar redirect
if ($content -match "Seguindo redirect") {
    Write-Host "✓ Redirect sendo seguido (v222 funcionando)" -ForegroundColor Green
} else {
    Write-Host "? Redirect nao encontrado" -ForegroundColor Yellow
}

# Verificar URL final
if ($content -match "URL final:") {
    Write-Host "✓ URL final capturada" -ForegroundColor Green
} else {
    Write-Host "? URL final nao encontrada" -ForegroundColor Yellow
}

# Verificar googleapis
if ($content -match "googleapis") {
    Write-Host "✓ URL do Google Storage encontrada" -ForegroundColor Green
} else {
    Write-Host "? URL googleapis nao encontrada" -ForegroundColor Yellow
}

# Verificar erros
if ($content -match "ERROR_CODE_IO_BAD_HTTP_STATUS|2004") {
    Write-Host "✗ ERRO 2004 detectado (URL nao funciona)" -ForegroundColor Red
} else {
    Write-Host "✓ Sem erro 2004" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    ARQUIVO GERADO                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  $logfile" -ForegroundColor White
Write-Host ""
Write-Host "  Envie este arquivo ou cole o conteudo para analise" -ForegroundColor Yellow
Write-Host ""
