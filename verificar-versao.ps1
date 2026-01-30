# Verificar versão do MaxSeries instalada

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "=== VERIFICAR VERSAO MAXSERIES ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Capturando logs de inicializacao..." -ForegroundColor Yellow
& $adb logcat -d > logs_versao.txt

Write-Host "Procurando versao..." -ForegroundColor Yellow
Write-Host ""

$versao = Select-String -Path logs_versao.txt -Pattern "MAXSERIES PROVIDER v\d+" 

if ($versao) {
    $ultimaVersao = $versao | Select-Object -Last 1
    Write-Host "VERSAO INSTALADA:" -ForegroundColor Cyan
    Write-Host $ultimaVersao.Line -ForegroundColor White
    Write-Host ""
    
    if ($ultimaVersao.Line -match "v222") {
        Write-Host "✓ v222 instalada (correto)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Mas o redirect nao esta funcionando..." -ForegroundColor Yellow
        Write-Host "Vou verificar os logs de redirect:" -ForegroundColor Yellow
        Write-Host ""
        
        $redirect = Select-String -Path logs_versao.txt -Pattern "Seguindo redirect|URL final"
        if ($redirect) {
            $redirect | ForEach-Object { Write-Host $_.Line }
        } else {
            Write-Host "NENHUM LOG DE REDIRECT ENCONTRADO!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Isso significa que o codigo de redirect nao foi executado." -ForegroundColor Yellow
        }
    } elseif ($ultimaVersao.Line -match "v221") {
        Write-Host "✗ v221 instalada (precisa atualizar para v222)" -ForegroundColor Red
    } elseif ($ultimaVersao.Line -match "v220") {
        Write-Host "✗ v220 instalada (precisa atualizar para v222)" -ForegroundColor Red
    }
} else {
    Write-Host "Versao nao encontrada nos logs" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== COMO ATUALIZAR ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Abrir Cloudstream" -ForegroundColor White
Write-Host "2. Menu (3 pontos) > Extensoes" -ForegroundColor White
Write-Host "3. Encontrar MaxSeries" -ForegroundColor White
Write-Host "4. Tocar em MaxSeries" -ForegroundColor White
Write-Host "5. Tocar em 'Atualizar' ou 'Update'" -ForegroundColor White
Write-Host "6. Aguardar download" -ForegroundColor White
Write-Host "7. Verificar se mostra v222" -ForegroundColor White
Write-Host ""
