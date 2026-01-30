# Teste simples PlayerEmbedAPI v222

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "1. Limpando logs..." -ForegroundColor Yellow
& $adb logcat -c

Write-Host "2. Teste no celular:" -ForegroundColor Cyan
Write-Host "   - Abrir filme no MaxSeries" -ForegroundColor White
Write-Host "   - Clicar PlayerEmbedAPI" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando terminar..." -ForegroundColor Yellow
Read-Host

Write-Host "3. Capturando..." -ForegroundColor Yellow
& $adb logcat -d > teste_v222.txt

Write-Host "4. Analisando..." -ForegroundColor Yellow
Write-Host ""

$lines = Select-String -Path teste_v222.txt -Pattern "MaxSeries|PlayerEmbedAPI|loadLinks|EXTRACT"

if ($lines.Count -eq 0) {
    Write-Host "NENHUM LOG ENCONTRADO!" -ForegroundColor Red
    Write-Host "MaxSeries pode nao estar instalado ou nao foi usado" -ForegroundColor Yellow
} else {
    Write-Host "Encontradas $($lines.Count) linhas relevantes:" -ForegroundColor Green
    Write-Host ""
    $lines | Select-Object -First 100 | ForEach-Object { Write-Host $_.Line }
}

Write-Host ""
Write-Host "Arquivo completo: teste_v222.txt" -ForegroundColor Cyan
