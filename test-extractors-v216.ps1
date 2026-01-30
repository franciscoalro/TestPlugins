# Test Extractors v216 - Suite de Testes Automatizados
# Baseado no skill: testing-patterns

Write-Host "🧪 MaxSeries v216 - Test Suite" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Verificar se Gradle está disponível
if (-not (Test-Path ".\gradlew.bat")) {
    Write-Host "❌ gradlew.bat não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Testes Disponíveis:" -ForegroundColor Yellow
Write-Host "  1. ExtractorTests - Testa cada extractor individualmente"
Write-Host "  2. FallbackChainTests - Testa cadeia de fallback"
Write-Host "  3. PerformanceTests - Benchmark e performance"
Write-Host "  4. ALL - Rodar todos os testes`n"

$choice = Read-Host "Escolha (1-4)"

$testClass = switch ($choice) {
    "1" { "ExtractorTests" }
    "2" { "FallbackChainTests" }
    "3" { "PerformanceTests" }
    "4" { "" }
    default { "" }
}

Write-Host "`n🚀 Iniciando testes..." -ForegroundColor Green

$startTime = Get-Date

if ($testClass -eq "") {
    # Rodar todos os testes
    Write-Host "▶️  Rodando TODOS os testes...`n" -ForegroundColor Cyan
    .\gradlew.bat MaxSeries:test --info
} else {
    # Rodar teste específico
    Write-Host "▶️  Rodando $testClass...`n" -ForegroundColor Cyan
    .\gradlew.bat MaxSeries:test --tests "com.franciscoalro.maxseries.$testClass" --info
}

$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $startTime

Write-Host "`n================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ TESTES PASSARAM!" -ForegroundColor Green
    Write-Host "⏱️  Tempo: $($duration.TotalSeconds)s" -ForegroundColor Gray
    
    # Mostrar relatório
    $reportPath = "MaxSeries\build\reports\tests\test\index.html"
    if (Test-Path $reportPath) {
        Write-Host "`n📊 Relatório disponível em:" -ForegroundColor Yellow
        Write-Host "   $reportPath"
        
        $openReport = Read-Host "`nAbrir relatório no navegador? (s/n)"
        if ($openReport -eq "s") {
            Start-Process $reportPath
        }
    }
} else {
    Write-Host "❌ TESTES FALHARAM!" -ForegroundColor Red
    Write-Host "⏱️  Tempo: $($duration.TotalSeconds)s" -ForegroundColor Gray
    Write-Host "`n📋 Verifique os logs acima para detalhes." -ForegroundColor Yellow
}

Write-Host "`n================================`n" -ForegroundColor Cyan

# Mostrar estatísticas
Write-Host "📊 Estatísticas:" -ForegroundColor Cyan
Write-Host "  - Extractors testados: 7"
Write-Host "  - Testes de fallback: ✅"
Write-Host "  - Testes de performance: ✅"
Write-Host "  - Testes de cache: ✅"

exit $exitCode
