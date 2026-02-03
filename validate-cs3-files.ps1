#!/usr/bin/env pwsh

Write-Host "=== Validação de Arquivos .cs3 ===" -ForegroundColor Green
Write-Host ""

$buildsPath = "builds"
$cs3Files = Get-ChildItem -Path $buildsPath -Filter "*.cs3"

if ($cs3Files.Count -eq 0) {
    Write-Host "❌ Nenhum arquivo .cs3 encontrado em $buildsPath" -ForegroundColor Red
    exit 1
}

$allValid = $true

foreach ($file in $cs3Files) {
    Write-Host "Validando: $($file.Name)" -ForegroundColor Cyan
    
    # Verificar se o arquivo existe e tem tamanho > 0
    if ($file.Length -eq 0) {
        Write-Host "  ❌ Arquivo vazio" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    # Verificar assinatura ZIP (PK)
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $header = [System.Text.Encoding]::ASCII.GetString($bytes[0..1])
        
        if ($header -eq "PK") {
            Write-Host "  ✅ Assinatura ZIP válida" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Assinatura ZIP invalida: $header" -ForegroundColor Red
            $allValid = $false
            continue
        }
    } catch {
        Write-Host "  ❌ Erro ao ler arquivo: $_" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    # Verificar se consegue abrir como ZIP
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($file.FullName)
        $entryCount = $zip.Entries.Count
        $zip.Dispose()
        
        Write-Host "  ✅ Arquivo ZIP valido com $entryCount entradas" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao abrir como ZIP: $_" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    # Verificar tamanho
    $sizeKB = [math]::Round($file.Length / 1024, 2)
    Write-Host "  📊 Tamanho: $sizeKB KB" -ForegroundColor Yellow
    
    # Verificar data de modificação
    Write-Host "  📅 Modificado: $($file.LastWriteTime)" -ForegroundColor Yellow
    
    Write-Host ""
}

# Verificar plugins.json
Write-Host "Validando plugins.json..." -ForegroundColor Cyan
$pluginsJsonPath = Join-Path $buildsPath "plugins.json"

if (Test-Path $pluginsJsonPath) {
    try {
        $pluginsContent = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json
        Write-Host "  ✅ plugins.json e um JSON valido" -ForegroundColor Green
        Write-Host "  📊 Contem $($pluginsContent.Count) plugins" -ForegroundColor Yellow
        
        # Verificar se todos os plugins tem os campos obrigatorios
        foreach ($plugin in $pluginsContent) {
            $requiredFields = @("name", "internalName", "version", "url", "jarUrl", "apiVersion")
            $missingFields = @()
            
            foreach ($field in $requiredFields) {
                if (-not $plugin.$field) {
                    $missingFields += $field
                }
            }
            
            if ($missingFields.Count -gt 0) {
                Write-Host "  ❌ Plugin '$($plugin.name)' esta faltando campos: $($missingFields -join ', ')" -ForegroundColor Red
                $allValid = $false
            } else {
                Write-Host "  ✅ Plugin '$($plugin.name)' v$($plugin.version) OK" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  ❌ Erro ao validar plugins.json: $_" -ForegroundColor Red
        $allValid = $false
    }
} else {
    Write-Host "  ❌ plugins.json nao encontrado" -ForegroundColor Red
    $allValid = $false
}

Write-Host ""

# Verificar repo.json
Write-Host "Validando repo.json..." -ForegroundColor Cyan
$repoJsonPath = Join-Path $buildsPath "repo.json"

if (Test-Path $repoJsonPath) {
    try {
        $repoContent = Get-Content $repoJsonPath -Raw | ConvertFrom-Json
        Write-Host "  ✅ repo.json e um JSON valido" -ForegroundColor Green
        
        $requiredFields = @("name", "manifestVersion", "pluginLists")
        $missingFields = @()
        
        foreach ($field in $requiredFields) {
            if (-not $repoContent.$field) {
                $missingFields += $field
            }
        }
        
        if ($missingFields.Count -gt 0) {
            Write-Host "  ❌ repo.json esta faltando campos: $($missingFields -join ', ')" -ForegroundColor Red
            $allValid = $false
        } else {
            Write-Host "  ✅ repo.json tem todos os campos obrigatorios" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ❌ Erro ao validar repo.json: $_" -ForegroundColor Red
        $allValid = $false
    }
} else {
    Write-Host "  ❌ repo.json nao encontrado" -ForegroundColor Red
    $allValid = $false
}

Write-Host ""
Write-Host "=== Resultado Final ===" -ForegroundColor Green

if ($allValid) {
    Write-Host "✅ Todos os arquivos estao validos e prontos para o Cloudstream!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Alguns arquivos tem problemas que precisam ser corrigidos." -ForegroundColor Red
    exit 1
}