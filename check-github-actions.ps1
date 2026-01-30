Write-Host "`n=== VERIFICANDO GITHUB ACTIONS ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔗 Links para verificar:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Actions do repositório:" -ForegroundColor White
Write-Host "   https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Workflow 'Build and Release':" -ForegroundColor White
Write-Host "   https://github.com/franciscoalro/TestPlugins/actions/workflows/release.yml" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Releases:" -ForegroundColor White
Write-Host "   https://github.com/franciscoalro/TestPlugins/releases" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Tag v216:" -ForegroundColor White
Write-Host "   https://github.com/franciscoalro/TestPlugins/releases/tag/v216" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Status esperado:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ⏳ Workflow 'Build and Release' deve estar rodando" -ForegroundColor White
Write-Host "  🔨 Compilando todos os providers" -ForegroundColor White
Write-Host "  📦 Criando artifacts" -ForegroundColor White
Write-Host "  🏷️ Criando release para tag v216" -ForegroundColor White
Write-Host ""

Write-Host "⏱️ Tempo estimado: 3-5 minutos" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 Dica:" -ForegroundColor Yellow
Write-Host "   Abra o primeiro link no navegador para ver o progresso em tempo real!" -ForegroundColor White
Write-Host ""

# Tentar abrir no navegador
$url = "https://github.com/franciscoalro/TestPlugins/actions"
Write-Host "🌐 Abrindo navegador..." -ForegroundColor Cyan
Start-Process $url

Write-Host ""
Write-Host "✅ Navegador aberto!" -ForegroundColor Green
Write-Host ""
