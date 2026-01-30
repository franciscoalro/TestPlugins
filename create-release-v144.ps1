# Create GitHub Release v144
$ErrorActionPreference = "Stop"

Write-Host "=== MaxSeries v144 Release ===" -ForegroundColor Cyan

# Verificar se o arquivo existe
$cs3File = "MaxSeries\build\MaxSeries.cs3"
if (-not (Test-Path $cs3File)) {
    Write-Host "Arquivo nao encontrado: $cs3File" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $cs3File).Length
Write-Host "Arquivo encontrado: $fileSize bytes" -ForegroundColor Green

# Criar tag e release
Write-Host "Criando tag v144..." -ForegroundColor Yellow
git tag -a v144 -m "MaxSeries v144 - Fix: Regex simplificado + logs detalhados"
git push origin v144

Write-Host "Criando release no GitHub..." -ForegroundColor Yellow
gh release create v144 --title "MaxSeries v144 - Fix: Regex Simplificado" --notes-file "release-notes-v144.md" "$cs3File"

Write-Host "Release v144 criado com sucesso!" -ForegroundColor Green
Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/download/v144/MaxSeries.cs3" -ForegroundColor Cyan
