#!/usr/bin/env pwsh
# MaxSeries v55 Release Script - AnimesOnlineCC Structure Fix

Write-Host "MaxSeries v55 Release - AnimesOnlineCC Structure Fix" -ForegroundColor Green

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
git commit -m "MaxSeries v55 - AnimesOnlineCC Structure Fix

Aplicadas correcoes baseadas no AnimesOnlineCC funcionando:
- Seletor: article.item -> div.items article.item
- URL: concatenacao manual -> fixUrl()
- Logs: println() -> Log.d() com detalhes
- Error handling: try/catch adicionado
- Debug: logs extensivos para troubleshooting
- Estrutura identica ao AnimesOnlineCC que funciona
- Deve resolver problema de conteudo nao aparecer"

git push origin main

# Criar tag
Write-Host "Criando tag v55.0..." -ForegroundColor Yellow

git tag -a "v55.0" -m "MaxSeries v55 - AnimesOnlineCC Structure Fix"
git push origin v55.0

Write-Host "Release v55 concluido com sucesso!" -ForegroundColor Green
Write-Host "Estrutura baseada no AnimesOnlineCC - conteudo deve aparecer" -ForegroundColor Cyan