# Deploy usando GitHub CLI
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY via GitHub CLI               " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repo = "franciscoalro/CloudstreamRepo"
$tempDir = "$env:TEMP\cs-deploy-$(Get-Random)"

# Criar pasta temporária
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

Write-Host "1. Preparando arquivos..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$tempDir\builds" | Out-Null
Copy-Item "builds\*.cs3" "$tempDir\builds\" -Force
Copy-Item "builds\*.jar" "$tempDir\builds\" -Force
Copy-Item "builds\plugins.json" "$tempDir\builds\" -Force
Copy-Item "builds\repo.json" "$tempDir\" -Force
Write-Host "   OK" -ForegroundColor Green

Write-Host "2. Fazendo upload dos arquivos..." -ForegroundColor Yellow
Set-Location $tempDir

# Criar um commit com todos os arquivos
gh repo clone $repo .
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO: Não foi possível clonar" -ForegroundColor Red
    exit 1
}

# Copiar arquivos para o repo clonado
Copy-Item "builds\*.cs3" "CloudstreamRepo\builds\" -Force -ErrorAction SilentlyContinue
Copy-Item "builds\*.jar" "CloudstreamRepo\builds\" -Force -ErrorAction SilentlyContinue
Copy-Item "builds\plugins.json" "CloudstreamRepo\builds\" -Force
Copy-Item "repo.json" "CloudstreamRepo\" -Force

Set-Location "CloudstreamRepo"
git add .
git commit -m "Deploy via CLI - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push

Set-Location -
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY CONCLUÍDO!                   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
