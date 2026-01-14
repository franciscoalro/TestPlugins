#!/usr/bin/env pwsh
# Script para atualizar MaxSeries v78 no repositório GitHub

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     MaxSeries v78 - Atualização do Repositório GitHub        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se o arquivo .cs3 existe
Write-Host "📦 Verificando arquivo MaxSeries.cs3..." -ForegroundColor Yellow
if (Test-Path "MaxSeries\build\MaxSeries.cs3") {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    
    # Copiar para raiz (opcional, para facilitar)
    Copy-Item "MaxSeries\build\MaxSeries.cs3" "MaxSeries.cs3" -Force
    Write-Host "✅ Copiado para raiz" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo MaxSeries.cs3 não encontrado!" -ForegroundColor Red
    Write-Host "Execute: ./gradlew.bat :MaxSeries:make" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar status do Git
Write-Host ""
Write-Host "📊 Status do Git:" -ForegroundColor Yellow
git status --short

# 3. Adicionar arquivos modificados
Write-Host ""
Write-Host "➕ Adicionando arquivos..." -ForegroundColor Yellow

# Arquivos principais
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt
git add MaxSeries/build.gradle.kts
git add MaxSeries/build/MaxSeries.cs3
git add plugins.json

# Documentação
git add MAXSERIES_V78_SEARCH_FIX.md
git add ANALISE_PROFUNDA_MAXSERIES.md

# Scripts de teste (opcional)
git add test-search-fix.py
git add test-maxseries-search.py
git add debug-search-html.py
git add deep-maxseries-advanced.py

Write-Host "✅ Arquivos adicionados" -ForegroundColor Green

# 4. Commit
Write-Host ""
Write-Host "💾 Criando commit..." -ForegroundColor Yellow

$commitMessage = @"
MaxSeries v78 - Correção de Busca

🐛 Problema Corrigido:
- Busca não retornava resultados no CloudStream
- Página de busca usa estrutura HTML diferente (.result-item)

✅ Solução:
- Novo seletor: .result-item article
- Nova função: toSearchResultFromSearch()
- Fallback para seletor normal
- Logs de debug melhorados

🧪 Testes:
- 5 queries testadas: 100% sucesso
- "gerente": 17 resultados
- "chapolin": 2 resultados
- "garota": 30 resultados
- "mil golpes": 4 resultados
- "breaking bad": 3 resultados

📦 Arquivos:
- MaxSeriesProvider.kt: search() reescrita
- build.gradle.kts: versão 78
- plugins.json: atualizado
- MAXSERIES_V78_SEARCH_FIX.md: documentação completa
- ANALISE_PROFUNDA_MAXSERIES.md: análise de 5 séries

🚀 Pronto para uso!
"@

git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao criar commit" -ForegroundColor Red
    exit 1
}

# 5. Push
Write-Host ""
Write-Host "🚀 Fazendo push para GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Erro ao fazer push. Tentando 'master'..." -ForegroundColor Yellow
    git push origin master
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
        exit 1
    }
}

# 6. Criar tag v78.0
Write-Host ""
Write-Host "🏷️ Criando tag v78.0..." -ForegroundColor Yellow
git tag -a v78.0 -m "MaxSeries v78 - Correção de Busca"
git push origin v78.0

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag criada e enviada!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Tag pode já existir ou erro ao enviar" -ForegroundColor Yellow
}

# 7. Resumo
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ ATUALIZAÇÃO COMPLETA!                   ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Criar release v78.0 no GitHub" -ForegroundColor White
Write-Host "  2. Fazer upload do MaxSeries.cs3" -ForegroundColor White
Write-Host "  3. Testar no CloudStream" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URL do repositório:" -ForegroundColor Cyan
Write-Host "  https://github.com/franciscoalro/TestPlugins" -ForegroundColor White
Write-Host ""
