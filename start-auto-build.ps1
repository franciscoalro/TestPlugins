# Quick Start - Auto Build v156

Write-Host "Iniciando auto-build v156..." -ForegroundColor Cyan
Write-Host ""
Write-Host "O script tentara compilar MaxSeries v156 automaticamente." -ForegroundColor White
Write-Host "Se o build funcionar, criara a release no GitHub." -ForegroundColor White
Write-Host ""

# Executar script principal
.\auto-build-release.ps1 -MaxAttempts 24 -IntervalMinutes 60
