# Script simples para verificar sintaxe
Write-Host "Verificando sintaxe Kotlin..."

$files = @(
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\MaxSeriesProvider.kt",
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors\PlayerEmbedAPIExtractor.kt",
    "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors\MegaEmbedExtractor.kt"
)

$errors = 0

foreach ($file in $files) {
    Write-Host "Verificando: $file"
    
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Verificar problemas basicos
        if ($content -match "source\s*=\s*name") {
            Write-Host "ERRO: Sintaxe deprecated newExtractorLink em $file"
            $errors++
        }
        
        if ($content -match "JsUnpacker" -and $content -notmatch "import.*JsUnpacker") {
            Write-Host "ERRO: Import JsUnpacker faltando em $file"
            $errors++
        }
        
        Write-Host "OK: $file"
    } else {
        Write-Host "ERRO: Arquivo nao encontrado $file"
        $errors++
    }
}

if ($errors -eq 0) {
    Write-Host "SUCESSO: Sintaxe OK"
} else {
    Write-Host "ERRO: $errors problemas encontrados"
}

exit $errors