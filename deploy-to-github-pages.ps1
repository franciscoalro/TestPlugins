# Script de Deploy para GitHub Pages
# BRCloudStream Repository

param(
    [string]$CommitMessage = "Update repository - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BRCloudStream - Deploy Script       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos em um repositorio git
if (-not (Test-Path .git)) {
    Write-Host "ERRO: Nao esta em um repositorio git!" -ForegroundColor Red
    Write-Host "Execute primeiro: git init" -ForegroundColor Yellow
    exit 1
}

# Copiar arquivos para a pasta builds (se necessario)
Write-Host "1. Verificando arquivos .cs3..." -ForegroundColor Yellow
$cs3Files = Get-ChildItem -Path "builds/*.cs3" -ErrorAction SilentlyContinue
if ($cs3Files.Count -eq 0) {
    Write-Host "   Copiando arquivos .aar para builds..." -ForegroundColor Gray
    New-Item -ItemType Directory -Force -Path "builds" | Out-Null
    Get-ChildItem -Path "*/build/outputs/aar/*-release.aar" | ForEach-Object {
        $name = $_.Name -replace "-release.aar", ".cs3"
        Copy-Item $_.FullName -Destination "builds/$name" -Force
        Write-Host "   Copiado: $name" -ForegroundColor Green
    }
}

# Verificar arquivos necessarios
Write-Host "2. Verificando arquivos do repositorio..." -ForegroundColor Yellow
$requiredFiles = @("builds/plugins.json", "builds/repo.json", "builds/index.html")
$allExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   OK: $file" -ForegroundColor Green
    } else {
        Write-Host "   FALTANDO: $file" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "ERRO: Alguns arquivos estao faltando!" -ForegroundColor Red
    exit 1
}

# Listar arquivos .cs3
Write-Host "3. Providers disponiveis:" -ForegroundColor Yellow
Get-ChildItem -Path "builds/*.cs3" | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1KB, 2)
    Write-Host "   - $($_.Name) (${sizeKB} KB)" -ForegroundColor Gray
}

# Verificar branch gh-pages
Write-Host "4. Configurando GitHub Pages..." -ForegroundColor Yellow
$branches = git branch -a
if ($branches -match "gh-pages") {
    Write-Host "   Branch gh-pages existe" -ForegroundColor Green
} else {
    Write-Host "   Criando branch gh-pages..." -ForegroundColor Gray
    git checkout --orphan gh-pages
    git rm -rf .
    git add builds/
    git mv builds/* .
    git commit -m "Initial GitHub Pages commit"
    git checkout main
    Write-Host "   Branch gh-pages criada!" -ForegroundColor Green
}

# Commit na main
Write-Host "5. Commitando alteracoes na main..." -ForegroundColor Yellow
git add .
git commit -m "$CommitMessage" -ErrorAction SilentlyContinue
Write-Host "   Commit realizado!" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "              PROXIMOS PASSOS          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para publicar no GitHub Pages:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Crie um repositorio no GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Envie o codigo:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/SEU_USUARIO/brcloudstream.git" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host "   git push origin gh-pages" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configure o GitHub Pages:" -ForegroundColor White
Write-Host "   - Va em Settings > Pages" -ForegroundColor Gray
Write-Host "   - Source: Deploy from a branch" -ForegroundColor Gray
Write-Host "   - Branch: gh-pages / root" -ForegroundColor Gray
Write-Host ""
Write-Host "4. URL do repositorio:" -ForegroundColor White
Write-Host "   https://SEU_USUARIO.github.io/brcloudstream/plugins.json" -ForegroundColor Green
Write-Host ""
Write-Host "5. Shortcode sugerido: 'brcs'" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
