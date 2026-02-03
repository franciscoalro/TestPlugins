Write-Host "=== Debug do Problema de Download ===" -ForegroundColor Red
Write-Host ""

$netlifyUrl = "https://resilient-arithmetic-9a594e.netlify.app"

Write-Host "1. Testando se os arquivos estao acessiveis..." -ForegroundColor Cyan

# Testar download real (nao apenas HEAD)
$testFiles = @("MaxSeries.cs3", "AnimesOnlineCC.cs3")

foreach ($file in $testFiles) {
    Write-Host "Testando download: $file" -ForegroundColor Yellow
    
    try {
        $url = "$netlifyUrl/$file"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 30
        
        if ($response.StatusCode -eq 200) {
            $size = $response.Content.Length
            $sizeKB = [math]::Round($size / 1024, 2)
            Write-Host "  ✅ Download OK - $sizeKB KB" -ForegroundColor Green
            
            # Verificar se e um ZIP valido
            $tempFile = [System.IO.Path]::GetTempFileName()
            [System.IO.File]::WriteAllBytes($tempFile, $response.Content)
            
            try {
                Add-Type -AssemblyName System.IO.Compression.FileSystem
                $zip = [System.IO.Compression.ZipFile]::OpenRead($tempFile)
                Write-Host "  ✅ Arquivo ZIP valido com $($zip.Entries.Count) entradas" -ForegroundColor Green
                $zip.Dispose()
            } catch {
                Write-Host "  ❌ Arquivo NAO e um ZIP valido: $_" -ForegroundColor Red
            }
            
            Remove-Item $tempFile -Force
            
        } else {
            Write-Host "  ❌ Status: $($response.StatusCode)" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "  ❌ Erro no download: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "2. Verificando metadados no plugins.json..." -ForegroundColor Cyan

try {
    $pluginsResponse = Invoke-WebRequest -Uri "$netlifyUrl/plugins.json"
    $plugins = $pluginsResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ plugins.json carregado - $($plugins.Count) plugins" -ForegroundColor Green
    
    # Verificar primeiro plugin em detalhes
    $firstPlugin = $plugins[0]
    Write-Host ""
    Write-Host "Analisando plugin: $($firstPlugin.name)" -ForegroundColor Yellow
    Write-Host "  URL: $($firstPlugin.url)" -ForegroundColor White
    Write-Host "  Tamanho esperado: $($firstPlugin.fileSize) bytes" -ForegroundColor White
    Write-Host "  Versao: $($firstPlugin.version)" -ForegroundColor White
    Write-Host "  API Version: $($firstPlugin.apiVersion)" -ForegroundColor White
    Write-Host "  Status: $($firstPlugin.status)" -ForegroundColor White
    
    # Verificar se o arquivo real tem o tamanho correto
    try {
        $fileResponse = Invoke-WebRequest -Uri $firstPlugin.url -Method Head
        $actualSize = [int]$fileResponse.Headers.'Content-Length'
        
        if ($actualSize -eq $firstPlugin.fileSize) {
            Write-Host "  ✅ Tamanho correto" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Tamanho incorreto: real=$actualSize, esperado=$($firstPlugin.fileSize)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Erro ao verificar tamanho: $_" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erro ao carregar plugins.json: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Verificando headers HTTP..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "$netlifyUrl/MaxSeries.cs3" -Method Head
    
    Write-Host "Headers importantes:" -ForegroundColor Yellow
    Write-Host "  Content-Type: $($response.Headers.'Content-Type')" -ForegroundColor White
    Write-Host "  Content-Length: $($response.Headers.'Content-Length')" -ForegroundColor White
    Write-Host "  Access-Control-Allow-Origin: $($response.Headers.'Access-Control-Allow-Origin')" -ForegroundColor White
    Write-Host "  Cache-Control: $($response.Headers.'Cache-Control')" -ForegroundColor White
    
    # Verificar se tem headers que podem causar problemas
    if ($response.Headers.'Content-Encoding') {
        Write-Host "  ⚠️  Content-Encoding: $($response.Headers.'Content-Encoding')" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erro ao obter headers: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Testando compatibilidade com diferentes User-Agents..." -ForegroundColor Cyan

$userAgents = @(
    "CloudStream/3.5.0 (Android 11; Mobile)",
    "okhttp/4.9.0",
    "Dalvik/2.1.0 (Linux; U; Android 11)"
)

foreach ($ua in $userAgents) {
    try {
        $headers = @{ "User-Agent" = $ua }
        $response = Invoke-WebRequest -Uri "$netlifyUrl/MaxSeries.cs3" -Headers $headers -Method Head -TimeoutSec 10
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $ua - OK" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $ua - Status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ $ua - Erro: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== POSSÍVEIS CAUSAS DO PROBLEMA ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ESTRUTURA DO ARQUIVO .cs3:" -ForegroundColor Cyan
Write-Host "   - Arquivo pode estar corrompido" -ForegroundColor White
Write-Host "   - Falta AndroidManifest.xml ou classes.jar" -ForegroundColor White
Write-Host "   - Estrutura interna incorreta" -ForegroundColor White
Write-Host ""
Write-Host "2. METADADOS INCORRETOS:" -ForegroundColor Cyan
Write-Host "   - Tamanho do arquivo diferente do real" -ForegroundColor White
Write-Host "   - URLs incorretas" -ForegroundColor White
Write-Host "   - Campos obrigatorios faltando" -ForegroundColor White
Write-Host ""
Write-Host "3. PROBLEMA NO CLOUDSTREAM:" -ForegroundColor Cyan
Write-Host "   - Versao muito antiga" -ForegroundColor White
Write-Host "   - Cache corrompido" -ForegroundColor White
Write-Host "   - Permissoes de armazenamento" -ForegroundColor White
Write-Host ""
Write-Host "4. PROBLEMA DE REDE:" -ForegroundColor Cyan
Write-Host "   - Bloqueio de dominio .netlify.app" -ForegroundColor White
Write-Host "   - Timeout de download" -ForegroundColor White
Write-Host "   - Problemas de SSL/TLS" -ForegroundColor White