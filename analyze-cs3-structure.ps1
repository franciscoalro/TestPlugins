Write-Host "=== Analisando Estrutura dos Arquivos .cs3 ===" -ForegroundColor Green
Write-Host ""

$cs3Files = Get-ChildItem "builds" -Filter "*.cs3" | Select-Object -First 3

foreach ($file in $cs3Files) {
    Write-Host "Analisando: $($file.Name)" -ForegroundColor Cyan
    
    $tempDir = "temp_analysis_$($file.BaseName)"
    
    try {
        # Extrair o arquivo
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($file.FullName, $tempDir)
        
        # Verificar estrutura
        Write-Host "  Estrutura encontrada:" -ForegroundColor Yellow
        Get-ChildItem $tempDir -Recurse | ForEach-Object {
            $relativePath = $_.FullName.Replace("$PWD\$tempDir\", "")
            if ($_.PSIsContainer) {
                Write-Host "    📁 $relativePath/" -ForegroundColor Blue
            } else {
                $sizeKB = [math]::Round($_.Length / 1024, 2)
                Write-Host "    📄 $relativePath ($sizeKB KB)" -ForegroundColor White
            }
        }
        
        # Verificar AndroidManifest.xml
        $manifestPath = Join-Path $tempDir "AndroidManifest.xml"
        if (Test-Path $manifestPath) {
            Write-Host "  ✅ AndroidManifest.xml presente" -ForegroundColor Green
            
            # Ler conteudo do manifest
            $manifestContent = Get-Content $manifestPath -Raw
            if ($manifestContent -match 'package="([^"]+)"') {
                Write-Host "    Package: $($matches[1])" -ForegroundColor Cyan
            }
        } else {
            Write-Host "  ❌ AndroidManifest.xml ausente" -ForegroundColor Red
        }
        
        # Verificar classes.jar
        $classesJarPath = Join-Path $tempDir "classes.jar"
        if (Test-Path $classesJarPath) {
            $jarSize = (Get-Item $classesJarPath).Length
            Write-Host "  ✅ classes.jar presente ($([math]::Round($jarSize / 1024, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ classes.jar ausente" -ForegroundColor Red
        }
        
        # Limpar
        Remove-Item $tempDir -Recurse -Force
        
    } catch {
        Write-Host "  ❌ Erro ao analisar: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== Verificando Compatibilidade com Cloudstream ===" -ForegroundColor Green
Write-Host ""

# Verificar se os arquivos .jar separados existem e sao diferentes dos classes.jar
$jarFiles = Get-ChildItem "builds" -Filter "*.jar" | Select-Object -First 3

foreach ($jarFile in $jarFiles) {
    Write-Host "Verificando: $($jarFile.Name)" -ForegroundColor Cyan
    
    $cs3Name = $jarFile.Name.Replace(".jar", ".cs3")
    $cs3Path = Join-Path "builds" $cs3Name
    
    if (Test-Path $cs3Path) {
        $jarSize = $jarFile.Length
        $cs3Size = (Get-Item $cs3Path).Length
        
        Write-Host "  JAR: $([math]::Round($jarSize / 1024, 2)) KB" -ForegroundColor Yellow
        Write-Host "  CS3: $([math]::Round($cs3Size / 1024, 2)) KB" -ForegroundColor Yellow
        
        if ($jarSize -ne $cs3Size) {
            Write-Host "  ✅ Arquivos diferentes (correto)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Arquivos identicos (pode ser problema)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
}