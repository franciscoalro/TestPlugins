# Script de Release Completo e Automatizado v263
# Faz TUDO: compila, cria release, upload e atualiza JSONs

param(
    [string]$Version = "263",
    [string]$RepoOwner = "franciscoalro",
    [string]$RepoName = "TestPlugins",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

# Cores
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==========================================" -ForegroundColor $Cyan
    Write-Host "  $Message" -ForegroundColor $Cyan
    Write-Host "==========================================" -ForegroundColor $Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "📌 $Message" -ForegroundColor $Yellow
}

# ========== INÍCIO ==========
Write-Step "MaxSeries Release Automatizado v$Version"

# Verificar Git
Write-Info "Verificando Git..."
$GitStatus = git status --porcelain 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git não inicializado ou não é um repositório"
    exit 1
}
Write-Success "Git OK"

# Verificar GITHUB_TOKEN
if (-not $env:GITHUB_TOKEN) {
    Write-Error "GITHUB_TOKEN não definido!"
    Write-Info "Defina com: `$env:GITHUB_TOKEN = 'seu_token'"
    exit 1
}
Write-Success "GITHUB_TOKEN definido"

# ========== 1. COMPILAR ==========
Write-Step "1. Compilando Projeto"

Set-Location MaxSeries

Write-Info "Limpando build anterior..."
.\..\gradlew.bat clean --no-daemon 2>&1 | Out-Null

Write-Info "Compilando..."
$BuildOutput = .\..\gradlew.bat assembleRelease -x test --no-daemon 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha na compilação!"
    Write-Host $BuildOutput -ForegroundColor $Red
    Set-Location ..
    exit 1
}

Write-Success "Build concluído!"
Set-Location ..

# ========== 2. GERAR .CS3 ==========
Write-Step "2. Gerando Arquivo .cs3"

$SourceAar = "MaxSeries\build\outputs\aar\MaxSeries-release.aar"
$DestCs3 = "MaxSeries.cs3"

if (-not (Test-Path $SourceAar)) {
    Write-Error "Arquivo AAR não encontrado: $SourceAar"
    exit 1
}

Copy-Item $SourceAar $DestCs3 -Force
$FileSize = (Get-Item $DestCs3).Length
$FileSizeKB = [math]::Round($FileSize / 1KB, 2)

Write-Success "MaxSeries.cs3 gerado ($FileSizeKB KB)"

# Calcular hash
$Hash = Get-FileHash $DestCs3 -Algorithm SHA256
Write-Info "SHA256: $($Hash.Hash)"

# ========== 3. ATUALIZAR JSONS ==========
Write-Step "3. Atualizando Arquivos JSON"

$FilesUpdated = @()

# plugins.json
$plugins = @([
    ordered]@{
        url = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/MaxSeries.cs3"
        status = 1
        version = [int]$Version
        apiVersion = 1
        name = "MaxSeries"
        internalName = "MaxSeries"
        authors = @("franciscoalro")
        description = "MaxSeries v$Version - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritário + V7 (WebView) com timeout 25s como fallback"
        repositoryUrl = "https://github.com/$RepoOwner/$RepoName"
        tvTypes = @("TvSeries", "Movie")
        language = "pt-BR"
        iconUrl = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/icon.png"
        fileSize = $FileSize
    }
)
$plugins | ConvertTo-Json -Depth 10 | Out-File "plugins.json" -Encoding UTF8
$FilesUpdated += "plugins.json"
Write-Success "plugins.json atualizado"

# repo.json
$repo = @{
    name = "MaxSeries"
    description = "MaxSeries v$Version - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritário + V7 (WebView) com timeout 25s como fallback"
    manifestVersion = 1
    pluginLists = @("https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/plugins.json")
}
$repo | ConvertTo-Json -Depth 10 | Out-File "repo.json" -Encoding UTF8
$FilesUpdated += "repo.json"
Write-Success "repo.json atualizado"

# plugins-simple.json
$pluginsSimple = @([
    ordered]@{
        url = "https://github.com/$RepoOwner/$RepoName/releases/download/v$Version/MaxSeries.cs3"
        status = 1
        version = [int]$Version
        name = "MaxSeries"
        description = "MaxSeries v$Version - PlayerEmbedAPI Otimizado"
    }
)
$pluginsSimple | ConvertTo-Json -Depth 10 | Out-File "plugins-simple.json" -Encoding UTF8
$FilesUpdated += "plugins-simple.json"
Write-Success "plugins-simple.json atualizado"

# plugins-minimal.json
$pluginsMinimal = @([
    ordered]@{
        name = "MaxSeries"
        description = "MaxSeries v$Version - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritário + V7 (WebView) com timeout 25s como fallback"
        version = $Version
        url = "https://github.com/$RepoOwner/$RepoName/releases/download/v$Version/MaxSeries.cs3"
        status = 1
        apiVersion = 1
    }
)
$pluginsMinimal | ConvertTo-Json -Depth 10 | Out-File "plugins-minimal.json" -Encoding UTF8
$FilesUpdated += "plugins-minimal.json"
Write-Success "plugins-minimal.json atualizado"

Write-Success "Todos os JSONs atualizados!"

# ========== 4. COMMIT ==========
Write-Step "4. Fazendo Commit das Alterações"

# Verificar se há mudanças
$Status = git status --porcelain
if ($Status) {
    Write-Info "Arquivos modificados:"
    $Status | ForEach-Object { Write-Host "   $_" }
    
    git add .
    git commit -m "Release v$Version - PlayerEmbedAPI Otimizado (V8 prioritário + V7 timeout 25s)" --quiet
    Write-Success "Commit feito!"
    
    # Push
    Write-Info "Enviando para GitHub..."
    git push origin $Branch --quiet
    Write-Success "Push concluído!"
} else {
    Write-Info "Nenhuma alteração para commit"
}

# ========== 5. CRIAR RELEASE GITHUB ==========
Write-Step "5. Criando Release no GitHub"

$ReleaseBody = @"
## 🚀 MaxSeries v$Version - PlayerEmbedAPI Otimizado

### Novidades
- **PlayerEmbedAPI V8 (Pure HTTP)** agora é tentado **primeiro** (~50-100ms)
- **PlayerEmbedAPI V7 (WebView)** usado como **fallback** com timeout de **25s**
- Carregamento de vídeos muito mais rápido e confiável

### Correções
- ✅ Fix: Timeout do V7 causando exception null
- ✅ Fix: Carregamento lento quando V7 era tentado primeiro
- ✅ Otimização do fluxo de extração

### Performance
| Método | Tempo Médio | Status |
|--------|-------------|--------|
| V8 (Pure HTTP) | ~50-100ms | 🚀 **Principal** |
| V7 (WebView) | Até 25s | 🔄 **Fallback** |

### Arquivos
- **MaxSeries.cs3**: $FileSizeKB KB
- **SHA256**: $($Hash.Hash)

### Instalação
1. Baixe o arquivo MaxSeries.cs3
2. Abra o Cloudstream3
3. Configurações → Extensões → Instalar de arquivo
4. Selecione o arquivo baixado

Ou use o repo:
```
https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/repo.json
```
"@

$ReleaseData = @{
    tag_name = "v$Version"
    target_commitish = $Branch
    name = "MaxSeries v$Version"
    body = $ReleaseBody
    draft = $false
    prerelease = $false
} | ConvertTo-Json -Depth 10

$Headers = @{
    "Accept" = "application/vnd.github+json"
    "Authorization" = "Bearer $env:GITHUB_TOKEN"
    "X-GitHub-Api-Version" = "2022-11-28"
}

try {
    Write-Info "Criando release..."
    $ReleaseResponse = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases" -Method Post -Headers $Headers -Body $ReleaseData -ContentType "application/json"
    
    $ReleaseId = $ReleaseResponse.id
    $ReleaseUrl = $ReleaseResponse.html_url
    Write-Success "Release criada!"
    Write-Info "URL: $ReleaseUrl"
    
} catch {
    Write-Error "Falha ao criar release: $_"
    exit 1
}

# ========== 6. UPLOAD DO ARQUIVO ==========
Write-Step "6. Fazendo Upload do MaxSeries.cs3"

$UploadUrl = "https://uploads.github.com/repos/$RepoOwner/$RepoName/releases/$ReleaseId/assets?name=MaxSeries.cs3"

$FileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $DestCs3))

$UploadHeaders = @{
    "Accept" = "application/vnd.github+json"
    "Authorization" = "Bearer $env:GITHUB_TOKEN"
    "X-GitHub-Api-Version" = "2022-11-28"
    "Content-Type" = "application/octet-stream"
}

try {
    Write-Info "Enviando arquivo ($FileSizeKB KB)..."
    $UploadResponse = Invoke-RestMethod -Uri $UploadUrl -Method Post -Headers $UploadHeaders -Body $FileBytes
    
    Write-Success "Upload concluído!"
    Write-Info "Download URL: $($UploadResponse.browser_download_url)"
    
} catch {
    Write-Error "Falha no upload: $_"
    exit 1
}

# ========== FIM ==========
Write-Step "Release v$Version Concluído! 🎉"

Write-Host "`n📊 Resumo:" -ForegroundColor $Cyan
Write-Host "   Versão: v$Version" -ForegroundColor White
Write-Host "   Arquivo: MaxSeries.cs3 ($FileSizeKB KB)" -ForegroundColor White
Write-Host "   SHA256: $($Hash.Hash)" -ForegroundColor White
Write-Host "   Release: $ReleaseUrl" -ForegroundColor White

Write-Host "`n📁 JSONs Atualizados:" -ForegroundColor $Cyan
$FilesUpdated | ForEach-Object { Write-Host "   ✅ $_" -ForegroundColor $Green }

Write-Host "`n🎯 Próximos passos:" -ForegroundColor $Yellow
Write-Host "   1. Teste a instalação no Cloudstream" -ForegroundColor White
Write-Host "   2. Verifique se o update aparece no app" -ForegroundColor White
Write-Host "   3. Teste o PlayerEmbedAPI em um vídeo" -ForegroundColor White

Write-Host "`n✨ Tudo automatizado com sucesso!" -ForegroundColor $Green
