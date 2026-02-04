#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script de deploy do MaxSeries.cs3 para nuvem
.DESCRIPTION
    Faz upload do plugin para GitHub Releases, Netlify, ou outro serviço
    e atualiza o repositório com a nova URL
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("github", "netlify", "transfer.sh", "bashupload")]
    [string]$Target = "github",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "v260",
    
    [Parameter(Mandatory=$false)]
    [string]$RepoOwner = "franciscoalro",
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "TestPlugins",
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken = $env:GITHUB_TOKEN
)

$ErrorActionPreference = "Stop"
$pluginPath = "MaxSeries/build/MaxSeries.cs3"
$jsonPath = "CloudstreamRepo/plugins.json"

Write-Host "🚀 DEPLOY DO MAXSERIES PLUGIN" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o arquivo existe
if (-not (Test-Path $pluginPath)) {
    Write-Error "❌ Arquivo não encontrado: $pluginPath"
    Write-Host "Execute primeiro: cd MaxSeries; ../gradlew make"
    exit 1
}

$fileSize = (Get-Item $pluginPath).Length / 1KB
Write-Host "📦 Arquivo: $pluginPath" -ForegroundColor Green
Write-Host "📊 Tamanho: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Green
Write-Host "🎯 Target: $Target" -ForegroundColor Green
Write-Host ""

switch ($Target) {
    "github" {
        Deploy-GitHubReleases
    }
    "netlify" {
        Deploy-Netlify
    }
    "transfer.sh" {
        Deploy-TransferSh
    }
    "bashupload" {
        Deploy-BashUpload
    }
}

function Deploy-GitHubReleases {
    Write-Host "📤 Fazendo deploy para GitHub Releases..." -ForegroundColor Yellow
    
    if (-not $GitHubToken) {
        Write-Error "❌ GITHUB_TOKEN não definido. Defina a variável de ambiente."
        Write-Host "Exemplo: `$env:GITHUB_TOKEN = 'seu_token_aqui'"
        exit 1
    }
    
    # Criar release
    $releaseData = @{
        tag_name = $Version
        name = "MaxSeries $Version"
        body = "Plugin MaxSeries versão $Version com FASES 1, 2 e 3 implementadas.`n`n- AES-CTR Decryptor`n- CDN Constructor`n- Session Manager"
        draft = $false
        prerelease = $false
    } | ConvertTo-Json
    
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases" `
            -Method Post `
            -Headers @{
                "Authorization" = "token $GitHubToken"
                "Accept" = "application/vnd.github.v3+json"
            } `
            -Body $releaseData
        
        $uploadUrl = $release.upload_url -replace "{\\?name,label}", "?name=MaxSeries.cs3"
        
        Write-Host "✅ Release criada: $($release.html_url)" -ForegroundColor Green
        
        # Upload do arquivo
        $fileBytes = [System.IO.File]::ReadAllBytes($pluginPath)
        $upload = Invoke-RestMethod -Uri $uploadUrl `
            -Method Post `
            -Headers @{
                "Authorization" = "token $GitHubToken"
                "Content-Type" = "application/octet-stream"
            } `
            -Body $fileBytes
        
        $downloadUrl = $upload.browser_download_url
        Write-Host "✅ Arquivo enviado: $downloadUrl" -ForegroundColor Green
        
        # Atualizar JSON
        Update-RepoJson $downloadUrl
        
    } catch {
        Write-Error "❌ Erro no deploy: $_"
        exit 1
    }
}

function Deploy-TransferSh {
    Write-Host "📤 Fazendo upload para transfer.sh..." -ForegroundColor Yellow
    
    try {
        $response = curl.exe --progress-bar --upload-file $pluginPath "https://transfer.sh/MaxSeries_$Version.cs3"
        $downloadUrl = $response.Trim()
        
        Write-Host "✅ Upload concluído!" -ForegroundColor Green
        Write-Host "🔗 URL: $downloadUrl" -ForegroundColor Cyan
        
        Update-RepoJson $downloadUrl
        
    } catch {
        Write-Error "❌ Erro no upload: $_"
        exit 1
    }
}

function Deploy-BashUpload {
    Write-Host "📤 Fazendo upload para bashupload.com..." -ForegroundColor Yellow
    
    try {
        $fileName = "MaxSeries_$Version.cs3"
        $response = curl.exe -X POST --data-binary "@$pluginPath" "https://bashupload.com/$fileName"
        
        # Extrair URL da resposta
        if ($response -match "https://bashupload\.com/[^\s]+") {
            $downloadUrl = $Matches[0]
            Write-Host "✅ Upload concluído!" -ForegroundColor Green
            Write-Host "🔗 URL: $downloadUrl" -ForegroundColor Cyan
            
            Update-RepoJson $downloadUrl
        } else {
            Write-Error "❌ Não foi possível extrair a URL da resposta"
            Write-Host "Resposta: $response"
            exit 1
        }
        
    } catch {
        Write-Error "❌ Erro no upload: $_"
        exit 1
    }
}

function Deploy-Netlify {
    Write-Host "📤 Instruções para Netlify:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Acesse: https://app.netlify.com/drop" -ForegroundColor Cyan
    Write-Host "2. Arraste o arquivo: $pluginPath" -ForegroundColor Cyan
    Write-Host "3. Copie a URL gerada" -ForegroundColor Cyan
    Write-Host ""
    
    $netlifyUrl = Read-Host "🔗 Cole a URL do Netlify aqui"
    
    if ($netlifyUrl -and $netlifyUrl.StartsWith("http")) {
        Update-RepoJson $netlifyUrl
    } else {
        Write-Error "❌ URL inválida"
        exit 1
    }
}

function Update-RepoJson($downloadUrl) {
    Write-Host ""
    Write-Host "📝 Atualizando repositório..." -ForegroundColor Yellow
    
    if (-not (Test-Path $jsonPath)) {
        Write-Warning "⚠️ Arquivo $jsonPath não encontrado. Criando novo..."
        New-RepoJson $downloadUrl
        return
    }
    
    try {
        $json = Get-Content $jsonPath -Raw | ConvertFrom-Json
        
        # Encontrar e atualizar o plugin MaxSeries
        $updated = $false
        foreach ($plugin in $json.plugins) {
            if ($plugin.name -eq "MaxSeries") {
                $plugin.url = $downloadUrl
                $plugin.version = $Version
                $plugin.lastUpdated = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                $updated = $true
                Write-Host "✅ Plugin MaxSeries atualizado" -ForegroundColor Green
                break
            }
        }
        
        # Se não encontrou, adicionar novo
        if (-not $updated) {
            $newPlugin = @{
                name = "MaxSeries"
                url = $downloadUrl
                version = $Version
                lastUpdated = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                status = 1
                description = "MaxSeries Provider com AES, CDN e Session Manager"
            }
            $json.plugins += $newPlugin
            Write-Host "✅ Plugin MaxSeries adicionado" -ForegroundColor Green
        }
        
        # Salvar JSON
        $json | ConvertTo-Json -Depth 10 | Set-Content $jsonPath -Encoding UTF8
        
        Write-Host "✅ Repositório atualizado: $jsonPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Resumo:" -ForegroundColor Cyan
        Write-Host "   Plugin: MaxSeries" -ForegroundColor White
        Write-Host "   Versão: $Version" -ForegroundColor White
        Write-Host "   URL: $downloadUrl" -ForegroundColor White
        Write-Host ""
        Write-Host "🎉 DEPLOY CONCLUÍDO!" -ForegroundColor Green
        
    } catch {
        Write-Error "❌ Erro ao atualizar JSON: $_"
        exit 1
    }
}

function New-RepoJson($downloadUrl) {
    $json = @{
        name = "MaxSeries Repository"
        description = "Repositório de plugins MaxSeries"
        plugins = @(@{
            name = "MaxSeries"
            url = $downloadUrl
            version = $Version
            lastUpdated = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            status = 1
            description = "MaxSeries Provider com AES, CDN e Session Manager"
        })
    }
    
    $json | ConvertTo-Json -Depth 10 | Set-Content $jsonPath -Encoding UTF8
    Write-Host "✅ Novo repositório criado: $jsonPath" -ForegroundColor Green
}

# Executar
Write-Host ""
Write-Host "🚀 Iniciando deploy..." -ForegroundColor Cyan
