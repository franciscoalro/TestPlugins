# Script de Deploy v232 - PlayerEmbedAPI ShortIcu Extractor

Write-Host "DEPLOY v232 - PlayerEmbedAPI ShortIcu Extractor" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Verificar se esta no diretorio correto
if (-not (Test-Path ".git")) {
    Write-Host "Erro: Nao esta em um repositorio git!" -ForegroundColor Red
    exit 1
}

# Mostrar arquivos modificados
Write-Host "Arquivos modificados:" -ForegroundColor Cyan
Write-Host "  - MaxSeries/build.gradle.kts (v232)"
Write-Host "  - MaxSeries/.../MaxSeriesProvider.kt (v232)"
Write-Host "  - MaxSeries/.../PlayerEmbedAPIShortIcuExtractor.kt (NOVO)"
Write-Host ""

# Adicionar apenas os arquivos do projeto
Write-Host "Adicionando arquivos do projeto..." -ForegroundColor Yellow

git add MaxSeries/build.gradle.kts
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIShortIcuExtractor.kt
git add .gitignore

Write-Host "Arquivos adicionados!" -ForegroundColor Green
Write-Host ""

# Criar commit
Write-Host "Criando commit..." -ForegroundColor Yellow
$commitMessage = "v232 - PlayerEmbedAPI ShortIcu Extractor`n`nNOVO: PlayerEmbedAPIShortIcuExtractor.kt`n- Extrai video via short.icu (mais rapido, sem WebView)`n- Fallback automatico para WebViewExtractor se necessario`n`nATUALIZACOES:`n- MaxSeriesProvider.kt: v232 com novo fluxo`n- build.gradle.kts: versao 232"

git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar commit!" -ForegroundColor Red
    exit 1
}

Write-Host "Commit criado!" -ForegroundColor Green
Write-Host ""

# Criar tag
Write-Host "Criando tag v232..." -ForegroundColor Yellow
git tag -a v232 -m "Release v232 - PlayerEmbedAPI ShortIcu Extractor"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tag v232 ja existe, atualizando..." -ForegroundColor Yellow
    git tag -d v232
    git tag -a v232 -m "Release v232 - PlayerEmbedAPI ShortIcu Extractor"
}

Write-Host "Tag v232 criada!" -ForegroundColor Green
Write-Host ""

# Push para origin
Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
Write-Host "Isso vai disparar o GitHub Actions!" -ForegroundColor Cyan
Write-Host ""

git push origin HEAD
git push origin v232

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao fazer push!" -ForegroundColor Red
    exit 1
}

Write-Host "Push realizado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "DEPLOY v232 CONCLUIDO!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Acesse: https://github.com/franciscoalro/TestPlugins/actions"
Write-Host "  2. Aguarde o workflow 'Build and Release' completar (~2-3 minutos)"
Write-Host "  3. O plugin sera publicado automaticamente em Releases"
Write-Host ""
Write-Host "Para atualizar no CloudStream:" -ForegroundColor Cyan
Write-Host "  1. Abra o CloudStream"
Write-Host "  2. Va em: Configuracoes -> Extensoes"
Write-Host "  3. Atualize o repositorio MaxSeries"
Write-Host ""
