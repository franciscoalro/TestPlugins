# Deploy MaxSeries v223 para GitHub
# Cria release e atualiza branch builds

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY MAXSERIES v223 - GITHUB       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se git está instalado
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se estamos na pasta correta
if (-not (Test-Path "./MaxSeries")) {
    Write-Host "❌ Execute este script na pasta brcloudstream" -ForegroundColor Red
    exit 1
}

# Verificar se há mudanças para commit
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Mudanças detectadas. Fazendo commit..." -ForegroundColor Yellow
    git add -A
    git commit -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix FINAL"
    git push origin main
    Write-Host "   ✅ Commit e push realizado!" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Nenhuma mudança para commitar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Verificando build..." -ForegroundColor Yellow

# Verificar se o build existe
$cs3Path = "./MaxSeries/build/MaxSeries.cs3"
if (-not (Test-Path $cs3Path)) {
    Write-Host "⚠️ Build não encontrado. Executando build..." -ForegroundColor Yellow
    .\gradlew.bat MaxSeries:make --no-daemon
    
    if (-not (Test-Path $cs3Path)) {
        Write-Host "❌ Build falhou!" -ForegroundColor Red
        exit 1
    }
}

$fileSize = [math]::Round((Get-Item $cs3Path).Length / 1KB, 2)
Write-Host "   ✅ Build encontrado: $fileSize KB" -ForegroundColor Green

Write-Host ""
Write-Host "🏷️ Criando tag v223..." -ForegroundColor Yellow

# Criar tag v223
$tagExists = git tag -l "v223"
if ($tagExists) {
    Write-Host "   ⚠️ Tag v223 já existe. Deletando..." -ForegroundColor Yellow
    git tag -d v223
    git push origin :refs/tags/v223
}

git tag -a v223 -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix FINAL`

🔄 FIX FINAL: Segue redirect sssrr.org → googleapis.com automaticamente`
🎯 Headers completos para Google Storage`
✅ Verificação de redirect bem-sucedido`
🐛 Corrige ERROR_CODE_IO_BAD_HTTP_STATUS (2004)

Build size: $fileSize KB"

git push origin v223
Write-Host "   ✅ Tag v223 criada e enviada!" -ForegroundColor Green

Write-Host ""
Write-Host "📤 Verificando branch builds..." -ForegroundColor Yellow

# Verificar se branch builds existe
$branchExists = git branch -r | Select-String "origin/builds"

if (-not $branchExists) {
    Write-Host "   🌿 Criando branch builds..." -ForegroundColor Yellow
    git checkout --orphan builds
    git rm -rf .
    git commit --allow-empty -m "Initial builds branch"
    git push origin builds
    git checkout main
    Write-Host "   ✅ Branch builds criada!" -ForegroundColor Green
} else {
    Write-Host "   ✅ Branch builds já existe" -ForegroundColor Green
}

# Fazer checkout da branch builds e copiar arquivos
git checkout builds

Write-Host ""
Write-Host "📋 Copiando arquivos para branch builds..." -ForegroundColor Yellow

# Copiar arquivos
Copy-Item $cs3Path ./MaxSeries.cs3 -Force
Copy-Item ./plugins.json ./plugins.json -Force
Copy-Item ./repo.json ./repo.json -Force

# Commit na branch builds
git add -A
$buildStatus = git status --porcelain
if ($buildStatus) {
    git commit -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix FINAL ($fileSize KB)"
    git push origin builds
    Write-Host "   ✅ Arquivos enviados para branch builds!" -ForegroundColor Green
} else {
    Write-Host "   ℹ️ Nada para commitar na branch builds" -ForegroundColor Yellow
}

# Voltar para main
git checkout main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY v223 CONCLUÍDO!            " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resumo:" -ForegroundColor Cyan
Write-Host "   • Tag v223 criada" -ForegroundColor White
Write-Host "   • Branch builds atualizada" -ForegroundColor White
Write-Host "   • Arquivos disponíveis:" -ForegroundColor White
Write-Host "     - MaxSeries.cs3 ($fileSize KB)" -ForegroundColor Gray
Write-Host "     - plugins.json" -ForegroundColor Gray
Write-Host "     - repo.json" -ForegroundColor Gray
Write-Host ""
Write-Host "🔗 Links:" -ForegroundColor Cyan
Write-Host "   • Release: https://github.com/franciscoalro/TestPlugins/releases/tag/v223" -ForegroundColor White
Write-Host "   • Download: https://github.com/franciscoalro/TestPlugins/releases/download/v223/MaxSeries.cs3" -ForegroundColor White
Write-Host "   • Repo: https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ Ação manual necessária:" -ForegroundColor Yellow
Write-Host "   Crie a release v223 manualmente no GitHub:" -ForegroundColor White
Write-Host "   1. Acesse: https://github.com/franciscoalro/TestPlugins/releases/new" -ForegroundColor Gray
Write-Host "   2. Selecione a tag 'v223'" -ForegroundColor Gray
Write-Host "   3. Título: 'MaxSeries v223 - PlayerEmbedAPI Redirect Fix'" -ForegroundColor Gray
Write-Host "   4. Faça upload do arquivo MaxSeries/build/MaxSeries.cs3" -ForegroundColor Gray
Write-Host "   5. Publique a release" -ForegroundColor Gray
Write-Host ""
