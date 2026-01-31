# Script para deploy do CloudstreamRepo para GitHub Pages
# Atualiza os JSONs e faz commit/push

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY CLOUDSTREAM REPO - GITHUB PAGES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$RepoDir = "C:\Users\KYTHOURS\Desktop\brcloudstream\CloudstreamRepo"

# Verificar se está na pasta correta
if (-not (Test-Path "$RepoDir\plugins.json")) {
    Write-Host "❌ ERRO: Pasta CloudstreamRepo não encontrada!" -ForegroundColor Red
    exit 1
}

Set-Location $RepoDir

# Verificar status do git
Write-Host "`n📊 Status do repositório:" -ForegroundColor Yellow
git status --short

# Adicionar arquivos modificados
Write-Host "`n📤 Adicionando arquivos..." -ForegroundColor Yellow
git add plugins.json
git add repo.json
git add releases\MaxSeries-v256.cs3

# Verificar se há algo para commitar
$status = git status --porcelain
if (-not $status) {
    Write-Host "`n⚠️ Nenhuma alteração para commitar." -ForegroundColor Yellow
    exit 0
}

# Criar commit
$CommitMessage = "Update to v256 - PlayerEmbedAPI V8+V7 Fixes`n`n- PlayerEmbedAPI V8: 12 URL patterns, improved regex`n- PlayerEmbedAPI V7: Memory leak fix, atomic cleanup flag`n- Provider: Timeout 25s, maxAttempts 5`n- MaxSeries.cs3: 638 KB`n- Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Host "`n📝 Criando commit..." -ForegroundColor Yellow
git commit -m $CommitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao criar commit" -ForegroundColor Red
    exit 1
}

# Push para origin
Write-Host "`n🚀 Fazendo push para GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha no push. Tentando pull primeiro..." -ForegroundColor Yellow
    git pull origin main --rebase
    git push origin main
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "`n📋 URLs atualizadas:" -ForegroundColor Cyan
    Write-Host "   Repo: https://franciscoalro.github.io/CloudstreamRepo/repo.json" -ForegroundColor White
    Write-Host "   Plugins: https://franciscoalro.github.io/CloudstreamRepo/plugins.json" -ForegroundColor White
    Write-Host "`n⏱️  Aguarde 1-2 minutos para o GitHub Pages atualizar..." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Falha no deploy" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
