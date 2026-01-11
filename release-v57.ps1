#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando Release v57.0 - MaxSeries Enhanced Stability" -ForegroundColor Green
Write-Host "=" * 60

# Configurações
$version = "57"
$releaseTag = "v57.0"
$releaseTitle = "MaxSeries v57 - Parse Real da Estrutura do Site"

Write-Host "📋 INFORMAÇÕES DO RELEASE:" -ForegroundColor Yellow
Write-Host "Versão: $version" -ForegroundColor White
Write-Host "Tag: $releaseTag" -ForegroundColor White
Write-Host "Título: $releaseTitle" -ForegroundColor White
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "build.gradle.kts")) {
    Write-Host "❌ Erro: build.gradle.kts não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto." -ForegroundColor Yellow
    exit 1
}

Write-Host "🔧 ETAPA 1: Verificando arquivos..." -ForegroundColor Cyan

# Verificar arquivos essenciais
$requiredFiles = @("plugins.json", "repo.json", "MaxSeries/build.gradle.kts")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n🏗️ ETAPA 2: Executando build..." -ForegroundColor Cyan

# Executar build
try {
    & .\gradlew.bat build --no-daemon
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build executado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro no build!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erro ao executar build: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 ETAPA 3: Verificando arquivos gerados..." -ForegroundColor Cyan

# Verificar se os arquivos .cs3 foram gerados
$cs3Files = Get-ChildItem -Path "build" -Filter "*.cs3" -Recurse
if ($cs3Files.Count -gt 0) {
    Write-Host "✅ Arquivos .cs3 encontrados:" -ForegroundColor Green
    foreach ($file in $cs3Files) {
        $sizeKB = [math]::Round($file.Length / 1KB, 2)
        Write-Host "  📄 $($file.Name) ($sizeKB KB)" -ForegroundColor White
    }
} else {
    Write-Host "❌ Nenhum arquivo .cs3 encontrado em build/" -ForegroundColor Red
    exit 1
}

Write-Host "`n📝 ETAPA 4: Preparando commit..." -ForegroundColor Cyan

# Adicionar arquivos ao git
try {
    git add .
    git commit -m "Release v$version - Parse Real da Estrutura do Site

- Análise completa da estrutura real do maxseries.one
- URLs corrigidas: /filmes/ e /series/ (não /movies/)
- Seletores baseados na estrutura HTML real
- Removido anime (site não possui animes)
- Detecção precisa filme vs série baseada na URL
- Parser inteligente com filtros por h3 e ano
- Suporte a metadados reais (rating IMDb, gêneros, temporadas)
- Testes automatizados validando a estrutura

Files updated:
- MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt (estrutura real)
- MaxSeries/build.gradle.kts (version $version)
- plugins.json (version $version)
- plugins-simple.json (version $version)
- providers.json (version $version)"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Commit criado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Aviso: Possível erro no commit (pode ser normal se não há mudanças)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Aviso: Erro no commit: $_" -ForegroundColor Yellow
}

Write-Host "`n🌐 ETAPA 5: Enviando para GitHub..." -ForegroundColor Cyan

# Push para GitHub
try {
    git push origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Código enviado para GitHub!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao enviar para GitHub!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erro no push: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🏷️ ETAPA 6: Criando tag..." -ForegroundColor Cyan

# Criar e enviar tag
try {
    git tag $releaseTag
    git push origin $releaseTag
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tag $releaseTag criada e enviada!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao criar/enviar tag!" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro na tag: $_" -ForegroundColor Red
}

Write-Host "`n🎯 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Acesse: https://github.com/franciscoalro/TestPlugins/releases/new?tag=$releaseTag" -ForegroundColor White
Write-Host "2. Título: $releaseTitle" -ForegroundColor White
Write-Host "3. Faça upload dos arquivos .cs3 da pasta build/" -ForegroundColor White
Write-Host "4. Publique o release" -ForegroundColor White

Write-Host "`n✅ RELEASE v$version PREPARADO COM SUCESSO!" -ForegroundColor Green
Write-Host "🔗 GitHub: https://github.com/franciscoalro/TestPlugins" -ForegroundColor Cyan
Write-Host "📱 Teste no CloudStream após criar o release manual" -ForegroundColor Cyan