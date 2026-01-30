# Create releases for all providers

Write-Host "🚀 CREATING GITHUB RELEASES FOR ALL PROVIDERS" -ForegroundColor Cyan
Write-Host "="*60

# Commit all changes first
Write-Host "`n📝 Committing all changes..." -ForegroundColor Yellow
git add .
git commit -m "feat: Build all 7 Brazilian providers - MaxSeries v209 + 6 others"
git push origin main

Write-Host "`n✅ Changes committed and pushed" -ForegroundColor Green

# Create tags
Write-Host "`n🏷️ Creating tags..." -ForegroundColor Yellow

# MaxSeries v209 (already created)
Write-Host "  v209 (MaxSeries) - Already exists" -ForegroundColor Gray

# All providers release
Write-Host "  Creating v1.0.0 for all providers..." -ForegroundColor White
git tag -a v1.0.0 -m "BRCloudstream v1.0.0 - All 7 Brazilian Providers"
git push origin v1.0.0

Write-Host "`n✅ Tags created" -ForegroundColor Green

Write-Host "`n" + ("="*60)
Write-Host "📋 MANUAL STEPS REQUIRED:" -ForegroundColor Cyan
Write-Host ("="*60)

Write-Host "`n1️⃣ Create MaxSeries v209 Release:" -ForegroundColor Yellow
Write-Host "   URL: https://github.com/franciscoalro/brcloudstream/releases/new?tag=v209" -ForegroundColor White
Write-Host "   Title: MaxSeries v209 - Multi-Extractor Support" -ForegroundColor White
Write-Host "   File: MaxSeries\build\MaxSeries.cs3" -ForegroundColor White
Write-Host "   Notes: Copy from RELEASE_NOTES_V209.md" -ForegroundColor White

Write-Host "`n2️⃣ Create All Providers v1.0.0 Release:" -ForegroundColor Yellow
Write-Host "   URL: https://github.com/franciscoalro/brcloudstream/releases/new?tag=v1.0.0" -ForegroundColor White
Write-Host "   Title: BRCloudstream v1.0.0 - All 7 Brazilian Providers" -ForegroundColor White
Write-Host "   Files:" -ForegroundColor White
Write-Host "     - MaxSeries\build\MaxSeries.cs3" -ForegroundColor Gray
Write-Host "     - AnimesOnlineCC\build\AnimesOnlineCC.cs3" -ForegroundColor Gray
Write-Host "     - MegaFlix\build\MegaFlix.cs3" -ForegroundColor Gray
Write-Host "     - NetCine\build\NetCine.cs3" -ForegroundColor Gray
Write-Host "     - OverFlix\build\OverFlix.cs3" -ForegroundColor Gray
Write-Host "     - PobreFlix\build\PobreFlix.cs3" -ForegroundColor Gray
Write-Host "     - Vizer\build\Vizer.cs3" -ForegroundColor Gray

Write-Host "`n" + ("="*60)
Write-Host "✅ PREPARATION COMPLETE!" -ForegroundColor Green
Write-Host ("="*60)
Write-Host ""
