# Deploy Manual para CloudstreamRepo
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY MANUAL - CloudstreamRepo     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/franciscoalro/CloudstreamRepo.git"
$tempDir = "$env:TEMP\cloudstream-deploy-$(Get-Random)"

# Clonar repositório
Write-Host "1. Clonando repositório..." -ForegroundColor Yellow
git clone $repoUrl $tempDir 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO: Não foi possível clonar" -ForegroundColor Red
    exit 1
}
Write-Host "   OK" -ForegroundColor Green

# Criar pasta builds se não existir
New-Item -ItemType Directory -Force -Path "$tempDir\builds" | Out-Null

# Copiar arquivos
Write-Host "2. Copiando arquivos..." -ForegroundColor Yellow
Copy-Item "builds\*.cs3" "$tempDir\builds\" -Force
Copy-Item "builds\*.jar" "$tempDir\builds\" -Force
Copy-Item "builds\plugins.json" "$tempDir\builds\" -Force
Copy-Item "builds\repo.json" "$tempDir\" -Force
Write-Host "   OK" -ForegroundColor Green

# Commit e push
Write-Host "3. Fazendo commit e push..." -ForegroundColor Yellow
Set-Location $tempDir
git add .
git commit -m "Deploy manual - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK: Deploy realizado!" -ForegroundColor Green
} else {
    Write-Host "   ERRO: Falha no push" -ForegroundColor Red
}

# Limpar
Set-Location -
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY CONCLUÍDO!                   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json" -ForegroundColor Green
