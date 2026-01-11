#!/usr/bin/env pwsh
# Release MaxSeries v45.0 - MegaEmbed WebView Interceptor (Encryption Bypass)

Write-Host "🚀 MAXSERIES V45.0 - MEGAEMBED WEBVIEW INTERCEPTOR" -ForegroundColor Green

# Verificar se estamos no diretório correto
if (-not (Test-Path "MaxSeries/build.gradle.kts")) {
    Write-Host "❌ Erro: Não foi possível encontrar MaxSeries/build.gradle.kts" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto" -ForegroundColor Yellow
    exit 1
}

# Limpar arquivos temporários
Write-Host "🧹 Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Path "build_log*.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "hs_err_pid*.log" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "gradle-8.*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "gradle_wrapper_*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "temp_wrapper_*" -Recurse -Force -ErrorAction SilentlyContinue

# Verificar se plugins.json já foi atualizado
$pluginsContent = Get-Content "plugins.json" -Raw | ConvertFrom-Json
$maxSeriesPlugin = $pluginsContent | Where-Object { $_.name -eq "MaxSeries" }

if ($maxSeriesPlugin.version -ne 45) {
    Write-Host "❌ Erro: plugins.json não está atualizado para versão 45" -ForegroundColor Red
    exit 1
}

Write-Host "✅ plugins.json já está atualizado para versão 45" -ForegroundColor Green

# Commit das mudanças
Write-Host "📤 Fazendo commit das mudanças..." -ForegroundColor Yellow

git add .
git commit -m "feat: MaxSeries v45.0 - MegaEmbed WebView Interceptor (Encryption Bypass)

* Implementado WebView interceptor para bypass de criptografia MegaEmbed
* Suporte a interceptacao de requisicoes JavaScript em tempo real  
* Decodificacao automatica de payloads criptografados
* Melhor compatibilidade com players modernos
* Fallbacks multiplos para maxima estabilidade

Fixes: Videos criptografados nao reproduziam no CloudStream"

# Criar e enviar tag
Write-Host "🏷️ Criando tag v45.0..." -ForegroundColor Yellow
git tag -a "v45.0" -m "MaxSeries v45.0 - MegaEmbed WebView Interceptor (Encryption Bypass)"

# Push das mudanças e tag
Write-Host "📤 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main
git push origin v45.0

Write-Host ""
Write-Host "✅ RELEASE V45.0 CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Links importantes:" -ForegroundColor Cyan
Write-Host "   Release: https://github.com/franciscoalro/TestPlugins/releases/tag/v45.0" -ForegroundColor White
Write-Host "   Actions: https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor White
Write-Host ""
Write-Host "📱 REPOSITÓRIO CLOUDSTREAM:" -ForegroundColor Yellow
Write-Host "   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ O GitHub Actions irá compilar automaticamente o plugin..." -ForegroundColor Yellow
Write-Host "📦 Download estará disponível em alguns minutos em:" -ForegroundColor Yellow
Write-Host "   https://github.com/franciscoalro/TestPlugins/releases/download/v45.0/MaxSeries.cs3" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 RELEASE CONCLUÍDO!" -ForegroundColor Green