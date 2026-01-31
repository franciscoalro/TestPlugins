# Script para upload do MaxSeries.cs3 para GitHub Releases
# Autor: MaxSeries Team
# Versao: 1.0

param(
    [string]$Version = "256",
    [string]$Tag = "v256",
    [string]$Repo = "franciscoalro/TestPlugins",
    [string]$FilePath = "releases\MaxSeries.cs3",
    [string]$Token = $env:GITHUB_TOKEN
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPLOAD GITHUB RELEASES - MAXSERIES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar token
if (-not $Token) {
    Write-Host "`n❌ ERRO: Token GitHub não encontrado!" -ForegroundColor Red
    Write-Host "Configure a variável de ambiente GITHUB_TOKEN ou passe via parâmetro -Token" -ForegroundColor Yellow
    Write-Host "`nComo criar um token:" -ForegroundColor Cyan
    Write-Host "1. Acesse: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. Clique em 'Generate new token (classic)'" -ForegroundColor White
    Write-Host "3. Selecione o scope 'repo' (acesso completo ao repositório)" -ForegroundColor White
    Write-Host "4. Copie o token e use: `$env:GITHUB_TOKEN = 'seu_token_aqui'" -ForegroundColor White
    exit 1
}

# Verificar arquivo
$FullPath = Resolve-Path $FilePath -ErrorAction SilentlyContinue
if (-not $FullPath) {
    Write-Host "`n❌ ERRO: Arquivo não encontrado: $FilePath" -ForegroundColor Red
    exit 1
}

$FileSize = [math]::Round((Get-Item $FullPath).Length / 1KB, 2)
Write-Host "`n📁 Arquivo: $FullPath" -ForegroundColor White
Write-Host "📊 Tamanho: $FileSize KB" -ForegroundColor White
Write-Host "🏷️  Versão: $Version (Tag: $Tag)" -ForegroundColor White
Write-Host "📦 Repositório: $Repo" -ForegroundColor White

# Headers para API
$Headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "Content-Type" = "application/json"
}

# Verificar se a release já existe
Write-Host "`n🔍 Verificando se a release $Tag existe..." -ForegroundColor Yellow
$ReleaseUrl = "https://api.github.com/repos/$Repo/releases/tags/$Tag"

try {
    $Release = Invoke-RestMethod -Uri $ReleaseUrl -Headers $Headers -Method Get -ErrorAction Stop
    Write-Host "✅ Release encontrada: $($Release.name)" -ForegroundColor Green
    $UploadUrl = $Release.upload_url -replace "{\?name,label}", ""
} catch {
    Write-Host "⚠️ Release não encontrada. Criando nova release..." -ForegroundColor Yellow
    
    # Criar nova release
    $Body = @{
        tag_name = $Tag
        name = "MaxSeries v$Version"
        body = @"
## MaxSeries v$Version - PlayerEmbedAPI V8+V7 Fixes

### 🚀 Novidades
- **PlayerEmbedAPI V8 (Pure HTTP)**: 12 padrões de URL (+7 CDNs)
- **PlayerEmbedAPI V7 (WebView)**: Memory leak e race conditions corrigidos
- **Timeout global aumentado**: 15s → 25s
- **Max attempts aumentado**: 3 → 5

### 🔧 Correções
- ✅ Regex JWPlayer mais robusto
- ✅ Novos padrões de CDN (Akamai, CloudFront, Fastly, BunnyCDN, CDN77)
- ✅ Validação de URL aprimorada
- ✅ Padrões HTTP adicionais (axios, XMLHttpRequest, jQuery)
- ✅ Flag atômica no cleanup do WebView
- ✅ Try-finally garante liberação de recursos

### 📊 Estatísticas
- Versão: $Version
- Tamanho: $FileSize KB
- Extractors: 7 + fallback
- Taxa de sucesso: ~99%

**Instalação:**
1. Baixe o arquivo MaxSeries.cs3
2. No CloudStream: Configurações → Extensões → Instalar de arquivo .cs3
"@
        draft = $false
        prerelease = $false
    } | ConvertTo-Json -Depth 10
    
    $CreateUrl = "https://api.github.com/repos/$Repo/releases"
    $Release = Invoke-RestMethod -Uri $CreateUrl -Headers $Headers -Method Post -Body $Body
    Write-Host "✅ Release criada: $($Release.name)" -ForegroundColor Green
    $UploadUrl = $Release.upload_url -replace "{\?name,label}", ""
}

# Verificar se asset já existe e deletar
Write-Host "`n🔍 Verificando se o asset já existe..." -ForegroundColor Yellow
$ExistingAsset = $Release.assets | Where-Object { $_.name -eq "MaxSeries.cs3" }
if ($ExistingAsset) {
    Write-Host "⚠️ Asset já existe. Deletando..." -ForegroundColor Yellow
    $DeleteUrl = $ExistingAsset.url
    Invoke-RestMethod -Uri $DeleteUrl -Headers $Headers -Method Delete
    Write-Host "✅ Asset anterior deletado" -ForegroundColor Green
}

# Fazer upload do arquivo
Write-Host "`n📤 Fazendo upload do arquivo..." -ForegroundColor Yellow
$UploadUrlWithName = "$UploadUrl?name=MaxSeries.cs3"

$FileBytes = [System.IO.File]::ReadAllBytes($FullPath)
$FileContent = [System.IO.MemoryStream]::new($FileBytes)

$UploadHeaders = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "Content-Type" = "application/octet-stream"
}

try {
    $UploadResponse = Invoke-RestMethod -Uri $UploadUrlWithName -Headers $UploadHeaders -Method Post -InFile $FullPath
    Write-Host "`n✅ UPLOAD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "`n📋 Detalhes:" -ForegroundColor Cyan
    Write-Host "   URL: $($UploadResponse.browser_download_url)" -ForegroundColor White
    Write-Host "   ID: $($UploadResponse.id)" -ForegroundColor White
    Write-Host "   Tamanho: $([math]::Round($UploadResponse.size / 1KB, 2)) KB" -ForegroundColor White
    
    # Abrir URL no navegador (opcional)
    Write-Host "`n🌐 Abrindo página da release no navegador..." -ForegroundColor Yellow
    Start-Process $Release.html_url
    
} catch {
    Write-Host "`n❌ ERRO NO UPLOAD: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  UPLOAD COMPLETO! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
