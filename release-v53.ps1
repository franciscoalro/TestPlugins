#!/usr/bin/env pwsh
# MaxSeries v53 Release Script - CSS Selectors Fix

Write-Host "MaxSeries v53 Release - CSS Selectors Fix" -ForegroundColor Green

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
git commit -m "MaxSeries v53 - CSS Selectors Fix

Corrigidos seletores CSS para nova estrutura do site:
- Antes: div.item -> Agora: article.item
- Antes: h3 a -> Agora: h3.title
- Estrutura HTML do site mudou completamente
- Conteudo agora aparecera corretamente no CloudStream
- Mantem URL correta: www.maxseries.one
- Mantem Anti-YouTube Filter e todos extractors"

git push origin main

# Criar tag
Write-Host "Criando tag v53.0..." -ForegroundColor Yellow

git tag -a "v53.0" -m "MaxSeries v53 - CSS Selectors Fix"
git push origin v53.0

Write-Host "Release v53 concluido com sucesso!" -ForegroundColor Green
Write-Host "Seletores CSS corrigidos - conteudo deve aparecer no app" -ForegroundColor Cyan