# Deploy Automático MaxSeries v223
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATICO MAXSERIES v223     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar git
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git nao encontrado!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "./MaxSeries")) {
    Write-Host "❌ Execute na pasta brcloudstream" -ForegroundColor Red
    exit 1
}

# Configurar git
$gitUser = git config user.name
if (-not $gitUser) {
    git config user.name "GitHub Action"
    git config user.email "action@github.com"
}

Write-Host "📍 Repositorio remoto:" -ForegroundColor Yellow
git remote -v | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "📝 Verificando alteracoes..." -ForegroundColor Yellow

$status = git status --porcelain
if ($status) {
    Write-Host "   Alteracoes detectadas:" -ForegroundColor Yellow
    git status --short | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
    
    Write-Host ""
    Write-Host "📤 Fazendo commit..." -ForegroundColor Yellow
    git add -A
    
    git commit -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix FINAL

FIX: Segue redirect sssrr.org para googleapis.com automaticamente
Headers completos para Google Storage
Verificacao de redirect bem-sucedido  
Corrige ERROR_CODE_IO_BAD_HTTP_STATUS (2004)"
    
    Write-Host "   ✅ Commit realizado!" -ForegroundColor Green
} else {
    Write-Host "   ℹ️ Nenhuma alteracao para commitar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📤 Push para origin main..." -ForegroundColor Yellow
git push origin main
Write-Host "   ✅ Push realizado!" -ForegroundColor Green

Write-Host ""
Write-Host "🏷️ Gerenciando tag v223..." -ForegroundColor Yellow

$tagExists = git tag -l "v223"
if ($tagExists) {
    Write-Host "   Tag v223 ja existe. Atualizando..." -ForegroundColor Yellow
    git tag -d v223
    git push origin :refs/tags/v223 2>$null
    Write-Host "   Tag antiga removida" -ForegroundColor Green
}

Write-Host "   Criando nova tag v223..." -ForegroundColor Yellow
git tag -a v223 -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix FINAL"
git push origin v223
Write-Host "   ✅ Tag v223 criada!" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Verificando branch builds..." -ForegroundColor Yellow

git checkout main
$branchExists = git branch -r | Select-String "origin/builds"

if (-not $branchExists) {
    Write-Host "   Criando branch builds..." -ForegroundColor Yellow
    git checkout --orphan builds
    git rm -rf . 2>$null
    git commit --allow-empty -m "Initial builds branch" 2>$null
    git push origin builds
    git checkout main
    Write-Host "   Branch builds criada!" -ForegroundColor Green
} else {
    Write-Host "   ✅ Branch builds ja existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY INICIADO!                  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resumo:" -ForegroundColor Cyan
Write-Host "   ✅ Commit na main" -ForegroundColor White
Write-Host "   ✅ Tag v223 criada" -ForegroundColor White
Write-Host "   ✅ Push realizado" -ForegroundColor White
Write-Host ""
Write-Host "⏳ GitHub Actions ira executar:" -ForegroundColor Yellow
Write-Host "   1. Build automatico" -ForegroundColor White
Write-Host "   2. Release v223 criada" -ForegroundColor White
Write-Host "   3. Branch builds atualizada" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Links:" -ForegroundColor Cyan
Write-Host "   Actions: github.com/franciscoalro/TestPlugins/actions" -ForegroundColor White
Write-Host "   Releases: github.com/franciscoalro/TestPlugins/releases" -ForegroundColor White
