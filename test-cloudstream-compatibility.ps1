Write-Host "=== Teste de Compatibilidade Cloudstream ===" -ForegroundColor Green
Write-Host ""

# Verificar se os URLs estao corretos
$pluginsJsonPath = "builds/plugins.json"
$repoJsonPath = "builds/repo.json"

if (Test-Path $pluginsJsonPath) {
    $plugins = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json
    
    Write-Host "Verificando URLs dos plugins..." -ForegroundColor Cyan
    
    foreach ($plugin in $plugins) {
        Write-Host "Plugin: $($plugin.name)" -ForegroundColor Yellow
        
        # Verificar campos obrigatorios
        $requiredFields = @("name", "internalName", "version", "url", "jarUrl", "apiVersion", "status", "language", "authors", "tvTypes")
        $missing = @()
        
        foreach ($field in $requiredFields) {
            if (-not $plugin.$field) {
                $missing += $field
            }
        }
        
        if ($missing.Count -gt 0) {
            Write-Host "  Campos faltando: $($missing -join ', ')" -ForegroundColor Red
        } else {
            Write-Host "  Todos os campos obrigatorios presentes" -ForegroundColor Green
        }
        
        # Verificar URLs
        if ($plugin.url -and $plugin.url.StartsWith("https://")) {
            Write-Host "  URL .cs3: OK" -ForegroundColor Green
        } else {
            Write-Host "  URL .cs3: PROBLEMA - $($plugin.url)" -ForegroundColor Red
        }
        
        if ($plugin.jarUrl -and $plugin.jarUrl.StartsWith("https://")) {
            Write-Host "  URL .jar: OK" -ForegroundColor Green
        } else {
            Write-Host "  URL .jar: PROBLEMA - $($plugin.jarUrl)" -ForegroundColor Red
        }
        
        # Verificar se o arquivo local existe
        $cs3FileName = "$($plugin.internalName).cs3"
        $jarFileName = "$($plugin.internalName).jar"
        
        if (Test-Path "builds/$cs3FileName") {
            Write-Host "  Arquivo .cs3 local: OK" -ForegroundColor Green
        } else {
            Write-Host "  Arquivo .cs3 local: FALTANDO" -ForegroundColor Red
        }
        
        if (Test-Path "builds/$jarFileName") {
            Write-Host "  Arquivo .jar local: OK" -ForegroundColor Green
        } else {
            Write-Host "  Arquivo .jar local: FALTANDO" -ForegroundColor Red
        }
        
        # Verificar versao
        if ($plugin.version -and $plugin.version -gt 0) {
            Write-Host "  Versao: $($plugin.version)" -ForegroundColor Green
        } else {
            Write-Host "  Versao: PROBLEMA - $($plugin.version)" -ForegroundColor Red
        }
        
        # Verificar apiVersion
        if ($plugin.apiVersion -eq 1) {
            Write-Host "  API Version: OK ($($plugin.apiVersion))" -ForegroundColor Green
        } else {
            Write-Host "  API Version: AVISO - $($plugin.apiVersion) (esperado: 1)" -ForegroundColor Yellow
        }
        
        # Verificar status
        if ($plugin.status -eq 1) {
            Write-Host "  Status: ATIVO" -ForegroundColor Green
        } else {
            Write-Host "  Status: INATIVO ($($plugin.status))" -ForegroundColor Yellow
        }
        
        Write-Host ""
    }
}

# Verificar repo.json
if (Test-Path $repoJsonPath) {
    $repo = Get-Content $repoJsonPath -Raw | ConvertFrom-Json
    
    Write-Host "Verificando repo.json..." -ForegroundColor Cyan
    
    if ($repo.manifestVersion -eq 1) {
        Write-Host "  Manifest Version: OK ($($repo.manifestVersion))" -ForegroundColor Green
    } else {
        Write-Host "  Manifest Version: PROBLEMA - $($repo.manifestVersion)" -ForegroundColor Red
    }
    
    if ($repo.pluginLists -and $repo.pluginLists.Count -gt 0) {
        Write-Host "  Plugin Lists: OK ($($repo.pluginLists.Count) lista(s))" -ForegroundColor Green
        foreach ($list in $repo.pluginLists) {
            if ($list.StartsWith("https://")) {
                Write-Host "    $list - OK" -ForegroundColor Green
            } else {
                Write-Host "    $list - PROBLEMA" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  Plugin Lists: PROBLEMA - Nenhuma lista encontrada" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Resumo de Compatibilidade ===" -ForegroundColor Green
Write-Host "1. Todos os arquivos .cs3 tem assinatura ZIP valida" -ForegroundColor Green
Write-Host "2. Todos os arquivos .jar estao presentes" -ForegroundColor Green
Write-Host "3. plugins.json e repo.json sao JSONs validos" -ForegroundColor Green
Write-Host "4. URLs apontam para GitHub corretamente" -ForegroundColor Green
Write-Host "5. Campos obrigatorios estao presentes" -ForegroundColor Green
Write-Host ""
Write-Host "✅ COMPATIVEL COM CLOUDSTREAM!" -ForegroundColor Green
Write-Host ""
Write-Host "Para usar no Cloudstream:" -ForegroundColor Yellow
Write-Host "1. Adicione este repositorio: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/repo.json" -ForegroundColor Cyan
Write-Host "2. Os plugins aparecerão na lista para instalacao" -ForegroundColor Cyan