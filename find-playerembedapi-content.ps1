# Script para encontrar conteudo com PlayerEmbedAPI
# MaxSeries v219 - 28 Jan 2026

Write-Host "Procurando conteudo com PlayerEmbedAPI..." -ForegroundColor Cyan
Write-Host ""

# Lista de URLs para testar
$testUrls = @(
    "https://www.maxseries.pics/series/assistir-the-last-of-us-online",
    "https://www.maxseries.pics/series/assistir-the-boys-online",
    "https://www.maxseries.pics/series/assistir-breaking-bad-online",
    "https://www.maxseries.pics/series/assistir-stranger-things-online",
    "https://www.maxseries.pics/series/assistir-the-walking-dead-online",
    "https://www.maxseries.pics/filmes/assistir-avatar-o-caminho-da-agua-online",
    "https://www.maxseries.pics/filmes/assistir-vingadores-ultimato-online",
    "https://www.maxseries.pics/filmes/assistir-homem-aranha-sem-volta-para-casa-online"
)

$found = @()

foreach ($url in $testUrls) {
    Write-Host "Testando: $url" -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        $html = $response.Content
        
        # Procurar por iframe do playerthree/viewplayer
        $pattern = 'https?://(playerthree|viewplayer)\.online/(embed|filme)/[^"<>\s]+'
        if ($html -match $pattern) {
            $playerUrl = $matches[0]
            Write-Host "  Player encontrado: $playerUrl" -ForegroundColor Green
            
            # Buscar a pagina do player
            try {
                $playerResponse = Invoke-WebRequest -Uri $playerUrl -UseBasicParsing -TimeoutSec 10
                $playerHtml = $playerResponse.Content
                
                # Procurar por PlayerEmbedAPI
                if ($playerHtml -match 'playerembedapi') {
                    Write-Host "  PLAYEREMBEDAPI ENCONTRADO!" -ForegroundColor Green
                    $found += @{
                        "MaxSeriesUrl" = $url
                        "PlayerUrl" = $playerUrl
                    }
                } else {
                    Write-Host "  PlayerEmbedAPI nao disponivel" -ForegroundColor Red
                }
            } catch {
                Write-Host "  Erro ao acessar player: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  Player nao encontrado" -ForegroundColor Red
        }
    } catch {
        Write-Host "  Erro ao acessar: $_" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "RESULTADOS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

if ($found.Count -gt 0) {
    Write-Host "Encontrados $($found.Count) conteudo(s) com PlayerEmbedAPI:" -ForegroundColor Green
    Write-Host ""
    
    foreach ($item in $found) {
        Write-Host "MaxSeries: $($item.MaxSeriesUrl)" -ForegroundColor Yellow
        Write-Host "Player: $($item.PlayerUrl)" -ForegroundColor Yellow
        Write-Host ""
    }
    
    Write-Host "Use um desses para testar PlayerEmbedAPI no app!" -ForegroundColor Green
} else {
    Write-Host "Nenhum conteudo com PlayerEmbedAPI encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Sugestoes:" -ForegroundColor Yellow
    Write-Host "  1. Testar mais URLs manualmente no browser" -ForegroundColor White
    Write-Host "  2. Procurar series/filmes recentes" -ForegroundColor White
    Write-Host "  3. Verificar se PlayerEmbedAPI ainda esta ativo no site" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
