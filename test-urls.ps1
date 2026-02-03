Write-Host "=== Testando URLs dos Plugins ===" -ForegroundColor Green
Write-Host ""

# URLs para testar
$urls = @(
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/repo.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/plugins.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/MaxSeries.cs3",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/MaxSeries.jar"
)

foreach ($url in $urls) {
    Write-Host "Testando: $url" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15
        Write-Host "  Status: $($response.StatusCode) - OK" -ForegroundColor Green
        
        if ($response.Headers.'Content-Length') {
            $size = [int]$response.Headers.'Content-Length'
            $sizeKB = [math]::Round($size / 1024, 2)
            Write-Host "  Tamanho: $sizeKB KB" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ERRO: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== Verificando Estrutura do Repositorio ===" -ForegroundColor Green

# Verificar se o branch esta correto
$branchUrl = "https://api.github.com/repos/franciscoalro/CloudstreamRepo/branches"
try {
    $branches = Invoke-RestMethod -Uri $branchUrl
    Write-Host "Branches disponiveis:" -ForegroundColor Cyan
    foreach ($branch in $branches) {
        Write-Host "  - $($branch.name)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Erro ao verificar branches: $_" -ForegroundColor Red
}