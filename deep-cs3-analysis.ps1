Write-Host "=== Analise Profunda dos Arquivos .cs3 ===" -ForegroundColor Green
Write-Host ""

# Analisar estrutura interna dos arquivos .cs3
$cs3Files = Get-ChildItem "netlify-simple" -Filter "*.cs3" | Select-Object -First 3

foreach ($file in $cs3Files) {
    Write-Host "Analisando: $($file.Name)" -ForegroundColor Cyan
    
    $tempDir = "temp_analysis_$($file.BaseName)"
    
    try {
        # Extrair arquivo
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($file.FullName, $tempDir)
        
        Write-Host "  ✅ Extraido com sucesso" -ForegroundColor Green
        
        # Verificar arquivos obrigatorios
        $requiredFiles = @("AndroidManifest.xml", "classes.jar")
        
        foreach ($reqFile in $requiredFiles) {
            $filePath = Join-Path $tempDir $reqFile
            if (Test-Path $filePath) {
                $size = (Get-Item $filePath).Length
                Write-Host "  ✅ $reqFile presente ($size bytes)" -ForegroundColor Green
                
                # Verificar conteudo do AndroidManifest.xml
                if ($reqFile -eq "AndroidManifest.xml") {
                    $manifest = Get-Content $filePath -Raw
                    if ($manifest -match 'package="([^"]+)"') {
                        Write-Host "    Package: $($matches[1])" -ForegroundColor Yellow
                    }
                    if ($manifest -match 'minSdkVersion="([^"]+)"') {
                        Write-Host "    MinSDK: $($matches[1])" -ForegroundColor Yellow
                    }
                }
                
                # Verificar se classes.jar e valido
                if ($reqFile -eq "classes.jar") {
                    try {
                        $jar = [System.IO.Compression.ZipFile]::OpenRead($filePath)
                        Write-Host "    ✅ JAR valido com $($jar.Entries.Count) entradas" -ForegroundColor Green
                        $jar.Dispose()
                    } catch {
                        Write-Host "    ❌ JAR invalido: $_" -ForegroundColor Red
                    }
                }
                
            } else {
                Write-Host "  ❌ $reqFile AUSENTE!" -ForegroundColor Red
            }
        }
        
        # Verificar estrutura META-INF
        $metaInfPath = Join-Path $tempDir "META-INF"
        if (Test-Path $metaInfPath) {
            Write-Host "  ✅ META-INF presente" -ForegroundColor Green
            $metaFiles = Get-ChildItem $metaInfPath -Recurse
            Write-Host "    Arquivos META-INF: $($metaFiles.Count)" -ForegroundColor Yellow
        } else {
            Write-Host "  ⚠️  META-INF ausente" -ForegroundColor Yellow
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

# Verificar se os arquivos seguem o padrao esperado pelo Cloudstream
Write-Host "Padroes esperados pelo Cloudstream:" -ForegroundColor Cyan
Write-Host "✅ Arquivo .cs3 deve ser um ZIP valido" -ForegroundColor Green
Write-Host "✅ Deve conter AndroidManifest.xml" -ForegroundColor Green
Write-Host "✅ Deve conter classes.jar" -ForegroundColor Green
Write-Host "✅ AndroidManifest.xml deve ter package definido" -ForegroundColor Green
Write-Host "✅ classes.jar deve ser um JAR valido" -ForegroundColor Green
Write-Host "✅ Tamanho do arquivo deve corresponder ao plugins.json" -ForegroundColor Green

Write-Host ""
Write-Host "=== POSSIVEL PROBLEMA ADICIONAL ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Se os arquivos estao corretos mas ainda nao baixam:" -ForegroundColor Cyan
Write-Host "1. VERSAO DO CLOUDSTREAM:" -ForegroundColor Yellow
Write-Host "   - Use Cloudstream 3.5.0 ou superior" -ForegroundColor White
Write-Host "   - Versoes antigas tem bugs de download" -ForegroundColor White
Write-Host ""
Write-Host "2. PERMISSOES DO ANDROID:" -ForegroundColor Yellow
Write-Host "   - Configuracoes > Apps > Cloudstream > Permissoes" -ForegroundColor White
Write-Host "   - Certifique-se que 'Armazenamento' esta permitido" -ForegroundColor White
Write-Host ""
Write-Host "3. ESPACO DE ARMAZENAMENTO:" -ForegroundColor Yellow
Write-Host "   - Verifique se ha espaco suficiente no dispositivo" -ForegroundColor White
Write-Host ""
Write-Host "4. CONEXAO DE REDE:" -ForegroundColor Yellow
Write-Host "   - Teste com WiFi e dados moveis" -ForegroundColor White
Write-Host "   - Alguns provedores podem bloquear .netlify.app" -ForegroundColor White
Write-Host ""
Write-Host "5. CACHE CORROMPIDO:" -ForegroundColor Yellow
Write-Host "   - Limpe o cache do Cloudstream" -ForegroundColor White
Write-Host "   - Reinicie o aplicativo" -ForegroundColor White
Write-Host "   - Se necessario, reinstale o Cloudstream" -ForegroundColor White