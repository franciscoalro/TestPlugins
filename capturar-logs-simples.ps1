# Script Simples - Capturar Logs PlayerEmbedAPI
# Execute este script quando ADB estiver conectado

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Captura Simples de Logs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar conexão
Write-Host "Verificando conexao ADB..." -ForegroundColor Yellow
& $adb devices
Write-Host ""

# Limpar logs
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c
Write-Host "Logs limpos!" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "AGORA:" -ForegroundColor Yellow
Write-Host "1. Abra o filme no Cloudstream" -ForegroundColor White
Write-Host "2. Clique em 'Fontes'" -ForegroundColor White
Write-Host "3. Clique em 'PlayerEmbedAPI HD'" -ForegroundColor White
Write-Host "4. Aguarde o erro aparecer" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando o erro aparecer..." -ForegroundColor Yellow
Read-Host

# Capturar
Write-Host ""
Write-Host "Capturando logs..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$arquivo = "playerembedapi_$timestamp.txt"

& $adb logcat -d | Select-String -Pattern "PlayerEmbedAPI|WebView|Captured|IMDB|Extract|Context|Loading|ERROR" > $arquivo

Write-Host "Salvo em: $arquivo" -ForegroundColor Green
Write-Host ""

# Análise rápida
$conteudo = Get-Content $arquivo -Raw

Write-Host "ANALISE RAPIDA:" -ForegroundColor Cyan
Write-Host ""

if ($conteudo -match "EXTRACT CHAMADO") {
    Write-Host "[OK] Extract foi chamado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Extract NAO foi chamado" -ForegroundColor Red
}

if ($conteudo -match "Captured:") {
    $count = ($conteudo | Select-String -Pattern "Captured:" -AllMatches).Matches.Count
    Write-Host "[OK] $count URL(s) capturada(s)" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Nenhuma URL capturada" -ForegroundColor Red
}

if ($conteudo -match "Context obtido") {
    Write-Host "[OK] Context obtido" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Context NAO obtido" -ForegroundColor Red
}

Write-Host ""
Write-Host "Arquivo completo: $arquivo" -ForegroundColor Yellow
