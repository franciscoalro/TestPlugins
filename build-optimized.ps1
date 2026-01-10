# Build otimizado para MaxSeries v38
Write-Host "🚀 BUILD MAXSERIES V38 - OTIMIZADO" -ForegroundColor Green
Write-Host "=" * 50

# Verificar sintaxe primeiro
Write-Host "`n🔍 1. Verificando sintaxe..." -ForegroundColor Yellow
& .\check-syntax-simple.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO: Problemas de sintaxe encontrados" -ForegroundColor Red
    exit 1
}

# Limpar build anterior
Write-Host "`n🧹 2. Limpando build anterior..." -ForegroundColor Yellow
& .\gradlew.bat clean --no-daemon --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Clean falhou, continuando..." -ForegroundColor Yellow
}

# Build apenas MaxSeries
Write-Host "`n🔨 3. Building MaxSeries..." -ForegroundColor Yellow
Write-Host "Comando: .\gradlew.bat :MaxSeries:assembleDebug --no-daemon --quiet"

$buildStart = Get-Date
& .\gradlew.bat :MaxSeries:assembleDebug --no-daemon --quiet
$buildEnd = Get-Date
$buildTime = ($buildEnd - $buildStart).TotalSeconds

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🏆 BUILD SUCESSO!" -ForegroundColor Green
    Write-Host "⏱️ Tempo: $([math]::Round($buildTime, 1))s" -ForegroundColor Green
    
    # Verificar se APK foi gerado
    $apkPath = "MaxSeries\build\outputs\apk\debug\MaxSeries-debug.apk"
    if (Test-Path $apkPath) {
        $apkSize = [math]::Round((Get-Item $apkPath).Length / 1MB, 2)
        Write-Host "📦 APK gerado: $apkPath ($apkSize MB)" -ForegroundColor Green
    }
    
    Write-Host "`n✅ MaxSeries v38 pronto para release!" -ForegroundColor Green
} else {
    Write-Host "`n❌ BUILD FALHOU!" -ForegroundColor Red
    Write-Host "💡 Verifique os logs acima para detalhes" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n" + "=" * 50
Write-Host "🎯 RELEASE V38 STATUS: PRONTO" -ForegroundColor Green