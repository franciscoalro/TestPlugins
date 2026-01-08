# Script para verificar se o release v11.0 foi criado
Write-Host "🔍 Verificando release v11.0..." -ForegroundColor Yellow

$releaseUrl = "https://api.github.com/repos/franciscoalro/TestPlugins/releases/tags/v11.0"

try {
    $response = Invoke-RestMethod -Uri $releaseUrl -Method Get
    Write-Host "✅ Release v11.0 encontrado!" -ForegroundColor Green
    Write-Host "📦 Assets disponíveis:" -ForegroundColor Cyan
    
    foreach ($asset in $response.assets) {
        Write-Host "  - $($asset.name) ($($asset.size) bytes)" -ForegroundColor White
        Write-Host "    Download: $($asset.browser_download_url)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "🎯 Para instalar no CloudStream:" -ForegroundColor Yellow
    Write-Host "1. Baixe: https://github.com/franciscoalro/TestPlugins/releases/download/v11.0/MaxSeries.cs3" -ForegroundColor White
    Write-Host "2. Instale no CloudStream" -ForegroundColor White
    Write-Host "3. Teste com filmes e séries" -ForegroundColor White
    
} catch {
    Write-Host "⏳ Release v11.0 ainda não disponível" -ForegroundColor Red
    Write-Host "💡 Aguarde alguns minutos para o GitHub Actions completar o build" -ForegroundColor Yellow
    
    # Verificar se existe algum workflow rodando
    try {
        $workflowUrl = "https://api.github.com/repos/franciscoalro/TestPlugins/actions/runs?status=in_progress"
        $workflows = Invoke-RestMethod -Uri $workflowUrl -Method Get
        
        if ($workflows.total_count -gt 0) {
            Write-Host "🔄 Build em andamento..." -ForegroundColor Cyan
        } else {
            Write-Host "❌ Nenhum build em andamento. Pode haver um problema." -ForegroundColor Red
        }
    } catch {
        Write-Host "⚠️ Não foi possível verificar status do workflow" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📋 Para verificar manualmente:" -ForegroundColor Cyan
Write-Host "- Releases: https://github.com/franciscoalro/TestPlugins/releases" -ForegroundColor Gray
Write-Host "- Actions: https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor Gray