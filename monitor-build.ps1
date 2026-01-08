# Script para monitorar o build e atualizar automaticamente
param(
    [int]$CheckInterval = 30  # Verificar a cada 30 segundos
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Monitor de Build - MaxSeries v10" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$buildUrl = "https://github.com/franciscoalro/TestPlugins/actions"
$releaseUrl = "https://github.com/franciscoalro/TestPlugins/releases"
$pluginUrl = "https://github.com/franciscoalro/TestPlugins/releases/download/v10.0/MaxSeries.cs3"

Write-Host "🔍 Monitorando build..." -ForegroundColor Blue
Write-Host "Build URL: $buildUrl" -ForegroundColor Gray
Write-Host "Plugin URL: $pluginUrl" -ForegroundColor Gray
Write-Host ""

$attempts = 0
$maxAttempts = 20  # 10 minutos máximo

while ($attempts -lt $maxAttempts) {
    $attempts++
    Write-Host "[$attempts/$maxAttempts] Verificando build..." -ForegroundColor Yellow
    
    try {
        # Verificar se o arquivo .cs3 está disponível
        $response = Invoke-WebRequest -Uri $pluginUrl -Method Head -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $fileSize = [math]::Round($response.Headers.'Content-Length' / 1KB, 2)
            Write-Host "✅ BUILD CONCLUÍDO!" -ForegroundColor Green
            Write-Host "📦 MaxSeries v10 disponível ($fileSize KB)" -ForegroundColor Green
            Write-Host ""
            
            # Atualizar plugins.json se necessário
            Write-Host "🔄 Verificando se plugins.json precisa ser atualizado..." -ForegroundColor Blue
            
            $currentPlugins = Get-Content "plugins.json" | ConvertFrom-Json
            $maxSeriesPlugin = $currentPlugins | Where-Object { $_.name -eq "MaxSeries" }
            
            if ($maxSeriesPlugin.url -ne $pluginUrl) {
                Write-Host "📝 Atualizando plugins.json..." -ForegroundColor Blue
                $maxSeriesPlugin.url = $pluginUrl
                $currentPlugins | ConvertTo-Json -Depth 10 | Set-Content "plugins.json"
                
                git add plugins.json
                git commit -m "Update MaxSeries v10 download URL after successful build"
                git push
                
                Write-Host "✅ plugins.json atualizado e commitado!" -ForegroundColor Green
            } else {
                Write-Host "ℹ️ plugins.json já está atualizado" -ForegroundColor Blue
            }
            
            Write-Host ""
            Write-Host "🎯 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
            Write-Host "1. Abra o CloudStream" -ForegroundColor White
            Write-Host "2. Remova e adicione o repositório novamente:" -ForegroundColor White
            Write-Host "   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json" -ForegroundColor Gray
            Write-Host "3. Instale MaxSeries v10" -ForegroundColor White
            Write-Host "4. Teste com uma série que antes mostrava 'Em breve'" -ForegroundColor White
            Write-Host "5. Verifique os logs para debug detalhado" -ForegroundColor White
            Write-Host ""
            Write-Host "📋 Use o guia: MAXSERIES_V10_TEST_GUIDE.md" -ForegroundColor Yellow
            
            break
        }
    } catch {
        Write-Host "⏳ Build ainda em andamento... (Erro: $($_.Exception.Message))" -ForegroundColor Yellow
    }
    
    if ($attempts -lt $maxAttempts) {
        Write-Host "⏱️ Aguardando $CheckInterval segundos..." -ForegroundColor Gray
        Start-Sleep -Seconds $CheckInterval
    }
}

if ($attempts -eq $maxAttempts) {
    Write-Host "⚠️ Timeout atingido. Verifique manualmente:" -ForegroundColor Red
    Write-Host "Build: $buildUrl" -ForegroundColor Red
    Write-Host "Releases: $releaseUrl" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Monitor finalizado" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan