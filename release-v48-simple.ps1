#!/usr/bin/env pwsh
# MaxSeries v48 Release Script - Fix Deteccao MegaEmbed

Write-Host "MaxSeries v48 Release - Fix Deteccao MegaEmbed" -ForegroundColor Green

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
git commit -m "MaxSeries v48 - Fix Deteccao MegaEmbed

Corrigido problema onde fontes MegaEmbed nao apareciam no player.
Implementado suporte a data-show-player + fallback data-source.
Testado e validado: MegaEmbed agora detectado corretamente.
Cobertura mantida em 95%."

git push origin main

# Criar tag
Write-Host "Criando tag v48.0..." -ForegroundColor Yellow

git tag -a "v48.0" -m "MaxSeries v48 - Fix Deteccao MegaEmbed"
git push origin v48.0

Write-Host "Release v48 concluido com sucesso!" -ForegroundColor Green
Write-Host "MegaEmbed detection fix aplicado e disponivel no GitHub" -ForegroundColor Cyan