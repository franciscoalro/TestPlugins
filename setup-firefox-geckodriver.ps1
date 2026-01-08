#!/usr/bin/env pwsh
# Script para instalar Firefox e configurar GeckoDriver

Write-Host "🦎 CONFIGURAÇÃO FIREFOX + GECKODRIVER" -ForegroundColor Green
Write-Host "=" * 50

# Verificar se GeckoDriver existe
$geckoPath = "D:\geckodriver.exe"
if (Test-Path $geckoPath) {
    Write-Host "✅ GeckoDriver encontrado: $geckoPath" -ForegroundColor Green
} else {
    Write-Host "❌ GeckoDriver não encontrado em $geckoPath" -ForegroundColor Red
    Write-Host "📥 Baixe em: https://github.com/mozilla/geckodriver/releases" -ForegroundColor Yellow
    exit 1
}

# Verificar se Firefox está instalado
$firefoxPaths = @(
    "${env:ProgramFiles}\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe",
    "${env:LOCALAPPDATA}\Mozilla Firefox\firefox.exe"
)

$firefoxFound = $false
$firefoxPath = ""

foreach ($path in $firefoxPaths) {
    if (Test-Path $path) {
        $firefoxFound = $true
        $firefoxPath = $path
        Write-Host "✅ Firefox encontrado: $path" -ForegroundColor Green
        break
    }
}

if (-not $firefoxFound) {
    Write-Host "❌ Firefox não encontrado" -ForegroundColor Red
    Write-Host "📥 Instalando Firefox..." -ForegroundColor Yellow
    
    try {
        # Baixar Firefox
        $firefoxUrl = "https://download.mozilla.org/?product=firefox-latest&os=win64&lang=pt-BR"
        $firefoxInstaller = "$env:TEMP\firefox-installer.exe"
        
        Write-Host "📥 Baixando Firefox..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $firefoxUrl -OutFile $firefoxInstaller -UseBasicParsing
        
        Write-Host "🔧 Instalando Firefox..." -ForegroundColor Yellow
        Start-Process -FilePath $firefoxInstaller -ArgumentList "/S" -Wait
        
        Write-Host "✅ Firefox instalado!" -ForegroundColor Green
        
        # Verificar novamente
        foreach ($path in $firefoxPaths) {
            if (Test-Path $path) {
                $firefoxPath = $path
                $firefoxFound = $true
                break
            }
        }
        
    } catch {
        Write-Host "❌ Erro ao instalar Firefox: $_" -ForegroundColor Red
        Write-Host "📥 Instale manualmente: https://www.mozilla.org/firefox/" -ForegroundColor Yellow
        exit 1
    }
}

if ($firefoxFound) {
    Write-Host "🔧 Configurando variáveis de ambiente..." -ForegroundColor Yellow
    
    # Adicionar Firefox ao PATH se necessário
    $firefoxDir = Split-Path $firefoxPath
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($currentPath -notlike "*$firefoxDir*") {
        Write-Host "📝 Adicionando Firefox ao PATH..." -ForegroundColor Yellow
        $newPath = "$currentPath;$firefoxDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    }
    
    # Configurar FIREFOX_BINARY
    [Environment]::SetEnvironmentVariable("FIREFOX_BINARY", $firefoxPath, "User")
    
    Write-Host "✅ Configuração concluída!" -ForegroundColor Green
    Write-Host "🔄 Reinicie o terminal para aplicar as mudanças" -ForegroundColor Yellow
    
    # Testar configuração
    Write-Host "🧪 Testando configuração..." -ForegroundColor Yellow
    
    try {
        $version = & $firefoxPath --version
        Write-Host "✅ Firefox: $version" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Erro ao testar Firefox: $_" -ForegroundColor Yellow
    }
    
    try {
        $geckoVersion = & $geckoPath --version
        Write-Host "✅ GeckoDriver: $geckoVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Erro ao testar GeckoDriver: $_" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Falha na instalação do Firefox" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Reinicie o terminal" -ForegroundColor White
Write-Host "2. Execute: python gecko-advanced-scraper.py" -ForegroundColor White
Write-Host "3. Ou execute: python gecko-simulation-scraper.py (sem Firefox)" -ForegroundColor White