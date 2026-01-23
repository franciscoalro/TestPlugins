# Monitor de Logs CloudStream MaxSeries v156

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGS DO MAXSERIES V156" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$adbPath = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

if (-not (Test-Path $adbPath)) {
    Write-Host "ERRO: ADB nao encontrado" -ForegroundColor Red
    exit 1
}

$devices = & $adbPath devices
if ($devices -notmatch "device$") {
    Write-Host "ERRO: Nenhum dispositivo conectado!" -ForegroundColor Red
    exit 1
}

Write-Host "OK Dispositivo conectado!" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

& $adbPath logcat -c | Out-Null

$logFile = "logs_v156_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Write-Host "Salvando em: $logFile" -ForegroundColor Cyan
Write-Host ""

& $adbPath logcat | ForEach-Object {
    if ($_ -match "MegaEmbed|MaxSeries|cloudstream") {
        
        $color = "White"
        if ($_ -match "SUCESSO|OK") { $color = "Green" }
        elseif ($_ -match "ERRO|ERROR|Failed") { $color = "Red" }
        elseif ($_ -match "AVISO|WARNING") { $color = "Yellow" }
        elseif ($_ -match "v156|V8|FETCH|XHR") { $color = "Cyan" }
        
        Write-Host $_ -ForegroundColor $color
        $_ | Out-File -Append $logFile
    }
}