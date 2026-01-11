#!/usr/bin/env pwsh
# MaxSeries v51 Release Script - Anti-YouTube Filter

Write-Host "MaxSeries v51 Release - Anti-YouTube Filter" -ForegroundColor Green

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
git commit -m "MaxSeries v51 - Anti-YouTube Filter

Implementado filtro inteligente para ignorar links do YouTube:
- isYouTubeUrl() detecta youtube.com, youtu.be e youtube-nocookie.com
- Filtro aplicado em botões de fonte e iframes
- Evita processamento desnecessário de trailers
- Foco apenas em players de vídeo válidos
- Logs informativos sobre links ignorados
- Melhora performance e experiência do usuário
- Compatível com todas as versões anteriores"

git push origin main

# Criar tag
Write-Host "Criando tag v51.0..." -ForegroundColor Yellow

git tag -a "v51.0" -m "MaxSeries v51 - Anti-YouTube Filter"
git push origin v51.0

Write-Host "Release v51 concluido com sucesso!" -ForegroundColor Green
Write-Host "Anti-YouTube Filter implementado e disponivel no GitHub" -ForegroundColor Cyan