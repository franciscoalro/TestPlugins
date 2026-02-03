Write-Host "=== Corrigindo Codificacao do JSON ===" -ForegroundColor Green
Write-Host ""

$pluginsJsonPath = "builds/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

# Corrigir caracteres especiais nas descricoes
foreach ($plugin in $plugins) {
    switch ($plugin.internalName) {
        "MaxSeries" {
            $plugin.description = "MaxSeries - Filmes e series com multiplos extractores"
        }
        "AnimesOnlineCC" {
            $plugin.description = "Animes Online CC - Animes com posters em alta qualidade via API"
        }
        "Doramas" {
            $plugin.description = "Doramas Online - Doramas coreanos, chineses e japoneses"
        }
        "NovelasFlix" {
            $plugin.description = "NovelasFlix - Novelas mexicanas, brasileiras e turcas"
        }
        "DonghuaNoSekai" {
            $plugin.description = "Donghua No Sekai - Animes chineses (Donghuas)"
        }
        "EmbedCanais" {
            $plugin.description = "EmbedCanais TV - TV Ao Vivo - Canais abertos, esportes, noticias"
        }
        "MegaFlix" {
            $plugin.description = "MegaFlix - Filmes e series online"
        }
        "NetCine" {
            $plugin.description = "NetCine - Filmes e series online"
        }
        "OverFlix" {
            $plugin.description = "OverFlix - Filmes e series online"
        }
        "PobreFlix" {
            $plugin.description = "PobreFlix - Filmes e series online"
        }
        "Vizer" {
            $plugin.description = "Vizer - Filmes e series online"
        }
    }
    
    Write-Host "Corrigido: $($plugin.name)" -ForegroundColor Green
}

# Salvar com codificacao UTF8 sem BOM
$jsonContent = $plugins | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($pluginsJsonPath, $jsonContent, [System.Text.UTF8Encoding]::new($false))

# Copiar para a raiz
Copy-Item $pluginsJsonPath "plugins.json" -Force

Write-Host ""
Write-Host "✅ JSON corrigido e salvo com codificacao UTF8!" -ForegroundColor Green