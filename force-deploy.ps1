# Deploy forçado para CloudstreamRepo
param([string]$Message = "Force update")

Write-Host "=== Deploy FORÇADO para CloudstreamRepo ===" -ForegroundColor Cyan

$tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    Write-Host "`nClonando CloudstreamRepo..." -ForegroundColor Yellow
    gh repo clone franciscoalro/CloudstreamRepo "$tempDir\repo" -- --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao clonar" -ForegroundColor Red
        exit 1
    }

    $repoDir = "$tempDir\repo"
    
    # Garantir que a pasta builds existe
    if (-not (Test-Path "$repoDir\builds")) {
        New-Item -ItemType Directory -Path "$repoDir\builds" | Out-Null
    }

    Write-Host "`nCopiando TODOS os arquivos..." -ForegroundColor Yellow
    
    # Copiar .cs3
    Copy-Item "builds\*.cs3" "$repoDir\builds\" -Force
    Write-Host "  ✅ Arquivos .cs3 copiados" -ForegroundColor Green
    
    # Copiar .jar
    Copy-Item "builds\*.jar" "$repoDir\builds\" -Force
    Write-Host "  ✅ Arquivos .jar copiados" -ForegroundColor Green
    
    # Copiar plugins.json
    Copy-Item "plugins.json" "$repoDir\builds\plugins.json" -Force
    Write-Host "  ✅ plugins.json copiado" -ForegroundColor Green
    
    # Copiar repo.json
    Copy-Item "repo.json" "$repoDir\builds\repo.json" -Force
    Write-Host "  ✅ repo.json copiado" -ForegroundColor Green

    Set-Location $repoDir
    
    # Configurar git
    git config user.email "action@github.com"
    git config user.name "GitHub Action"
    
    # Adicionar todos os arquivos explicitamente
    git add builds/*.cs3 builds/*.jar builds/plugins.json builds/repo.json
    
    # Verificar status
    $status = git status --porcelain
    Write-Host "`nStatus do git:" -ForegroundColor Gray
    git status --short
    
    # Commit e push
    git commit -m "Force deploy: $Message [$(Get-Date -Format 'yyyy-MM-dd HH:mm')]" --quiet
    if ($LASTEXITCODE -eq 0) {
        git push origin main --quiet
        Write-Host "`n✅ Deploy forçado realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️ Nada para commitar ou erro no commit" -ForegroundColor Yellow
    }

    Write-Host "`nURL para CloudStream:" -ForegroundColor Cyan
    Write-Host "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor White

} finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
}
