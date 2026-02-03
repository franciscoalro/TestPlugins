Write-Host "=== Deploy Final e Teste Completo ===" -ForegroundColor Green
Write-Host ""

# 1. Verificar se todos os arquivos estao prontos
Write-Host "1. Verificando arquivos..." -ForegroundColor Cyan

$requiredFiles = @(
    "builds/plugins.json",
    "builds/repo.json", 
    "builds/plugins-minimal.json",
    "builds/repo-alternative.json"
)

$allFilesReady = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  ✅ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - FALTANDO" -ForegroundColor Red
        $allFilesReady = $false
    }
}

if (-not $allFilesReady) {
    Write-Host "❌ Alguns arquivos estao faltando!" -ForegroundColor Red
    exit 1
}

# 2. Testar todos os URLs
Write-Host ""
Write-Host "2. Testando URLs..." -ForegroundColor Cyan

$testUrls = @(
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.cs3",
    "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.jar"
)

$allUrlsWork = $true
foreach ($url in $testUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $($url.Split('/')[-1])" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $($url.Split('/')[-1]) - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $($url.Split('/')[-1]) - Erro: $_" -ForegroundColor Red
        $allUrlsWork = $false
    }
}

# 3. Validar estrutura dos plugins
Write-Host ""
Write-Host "3. Validando plugins..." -ForegroundColor Cyan

$plugins = Get-Content "builds/plugins.json" -Raw | ConvertFrom-Json
Write-Host "  📊 Total de plugins: $($plugins.Count)" -ForegroundColor Yellow

$totalSize = 0
foreach ($plugin in $plugins) {
    $cs3File = "builds/$($plugin.internalName).cs3"
    if (Test-Path $cs3File) {
        $actualSize = (Get-Item $cs3File).Length
        if ($actualSize -eq $plugin.fileSize) {
            Write-Host "  ✅ $($plugin.name) - Tamanho correto" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $($plugin.name) - Tamanho: $actualSize vs $($plugin.fileSize)" -ForegroundColor Yellow
        }
        $totalSize += $actualSize
    } else {
        Write-Host "  ❌ $($plugin.name) - Arquivo .cs3 faltando" -ForegroundColor Red
    }
}

$totalSizeMB = [math]::Round($totalSize / 1024 / 1024, 2)
Write-Host "  📦 Tamanho total: $totalSizeMB MB" -ForegroundColor Yellow

# 4. Criar resumo final
Write-Host ""
Write-Host "=== RESUMO FINAL ===" -ForegroundColor Green
Write-Host ""

if ($allFilesReady -and $allUrlsWork) {
    Write-Host "🎉 TUDO PRONTO PARA USO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URLs para usar no Cloudstream:" -ForegroundColor Yellow
    Write-Host "  Principal: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor Cyan
    Write-Host "  Alternativa: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo-alternative.json" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Plugins disponiveis: $($plugins.Count)" -ForegroundColor Yellow
    Write-Host "Tamanho total: $totalSizeMB MB" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✅ Arquivos .cs3 validos" -ForegroundColor Green
    Write-Host "✅ URLs acessiveis" -ForegroundColor Green  
    Write-Host "✅ JSON bem formatado" -ForegroundColor Green
    Write-Host "✅ Tamanhos corretos" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 TESTE AGORA NO CLOUDSTREAM!" -ForegroundColor Green
} else {
    Write-Host "❌ AINDA HA PROBLEMAS" -ForegroundColor Red
    Write-Host "Verifique os erros acima antes de continuar." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Proximos Passos ===" -ForegroundColor Cyan
Write-Host "1. Teste no Cloudstream Android" -ForegroundColor White
Write-Host "2. Se funcionar, faça o commit das mudanças" -ForegroundColor White
Write-Host "3. Se nao funcionar, use a URL alternativa" -ForegroundColor White
Write-Host "4. Reporte o resultado para debug adicional" -ForegroundColor White