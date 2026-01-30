# Build MaxSeries com PlayerEmbedAPI v3
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Build MaxSeries - PlayerEmbedAPI v3" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar diretório
if (-not (Test-Path "MaxSeries")) {
    Write-Host "Erro: Diretorio MaxSeries nao encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "Diretorio MaxSeries encontrado" -ForegroundColor Green
Write-Host ""

# Limpar build anterior
Write-Host "Limpando build anterior..." -ForegroundColor Cyan
if (Test-Path "MaxSeries/build") {
    Remove-Item -Recurse -Force "MaxSeries/build"
    Write-Host "Build anterior removido" -ForegroundColor Green
}
Write-Host ""

# Build
Write-Host "Iniciando build..." -ForegroundColor Cyan
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Yellow
Write-Host ""

$buildStart = Get-Date

& .\gradlew.bat :MaxSeries:make

if ($LASTEXITCODE -eq 0) {
    $buildEnd = Get-Date
    $buildTime = ($buildEnd - $buildStart).TotalSeconds
    
    Write-Host ""
    Write-Host "Build concluido com sucesso!" -ForegroundColor Green
    Write-Host "Tempo: $([math]::Round($buildTime, 2)) segundos" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "MaxSeries.cs3") {
        $cs3Size = (Get-Item "MaxSeries.cs3").Length / 1KB
        Write-Host "Arquivo gerado: MaxSeries.cs3" -ForegroundColor Green
        Write-Host "Tamanho: $([math]::Round($cs3Size, 2)) KB" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Proximos passos:" -ForegroundColor Yellow
        Write-Host "1. Copiar MaxSeries.cs3 para o dispositivo" -ForegroundColor White
        Write-Host "2. Instalar no CloudStream" -ForegroundColor White
        Write-Host "3. Testar com episodio do MaxSeries" -ForegroundColor White
    } else {
        Write-Host "Aviso: MaxSeries.cs3 nao encontrado" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Build falhou!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Build finalizado!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
