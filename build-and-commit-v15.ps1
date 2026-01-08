#!/usr/bin/env pwsh
# Build e Commit MaxSeries v15 - Versão Final GeckoDriver

Write-Host "🚀 BUILD E COMMIT MAXSERIES V15" -ForegroundColor Green
Write-Host "=" * 50

# 1. Verificar mudanças
Write-Host "📋 Verificando mudanças..." -ForegroundColor Yellow
git status

# 2. Adicionar mudanças
Write-Host "📝 Adicionando mudanças..." -ForegroundColor Yellow
git add MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt
git add plugins.json

# 3. Commit
$commitMessage = "feat: MaxSeries v15.0 - Versão Final baseada em análise GeckoDriver

- Análise completa com GeckoDriver realizada
- 5 episódios detectados por série via playerthree.online iframes
- Players reais detectados: playerembedapi.link, megaembed.link
- Estrutura de navegação por fragmentos (#12962_255703, etc.)
- gleam.config detectado e implementado
- Múltiplas estratégias de fallback
- Logs detalhados para debug
- Correção do problema 'Em breve' nos episódios
- Correção da detecção de links de vídeo"

Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m $commitMessage

# 4. Push
Write-Host "🚀 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main

# 5. Criar tag
Write-Host "🏷️ Criando tag v15.0..." -ForegroundColor Yellow
git tag v15.0
git push origin v15.0

Write-Host "✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host "🎯 Tag v15.0 criada - GitHub Actions irá gerar o build automaticamente" -ForegroundColor Cyan
Write-Host "📦 Aguarde alguns minutos para o release aparecer em:" -ForegroundColor White
Write-Host "   https://github.com/franciscoalro/TestPlugins/releases" -ForegroundColor White