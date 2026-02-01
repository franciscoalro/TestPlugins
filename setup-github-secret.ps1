# Script para configurar o CLOUDSTREAM_REPO_TOKEN no GitHub
# Requer GitHub CLI (gh) instalado e autenticado

param(
    [Parameter(Mandatory=$true)]
    [string]$Token
)

Write-Host "=== Configurando GitHub Secret ===" -ForegroundColor Cyan

# Verificar se gh está instalado
$ghPath = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghPath) {
    Write-Host "❌ GitHub CLI (gh) não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Não autenticado no GitHub CLI" -ForegroundColor Red
    Write-Host "Execute: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Autenticado" -ForegroundColor Green

# Configurar o secret
Write-Host "`nConfigurando secret CLOUDSTREAM_REPO_TOKEN..." -ForegroundColor Yellow

$token | gh secret set CLOUDSTREAM_REPO_TOKEN --repo franciscoalro/TestPlugins

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Secret configurado com sucesso!" -ForegroundColor Green
    Write-Host "`nO workflow 'Deploy to CloudstreamRepo' agora funcionará automaticamente." -ForegroundColor Cyan
} else {
    Write-Host "❌ Erro ao configurar secret" -ForegroundColor Red
    exit 1
}
