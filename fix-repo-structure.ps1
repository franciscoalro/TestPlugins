# Corrige estrutura do CloudstreamRepo
# Move repo.json para dentro da pasta builds/

Write-Host "=== Corrigindo estrutura do CloudstreamRepo ===" -ForegroundColor Cyan

$tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    Write-Host "`nClonando CloudstreamRepo..." -ForegroundColor Yellow
    gh repo clone franciscoalro/CloudstreamRepo "$tempDir\CloudstreamRepo" -- --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao clonar" -ForegroundColor Red
        exit 1
    }

    Set-Location "$tempDir\CloudstreamRepo"

    Write-Host "`nVerificando estrutura atual..." -ForegroundColor Yellow
    
    # Verificar se repo.json existe na raiz
    if (Test-Path "repo.json") {
        Write-Host "repo.json encontrado na raiz - movendo para builds/" -ForegroundColor Yellow
        
        # Copiar para builds/
        Copy-Item "repo.json" "builds\repo.json" -Force
        
        # Remover da raiz
        Remove-Item "repo.json" -Force
        
        Write-Host "repo.json movido com sucesso" -ForegroundColor Green
    }
    
    # Verificar se plugins.json existe na raiz (deve estar apenas em builds/)
    if (Test-Path "plugins.json") {
        Write-Host "plugins.json encontrado na raiz - removendo duplicata" -ForegroundColor Yellow
        Remove-Item "plugins.json" -Force
    }

    # Verificar status
    $status = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "Nenhuma alteracao necessaria" -ForegroundColor Yellow
        exit 0
    }

    Write-Host "`nAlteracoes:" -ForegroundColor Gray
    git status --short

    # Commit
    Write-Host "`nFazendo commit..." -ForegroundColor Yellow
    git config user.email "action@github.com"
    git config user.name "GitHub Action"
    git add .
    git commit -m "Fix: Move repo.json para builds/ (estrutura correta)" --quiet
    git push origin main --quiet

    Write-Host "`n✅ Estrutura corrigida!" -ForegroundColor Green
    Write-Host "`nNova URL para CloudStream:" -ForegroundColor Cyan
    Write-Host "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor White

} finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
}
