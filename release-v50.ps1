#!/usr/bin/env pwsh
# MaxSeries v50 Release Script - CDN Dinamico

Write-Host "MaxSeries v50 Release - CDN Dinamico" -ForegroundColor Green

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
git commit -m "MaxSeries v50 - CDN Dinamico

Implementado interceptacao inteligente do CDN real:
- MegaEmbedExtractorV4 com captura dinamica de CDN
- Intercepta qualquer CDN marvellaholdings.sbs automaticamente
- Nao precisa adivinhar qual CDN sera usado
- Funciona com CDNs novos sem atualizacao
- Baseado no fluxo real observado no navegador
- 4 metodos de fallback para maxima confiabilidade
- Solucao definitiva para o problema do CDN dinamico"

git push origin main

# Criar tag
Write-Host "Criando tag v50.0..." -ForegroundColor Yellow

git tag -a "v50.0" -m "MaxSeries v50 - CDN Dinamico"
git push origin v50.0

Write-Host "Release v50 concluido com sucesso!" -ForegroundColor Green
Write-Host "CDN Dinamico implementation disponivel no GitHub" -ForegroundColor Cyan