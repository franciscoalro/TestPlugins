Write-Host "Verificando release v12.0..." -ForegroundColor Yellow

$releaseUrl = "https://api.github.com/repos/franciscoalro/TestPlugins/releases/tags/v12.0"

try {
    $response = Invoke-RestMethod -Uri $releaseUrl -Method Get
    Write-Host "Release v12.0 encontrado!" -ForegroundColor Green
    Write-Host "Assets disponíveis:" -ForegroundColor Cyan
    
    foreach ($asset in $response.assets) {
        Write-Host "- $($asset.name)" -ForegroundColor White
        Write-Host "  Download: $($asset.browser_download_url)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "INSTALE AGORA:" -ForegroundColor Yellow
    Write-Host "https://github.com/franciscoalro/TestPlugins/releases/download/v12.0/MaxSeries.cs3" -ForegroundColor Green
    
} catch {
    Write-Host "Release v12.0 ainda não disponível" -ForegroundColor Red
    Write-Host "Aguarde alguns minutos para o GitHub Actions completar" -ForegroundColor Yellow
}