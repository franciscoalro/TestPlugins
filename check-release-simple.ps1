Write-Host "Verificando release v11.0..." -ForegroundColor Yellow

$releaseUrl = "https://api.github.com/repos/franciscoalro/TestPlugins/releases/tags/v11.0"

try {
    $response = Invoke-RestMethod -Uri $releaseUrl -Method Get
    Write-Host "Release v11.0 encontrado!" -ForegroundColor Green
    Write-Host "Assets disponíveis:" -ForegroundColor Cyan
    
    foreach ($asset in $response.assets) {
        Write-Host "- $($asset.name)" -ForegroundColor White
        Write-Host "  Download: $($asset.browser_download_url)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Release v11.0 ainda não disponível" -ForegroundColor Red
    Write-Host "Aguarde alguns minutos para o GitHub Actions completar" -ForegroundColor Yellow
}