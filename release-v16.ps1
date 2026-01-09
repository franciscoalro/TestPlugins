#!/usr/bin/env pwsh
# Release MaxSeries v16.0 - Extractors Corrigidos

Write-Host "🚀 MAXSERIES V16.0 - EXTRACTORS CORRIGIDOS" -ForegroundColor Green

# Atualizar versão no build.gradle.kts
$buildGradleContent = Get-Content "build.gradle.kts" -Raw
$buildGradleContent = $buildGradleContent -replace 'version = \d+', 'version = 16'
Set-Content "build.gradle.kts" -Value $buildGradleContent
Write-Host "✅ Versão atualizada para 16" -ForegroundColor Green

# Atualizar plugins.json
$pluginsContent = @'
[
    {
        "url": "https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/AnimesOnlineCC.cs3",
        "status": 1,
        "version": 6,
        "apiVersion": 1,
        "name": "AnimesOnlineCC",
        "internalName": "AnimesOnlineCC",
        "authors": ["franciscoalro"],
        "description": "Assista animes online gratis em HD no AnimesOnlineCC. Grande catalogo de animes legendados e dublados.",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["Anime", "OVA", "AnimeMovie"],
        "language": "pt-BR",
        "iconUrl": "https://animesonlinecc.to/wp-content/uploads/2020/01/cropped-favicon-32x32.png",
        "isAdult": false
    },
    {
        "url": "https://github.com/franciscoalro/TestPlugins/releases/download/v16.0/MaxSeries.cs3",
        "status": 1,
        "version": 16,
        "apiVersion": 1,
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "authors": ["franciscoalro"],
        "description": "MaxSeries v16.0 - EXTRACTORS CORRIGIDOS! Implementados extractors customizados para PlayerEmbedAPI e MegaEmbed que realmente funcionam.",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "iconUrl": "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png",
        "isAdult": false
    }
]
'@

Set-Content "plugins.json" -Value $pluginsContent -Encoding UTF8
Write-Host "✅ plugins.json atualizado" -ForegroundColor Green

# Commit e push
Write-Host "📤 Fazendo commit e push..." -ForegroundColor Yellow

git add .
git commit -m "feat: MaxSeries v16.0 - Extractors corrigidos

- Implementados extractors customizados para PlayerEmbedAPI e MegaEmbed
- Solução para players JavaScript complexos que não funcionavam
- Suporte a decodificação Base64 e assets modernos
- Múltiplos fallbacks para máxima compatibilidade

Fixes: Vídeos não reproduziam no CloudStream"

git tag -a "v16.0" -m "MaxSeries v16.0 - Extractors Corrigidos"
git push origin main
git push origin v16.0

Write-Host "✅ Release v16.0 criado!" -ForegroundColor Green
Write-Host "🔗 Acesse: https://github.com/franciscoalro/TestPlugins/releases/tag/v16.0" -ForegroundColor Cyan