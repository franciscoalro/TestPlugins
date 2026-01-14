# MaxSeries v78 - Update Repository

Write-Host "MaxSeries v78 - Atualizando repositorio..." -ForegroundColor Cyan

# Verificar arquivo
if (Test-Path "MaxSeries\build\MaxSeries.cs3") {
    Write-Host "OK: Arquivo MaxSeries.cs3 encontrado" -ForegroundColor Green
    Copy-Item "MaxSeries\build\MaxSeries.cs3" "MaxSeries.cs3" -Force
} else {
    Write-Host "ERRO: MaxSeries.cs3 nao encontrado!" -ForegroundColor Red
    exit 1
}

# Git status
Write-Host ""
Write-Host "Status do Git:" -ForegroundColor Yellow
git status --short

# Add files
Write-Host ""
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt
git add MaxSeries/build.gradle.kts
git add MaxSeries/build/MaxSeries.cs3
git add plugins.json
git add MAXSERIES_V78_SEARCH_FIX.md
git add ANALISE_PROFUNDA_MAXSERIES.md
git add test-search-fix.py
git add MaxSeries.cs3

Write-Host "OK: Arquivos adicionados" -ForegroundColor Green

# Commit
Write-Host ""
Write-Host "Criando commit..." -ForegroundColor Yellow

$msg = "MaxSeries v78 - Correcao de Busca

- Busca corrigida: suporte a .result-item
- Nova funcao: toSearchResultFromSearch()
- Fallback para seletor normal
- Logs de debug melhorados
- Testado: 5 queries com 100% sucesso
- Documentacao completa adicionada"

git commit -m $msg

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Commit criado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no commit" -ForegroundColor Red
    exit 1
}

# Push
Write-Host ""
Write-Host "Fazendo push..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tentando branch master..." -ForegroundColor Yellow
    git push origin master
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Push realizado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no push" -ForegroundColor Red
    exit 1
}

# Tag
Write-Host ""
Write-Host "Criando tag v78.0..." -ForegroundColor Yellow
git tag -a v78.0 -m "MaxSeries v78 - Correcao de Busca"
git push origin v78.0

Write-Host ""
Write-Host "CONCLUIDO!" -ForegroundColor Green
Write-Host "Proximo passo: Criar release v78.0 no GitHub" -ForegroundColor Cyan
Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/new" -ForegroundColor White
