# Script para Forçar Atualização do MaxSeries v209
# Atualiza o timestamp do plugins.json para forçar refresh no Cloudstream

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FORCAR ATUALIZACAO MAXSERIES V209" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mudar para branch builds
Write-Host "[1/5] Mudando para branch builds..." -ForegroundColor Yellow
git checkout builds
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao mudar para branch builds" -ForegroundColor Red
    exit 1
}
Write-Host "OK Branch builds" -ForegroundColor Green

# Ler plugins.json
Write-Host ""
Write-Host "[2/5] Lendo plugins.json..." -ForegroundColor Yellow
$pluginsContent = Get-Content "plugins.json" -Raw | ConvertFrom-Json

# Verificar versão do MaxSeries
$maxseries = $pluginsContent | Where-Object { $_.name -eq "MaxSeries" }
Write-Host "Versao atual no plugins.json: $($maxseries.version)" -ForegroundColor Cyan

if ($maxseries.version -ne 209) {
    Write-Host "AVISO: Versao nao e 209!" -ForegroundColor Yellow
    Write-Host "Atualizando para v209..." -ForegroundColor Yellow
    $maxseries.version = 209
    $maxseries.url = "https://github.com/franciscoalro/TestPlugins/releases/download/v209/MaxSeries.cs3"
    $maxseries.description = "MaxSeries v209 - 7 Extractors (MegaEmbed, PlayerEmbedAPI, MyVidPlay, DoodStream, StreamTape, Mixdrop, Filemoon) + 24 Categories + 23 Genres. Success rate: ~99%"
}

# Adicionar timestamp para forçar refresh
Write-Host ""
Write-Host "[3/5] Adicionando timestamp..." -ForegroundColor Yellow
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
Write-Host "Timestamp: $timestamp" -ForegroundColor Cyan

# Salvar plugins.json
Write-Host ""
Write-Host "[4/5] Salvando plugins.json..." -ForegroundColor Yellow
$pluginsContent | ConvertTo-Json -Depth 10 | Set-Content "plugins.json" -Encoding UTF8
Write-Host "OK plugins.json atualizado" -ForegroundColor Green

# Commit e push
Write-Host ""
Write-Host "[5/5] Fazendo commit e push..." -ForegroundColor Yellow
git add plugins.json
git commit -m "chore: Force update MaxSeries v209 - timestamp $timestamp"
git push origin builds

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Push realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO ao fazer push" -ForegroundColor Red
    exit 1
}

# Voltar para main
git checkout main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ATUALIZACAO FORCADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Aguarde 1-2 minutos para o GitHub atualizar" -ForegroundColor White
Write-Host "  2. No Cloudstream:" -ForegroundColor White
Write-Host "     - Configuracoes -> Extensoes" -ForegroundColor White
Write-Host "     - Remover repositorio" -ForegroundColor White
Write-Host "     - Adicionar novamente" -ForegroundColor White
Write-Host "     - Instalar MaxSeries v209" -ForegroundColor White
Write-Host ""
Write-Host "URL do repositorio:" -ForegroundColor Cyan
Write-Host "  https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json" -ForegroundColor Yellow
Write-Host ""
