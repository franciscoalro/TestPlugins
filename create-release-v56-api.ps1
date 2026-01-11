#!/usr/bin/env pwsh

Write-Host "🚀 Criando GitHub Release v56.0 automaticamente via API" -ForegroundColor Green
Write-Host "=" * 60

# Verificar se o arquivo .cs3 existe
if (-not (Test-Path "MaxSeries.cs3")) {
    Write-Host "❌ Arquivo MaxSeries.cs3 não encontrado!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item "MaxSeries.cs3").Length
Write-Host "📦 Arquivo MaxSeries.cs3: $fileSize bytes" -ForegroundColor Cyan

# Configurações do repositório
$owner = "franciscoalro"
$repo = "TestPlugins"
$tag = "v56.0"
$name = "MaxSeries v56 - Critical AnimesOnlineCC Fixes"

# Corpo da release
$body = @"
## 🔧 MaxSeries v56 - Critical AnimesOnlineCC Fixes

### ✅ CORREÇÕES CRÍTICAS APLICADAS:
- **Tratamento de erro robusto**: Try/catch em todas as funções principais
- **Logs detalhados**: Log.d() ao invés de println() para debug no Android
- **Busca de imagem robusta**: Suporte a src, data-src, data-lazy-src, data-original
- **URLs consistentes**: Uso de fixUrl() e fixUrlNull() em todos os lugares
- **Melhor busca de elementos**: Seletores mais robustos para título e poster
- **Suporte híbrido**: Funciona com formato MaxSeries e AnimesOnlineCC de episódios

### 🎯 BASEADO NO ANIMESONLINECC FUNCIONANDO:
- Estrutura de error handling idêntica ao AnimesOnlineCC
- Padrões de busca de elementos similares
- Logs detalhados para facilitar troubleshooting
- Tratamento robusto de URLs e imagens

### 📱 DEVE RESOLVER:
- **Problema principal**: Conteúdo não aparecendo no CloudStream app
- **Logs vazios**: Agora com logs detalhados para debug
- **Imagens quebradas**: Busca robusta em múltiplos atributos
- **URLs malformadas**: fixUrl() consistente

### 🔍 TESTE AUTOMATIZADO:
```
🌐 Site: https://www.maxseries.one ✅ (Status: 200)
🔍 Seletor 'div.items article.item': ✅ (36 itens encontrados)
🎬 Página de filmes: ✅ (1 filme encontrado)
📺 Página de séries: ✅ (42 séries encontradas)
🔍 Pesquisa: ✅ (funcional)
```

**Site**: https://www.maxseries.one/
**Filtro YouTube**: ✅ Ativo
**Extractors**: DoodStream, MegaEmbed, PlayerEmbedAPI
"@

try {
    Write-Host "🏷️ Criando release via API do GitHub..." -ForegroundColor Yellow
    
    # Obter o SHA do commit atual
    $commitSha = git rev-parse HEAD
    Write-Host "📝 Commit SHA: $commitSha" -ForegroundColor Cyan
    
    # Criar o payload da release
    $releaseData = @{
        tag_name = $tag
        target_commitish = $commitSha
        name = $name
        body = $body
        draft = $false
        prerelease = $false
    } | ConvertTo-Json -Depth 10
    
    # Tentar usar credenciais do git
    Write-Host "🔑 Tentando obter token do git..." -ForegroundColor Yellow
    
    # Método 1: Tentar usar git credential helper
    $gitRemote = git remote get-url origin
    Write-Host "📡 Remote URL: $gitRemote" -ForegroundColor Cyan
    
    # Extrair informações do remote
    if ($gitRemote -match "github\.com[:/]([^/]+)/([^/]+)\.git") {
        $actualOwner = $matches[1]
        $actualRepo = $matches[2]
        Write-Host "👤 Owner: $actualOwner, Repo: $actualRepo" -ForegroundColor Cyan
    }
    
    # Criar release usando curl (mais compatível)
    Write-Host "🌐 Criando release via curl..." -ForegroundColor Yellow
    
    # Salvar dados em arquivo temporário
    $releaseData | Out-File -FilePath "release_data.json" -Encoding UTF8
    
    # Tentar diferentes métodos de autenticação
    $apiUrl = "https://api.github.com/repos/$owner/$repo/releases"
    
    Write-Host "📡 URL da API: $apiUrl" -ForegroundColor Cyan
    Write-Host "🔄 Tentando criar release..." -ForegroundColor Yellow
    
    # Método usando Invoke-RestMethod sem autenticação (público)
    try {
        $headers = @{
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "PowerShell-Release-Creator"
        }
        
        $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Body $releaseData -Headers $headers -ContentType "application/json"
        
        Write-Host "✅ Release criado com sucesso!" -ForegroundColor Green
        Write-Host "🔗 URL: $($response.html_url)" -ForegroundColor Cyan
        Write-Host "📦 Upload URL: $($response.upload_url)" -ForegroundColor Cyan
        
        # Agora fazer upload do arquivo
        $uploadUrl = $response.upload_url -replace '\{\?name,label\}', "?name=MaxSeries.cs3"
        
        Write-Host "📤 Fazendo upload do MaxSeries.cs3..." -ForegroundColor Yellow
        
        $fileBytes = [System.IO.File]::ReadAllBytes("MaxSeries.cs3")
        $uploadHeaders = @{
            "Accept" = "application/vnd.github.v3+json"
            "Content-Type" = "application/octet-stream"
            "User-Agent" = "PowerShell-Release-Creator"
        }
        
        $uploadResponse = Invoke-RestMethod -Uri $uploadUrl -Method POST -Body $fileBytes -Headers $uploadHeaders
        
        Write-Host "✅ Arquivo MaxSeries.cs3 enviado com sucesso!" -ForegroundColor Green
        Write-Host "📥 Download URL: $($uploadResponse.browser_download_url)" -ForegroundColor Cyan
        
    } catch {
        Write-Host "❌ Erro na API do GitHub: $($_.Exception.Message)" -ForegroundColor Red
        
        # Método alternativo: usar git para criar tag e depois interface web
        Write-Host "🔄 Tentando método alternativo..." -ForegroundColor Yellow
        
        # Criar tag local
        git tag -a $tag -m $name
        git push origin $tag
        
        Write-Host "✅ Tag $tag criada e enviada!" -ForegroundColor Green
        Write-Host "🌐 Acesse manualmente: https://github.com/$owner/$repo/releases/new?tag=$tag" -ForegroundColor Cyan
        Write-Host "📋 Copie e cole a descrição do arquivo CREATE_GITHUB_RELEASE_V56.md" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erro geral: $($_.Exception.Message)" -ForegroundColor Red
    
    # Fallback: criar tag e instruções
    Write-Host "🔄 Criando tag como fallback..." -ForegroundColor Yellow
    
    try {
        git tag -a $tag -m $name
        git push origin $tag
        
        Write-Host "✅ Tag $tag criada com sucesso!" -ForegroundColor Green
        Write-Host "🌐 Acesse: https://github.com/$owner/$repo/releases/new?tag=$tag" -ForegroundColor Cyan
        Write-Host "📤 Faça upload manual do arquivo MaxSeries.cs3" -ForegroundColor Yellow
        
    } catch {
        Write-Host "❌ Erro ao criar tag: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "🌐 Acesse manualmente: https://github.com/$owner/$repo/releases/new" -ForegroundColor Cyan
    }
} finally {
    # Limpar arquivo temporário
    if (Test-Path "release_data.json") {
        Remove-Item "release_data.json" -Force
    }
}

Write-Host "`n🎯 VERIFICAÇÃO FINAL:" -ForegroundColor Yellow
Write-Host "1. Acesse: https://github.com/$owner/$repo/releases" -ForegroundColor White
Write-Host "2. Verifique se o release v56.0 foi criado" -ForegroundColor White
Write-Host "3. Confirme se o arquivo MaxSeries.cs3 está disponível" -ForegroundColor White
Write-Host "4. Teste no CloudStream app" -ForegroundColor White