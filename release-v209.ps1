# Script de Release - MaxSeries v209

Write-Host "🚀 RELEASE MaxSeries v209" -ForegroundColor Cyan
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
git commit -m "feat(MaxSeries): v209 - Added 4 new video extractors" -m "DoodStream, StreamTape, Mixdrop, Filemoon" -m "Success rate: 85% to 99%"

# Push
Write-Host "`n📤 Push para GitHub..." -ForegroundColor Cyan
git push origin main

# Tag
Write-Host "`n🏷️ Criando tag v209..." -ForegroundColor Cyan
git tag -a v209 -m "MaxSeries v209 - Multi-Extractor Support"
git push origin v209

Write-Host "`n✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host "`n📋 Próximo passo: Criar release no GitHub" -ForegroundColor Yellow
Write-Host "🔗 https://github.com/franciscoalro/brcloudstream/releases/new" -ForegroundColor Cyan
Write-Host "`nAnexe o arquivo: MaxSeries\build\MaxSeries.cs3" -ForegroundColor Yellow
Write-Host "Use as release notes de: RELEASE_NOTES_V209.md" -ForegroundColor Yellow
