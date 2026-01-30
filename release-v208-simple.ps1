# Script Simples de Release - MaxSeries v208

Write-Host "🚀 RELEASE MaxSeries v208" -ForegroundColor Cyan
Write-Host "="*60

# Verificar build
if (-not (Test-Path "MaxSeries\build\MaxSeries.cs3")) {
    Write-Host "❌ Build não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build encontrado" -ForegroundColor Green

# Commit
Write-Host "`n📝 Commitando alterações..." -ForegroundColor Cyan
git add MaxSeries/
git add *.md
git add *.ps1
git commit -m "feat(MaxSeries): v208 - 17 new genres + trending"

# Push
Write-Host "`n📤 Push para GitHub..." -ForegroundColor Cyan
git push origin main

# Tag
Write-Host "`n🏷️ Criando tag v208..." -ForegroundColor Cyan
git tag -a v208 -m "MaxSeries v208"
git push origin v208

Write-Host "`n✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host "📋 Próximo passo: Criar release manualmente no GitHub" -ForegroundColor Yellow
Write-Host "🔗 https://github.com/franciscoalro/brcloudstream/releases/new" -ForegroundColor Cyan
Write-Host "`nAnexe o arquivo: MaxSeries\build\MaxSeries.cs3" -ForegroundColor Yellow
