# Script para commit e push das mudanças v206

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Git Commit & Push - v206" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar status do git
Write-Host "Status do repositório:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "Arquivos a serem commitados:" -ForegroundColor Yellow
Write-Host "  - plugins.json (atualizado com 7 providers)" -ForegroundColor White
Write-Host "  - build.gradle.kts (versões atualizadas)" -ForegroundColor White
Write-Host "  - Vizer.kt (correção API Score)" -ForegroundColor White
Write-Host "  - build.gradle.kts (Kotlin 2.3.0)" -ForegroundColor White
Write-Host "  - settings.gradle.kts (providers desabilitados)" -ForegroundColor White
Write-Host ""

# Adicionar arquivos
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add plugins.json
git add build.gradle.kts
git add settings.gradle.kts
git add */build.gradle.kts
git add Vizer/src/main/kotlin/com/Vizer/Vizer.kt
git add BUILD_SUCCESS_KOTLIN_2.3.0.md
git add RELEASE_NOTES_V206.md
git add create-release-v206.ps1
git add commit-and-push-v206.ps1

Write-Host "✅ Arquivos adicionados" -ForegroundColor Green
Write-Host ""

# Criar commit
$commitMessage = @"
Release v206 - Kotlin 2.3.0 Upgrade (7 Providers)

## Mudanças Principais
- Upgrade Kotlin 1.9.23 → 2.3.0
- Corrigido Vizer.kt (API Score)
- Atualizado plugins.json com 7 providers
- Versões incrementadas:
  * MaxSeries: v205 → v206
  * AnimesOnlineCC: v9 → v10
  * MegaFlix, NetCine, OverFlix, PobreFlix, Vizer: v1 → v2

## Providers Incluídos
- AnimesOnlineCC v10
- MaxSeries v206
- MegaFlix v2
- NetCine v2
- OverFlix v2
- PobreFlix v2
- Vizer v2

## Build Status
✅ Todos os 7 providers compilando com sucesso
✅ Compatível com Cloudstream library 8a4480dc42
✅ GitHub Actions ready
"@

Write-Host "Criando commit..." -ForegroundColor Yellow
git commit -m "$commitMessage"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit criado com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao criar commit" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Push para o GitHub
Write-Host "Fazendo push para o GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Push realizado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximo passo:" -ForegroundColor Yellow
    Write-Host "Execute: .\create-release-v206.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    exit 1
}
