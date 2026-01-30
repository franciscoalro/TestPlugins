# Build MaxSeries v223 - PlayerEmbedAPI Redirect Fix
# Autor: Assistente AI
# Data: 28 Jan 2026

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD MAXSERIES v223 - REDIRECT FIX   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está na pasta correta
if (-not (Test-Path "./MaxSeries")) {
    Write-Host "❌ Erro: Execute este script na pasta brcloudstream" -ForegroundColor Red
    exit 1
}

# Limpar build anterior
Write-Host "🧹 Limpando build anterior..." -ForegroundColor Yellow
if (Test-Path "./MaxSeries/build") {
    Remove-Item -Recurse -Force "./MaxSeries/build"
    Write-Host "   ✓ Build anterior removido" -ForegroundColor Green
}

# Build
Write-Host ""
Write-Host "🔨 Iniciando build do MaxSeries v223..." -ForegroundColor Yellow
Write-Host "   Features: PlayerEmbedAPI Redirect Fix" -ForegroundColor Gray
Write-Host ""

try {
    # Usar o wrapper do Gradle
    if (Test-Path "./gradlew.bat") {
        .\gradlew.bat MaxSeries:make --no-daemon --console=plain 2>&1 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ gradlew.bat não encontrado!" -ForegroundColor Red
        exit 1
    }
    
    # Verificar se o build foi bem-sucedido
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ BUILD BEM-SUCEDIDO!" -ForegroundColor Green
        Write-Host ""
        
        # Verificar se o arquivo .cs3 foi gerado
        $cs3File = Get-ChildItem "./MaxSeries/build/*.cs3" -ErrorAction SilentlyContinue | Select-Object -First 1
        
        if ($cs3File) {
            $fileSize = [math]::Round($cs3File.Length / 1KB, 2)
            Write-Host "📦 Arquivo gerado:" -ForegroundColor Cyan
            Write-Host "   Nome: $($cs3File.Name)" -ForegroundColor White
            Write-Host "   Tamanho: $fileSize KB" -ForegroundColor White
            Write-Host "   Caminho: $($cs3File.FullName)" -ForegroundColor White
            Write-Host ""
            Write-Host "🚀 Próximos passos:" -ForegroundColor Yellow
            Write-Host "   1. Instale o arquivo .cs3 no CloudStream" -ForegroundColor White
            Write-Host "   2. Teste o PlayerEmbedAPI com um filme/série" -ForegroundColor White
            Write-Host "   3. Verifique os logs com: adb logcat -s 'MaxSeriesProvider','PlayerEmbedAPI'" -ForegroundColor White
        } else {
            Write-Host "⚠️ Build concluído mas arquivo .cs3 não encontrado" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "❌ BUILD FALHOU! (Código: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERRO DURANTE O BUILD:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
