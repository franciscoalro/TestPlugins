#!/usr/bin/env pwsh
# MaxSeries v54 Release Script - URL and TvType Fix

Write-Host "MaxSeries v54 Release - URL and TvType Fix" -ForegroundColor Green

# Verificar arquivos
if (Test-Path "MaxSeries.cs3") {
    Write-Host "MaxSeries.cs3 encontrado" -ForegroundColor Green
} else {
    Write-Host "MaxSeries.cs3 nao encontrado!" -ForegroundColor Red
    exit 1
}

# Commit e push
Write-Host "Fazendo commit e push..." -ForegroundColor Yellow

git add .
git commit -m "MaxSeries v54 - URL and TvType Fix

Corrigidas URLs e deteccao de tipo de conteudo:
- URLs absolutas garantidas (mainUrl + href se relativo)
- Deteccao inteligente de TvType (Series/Movie/Anime)
- Baseado na URL: /series/ -> TvSeries, /filme/ -> Movie
- Baseado no elemento: .item_type SERIE -> TvSeries
- Default: TvSeries (maioria do conteudo)
- Deve resolver problema de conteudo nao aparecer no app"

git push origin main

# Criar tag
Write-Host "Criando tag v54.0..." -ForegroundColor Yellow

git tag -a "v54.0" -m "MaxSeries v54 - URL and TvType Fix"
git push origin v54.0

Write-Host "Release v54 concluido com sucesso!" -ForegroundColor Green
Write-Host "URLs e TvTypes corrigidos - conteudo deve aparecer no app" -ForegroundColor Cyan