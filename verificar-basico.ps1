# Verificação básica

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "=== VERIFICACAO BASICA ===" -ForegroundColor Cyan
Write-Host ""

# 1. Dispositivo conectado?
Write-Host "1. Dispositivo:" -ForegroundColor Yellow
& $adb devices
Write-Host ""

# 2. Cloudstream rodando?
Write-Host "2. Cloudstream rodando?" -ForegroundColor Yellow
$process = & $adb shell "ps | grep cloudstream"
if ($process) {
    Write-Host "   SIM - Cloudstream esta rodando" -ForegroundColor Green
} else {
    Write-Host "   NAO - Cloudstream nao esta rodando" -ForegroundColor Red
    Write-Host "   Abra o Cloudstream no celular!" -ForegroundColor Yellow
}
Write-Host ""

# 3. Capturar logs dos ultimos 5 minutos
Write-Host "3. Capturando logs recentes..." -ForegroundColor Yellow
& $adb logcat -d -t 500 > logs_recentes.txt

# 4. Procurar por MaxSeries
Write-Host "4. Procurando MaxSeries nos logs..." -ForegroundColor Yellow
$maxseries = Select-String -Path logs_recentes.txt -Pattern "MaxSeries" -SimpleMatch
if ($maxseries) {
    Write-Host "   ENCONTRADO! ($($maxseries.Count) linhas)" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Ultimas linhas:" -ForegroundColor Cyan
    $maxseries | Select-Object -Last 10 | ForEach-Object { Write-Host "   $_" }
} else {
    Write-Host "   NAO ENCONTRADO" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Isso significa que:" -ForegroundColor Yellow
    Write-Host "   - MaxSeries nao esta instalado, OU" -ForegroundColor White
    Write-Host "   - Voce nao abriu nenhum conteudo do MaxSeries, OU" -ForegroundColor White
    Write-Host "   - O plugin crashou ao carregar" -ForegroundColor White
}
Write-Host ""

# 5. Procurar por erros
Write-Host "5. Procurando erros..." -ForegroundColor Yellow
$errors = Select-String -Path logs_recentes.txt -Pattern "Exception|Error|crash" -SimpleMatch
if ($errors) {
    Write-Host "   Encontrados $($errors.Count) erros" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Primeiros erros:" -ForegroundColor Cyan
    $errors | Select-Object -First 5 | ForEach-Object { Write-Host "   $_" }
}
Write-Host ""

Write-Host "=== PROXIMO PASSO ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se MaxSeries NAO foi encontrado:" -ForegroundColor Yellow
Write-Host "1. Abra Cloudstream no celular" -ForegroundColor White
Write-Host "2. Va em Extensoes" -ForegroundColor White
Write-Host "3. Verifique se MaxSeries esta instalado" -ForegroundColor White
Write-Host "4. Verifique a versao (deve ser v222)" -ForegroundColor White
Write-Host "5. Abra um FILME do MaxSeries" -ForegroundColor White
Write-Host "6. Execute este script novamente" -ForegroundColor White
Write-Host ""
