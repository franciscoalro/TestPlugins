# Status do Deploy - BRCloudStream
# Mostra informações sobre o deploy e tokens

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   STATUS DO DEPLOY - BRCloudStream    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Git
Write-Host "1. Git Configuration" -ForegroundColor Yellow
git --version
git remote -v
Write-Host ""

# Verificar GitHub CLI
Write-Host "2. GitHub CLI" -ForegroundColor Yellow
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    gh --version | Select-Object -First 1
    
    # Verificar autenticação
    $auth = gh auth status 2>&1
    if ($auth -match "Logged in") {
        Write-Host "   Status: Autenticado" -ForegroundColor Green
    } else {
        Write-Host "   Status: Não autenticado" -ForegroundColor Red
        Write-Host "   Execute: gh auth login" -ForegroundColor Yellow
    }
} else {
    Write-Host "   GitHub CLI não instalado" -ForegroundColor Red
    Write-Host "   Download: https://cli.github.com/" -ForegroundColor Gray
}
Write-Host ""

# Verificar arquivos
Write-Host "3. Arquivos de Build" -ForegroundColor Yellow
if (Test-Path "builds") {
    $files = Get-ChildItem "builds\*.cs3" -ErrorAction SilentlyContinue
    Write-Host "   Total de plugins: $($files.Count)" -ForegroundColor Green
    $files | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }
} else {
    Write-Host "   Pasta builds/ não encontrada" -ForegroundColor Red
}
Write-Host ""

# Verificar workflows
Write-Host "4. GitHub Actions Workflows" -ForegroundColor Yellow
if (Test-Path ".github\workflows") {
    $workflows = Get-ChildItem ".github\workflows\*.yml"
    Write-Host "   Workflows encontrados:" -ForegroundColor Green
    $workflows | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }
} else {
    Write-Host "   Pasta .github/workflows não encontrada" -ForegroundColor Red
}
Write-Host ""

# Mostrar secrets necessários
Write-Host "5. Secrets Necessários (GitHub)" -ForegroundColor Yellow
Write-Host "   Para deploy automático, configure em:" -ForegroundColor Gray
Write-Host "   Settings > Secrets and variables > Actions" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secrets:" -ForegroundColor White
Write-Host "   - CLOUDSTREAM_REPO_TOKEN : Token para acessar CloudstreamRepo" -ForegroundColor Yellow
Write-Host "   - GITHUB_TOKEN           : Token padrão (automático)" -ForegroundColor Gray
Write-Host ""

# URLs
Write-Host "6. URLs do Repositório" -ForegroundColor Yellow
Write-Host "   TestPlugins: https://github.com/franciscoalro/TestPlugins" -ForegroundColor White
Write-Host "   CloudstreamRepo: https://github.com/franciscoalro/CloudstreamRepo" -ForegroundColor White
Write-Host "   Plugins JSON: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   COMO DEPLOYAR                        " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opção 1 - Automático (GitHub Actions):" -ForegroundColor Yellow
Write-Host "   git add ." -ForegroundColor White
Write-Host "   git commit -m 'Update plugins'" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor White
Write-Host "   git tag v256" -ForegroundColor White
Write-Host "   git push origin v256" -ForegroundColor White
Write-Host ""
Write-Host "Opção 2 - Script PowerShell:" -ForegroundColor Yellow
Write-Host "   .\deploy-direto.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Opção 3 - Manual:" -ForegroundColor Yellow
Write-Host "   Copie os arquivos .cs3 para o repositório CloudstreamRepo" -ForegroundColor White
Write-Host ""
