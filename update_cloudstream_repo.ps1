#requires -Version 5.1
<#
.SYNOPSIS
    Script para atualizar o plugins.json no repositório CloudstreamRepo com a versão mais recente do MaxSeries.

.DESCRIPTION
    Este script automatiza o processo de:
    1. Verificar se o repositório CloudstreamRepo existe localmente
    2. Copiar o arquivo MaxSeries.cs3 gerado para o CloudstreamRepo
    3. Ler o plugins.json existente
    4. Atualizar a entrada do MaxSeries com nova versão, URL, descrição e timestamp
    5. Salvar o plugins.json atualizado
    6. Fazer commit e push no CloudstreamRepo

.PARAMETER Version
    Número da versão a ser definida (padrão: 253)

.PARAMETER SourceCs3Path
    Caminho do arquivo MaxSeries.cs3 de origem

.PARAMETER RepoPath
    Caminho do repositório CloudstreamRepo

.PARAMETER SkipGit
    Ignorar operações git (commit/push)

.EXAMPLE
    .\update_cloudstream_repo.ps1
    Atualiza com a versão padrão (253)

.EXAMPLE
    .\update_cloudstream_repo.ps1 -Version 254
    Atualiza com versão específica

.EXAMPLE
    .\update_cloudstream_repo.ps1 -SkipGit
    Atualiza sem fazer commit/push
#>

[CmdletBinding()]
param(
    [int]$Version = 253,
    [string]$SourceCs3Path = "C:\Users\KYTHOURS\Desktop\brcloudstream\MaxSeries.cs3",
    [string]$RepoPath = "C:\Users\KYTHOURS\Desktop\brcloudstream\CloudstreamRepo",
    [switch]$SkipGit
)

#region Funções Auxiliares

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[AVISO] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERRO] $Message" -ForegroundColor Red
}

function Get-FileHashSHA256 {
    param([string]$FilePath)
    try {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA256 -ErrorAction Stop
        return $hash.Hash
    }
    catch {
        return $null
    }
}

function Test-GitAvailable {
    try {
        $null = git --version 2>&1
        return $true
    }
    catch {
        return $false
    }
}

#endregion

#region Script Principal

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$dateRelease = Get-Date -Format "yyyyMMdd-HHmmss"

Write-Info "Iniciando atualização do CloudstreamRepo"
Write-Info "Timestamp: $timestamp"
Write-Info "Versão alvo: $Version"

# 1. Verificar se o repositório CloudstreamRepo existe
Write-Info "Verificando repositório CloudstreamRepo..."

if (-not (Test-Path -Path $RepoPath)) {
    Write-Warning "Repositório CloudstreamRepo não encontrado em: $RepoPath"
    Write-Info "Criando estrutura de demonstração (mock)..."
    
    try {
        New-Item -ItemType Directory -Path $RepoPath -Force | Out-Null
        New-Item -ItemType Directory -Path "$RepoPath\releases" -Force | Out-Null
        Write-Success "Diretórios criados"
    }
    catch {
        Write-Error "Falha ao criar diretórios: $_"
        exit 1
    }
    
    $mockMode = $true
}
else {
    $mockMode = $false
    Write-Success "Repositório encontrado: $RepoPath"
}

# 2. Verificar arquivo MaxSeries.cs3 de origem
Write-Info "Verificando arquivo MaxSeries.cs3..."

$sourcePaths = @(
    $SourceCs3Path,
    "C:\Users\KYTHOURS\Desktop\brcloudstream\MaxSeries\build\MaxSeries.cs3",
    "C:\Users\KYTHOURS\Desktop\brcloudstream\MaxSeries.cs3"
)

$foundSource = $null
foreach ($path in $sourcePaths) {
    if (Test-Path -Path $path) {
        $foundSource = $path
        break
    }
}

if (-not $foundSource) {
    Write-Error "Arquivo MaxSeries.cs3 não encontrado nos caminhos padrão"
    Write-Info "Caminhos verificados:"
    $sourcePaths | ForEach-Object { Write-Info "  - $_" }
    exit 1
}

$sourceFile = Get-Item -Path $foundSource
$fileSize = $sourceFile.Length
$fileHash = Get-FileHashSHA256 -FilePath $foundSource

Write-Success "Arquivo encontrado: $foundSource"
Write-Info "Tamanho: $fileSize bytes"
Write-Info "SHA256: $fileHash"

# 3. Copiar arquivo para o repositório
$destCs3Path = Join-Path -Path $RepoPath -ChildPath "releases"
$destCs3File = Join-Path -Path $destCs3Path -ChildPath "MaxSeries_v$Version.cs3"

Write-Info "Copiando arquivo para o repositório..."

try {
    if (-not (Test-Path -Path $destCs3Path)) {
        New-Item -ItemType Directory -Path $destCs3Path -Force | Out-Null
    }
    
    Copy-Item -Path $foundSource -Destination $destCs3File -Force
    Write-Success "Arquivo copiado para: $destCs3File"
}
catch {
    Write-Error "Falha ao copiar arquivo: $_"
    exit 1
}

# 4. Ler e atualizar plugins.json
$pluginsJsonPath = Join-Path -Path $RepoPath -ChildPath "plugins.json"

Write-Info "Processando plugins.json..."

# Definir URL do download (GitHub releases)
$githubRepoUrl = "https://github.com/franciscoalro/TestPlugins"
$downloadUrl = "$githubRepoUrl/releases/download/v$Version/MaxSeries.cs3"

# Criar ou ler plugins.json
if (Test-Path -Path $pluginsJsonPath) {
    try {
        $jsonContent = Get-Content -Path $pluginsJsonPath -Raw -Encoding UTF8
        $plugins = $jsonContent | ConvertFrom-Json
        Write-Success "plugins.json carregado com sucesso"
    }
    catch {
        Write-Warning "Erro ao ler plugins.json: $_"
        Write-Info "Criando novo arquivo..."
        $plugins = @()
    }
}
else {
    Write-Info "plugins.json não existe. Criando novo arquivo..."
    $plugins = @()
}

# Procurar entrada existente do MaxSeries
$maxSeriesEntry = $plugins | Where-Object { $_.name -eq "MaxSeries" -or $_.internalName -eq "MaxSeries" }

# Construir nova descrição
$description = "MaxSeries v$Version - Plugin de streaming com suporte a séries e filmes em português. " +
               "Atualizado em $timestamp com melhorias de performance e estabilidade. " +
               "Sistema completo de extração de vídeo com múltiplas fontes."

# Definir novo ícone (usando favicon padrão ou atualizado)
$iconUrl = "https://www.maxseries.pics/wp-content/themes/dooplay/assets/img/favicon.png"

if ($maxSeriesEntry) {
    # Atualizar entrada existente
    Write-Info "Atualizando entrada existente do MaxSeries..."
    
    $maxSeriesEntry.version = $Version
    $maxSeriesEntry.description = $description
    $maxSeriesEntry.url = $downloadUrl
    $maxSeriesEntry.fileSize = $fileSize
    
    # Adicionar/atualizar fileHash
    if ($maxSeriesEntry.PSObject.Properties['fileHash']) {
        $maxSeriesEntry.fileHash = $fileHash
    }
    else {
        $maxSeriesEntry | Add-Member -NotePropertyName "fileHash" -NotePropertyValue $fileHash
    }
    
    # Adicionar/atualizar updatedAt
    if ($maxSeriesEntry.PSObject.Properties['updatedAt']) {
        $maxSeriesEntry.updatedAt = $timestamp
    }
    else {
        $maxSeriesEntry | Add-Member -NotePropertyName "updatedAt" -NotePropertyValue $timestamp
    }
    
    Write-Success "Entrada do MaxSeries atualizada"
}
else {
    # Criar nova entrada
    Write-Info "Criando nova entrada para MaxSeries..."
    
    $newEntry = @{
        name = "MaxSeries"
        internalName = "MaxSeries"
        description = $description
        version = $Version
        authors = @("franciscoalro")
        repositoryUrl = $githubRepoUrl
        status = 1  # 1 = ativo
        language = "pt-BR"
        tvTypes = @("TvSeries", "Movie")
        iconUrl = $iconUrl
        apiVersion = 1
        isAdult = $false
        fileSize = $fileSize
        fileHash = $fileHash
        url = $downloadUrl
        createdAt = $timestamp
        updatedAt = $timestamp
    }
    
    # Converter para PSCustomObject e adicionar ao array
    $plugins += [PSCustomObject]$newEntry
    Write-Success "Nova entrada do MaxSeries criada"
}

# 5. Salvar plugins.json atualizado
Write-Info "Salvando plugins.json..."

try {
    # Converter para JSON com indentação
    $jsonOutput = $plugins | ConvertTo-Json -Depth 10
    
    # Salvar com codificação UTF-8 sem BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($pluginsJsonPath, $jsonOutput, $utf8NoBom)
    
    Write-Success "plugins.json salvo em: $pluginsJsonPath"
}
catch {
    Write-Error "Falha ao salvar plugins.json: $_"
    exit 1
}

# Exibir resumo da atualização
Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "RESUMO DA ATUALIZAÇÃO" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Plugin: MaxSeries" -ForegroundColor White
Write-Host "Versão: $Version" -ForegroundColor White
Write-Host "Arquivo: MaxSeries_v$Version.cs3" -ForegroundColor White
Write-Host "Tamanho: $fileSize bytes" -ForegroundColor White
Write-Host "SHA256: $fileHash" -ForegroundColor White
Write-Host "URL: $downloadUrl" -ForegroundColor White
Write-Host "Timestamp: $timestamp" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Blue

# 6. Operações Git (se não estiver em modo mock e não for skip)
if (-not $SkipGit -and -not $mockMode) {
    if (-not (Test-GitAvailable)) {
        Write-Warning "Git não está disponível. Pulando operações de commit/push."
    }
    else {
        Write-Info "Executando operações Git..."
        
        # Mudar para o diretório do repositório
        $originalLocation = Get-Location
        Set-Location -Path $RepoPath
        
        try {
            # Verificar se é um repositório git
            $gitDir = Join-Path -Path $RepoPath -ChildPath ".git"
            if (-not (Test-Path -Path $gitDir)) {
                Write-Info "Inicializando repositório Git..."
                git init
                git remote add origin "https://github.com/franciscoalro/CloudstreamRepo.git" 2>$null
            }
            
            # Configurar usuário git se necessário
            $gitUserName = git config user.name 2>$null
            $gitUserEmail = git config user.email 2>$null
            
            if (-not $gitUserName) {
                git config user.name "Auto Deploy"
            }
            if (-not $gitUserEmail) {
                git config user.email "deploy@automation.local"
            }
            
            # Adicionar arquivos
            Write-Info "Adicionando arquivos ao stage..."
            git add plugins.json
            git add "releases/MaxSeries_v$Version.cs3"
            
            # Verificar se há alterações para commit
            $status = git status --porcelain
            if ($status) {
                # Criar commit
                $commitMessage = "Update MaxSeries to v$Version`n`n" +
                                "- Version: $Version`n" +
                                "- File: MaxSeries_v$Version.cs3`n" +
                                "- Size: $fileSize bytes`n" +
                                "- SHA256: $fileHash`n" +
                                "- Timestamp: $timestamp"
                
                Write-Info "Criando commit..."
                git commit -m $commitMessage
                Write-Success "Commit criado"
                
                # Push
                Write-Info "Enviando para o repositório remoto..."
                git push origin HEAD
                Write-Success "Push realizado com sucesso!"
            }
            else {
                Write-Info "Nenhuma alteração para commitar"
            }
        }
        catch {
            Write-Error "Erro durante operações Git: $_"
        }
        finally {
            # Retornar ao diretório original
            Set-Location -Path $originalLocation
        }
    }
}
else {
    if ($SkipGit) {
        Write-Info "Operações Git ignoradas (modo SkipGit)"
    }
    if ($mockMode) {
        Write-Info "Operações Git ignoradas (modo mock/demo)"
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "ATUALIZAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Retornar estrutura do JSON atualizado
Write-Host "`nEstrutura do plugins.json atualizado:" -ForegroundColor Cyan
$plugins | ConvertTo-Json -Depth 10

#endregion
