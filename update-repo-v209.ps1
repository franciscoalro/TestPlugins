# Script para atualizar repositório com v209

Write-Host "🔄 ATUALIZANDO REPOSITÓRIO PARA v209" -ForegroundColor Cyan
Write-Host "="*60

# Verificar se estamos no branch correto
$currentBranch = git branch --show-current
Write-Host "`n📍 Branch atual: $currentBranch" -ForegroundColor White

if ($currentBranch -ne "main") {
    Write-Host "⚠️ Mudando para branch main..." -ForegroundColor Yellow
    git checkout main
}

# Verificar se há alterações não commitadas
$status = git status --porcelain
if ($status) {
    Write-Host "`n📝 Commitando alterações pendentes..." -ForegroundColor Yellow
    git add .
    git commit -m "chore: Prepare for v209 release"
    git push origin main
}

Write-Host "`n✅ Branch main atualizado!" -ForegroundColor Green

# Instruções para atualizar branch builds
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "📋 PRÓXIMOS PASSOS MANUAIS:" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan

Write-Host "`n1️⃣ Criar Release no GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/franciscoalro/brcloudstream/releases/new" -ForegroundColor White
Write-Host "   - Tag: v209" -ForegroundColor White
Write-Host "   - Título: MaxSeries v209 - Multi-Extractor Support" -ForegroundColor White
Write-Host "   - Anexar: MaxSeries\build\MaxSeries.cs3" -ForegroundColor White
Write-Host "   - Release notes: RELEASE_NOTES_V209.md" -ForegroundColor White

Write-Host "`n2️⃣ Atualizar Branch Builds:" -ForegroundColor Yellow
Write-Host "   git checkout builds" -ForegroundColor White
Write-Host "   # Editar plugins.json (version: 209, url: v209)" -ForegroundColor White
Write-Host "   git add plugins.json" -ForegroundColor White
Write-Host "   git commit -m 'chore: Update MaxSeries to v209'" -ForegroundColor White
Write-Host "   git push origin builds" -ForegroundColor White
Write-Host "   git checkout main" -ForegroundColor White

Write-Host "`n3️⃣ Testar no Cloudstream:" -ForegroundColor Yellow
Write-Host "   - Adicionar repositório" -ForegroundColor White
Write-Host "   - Verificar se v209 aparece" -ForegroundColor White
Write-Host "   - Instalar e testar vídeos" -ForegroundColor White

Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "✅ PREPARAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ("="*60) -ForegroundColor Cyan
