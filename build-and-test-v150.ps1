# Build e teste v150 - MegaEmbed V7 melhorado
param(
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== BUILD E TESTE v150 ===" -ForegroundColor Cyan
Write-Host ""

# Build
if (-not $SkipBuild) {
    Write-Host "📦 Compilando..." -ForegroundColor Yellow
    .\gradlew.bat MaxSeries:make
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro na compilação" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Compilação concluída" -ForegroundColor Green
    Write-Host ""
}

# Verificar se APK existe
$apkPath = "MaxSeries\build\MaxSeries.cs3"
if (-not (Test-Path $apkPath)) {
    Write-Host "❌ APK não encontrado: $apkPath" -ForegroundColor Red
    exit 1
}

# Instalar no dispositivo
Write-Host "📱 Instalando no dispositivo..." -ForegroundColor Yellow
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe push $apkPath /storage/emulated/0/Cloudstream3/plugins/

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Instalado com sucesso" -ForegroundColor Green
Write-Host ""

# Limpar logs
Write-Host "🧹 Limpando logs antigos..." -ForegroundColor Yellow
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -c
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "=== INSTRUÇÕES ===" -ForegroundColor Cyan
Write-Host "1. Abra o CloudStream no dispositivo" -ForegroundColor White
Write-Host "2. Vá em Settings > Extensions" -ForegroundColor White
Write-Host "3. Desative e reative o MaxSeries" -ForegroundColor White
Write-Host "4. Tente reproduzir um vídeo" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER para iniciar monitoramento de logs..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "=== MONITORANDO LOGS ===" -ForegroundColor Cyan
Write-Host "Procurando por:" -ForegroundColor Yellow
Write-Host "  - Padrões encontrados no HTML" -ForegroundColor White
Write-Host "  - Dados extraídos (host/cluster/videoId)" -ForegroundColor White
Write-Host "  - URLs testadas" -ForegroundColor White
Write-Host "  - Sucessos e falhas" -ForegroundColor White
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "adb_logs_v150_$timestamp.txt"

C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat | Select-String -Pattern "MegaEmbedV7|encontrado|extraídos|Testando|SUCESSO|válida|ExtractorLink" | Tee-Object -FilePath $logFile
