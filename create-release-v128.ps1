# Script para criar release v128.0 no GitHub
# Data: 19 de Janeiro de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIAR RELEASE v128.0 NO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gh CLI está instalado
Write-Host "[1/5] Verificando GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "❌ GitHub CLI não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale com: winget install --id GitHub.cli" -ForegroundColor Yellow
    Write-Host "Ou baixe em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ GitHub CLI encontrado" -ForegroundColor Green
Write-Host ""

# Verificar se está autenticado
Write-Host "[2/5] Verificando autenticação..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Não autenticado no GitHub!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute: gh auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Autenticado no GitHub" -ForegroundColor Green
Write-Host ""

# Verificar se o arquivo MaxSeries.cs3 existe
Write-Host "[3/5] Verificando arquivo MaxSeries.cs3..." -ForegroundColor Yellow
if (-not (Test-Path "MaxSeries.cs3")) {
    Write-Host "❌ Arquivo MaxSeries.cs3 não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Compile primeiro com: .\gradlew :MaxSeries:assembleDebug" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Arquivo MaxSeries.cs3 encontrado" -ForegroundColor Green
Write-Host ""

# Criar tag v128.0
Write-Host "[4/5] Criando tag v128.0..." -ForegroundColor Yellow
git tag -a v128.0 -m "Release v128.0 - MegaEmbed V7 Completo" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag v128.0 criada" -ForegroundColor Green
} else {
    Write-Host "⚠️  Tag v128.0 já existe, continuando..." -ForegroundColor Yellow
}

# Push da tag
Write-Host "   Enviando tag para GitHub..." -ForegroundColor Yellow
git push origin v128.0 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag enviada para GitHub" -ForegroundColor Green
} else {
    Write-Host "⚠️  Tag já existe no GitHub, continuando..." -ForegroundColor Yellow
}
Write-Host ""

# Criar release no GitHub
Write-Host "[5/5] Criando release no GitHub..." -ForegroundColor Yellow
Write-Host ""

# Criar release usando arquivo de release notes
gh release create v128.0 `
    --title "v128.0 - MegaEmbed V7 Completo" `
    --notes-file "release-notes-v128.md" `
    MaxSeries.cs3

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Release v128.0 criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/tag/v128.0" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Erro ao criar release!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente manualmente:" -ForegroundColor Yellow
    Write-Host "1. Acesse: https://github.com/franciscoalro/TestPlugins/releases/new" -ForegroundColor Yellow
    Write-Host "2. Tag: v128.0" -ForegroundColor Yellow
    Write-Host "3. Anexe: MaxSeries.cs3" -ForegroundColor Yellow
    Write-Host "4. Cole as release notes de: release-notes-v128.md" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PROCESSO CONCLUIDO" -ForegroundColor Cyan
