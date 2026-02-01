# Script de Deploy Manual para GitHub Pages
# Uso: ./manual-deploy.ps1

Write-Host "=== Deploy Manual para GitHub Pages ===" -ForegroundColor Cyan

# Verificar se estamos na branch correta
$currentBranch = git branch --show-current 2>$null
Write-Host "Branch atual: $currentBranch" -ForegroundColor Yellow

# Verificar arquivos necessarios
Write-Host "`nVerificando arquivos..." -ForegroundColor Yellow

$requiredFiles = @(
    "repo.json",
    "builds/plugins.json",
    "builds/MaxSeries.jar",
    "builds/AnimesOnlineCC.jar"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
        Write-Host "  X $file NAO ENCONTRADO" -ForegroundColor Red
    } else {
        Write-Host "  OK $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`nArquivos faltando! Corrija antes de continuar." -ForegroundColor Red
    exit 1
}

# Commit e push
Write-Host "`nFazendo commit e push..." -ForegroundColor Yellow

git add builds/
git add repo.json
git add plugins.json 2>$null
git add .github/workflows/ 2>$null

git commit -m "Deploy: Update plugins with .jar files [$(Get-Date -Format 'yyyy-MM-dd HH:mm')]" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Commit criado" -ForegroundColor Green
} else {
    Write-Host "  Nada para commitar" -ForegroundColor Yellow
}

Write-Host "`nPush para origin/$currentBranch..." -ForegroundColor Yellow
git push origin $currentBranch
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Push realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "  X Erro no push" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Deploy Enviado! ===" -ForegroundColor Cyan
Write-Host "`nAcoes necessarias:" -ForegroundColor Yellow
Write-Host "1. Va em Settings - Pages no GitHub" -ForegroundColor White
Write-Host "2. Ative GitHub Actions como source" -ForegroundColor White
Write-Host "3. Aguarde o workflow completar" -ForegroundColor White
Write-Host "`nURL para CloudStream:" -ForegroundColor Green
Write-Host "https://franciscoalro.github.io/TestPlugins/repo.json" -ForegroundColor Cyan
