Write-Host "=== Deploy das Correcoes ===" -ForegroundColor Green
Write-Host ""

# Verificar se git esta configurado
try {
    $gitStatus = git status 2>&1
    Write-Host "Git status: OK" -ForegroundColor Green
} catch {
    Write-Host "Git nao configurado. Configure primeiro:" -ForegroundColor Red
    Write-Host "git config --global user.name 'Seu Nome'" -ForegroundColor Yellow
    Write-Host "git config --global user.email 'seu@email.com'" -ForegroundColor Yellow
    exit 1
}

# Adicionar arquivos modificados
Write-Host "Adicionando arquivos modificados..." -ForegroundColor Cyan
git add builds/plugins.json
git add builds/repo.json
git add plugins.json
git add repo.json

# Commit das correcoes
$commitMessage = "fix: Corrigir URLs e codificacao para resolver problema de download no Cloudstream

- Simplificar URLs (remover refs/heads/)
- Corrigir codificacao UTF-8 sem BOM
- Atualizar tamanhos dos arquivos no plugins.json
- Remover caracteres especiais das descricoes

Fixes: Plugins listavam mas nao baixavam no Cloudstream Android"

Write-Host "Fazendo commit..." -ForegroundColor Cyan
git commit -m $commitMessage

# Push para GitHub
Write-Host "Enviando para GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "✅ Deploy concluido!" -ForegroundColor Green
Write-Host "Os usuarios agora podem usar a URL corrigida:" -ForegroundColor Yellow
Write-Host "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor Cyan