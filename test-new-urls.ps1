Write-Host "=== Testando Novas URLs Simplificadas ===" -ForegroundColor Green
Write-Host ""

$urls = @(
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.cs3",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.jar"
)

foreach ($url in $urls) {
    Write-Host "Testando: $url" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15
        Write-Host "  ✅ Status: $($response.StatusCode) - OK" -ForegroundColor Green
        
        if ($response.Headers.'Content-Length') {
            $size = [int]$response.Headers.'Content-Length'
            $sizeKB = [math]::Round($size / 1024, 2)
            Write-Host "  📊 Tamanho: $sizeKB KB" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ ERRO: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== URL Final para o Cloudstream ===" -ForegroundColor Green
Write-Host "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor Cyan