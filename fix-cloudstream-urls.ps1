Write-Host "=== Corrigindo URLs para Cloudstream ===" -ForegroundColor Green
Write-Host ""

$pluginsJsonPath = "builds/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

# Usar URLs mais simples sem refs/heads
$baseUrl = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds"

foreach ($plugin in $plugins) {
    $oldCs3Url = $plugin.url
    $oldJarUrl = $plugin.jarUrl
    
    # Atualizar URLs
    $plugin.url = "$baseUrl/$($plugin.internalName).cs3"
    $plugin.jarUrl = "$baseUrl/$($plugin.internalName).jar"
    
    Write-Host "Plugin: $($plugin.name)" -ForegroundColor Cyan
    Write-Host "  CS3: $oldCs3Url" -ForegroundColor Red
    Write-Host "  ->   $($plugin.url)" -ForegroundColor Green
    Write-Host "  JAR: $oldJarUrl" -ForegroundColor Red  
    Write-Host "  ->   $($plugin.jarUrl)" -ForegroundColor Green
    Write-Host ""
}

# Salvar plugins.json atualizado
$jsonContent = $plugins | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($pluginsJsonPath, $jsonContent, [System.Text.UTF8Encoding]::new($false))

# Copiar para raiz
Copy-Item $pluginsJsonPath "plugins.json" -Force

Write-Host "✅ URLs atualizados!" -ForegroundColor Green
Write-Host ""

# Testar novos URLs
Write-Host "Testando novos URLs..." -ForegroundColor Cyan
$testUrls = @(
    "$baseUrl/MaxSeries.cs3",
    "$baseUrl/MaxSeries.jar"
)

foreach ($url in $testUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10
        Write-Host "✅ $url - OK ($($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "❌ $url - ERRO: $_" -ForegroundColor Red
    }
}