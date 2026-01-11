#!/usr/bin/env pwsh
# Upload MaxSeries.cs3 to GitHub Release v52.0

$releaseTag = "v52.0"
$repoOwner = "franciscoalro"
$repoName = "TestPlugins"
$assetPath = "MaxSeries.cs3"

Write-Host "Uploading MaxSeries.cs3 to release $releaseTag..." -ForegroundColor Green

# Verificar se o arquivo existe
if (!(Test-Path $assetPath)) {
    Write-Host "Erro: $assetPath nao encontrado!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $assetPath).Length
Write-Host "Arquivo encontrado: $assetPath ($fileSize bytes)" -ForegroundColor Green

# Usar GitHub CLI se disponível
try {
    $ghVersion = gh --version
    Write-Host "GitHub CLI encontrado: $ghVersion" -ForegroundColor Green
    
    # Upload usando gh CLI
    Write-Host "Fazendo upload via GitHub CLI..." -ForegroundColor Yellow
    gh release upload $releaseTag $assetPath --clobber --repo "$repoOwner/$repoName"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Upload concluido com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Erro no upload via GitHub CLI" -ForegroundColor Red
    }
} catch {
    Write-Host "GitHub CLI nao encontrado. Instrucoes manuais:" -ForegroundColor Yellow
    Write-Host "1. Acesse: https://github.com/$repoOwner/$repoName/releases/tag/$releaseTag" -ForegroundColor White
    Write-Host "2. Clique em 'Edit release'" -ForegroundColor White
    Write-Host "3. Arraste o arquivo $assetPath para a area de assets" -ForegroundColor White
    Write-Host "4. Clique em 'Update release'" -ForegroundColor White
}

Write-Host "`nVerificacao:" -ForegroundColor Cyan
Write-Host "URL do release: https://github.com/$repoOwner/$repoName/releases/tag/$releaseTag" -ForegroundColor White
Write-Host "URL do download: https://github.com/$repoOwner/$repoName/releases/download/$releaseTag/$assetPath" -ForegroundColor White