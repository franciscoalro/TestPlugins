Write-Host "=== Verificacao de Integridade dos Arquivos ===" -ForegroundColor Green
Write-Host ""

# Verificar se os arquivos .cs3 podem ser abertos como ZIP
$buildsPath = "builds"
$cs3Files = Get-ChildItem -Path $buildsPath -Filter "*.cs3"

foreach ($file in $cs3Files) {
    Write-Host "Testando integridade: $($file.Name)" -ForegroundColor Cyan
    
    try {
        # Tentar extrair para uma pasta temporaria
        $tempDir = "temp_integrity_test_$($file.BaseName)"
        
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
        
        # Usar .NET para extrair o ZIP
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($file.FullName, $tempDir)
        
        # Verificar se extraiu corretamente
        $extractedFiles = Get-ChildItem $tempDir -Recurse
        Write-Host "  ✅ Extraido com sucesso - $($extractedFiles.Count) arquivos" -ForegroundColor Green
        
        # Verificar se tem os arquivos esperados de um plugin Cloudstream
        $hasManifest = Test-Path (Join-Path $tempDir "plugin.json")
        $hasClasses = (Get-ChildItem $tempDir -Filter "*.dex" -Recurse).Count -gt 0
        
        if ($hasManifest) {
            Write-Host "  ✅ plugin.json encontrado" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  plugin.json nao encontrado" -ForegroundColor Yellow
        }
        
        if ($hasClasses) {
            Write-Host "  ✅ Arquivos .dex encontrados" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Arquivos .dex nao encontrados" -ForegroundColor Yellow
        }
        
        # Limpar pasta temporaria
        Remove-Item $tempDir -Recurse -Force
        
    } catch {
        Write-Host "  ❌ Erro ao extrair: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Verificar tamanhos dos arquivos
Write-Host "Verificando tamanhos dos arquivos..." -ForegroundColor Cyan
$plugins = Get-Content "builds/plugins.json" -Raw | ConvertFrom-Json

foreach ($plugin in $plugins) {
    $cs3File = "builds/$($plugin.internalName).cs3"
    $jarFile = "builds/$($plugin.internalName).jar"
    
    if (Test-Path $cs3File) {
        $actualSize = (Get-Item $cs3File).Length
        $expectedSize = $plugin.fileSize
        
        if ($actualSize -eq $expectedSize) {
            Write-Host "  ✅ $($plugin.internalName).cs3 - Tamanho correto ($actualSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $($plugin.internalName).cs3 - Tamanho diferente: atual=$actualSize, esperado=$expectedSize" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "=== Resultado da Verificacao ===" -ForegroundColor Green
Write-Host "Se todos os arquivos foram extraidos com sucesso, eles estao integros" -ForegroundColor Green
Write-Host "e o Cloudstream conseguira le-los corretamente." -ForegroundColor Green