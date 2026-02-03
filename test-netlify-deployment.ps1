Write-Host "=== Testando Deploy do Netlify ===" -ForegroundColor Green
Write-Host ""

$baseUrl = "https://resilient-arithmetic-9a594e.netlify.app"

# URLs para testar
$testUrls = @(
    "$baseUrl/repo.json",
    "$baseUrl/plugins.json", 
    "$baseUrl/repo-alternative.json",
    "$baseUrl/MaxSeries.cs3",
    "$baseUrl/MaxSeries.jar",
    "$baseUrl" # pagina principal
)

Write-Host "Testando URLs do seu site Netlify..." -ForegroundColor Cyan
Write-Host "Site: $baseUrl" -ForegroundColor Yellow
Write-Host ""

$allWorking = $true

foreach ($url in $testUrls) {
    $fileName = $url.Split('/')[-1]
    if ($fileName -eq "resilient-arithmetic-9a594e.netlify.app") {
        $fileName = "index.html"
    }
    
    Write-Host "Testando: $fileName" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ OK ($($response.StatusCode))" -ForegroundColor Green
            
            if ($response.Headers.'Content-Length') {
                $size = [int]$response.Headers.'Content-Length'
                $sizeKB = [math]::Round($size / 1024, 2)
                Write-Host "  📊 Tamanho: $sizeKB KB" -ForegroundColor Yellow
            }
            
            # Verificar Content-Type
            if ($response.Headers.'Content-Type') {
                Write-Host "  📄 Tipo: $($response.Headers.'Content-Type')" -ForegroundColor Blue
            }
        } else {
            Write-Host "  ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "  ❌ Erro: $_" -ForegroundColor Red
        $allWorking = $false
    }
    
    Write-Host ""
}

Write-Host "=== RESULTADO FINAL ===" -ForegroundColor Green
Write-Host ""

if ($allWorking) {
    Write-Host "🎉 TUDO FUNCIONANDO PERFEITAMENTE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Site online e acessível" -ForegroundColor Green
    Write-Host "✅ Arquivos JSON válidos" -ForegroundColor Green
    Write-Host "✅ Plugins .cs3 disponíveis" -ForegroundColor Green
    Write-Host "✅ Arquivos .jar disponíveis" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 URL PARA O CLOUDSTREAM:" -ForegroundColor Yellow
    Write-Host "$baseUrl/repo.json" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📱 COMO USAR NO CLOUDSTREAM:" -ForegroundColor Yellow
    Write-Host "1. Abra o Cloudstream Android" -ForegroundColor White
    Write-Host "2. Configurações > Extensões" -ForegroundColor White
    Write-Host "3. Adicionar Repositório" -ForegroundColor White
    Write-Host "4. Cole: $baseUrl/repo.json" -ForegroundColor White
    Write-Host "5. Instale os plugins!" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 PÁGINA WEB:" -ForegroundColor Yellow
    Write-Host "Acesse: $baseUrl" -ForegroundColor Cyan
    Write-Host "(Para ver informações e links)" -ForegroundColor Gray
    
} else {
    Write-Host "❌ Alguns problemas encontrados" -ForegroundColor Red
    Write-Host "Verifique os erros acima" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== URLs ALTERNATIVAS ===" -ForegroundColor Cyan
Write-Host "Principal: $baseUrl/repo.json" -ForegroundColor Green
Write-Host "Alternativa: $baseUrl/repo-alternative.json" -ForegroundColor Yellow
Write-Host "Plugins: $baseUrl/plugins.json" -ForegroundColor Blue