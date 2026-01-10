# Script para verificar sintaxe Kotlin sem build completo
Write-Host "🔍 VERIFICANDO SINTAXE KOTLIN" -ForegroundColor Green
Write-Host "=" * 50

# Verificar arquivos Kotlin principais
$kotlinFiles = @(
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\MaxSeriesProvider.kt",
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors\PlayerEmbedAPIExtractor.kt",
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors\MegaEmbedExtractor.kt"
)

$errors = 0

foreach ($file in $kotlinFiles) {
    Write-Host "`n📄 Verificando: $file" -ForegroundColor Yellow
    
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Verificar problemas comuns
        $issues = @()
        
        # 1. Verificar imports duplicados ou conflitantes
        if ($content -match "import.*getPacked" -and $content -match "private fun getPacked") {
            $issues += "❌ Conflito: import getPacked + definição local"
        }
        
        # 2. Verificar sintaxe newExtractorLink
        if ($content -match "newExtractorLink\s*\(\s*source\s*=") {
            $issues += "❌ Sintaxe deprecated: newExtractorLink com source="
        }
        
        # 3. Verificar sintaxe M3u8Helper
        if ($content -match "M3u8Helper\.generateM3u8\([^)]*headers\s*=") {
            $issues += "❌ Sintaxe incorreta: M3u8Helper com headers="
        }
        
        # 4. Verificar imports necessários
        if ($content -match "JsUnpacker" -and $content -notmatch "import.*JsUnpacker") {
            $issues += "❌ Import faltando: JsUnpacker"
        }
        
        # 5. Verificar chaves balanceadas
        $openBraces = ($content -split '\{').Count - 1
        $closeBraces = ($content -split '\}').Count - 1
        if ($openBraces -ne $closeBraces) {
            $issues += "❌ Chaves desbalanceadas: { $openBraces vs } $closeBraces"
        }
        
        # 6. Verificar parênteses balanceados
        $openParens = ($content -split '\(').Count - 1
        $closeParens = ($content -split '\)').Count - 1
        if ($openParens -ne $closeParens) {
            $issues += "❌ Parênteses desbalanceados: ( $openParens vs ) $closeParens"
        }
        
        if ($issues.Count -eq 0) {
            Write-Host "   ✅ Sintaxe OK" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Problemas encontrados:" -ForegroundColor Red
            foreach ($issue in $issues) {
                Write-Host "      $issue" -ForegroundColor Red
            }
            $errors += $issues.Count
        }
    } else {
        Write-Host "   ❌ Arquivo não encontrado" -ForegroundColor Red
        $errors++
    }
}

Write-Host "`n" + "=" * 50
if ($errors -eq 0) {
    Write-Host "🏆 SINTAXE OK - Todos os arquivos verificados" -ForegroundColor Green
    Write-Host "✅ Pronto para build" -ForegroundColor Green
} else {
    Write-Host "❌ ERROS ENCONTRADOS: $errors" -ForegroundColor Red
    Write-Host "💡 Corrija os problemas antes do build" -ForegroundColor Yellow
}

exit $errors