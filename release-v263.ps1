# Script de Release v263 - MaxSeries
# PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritário + V7 (WebView) timeout 25s

param(
    [string]$Version = "263",
    [string]$RepoOwner = "franciscoalro",
    [string]$RepoName = "TestPlugins"
)

$ErrorActionPreference = "Stop"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   MaxSeries Release Script v$Version" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o arquivo existe
$Cs3File = "MaxSeries.cs3"
if (-not (Test-Path $Cs3File)) {
    Write-Host "❌ Erro: Arquivo $Cs3File não encontrado!" -ForegroundColor Red
    exit 1
}

$FileSize = (Get-Item $Cs3File).Length
$FileSizeKB = [math]::Round($FileSize / 1KB, 2)
Write-Host "✅ Arquivo encontrado: $Cs3File ($FileSizeKB KB)" -ForegroundColor Green

# Calcular checksum
Write-Host "📊 Calculando checksum..." -ForegroundColor Yellow
$Hash = Get-FileHash $Cs3File -Algorithm SHA256
Write-Host "   SHA256: $($Hash.Hash)" -ForegroundColor Gray

# Criar release no GitHub
Write-Host ""
Write-Host "🚀 Criando release v$Version no GitHub..." -ForegroundColor Yellow

$ReleaseNotes = @"
## MaxSeries v$Version - PlayerEmbedAPI Otimizado

### 🚀 Novidades
- **PlayerEmbedAPI V8 (Pure HTTP)** agora é tentado primeiro (~50-100ms)
- **PlayerEmbedAPI V7 (WebView)** é usado como fallback com timeout de 25s
- Carregamento de vídeos muito mais rápido

### 🔧 Correções
- Fix: Timeout do V7 causando exception null
- Fix: Carregamento lento quando V7 era tentado primeiro
- Otimização do fluxo de extração

### 📊 Performance
| Método | Tempo | Status |
|--------|-------|--------|
| V8 (Pure HTTP) | ~50-100ms | ✅ Principal |
| V7 (WebView) | Até 25s | 🔄 Fallback |

### 📁 Arquivos
- MaxSeries.cs3 ($FileSizeKB KB)
- SHA256: $($Hash.Hash)
"@

try {
    # Criar release
    $ReleaseData = @{
        tag_name = "v$Version"
        target_commitish = "main"
        name = "MaxSeries v$Version"
        body = $ReleaseNotes
        draft = $false
        prerelease = $false
    } | ConvertTo-Json -Depth 10

    $Headers = @{
        "Accept" = "application/vnd.github+json"
        "Authorization" = "Bearer `$env:GITHUB_TOKEN"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $ReleaseResponse = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases" -Method Post -Headers $Headers -Body $ReleaseData -ContentType "application/json"
    
    Write-Host "✅ Release criada com sucesso!" -ForegroundColor Green
    Write-Host "   URL: $($ReleaseResponse.html_url)" -ForegroundColor Cyan
    
    # Upload do arquivo
    Write-Host ""
    Write-Host "📤 Fazendo upload do MaxSeries.cs3..." -ForegroundColor Yellow
    
    $UploadUrl = $ReleaseResponse.upload_url -replace "{\\?name,label}", "?name=MaxSeries.cs3"
    $FileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $Cs3File))
    
    Invoke-RestMethod -Uri $UploadUrl -Method Post -Headers @{ 
        "Accept" = "application/vnd.github+json"
        "Authorization" = "Bearer `$env:GITHUB_TOKEN"
        "Content-Type" = "application/octet-stream"
    } -Body $FileBytes
    
    Write-Host "✅ Upload concluído!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erro ao criar release: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   Release v$Version concluído! 🎉" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Verifique a release em: https://github.com/$RepoOwner/$RepoName/releases/tag/v$Version"
Write-Host "2. Teste a instalação no Cloudstream"
Write-Host "3. Atualize o repo.json se necessário"
