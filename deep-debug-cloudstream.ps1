Write-Host "=== Analise Profunda do Cloudstream ===" -ForegroundColor Green
Write-Host ""

# Verificar se ha problemas especificos com o formato dos arquivos
Write-Host "1. Verificando formato dos arquivos .cs3..." -ForegroundColor Cyan

$cs3Files = Get-ChildItem "builds" -Filter "*.cs3" | Select-Object -First 2

foreach ($file in $cs3Files) {
    Write-Host "  Analisando: $($file.Name)" -ForegroundColor Yellow
    
    # Verificar se e um ZIP valido
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($file.FullName)
        
        Write-Host "    ✅ ZIP valido com $($zip.Entries.Count) entradas" -ForegroundColor Green
        
        # Verificar entradas especificas
        $hasManifest = $zip.Entries | Where-Object { $_.Name -eq "AndroidManifest.xml" }
        $hasClasses = $zip.Entries | Where-Object { $_.Name -eq "classes.jar" }
        
        if ($hasManifest) {
            Write-Host "    ✅ AndroidManifest.xml presente" -ForegroundColor Green
        } else {
            Write-Host "    ❌ AndroidManifest.xml ausente" -ForegroundColor Red
        }
        
        if ($hasClasses) {
            Write-Host "    ✅ classes.jar presente" -ForegroundColor Green
        } else {
            Write-Host "    ❌ classes.jar ausente" -ForegroundColor Red
        }
        
        $zip.Dispose()
        
    } catch {
        Write-Host "    ❌ Erro ao abrir ZIP: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "2. Verificando compatibilidade com diferentes clientes HTTP..." -ForegroundColor Cyan

# Testar com diferentes user agents (simular diferentes clientes)
$userAgents = @(
    "CloudStream/3.5.0 (Android)",
    "okhttp/4.9.0",
    "Mozilla/5.0 (Android)"
)

$testUrl = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.cs3"

foreach ($ua in $userAgents) {
    try {
        $headers = @{ "User-Agent" = $ua }
        $response = Invoke-WebRequest -Uri $testUrl -Method Head -Headers $headers -TimeoutSec 10
        Write-Host "  ✅ $ua - OK ($($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $ua - Erro: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "3. Verificando headers HTTP..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $testUrl -Method Head
    
    Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Yellow
    Write-Host "  Content-Type: $($response.Headers.'Content-Type')" -ForegroundColor Yellow
    Write-Host "  Content-Length: $($response.Headers.'Content-Length')" -ForegroundColor Yellow
    Write-Host "  Cache-Control: $($response.Headers.'Cache-Control')" -ForegroundColor Yellow
    Write-Host "  ETag: $($response.Headers.'ETag')" -ForegroundColor Yellow
    
} catch {
    Write-Host "  ❌ Erro ao obter headers: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Testando download parcial (Range requests)..." -ForegroundColor Cyan

try {
    $headers = @{ "Range" = "bytes=0-1023" }
    $response = Invoke-WebRequest -Uri $testUrl -Headers $headers -TimeoutSec 10
    
    if ($response.StatusCode -eq 206) {
        Write-Host "  ✅ Range requests suportados" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Range requests nao suportados (Status: $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Erro no teste de range: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Verificando JSON com diferentes parsers..." -ForegroundColor Cyan

$pluginsJsonPath = "builds/plugins.json"

# Testar com ConvertFrom-Json
try {
    $plugins1 = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json
    Write-Host "  ✅ PowerShell ConvertFrom-Json: OK ($($plugins1.Count) plugins)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ PowerShell ConvertFrom-Json: $_" -ForegroundColor Red
}

# Verificar se ha caracteres nao-ASCII
$jsonContent = Get-Content $pluginsJsonPath -Raw
$nonAsciiChars = [regex]::Matches($jsonContent, '[^\x00-\x7F]')

if ($nonAsciiChars.Count -gt 0) {
    Write-Host "  ⚠️  $($nonAsciiChars.Count) caracteres nao-ASCII encontrados" -ForegroundColor Yellow
    $nonAsciiChars | Select-Object -First 5 | ForEach-Object {
        Write-Host "    Char: '$($_.Value)' na posicao $($_.Index)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ Apenas caracteres ASCII no JSON" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Recomendacoes ===" -ForegroundColor Green

Write-Host "Se o problema persistir:" -ForegroundColor Yellow
Write-Host "1. Verifique a versao do Cloudstream (minimo 3.5.0)" -ForegroundColor Cyan
Write-Host "2. Teste com outro dispositivo Android" -ForegroundColor Cyan
Write-Host "3. Verifique se nao ha bloqueio de rede/firewall" -ForegroundColor Cyan
Write-Host "4. Limpe completamente o cache do Cloudstream" -ForegroundColor Cyan
Write-Host "5. Reinstale o Cloudstream se necessario" -ForegroundColor Cyan