Write-Host "=== Debug do Problema de Download ===" -ForegroundColor Red
Write-Host ""

# Verificar se os URLs estao realmente acessiveis
$pluginsJsonPath = "builds/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json

Write-Host "Testando acessibilidade dos URLs..." -ForegroundColor Cyan

foreach ($plugin in $plugins) {
    Write-Host "Plugin: $($plugin.name)" -ForegroundColor Yellow
    
    # Testar URL do .cs3
    try {
        $response = Invoke-WebRequest -Uri $plugin.url -Method Head -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ URL .cs3 acessivel ($($response.StatusCode))" -ForegroundColor Green
            Write-Host "  📊 Content-Length: $($response.Headers.'Content-Length')" -ForegroundColor Cyan
        } else {
            Write-Host "  ❌ URL .cs3 problema: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ URL .cs3 inacessivel: $_" -ForegroundColor Red
    }
    
    # Testar URL do .jar
    try {
        $response = Invoke-WebRequest -Uri $plugin.jarUrl -Method Head -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ URL .jar acessivel ($($response.StatusCode))" -ForegroundColor Green
        } else {
            Write-Host "  ❌ URL .jar problema: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ URL .jar inacessivel: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "Testando URL do plugins.json..." -ForegroundColor Cyan
$pluginsUrl = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/plugins.json"

try {
    $response = Invoke-WebRequest -Uri $pluginsUrl -Method Head -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ plugins.json acessivel ($($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "❌ plugins.json problema: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ plugins.json inacessivel: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Testando URL do repo.json..." -ForegroundColor Cyan
$repoUrl = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/repo.json"

try {
    $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ repo.json acessivel ($($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "❌ repo.json problema: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ repo.json inacessivel: $_" -ForegroundColor Red
}