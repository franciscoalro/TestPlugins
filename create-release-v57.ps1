#!/usr/bin/env pwsh
# Script para criar release v57 no GitHub via API

param(
    [Parameter(Mandatory=$false)]
    [string]$Token = $env:GITHUB_TOKEN
)

$owner = "franciscoalro"
$repo = "TestPlugins"
$tag = "v57.0"
$releaseName = "MaxSeries v57 - Parse Real da Estrutura do Site"
$releaseBody = @"
## MaxSeries v57 - Parse Real da Estrutura do Site

### Mudanças principais:
- ✅ Análise completa da estrutura real do maxseries.one
- ✅ URLs corrigidas: `/filmes/` e `/series/` (não `/movies/`)
- ✅ Seletores baseados na estrutura HTML real
- ✅ Removido anime (site não possui animes)
- ✅ Detecção precisa filme vs série baseada na URL
- ✅ Parser inteligente com filtros por h3 e ano
- ✅ Suporte a metadados reais (rating IMDb, gêneros, temporadas)

### Instalação:
1. Abra o CloudStream
2. Vá em Configurações > Extensões > Repositórios
3. Adicione: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json`
4. Instale/Atualize MaxSeries

### Arquivos:
- `MaxSeries.cs3` - Plugin principal
"@

$cs3Path = "MaxSeries/build/MaxSeries.cs3"

if (-not $Token) {
    Write-Host "❌ Token do GitHub não fornecido!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para criar o release automaticamente, você precisa:" -ForegroundColor Yellow
    Write-Host "1. Criar um Personal Access Token em: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. Executar: .\create-release-v57.ps1 -Token SEU_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou crie manualmente em:" -ForegroundColor Yellow
    Write-Host "https://github.com/$owner/$repo/releases/new?tag=$tag" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Título: $releaseName" -ForegroundColor White
    Write-Host "Arquivo para upload: $cs3Path" -ForegroundColor White
    exit 1
}

Write-Host "🚀 Criando release $tag..." -ForegroundColor Green

# Criar release
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    tag_name = $tag
    name = $releaseName
    body = $releaseBody
    draft = $false
    prerelease = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "✅ Release criado! ID: $($response.id)" -ForegroundColor Green
    
    # Upload do arquivo .cs3
    if (Test-Path $cs3Path) {
        Write-Host "📦 Fazendo upload do MaxSeries.cs3..." -ForegroundColor Cyan
        $uploadUrl = $response.upload_url -replace '\{\?name,label\}', "?name=MaxSeries.cs3"
        
        $uploadHeaders = @{
            "Authorization" = "token $Token"
            "Content-Type" = "application/octet-stream"
        }
        
        $fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $cs3Path))
        $uploadResponse = Invoke-RestMethod -Uri $uploadUrl -Method Post -Headers $uploadHeaders -Body $fileBytes
        
        Write-Host "✅ Upload concluído!" -ForegroundColor Green
        Write-Host "🔗 Release: $($response.html_url)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ Arquivo $cs3Path não encontrado. Faça upload manualmente." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Crie manualmente em:" -ForegroundColor Yellow
    Write-Host "https://github.com/$owner/$repo/releases/new?tag=$tag" -ForegroundColor Cyan
}
