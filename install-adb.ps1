#!/usr/bin/env pwsh
# Script para instalar ADB no Windows

Write-Host "📱 Instalando ADB (Android Debug Bridge)..." -ForegroundColor Green

# Criar pasta para ADB
$adbPath = "C:\adb"
if (!(Test-Path $adbPath)) {
    New-Item -ItemType Directory -Path $adbPath -Force
    Write-Host "✅ Pasta criada: $adbPath" -ForegroundColor Green
}

# Download ADB
$adbUrl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
$zipPath = "$adbPath\platform-tools.zip"

Write-Host "⬇️ Baixando ADB..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $adbUrl -OutFile $zipPath
    Write-Host "✅ Download concluído" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro no download: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Extrair ZIP
Write-Host "📦 Extraindo arquivos..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipPath -DestinationPath $adbPath -Force
    Write-Host "✅ Arquivos extraídos" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro na extração: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Adicionar ao PATH
$platformToolsPath = "$adbPath\platform-tools"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

if ($currentPath -notlike "*$platformToolsPath*") {
    Write-Host "🔧 Adicionando ADB ao PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$platformToolsPath", "User")
    Write-Host "✅ ADB adicionado ao PATH" -ForegroundColor Green
    Write-Host "⚠️ Reinicie o PowerShell para usar 'adb' diretamente" -ForegroundColor Yellow
}

# Testar ADB
Write-Host "🧪 Testando ADB..." -ForegroundColor Yellow
try {
    & "$platformToolsPath\adb.exe" version
    Write-Host "✅ ADB instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao testar ADB" -ForegroundColor Red
}

# Limpar arquivo ZIP
Remove-Item $zipPath -Force

Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Conecte o celular via USB" -ForegroundColor White
Write-Host "2. Ative 'Depuração USB' no celular" -ForegroundColor White
Write-Host "3. Execute: adb devices" -ForegroundColor White
Write-Host "4. Execute: adb logcat | findstr MaxSeries" -ForegroundColor White

Write-Host "`n🎯 COMANDOS ÚTEIS:" -ForegroundColor Cyan
Write-Host "adb devices                    # Listar dispositivos" -ForegroundColor White
Write-Host "adb logcat | findstr MaxSeries # Ver logs do MaxSeries" -ForegroundColor White
Write-Host "adb logcat -c                  # Limpar logs" -ForegroundColor White