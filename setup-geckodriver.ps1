# Setup automático do GeckoDriver para análise do MaxSeries
Write-Host "🦎 Configurando GeckoDriver para análise automática..." -ForegroundColor Green

# 1. Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Instalando..." -ForegroundColor Red
    # Baixar e instalar Python se necessário
    winget install Python.Python.3.11
}

# 2. Instalar dependências Python
Write-Host "📦 Instalando dependências Python..." -ForegroundColor Yellow
pip install selenium beautifulsoup4 requests lxml

# 3. Baixar GeckoDriver
Write-Host "⬇️ Baixando GeckoDriver..." -ForegroundColor Yellow
$geckoUrl = "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.34.0-win64.zip"
$geckoZip = "geckodriver.zip"

Invoke-WebRequest -Uri $geckoUrl -OutFile $geckoZip
Expand-Archive -Path $geckoZip -DestinationPath "." -Force
Remove-Item $geckoZip

Write-Host "✅ GeckoDriver instalado!" -ForegroundColor Green

# 4. Verificar Firefox
try {
    $firefoxPath = Get-Command firefox -ErrorAction Stop
    Write-Host "✅ Firefox encontrado: $($firefoxPath.Source)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Firefox não encontrado no PATH" -ForegroundColor Yellow
    Write-Host "📥 Baixe Firefox em: https://www.mozilla.org/firefox/" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 Setup concluído!" -ForegroundColor Green
Write-Host "📋 Próximo passo: Execute .\analyze-maxseries.py" -ForegroundColor Cyan