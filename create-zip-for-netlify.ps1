Write-Host "=== Criando ZIP para Netlify ===" -ForegroundColor Green
Write-Host ""

# Verificar se a pasta existe
if (-not (Test-Path "cloud-deploy")) {
    Write-Host "Pasta cloud-deploy nao encontrada!" -ForegroundColor Red
    exit 1
}

# Criar ZIP
$zipPath = "brcloudstream-netlify.zip"

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
    Write-Host "ZIP antigo removido" -ForegroundColor Yellow
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory("cloud-deploy", $zipPath)
    
    $zipSize = (Get-Item $zipPath).Length
    $zipSizeMB = [math]::Round($zipSize / 1024 / 1024, 2)
    
    Write-Host "ZIP criado com sucesso!" -ForegroundColor Green
    Write-Host "Arquivo: $zipPath" -ForegroundColor Cyan
    Write-Host "Tamanho: $zipSizeMB MB" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "=== OPCOES DE UPLOAD ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "OPCAO 1 - Upload da pasta (Recomendado):" -ForegroundColor Cyan
    Write-Host "1. Acesse https://netlify.com" -ForegroundColor White
    Write-Host "2. Arraste a pasta 'cloud-deploy' inteira para o site" -ForegroundColor White
    Write-Host ""
    Write-Host "OPCAO 2 - Upload do ZIP:" -ForegroundColor Cyan
    Write-Host "1. Acesse https://netlify.com" -ForegroundColor White
    Write-Host "2. Arraste o arquivo '$zipPath' para o site" -ForegroundColor White
    Write-Host "3. O Netlify extraira automaticamente" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Ambas as opcoes funcionam perfeitamente!" -ForegroundColor Green
    
} catch {
    Write-Host "Erro ao criar ZIP: $_" -ForegroundColor Red
}