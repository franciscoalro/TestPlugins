#!/usr/bin/env pwsh
# MaxSeries v52 Release Script - URL Correction

Write-Host "MaxSeries v52 Release - URL Correction" -ForegroundColor Green

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
git commit -m "MaxSeries v52 - URL Correction

Corrigido mainUrl para o endereço correto:
- Antes: https://maxseries.cc (incorreto)
- Depois: https://www.maxseries.one (correto)
- Mantém todas as funcionalidades da v51
- Anti-YouTube Filter ativo
- MegaEmbed, PlayerEmbedAPI e DoodStream funcionando
- URL correta para scraping do site oficial"

git push origin main

# Criar tag
Write-Host "Criando tag v52.0..." -ForegroundColor Yellow

git tag -a "v52.0" -m "MaxSeries v52 - URL Correction"
git push origin v52.0

Write-Host "Release v52 concluido com sucesso!" -ForegroundColor Green
Write-Host "URL corrigida para www.maxseries.one" -ForegroundColor Cyan