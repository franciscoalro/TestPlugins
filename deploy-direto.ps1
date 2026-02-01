# Deploy Direto - BRCloudStream
# Faz deploy manual dos plugins para o repositório CloudstreamRepo

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY DIRETO - BRCloudStream       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$repoUrl = "https://github.com/franciscoalro/CloudstreamRepo.git"
$tempDir = "$env:TEMP\cloudstream-deploy-$(Get-Random)"
$buildsDir = "builds"

# Verificar arquivos
Write-Host "1. Verificando arquivos de build..." -ForegroundColor Yellow
if (-not (Test-Path "$buildsDir\*.cs3")) {
    Write-Host "   ERRO: Nenhum arquivo .cs3 encontrado em builds/" -ForegroundColor Red
    Write-Host "   Execute primeiro: .\gradlew.bat build" -ForegroundColor Yellow
    exit 1
}

Get-ChildItem "$buildsDir\*.cs3" | ForEach-Object {
    Write-Host "   OK: $($_.Name)" -ForegroundColor Green
}
Write-Host ""

# Clonar repositório de destino
Write-Host "2. Clonando repositório CloudstreamRepo..." -ForegroundColor Yellow
Write-Host "   URL: $repoUrl" -ForegroundColor Gray

try {
    git clone $repoUrl $tempDir 2>&1 | Out-Null
    Write-Host "   OK: Repositório clonado" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: Não foi possível clonar o repositório" -ForegroundColor Red
    Write-Host "   Verifique se você tem acesso ao repositório" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Copiar arquivos
Write-Host "3. Copiando arquivos..." -ForegroundColor Yellow
Copy-Item "$buildsDir\*.cs3" $tempDir -Force
Copy-Item "$buildsDir\plugins.json" $tempDir -Force
Copy-Item "$buildsDir\repo.json" $tempDir -Force
Copy-Item "$buildsDir\index.html" $tempDir -Force
Write-Host "   OK: Arquivos copiados" -ForegroundColor Green
Write-Host ""

# Verificar alterações
Write-Host "4. Verificando alterações..." -ForegroundColor Yellow
Set-Location $tempDir
$status = git status --porcelain

if (-not $status) {
    Write-Host "   Nenhuma alteração detectada" -ForegroundColor Yellow
    Set-Location -
    Remove-Item $tempDir -Recurse -Force
    exit 0
}

Write-Host "   Alterações detectadas:" -ForegroundColor Green
$status | ForEach-Object { Write-Host "     $_" }
Write-Host ""

# Commit e push
Write-Host "5. Fazendo commit e push..." -ForegroundColor Yellow
git add .
git commit -m "Update plugins - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Host "   Fazendo push para main..." -ForegroundColor Gray
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK: Push realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "   ERRO: Falha no push" -ForegroundColor Red
    Set-Location -
    exit 1
}

# Limpar
Set-Location -
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY CONCLUÍDO!                   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL dos plugins:" -ForegroundColor Yellow
Write-Host "  https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json" -ForegroundColor Green
Write-Host ""
Write-Host "Para adicionar ao CloudStream:" -ForegroundColor Yellow
Write-Host "  1. Abra o CloudStream" -ForegroundColor White
Write-Host "  2. Configurações > Extensões" -ForegroundColor White
Write-Host "  3. Adicionar Repositório" -ForegroundColor White
Write-Host "  4. Cole a URL acima" -ForegroundColor White
Write-Host ""
