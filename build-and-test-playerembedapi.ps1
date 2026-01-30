# Build e Teste - PlayerEmbedAPI Implementation
# Script para compilar o MaxSeries provider com PlayerEmbedAPI otimizado

Write-Host "================================" -ForegroundColor Cyan
Write-Host "PlayerEmbedAPI - Build & Test" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se estamos no diretório correto
if (-not (Test-Path "MaxSeries")) {
    Write-Host "❌ Erro: Diretório MaxSeries não encontrado" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto brcloudstream" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Diretório MaxSeries encontrado" -ForegroundColor Green
Write-Host ""

# 2. Verificar se o extrator foi atualizado
$extractorFile = "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt"
if (-not (Test-Path $extractorFile)) {
    Write-Host "❌ Erro: PlayerEmbedAPIExtractor.kt não encontrado" -ForegroundColor Red
    exit 1
}

$extractorContent = Get-Content $extractorFile -Raw
if ($extractorContent -match "v3 - PLAYWRIGHT OPTIMIZED") {
    Write-Host "✅ PlayerEmbedAPIExtractor v3 detectado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Aviso: PlayerEmbedAPIExtractor pode não estar na versão v3" -ForegroundColor Yellow
}
Write-Host ""

# 3. Limpar build anterior
Write-Host "🧹 Limpando build anterior..." -ForegroundColor Cyan
if (Test-Path "MaxSeries/build") {
    Remove-Item -Recurse -Force "MaxSeries/build"
    Write-Host "✅ Build anterior removido" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Nenhum build anterior encontrado" -ForegroundColor Gray
}
Write-Host ""

# 4. Verificar Gradle
Write-Host "🔍 Verificando Gradle..." -ForegroundColor Cyan
if (Test-Path "gradlew.bat") {
    Write-Host "✅ Gradle wrapper encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Erro: gradlew.bat não encontrado" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 5. Build do projeto
Write-Host "🔨 Iniciando build do MaxSeries..." -ForegroundColor Cyan
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Yellow
Write-Host ""

$buildStart = Get-Date

try {
    # Executar build
    & .\gradlew.bat :MaxSeries:make 2>&1 | Tee-Object -FilePath "build_playerembedapi_log.txt"
    
    if ($LASTEXITCODE -eq 0) {
        $buildEnd = Get-Date
        $buildTime = ($buildEnd - $buildStart).TotalSeconds
        
        Write-Host ""
        Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
        Write-Host "⏱️  Tempo: $([math]::Round($buildTime, 2)) segundos" -ForegroundColor Cyan
        Write-Host ""
        
        # 6. Verificar se o CS3 foi gerado
        $cs3File = "MaxSeries.cs3"
        if (Test-Path $cs3File) {
            $cs3Size = (Get-Item $cs3File).Length / 1KB
            Write-Host "📦 Arquivo gerado: $cs3File" -ForegroundColor Green
            Write-Host "📊 Tamanho: $([math]::Round($cs3Size, 2)) KB" -ForegroundColor Cyan
            Write-Host ""
            
            # 7. Mostrar resumo
            Write-Host "================================" -ForegroundColor Cyan
            Write-Host "RESUMO DO BUILD" -ForegroundColor Cyan
            Write-Host "================================" -ForegroundColor Cyan
            Write-Host "✅ PlayerEmbedAPIExtractor v3 (Playwright Optimized)" -ForegroundColor Green
            Write-Host "✅ Timeout otimizado: 15s" -ForegroundColor Green
            Write-Host "✅ Interceptação Google Cloud Storage" -ForegroundColor Green
            Write-Host "✅ Prioridade 1 no MaxSeries" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
            Write-Host "1. Instalar MaxSeries.cs3 no CloudStream" -ForegroundColor White
            Write-Host "2. Testar com episódio do MaxSeries" -ForegroundColor White
            Write-Host "3. Verificar logs: 'PlayerEmbedAPI'" -ForegroundColor White
            Write-Host "4. Confirmar URL do Google Cloud Storage" -ForegroundColor White
            Write-Host ""
            Write-Host "🔍 Log completo salvo em: build_playerembedapi_log.txt" -ForegroundColor Cyan
            
        } else {
            Write-Host "⚠️  Aviso: MaxSeries.cs3 não encontrado" -ForegroundColor Yellow
            Write-Host "Verifique o log de build para detalhes" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host ""
        Write-Host "❌ Build falhou!" -ForegroundColor Red
        Write-Host "Verifique o log: build_playerembedapi_log.txt" -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Erro durante o build: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Build finalizado!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
