# Script de deploy para GitHub - MaxSeries v260
# Autor: franciscoalro

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY GITHUB - MaxSeries v260" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configuracoes
$PluginSource = "MaxSeries\build\MaxSeries.cs3"
$GithubRepo = "https://github.com/franciscoalro/TestPlugins.git"
$TempDir = "$env:TEMP\maxseries-deploy"
$Version = "v260"

# Verificar se o plugin existe
if (-not (Test-Path $PluginSource)) {
    Write-Host "ERRO: Plugin nao encontrado em $PluginSource" -ForegroundColor Red
    Write-Host "Execute primeiro: .\gradlew make" -ForegroundColor Yellow
    exit 1
}

$Size = (Get-Item $PluginSource).Length
Write-Host "Plugin encontrado: $PluginSource" -ForegroundColor Green
Write-Host "Tamanho: $([math]::Round($Size/1024, 2)) KB" -ForegroundColor Gray
Write-Host ""

# Verificar Git
$gitExists = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitExists) {
    Write-Host "ERRO: Git nao encontrado. Instale o Git primeiro." -ForegroundColor Red
    exit 1
}

# Limpar diretorio temporario
if (Test-Path $TempDir) {
    Remove-Item -Recurse -Force $TempDir
}

# Clonar repositorio
Write-Host "Clonando repositorio GitHub..." -ForegroundColor Cyan
try {
    git clone $GithubRepo $TempDir 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Falha ao clonar" }
} catch {
    Write-Host "ERRO ao clonar repositorio: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Repositorio clonado com sucesso!" -ForegroundColor Green
Write-Host ""

# Copiar plugin
Write-Host "Copiando plugin..." -ForegroundColor Cyan
Copy-Item $PluginSource "$TempDir\MaxSeries.cs3" -Force

# Copiar arquivos JSON atualizados
Write-Host "Copiando arquivos JSON..." -ForegroundColor Cyan
Copy-Item "plugins.json" "$TempDir\plugins.json" -Force
Copy-Item "repo.json" "$TempDir\repo.json" -Force

# Calcular hash
Write-Host "Calculando hash SHA256..." -ForegroundColor Cyan
$hash = (certutil -hashfile "$TempDir\MaxSeries.cs3" SHA256)[1].Trim().Replace(" ", "")
Write-Host "SHA256: $hash" -ForegroundColor Gray
Write-Host ""

# Commit e push
Write-Host "Enviando para GitHub..." -ForegroundColor Cyan
Set-Location $TempDir

# Configurar git (se necessario)
git config user.email "deploy@maxseries.local" 2>$null
git config user.name "Deploy Script" 2>$null

# Adicionar arquivos
git add MaxSeries.cs3 plugins.json repo.json

# Verificar se ha mudancas
$status = git status --porcelain
if (-not $status) {
    Write-Host "Nenhuma mudanca detectada." -ForegroundColor Yellow
} else {
    # Commit
git commit -m "MaxSeries $Version - AES Decryptor + CDN Constructor + Session Manager

- Fase 1: AES-CTR Decryptor com 8 estrategias de chave
- Fase 2: CDN Constructor com 4 CDNs e 40+ padroes
- Fase 3: Session Manager com cache e auto-renewal
- PlayerEmbedAPI v8.7 com cascading fallback
- Performance: 3-8s -> 50-150ms (98% mais rapido)

SHA256: $hash
Size: $([math]::Round($Size/1024, 2)) KB" 2>&1 | Out-Null
    
    # Push
    Write-Host "Fazendo push para GitHub..." -ForegroundColor Cyan
    git push origin main 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Push concluido com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "AVISO: Push pode ter falhado. Verifique manualmente." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  DEPLOY CONCLUIDO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do Plugin:" -ForegroundColor Cyan
Write-Host "  https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3"
Write-Host ""
Write-Host "URL do Repo JSON:" -ForegroundColor Cyan
Write-Host "  https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json"
Write-Host ""
Write-Host "Adicione no CloudStream:" -ForegroundColor Yellow
Write-Host "  https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json"
Write-Host ""

# Limpar
Set-Location $env:TEMP
Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue

Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
