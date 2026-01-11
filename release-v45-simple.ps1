#!/usr/bin/env pwsh
# Release MaxSeries v45.0 - Simple Version

Write-Host "🚀 MAXSERIES V45.0 RELEASE" -ForegroundColor Green

# Limpar arquivos temporários
Write-Host "🧹 Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Path "build_log*.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "hs_err_pid*.log" -Force -ErrorAction SilentlyContinue

# Commit das mudanças
Write-Host "📤 Fazendo commit das mudanças..." -ForegroundColor Yellow
git add .
git commit -m "feat: MaxSeries v45.0 - MegaEmbed WebView Interceptor"

# Criar tag
Write-Host "🏷️ Criando tag v45.0..." -ForegroundColor Yellow
git tag -a "v45.0" -m "MaxSeries v45.0 - MegaEmbed WebView Interceptor"

# Push das mudanças e tag
Write-Host "📤 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main
git push origin v45.0

Write-Host ""
Write-Host "✅ RELEASE V45.0 CRIADO!" -ForegroundColor Green
Write-Host "🔗 Release: https://github.com/franciscoalro/TestPlugins/releases/tag/v45.0" -ForegroundColor Cyan
Write-Host "📱 Repositório: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" -ForegroundColor Green