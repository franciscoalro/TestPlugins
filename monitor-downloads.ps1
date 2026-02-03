Write-Host "=== Monitoramento de Downloads ===" -ForegroundColor Green
Write-Host ""

# URLs para monitorar
$urls = @(
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.cs3"
)

foreach ($url in $urls) {
    Write-Host "Testando: $($url.Split('/')[-1])" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10
        $status = $response.StatusCode
        
        if ($status -eq 200) {
            Write-Host "  ✅ OK ($status)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Status: $status" -ForegroundColor Yellow
        }
        
        # Verificar cache headers
        if ($response.Headers.'Cache-Control') {
            Write-Host "  📦 Cache: $($response.Headers.'Cache-Control')" -ForegroundColor Blue
        }
        
    } catch {
        Write-Host "  ❌ Erro: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Status dos Arquivos ===" -ForegroundColor Green

$plugins = Get-Content "builds/plugins.json" -Raw | ConvertFrom-Json
Write-Host "Plugins no repositorio: $($plugins.Count)" -ForegroundColor Cyan

$totalSize = 0
foreach ($plugin in $plugins) {
    $totalSize += $plugin.fileSize
}

$totalSizeMB = [math]::Round($totalSize / 1024 / 1024, 2)
Write-Host "Tamanho total: $totalSizeMB MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "URL para usuarios: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor Yellow