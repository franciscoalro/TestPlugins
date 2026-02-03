# Deploy Manual para CloudstreamRepo usando GitHub CLI
# Agora envia repo.json para builds/ (estrutura correta)
param([string]$Message = "Manual deploy")

Write-Host "=== Deploy Manual para CloudstreamRepo ===" -ForegroundColor Cyan

$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nao autenticado no GitHub CLI" -ForegroundColor Red
    exit 1
}

$tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path $tempDir | Out-Null
Write-Host "Diretorio temporario: $tempDir" -ForegroundColor Gray

try {
    Write-Host "`nClonando CloudstreamRepo..." -ForegroundColor Yellow
    gh repo clone franciscoalro/CloudstreamRepo "$tempDir\CloudstreamRepo" -- --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao clonar CloudstreamRepo" -ForegroundColor Red
        exit 1
    }
    Write-Host "Repositorio clonado" -ForegroundColor Green

    Write-Host "`nCopiando arquivos..." -ForegroundColor Yellow
    
    if (-not (Test-Path "$tempDir\CloudstreamRepo\builds")) {
        New-Item -ItemType Directory -Path "$tempDir\CloudstreamRepo\builds" | Out-Null
    }
    
    $cs3Files = Get-ChildItem "builds\*.cs3" -ErrorAction SilentlyContinue
    $jarFiles = Get-ChildItem "builds\*.jar" -ErrorAction SilentlyContinue
    
    Write-Host "  Encontrados $($cs3Files.Count) arquivos .cs3" -ForegroundColor Gray
    Write-Host "  Encontrados $($jarFiles.Count) arquivos .jar" -ForegroundColor Gray
    
    # Copiar .cs3 e .jar para builds/
    Copy-Item "builds\*.cs3" "$tempDir\CloudstreamRepo\builds\" -ErrorAction SilentlyContinue
    Copy-Item "builds\*.jar" "$tempDir\CloudstreamRepo\builds\" -ErrorAction SilentlyContinue
    
    # Copiar plugins.json para builds/
    Copy-Item "plugins.json" "$tempDir\CloudstreamRepo\builds\" -Force
    
    # Copiar repo.json para builds/ (estrutura correta!)
    Copy-Item "repo.json" "$tempDir\CloudstreamRepo\builds\" -Force
    
    Write-Host "Arquivos copiados" -ForegroundColor Green

    Write-Host "`nVerificando alteracoes..." -ForegroundColor Yellow
    Set-Location "$tempDir\CloudstreamRepo"
    
    git config user.email "action@github.com"
    git config user.name "GitHub Action"
    
    $status = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "Nenhuma alteracao para commitar" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Alteracoes detectadas:" -ForegroundColor Gray
    git status --short

    Write-Host "`nFazendo commit e push..." -ForegroundColor Yellow
    git add .
    git commit -m "Deploy: $Message [$(Get-Date -Format 'yyyy-MM-dd HH:mm')]" --quiet
    git push origin main --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deploy realizado com sucesso!" -ForegroundColor Green
        Write-Host "`nURL para CloudStream:" -ForegroundColor Cyan
        Write-Host "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor White
    } else {
        Write-Host "Erro no push" -ForegroundColor Red
        exit 1
    }

} finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    Write-Host "Limpeza concluida" -ForegroundColor Gray
}
