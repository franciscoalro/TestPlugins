Write-Host "=== Verificacao Simples dos CS3 ===" -ForegroundColor Green
Write-Host ""

# Extrair um arquivo CS3 para verificar estrutura
$testFile = "builds/MaxSeries.cs3"
$tempDir = "temp_cs3_simple"

if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($testFile, $tempDir)
    
    Write-Host "Estrutura do MaxSeries.cs3:" -ForegroundColor Cyan
    Get-ChildItem $tempDir -Recurse | ForEach-Object {
        if ($_.PSIsContainer) {
            Write-Host "  Pasta: $($_.Name)" -ForegroundColor Blue
        } else {
            $sizeKB = [math]::Round($_.Length / 1024, 2)
            Write-Host "  Arquivo: $($_.Name) - $sizeKB KB" -ForegroundColor White
        }
    }
    
    # Verificar AndroidManifest.xml
    $manifestPath = Join-Path $tempDir "AndroidManifest.xml"
    if (Test-Path $manifestPath) {
        Write-Host ""
        Write-Host "AndroidManifest.xml encontrado:" -ForegroundColor Green
        $manifest = Get-Content $manifestPath -Raw
        Write-Host $manifest.Substring(0, [Math]::Min(500, $manifest.Length))
    }
    
    Remove-Item $tempDir -Recurse -Force
    
} catch {
    Write-Host "Erro: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Possivel Problema ===" -ForegroundColor Yellow
Write-Host "O Cloudstream pode estar tendo problemas com:" -ForegroundColor Yellow
Write-Host "1. Codificacao dos arquivos JSON" -ForegroundColor Cyan
Write-Host "2. Estrutura interna dos arquivos .cs3" -ForegroundColor Cyan
Write-Host "3. Permissoes de download no Android" -ForegroundColor Cyan
Write-Host "4. Cache do Cloudstream" -ForegroundColor Cyan