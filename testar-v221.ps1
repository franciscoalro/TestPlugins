# Teste MaxSeries v221 - PlayerEmbedAPI Fast Detection

Write-Host "=== TESTE MAXSERIES V221 ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar ADB
Write-Host "1. Verificando ADB..." -ForegroundColor Yellow
cd C:\Users\KYTHOURS\Desktop\platform-tools
$devices = .\adb.exe devices
Write-Host $devices
Write-Host ""

# 2. Limpar logs
Write-Host "2. Limpando logs..." -ForegroundColor Yellow
.\adb.exe logcat -c
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# 3. Instruções
Write-Host "3. AGORA TESTE NO CELULAR:" -ForegroundColor Cyan
Write-Host "   a) Abrir Cloudstream" -ForegroundColor White
Write-Host "   b) Atualizar MaxSeries para v221" -ForegroundColor White
Write-Host "   c) Abrir um FILME (nao serie)" -ForegroundColor White
Write-Host "   d) Clicar em PlayerEmbedAPI" -ForegroundColor White
Write-Host "   e) Observar tempo de carregamento" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando terminar o teste..." -ForegroundColor Yellow
Read-Host

# 4. Capturar logs
Write-Host "4. Capturando logs..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "v221_test_$timestamp.txt"
.\adb.exe logcat -d > $logfile
Write-Host "Logs salvos em: $logfile" -ForegroundColor Green
Write-Host ""

# 5. Verificar logs importantes
Write-Host "5. Verificando logs..." -ForegroundColor Yellow
$content = Get-Content $logfile -Raw

if ($content -match "MAXSERIES PROVIDER v221") {
    Write-Host "[OK] v221 carregada" -ForegroundColor Green
} else {
    Write-Host "[ERRO] v221 nao encontrada" -ForegroundColor Red
}

if ($content -match "FAST MODE") {
    Write-Host "[OK] Fast mode ativado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Fast mode nao encontrado" -ForegroundColor Yellow
}

if ($content -match "MutationObserver") {
    Write-Host "[OK] MutationObserver detectado" -ForegroundColor Green
}

if ($content -match "Button detected via MutationObserver") {
    Write-Host "[OK] Botao detectado via MutationObserver" -ForegroundColor Green
}

if ($content -match "Overlay detected via MutationObserver") {
    Write-Host "[OK] Overlay detectado via MutationObserver" -ForegroundColor Green
}

if ($content -match "Video found in fast check") {
    Write-Host "[OK] Video encontrado em fast check" -ForegroundColor Green
}

if ($content -match "Captured:.*googleapis") {
    Write-Host "[OK] URL capturada (googleapis)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== TESTE CONCLUIDO ===" -ForegroundColor Cyan
Write-Host "Arquivo de log: $logfile" -ForegroundColor White
