#requires -Version 5.1
<#
.SYNOPSIS
    Script Mestre de Release - PlayerEmbedAPI v5.0
    
.DESCRIPTION
    Automatiza todo o processo de release do PlayerEmbedAPI v5.0 incluindo:
    - Verificação de pré-requisitos
    - Validação de build e testes
    - Criação de tag git v253
    - Commit e push das alterações
    - Criação de release no GitHub
    - Upload do arquivo .cs3
    - Atualização do plugins.json
    - Geração de relatório final

.PARAMETER SkipTests
    Ignora a verificação de testes (não recomendado)

.PARAMETER SkipGitHubRelease
    Pula a criação da release no GitHub

.PARAMETER DryRun
    Executa em modo simulação sem fazer alterações reais

.EXAMPLE
    .\full_release_v5.ps1
    
.EXAMPLE
    .\full_release_v5.ps1 -DryRun

.NOTES
    Autor: Release Automation System
    Versão: 5.0
    Data: 2026-01-31
#>

[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$SkipGitHubRelease,
    [switch]$DryRun,
    [string]$VersionTag = "v253",
    [string]$ReleaseTitle = "PlayerEmbedAPI v5.0",
    [string]$Cs3SourcePath = "MaxSeries\build\MaxSeries.cs3",
    [string]$PluginsJsonPath = "plugins.json"
)

#==============================================================================
# CONFIGURAÇÕES
#==============================================================================
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"
$script:StartTime = Get-Date
$script:LogFile = "release_v5_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$script:Errors = @()
$script:Warnings = @()
$script:SuccessSteps = @()

#==============================================================================
# CORES PARA OUTPUT
#==============================================================================
$Colors = @{
    Reset     = "`e[0m"
    Black     = "`e[30m"
    Red       = "`e[31m"
    Green     = "`e[32m"
    Yellow    = "`e[33m"
    Blue      = "`e[34m"
    Magenta   = "`e[35m"
    Cyan      = "`e[36m"
    White     = "`e[37m"
    Bold      = "`e[1m"
    Dim       = "`e[2m"
    Underline = "`e[4m"
    BgRed     = "`e[41m"
    BgGreen   = "`e[42m"
    BgYellow  = "`e[43m"
    BgBlue    = "`e[44m"
}

#==============================================================================
# FUNÇÕES DE LOG
#==============================================================================
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoConsole
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Escreve no arquivo de log
    Add-Content -Path $script:LogFile -Value $logEntry -ErrorAction SilentlyContinue
    
    if (-not $NoConsole) {
        switch ($Level) {
            "INFO"  { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor Cyan }
            "SUCCESS" { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor Green }
            "WARNING" { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor Yellow }
            "ERROR" { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor Red }
            "STEP"  { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor Magenta }
            "DRYRUN" { Write-Host "$(Get-FormattedPrefix $Level) $Message" -ForegroundColor DarkGray }
            "HEADER" { Write-Host "$Message" -ForegroundColor White }
        }
    }
}

function Get-FormattedPrefix {
    param([string]$Level)
    
    switch ($Level) {
        "INFO"    { return "$($Colors.Cyan)[ℹ]$($Colors.Reset)" }
        "SUCCESS" { return "$($Colors.Green)[✓]$($Colors.Reset)" }
        "WARNING" { return "$($Colors.Yellow)[⚠]$($Colors.Reset)" }
        "ERROR"   { return "$($Colors.Red)[✗]$($Colors.Reset)" }
        "STEP"    { return "$($Colors.Magenta)[→]$($Colors.Reset)" }
        "DRYRUN"  { return "$($Colors.Dim)[○]$($Colors.Reset)" }
        "HEADER"  { return "" }
    }
    return "[$Level]"
}

function Write-Header {
    param([string]$Title)
    $width = 70
    $padLeft = [math]::Floor(($width - $Title.Length) / 2)
    $padRight = $width - $Title.Length - $padLeft
    
    Write-Host ""
    Write-Host "$($Colors.BgBlue)$($Colors.White)$($Colors.Bold)$('═' * $width)$($Colors.Reset)"
    Write-Host "$($Colors.BgBlue)$($Colors.White)$($Colors.Bold)$(' ' * $padLeft)$Title$(' ' * $padRight)$($Colors.Reset)"
    Write-Host "$($Colors.BgBlue)$($Colors.White)$($Colors.Bold)$('═' * $width)$($Colors.Reset)"
    Write-Host ""
    Write-Log "══════════════════════════════════════════════════════════════════════" "HEADER"
    Write-Log $Title "HEADER"
    Write-Log "══════════════════════════════════════════════════════════════════════" "HEADER"
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "$($Colors.Cyan)$($Colors.Bold)▶ $Title$($Colors.Reset)" -ForegroundColor Cyan
    Write-Log "▶ $Title" "STEP"
}

function Write-Success {
    param([string]$Message)
    Write-Log $Message "SUCCESS"
    $script:SuccessSteps += $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Log $Message "WARNING"
    $script:Warnings += $Message
}

function Write-Error {
    param([string]$Message)
    Write-Log $Message "ERROR"
    $script:Errors += $Message
}

#==============================================================================
# FUNÇÕES DE UTILIDADE
#==============================================================================
function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Test-GitRepository {
    try {
        $null = git rev-parse --git-dir 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Get-GitRemoteUrl {
    try {
        $remote = git remote get-url origin 2>$null
        return $remote
    }
    catch {
        return $null
    }
}

function Invoke-Step {
    param(
        [string]$StepName,
        [scriptblock]$ScriptBlock,
        [switch]$Critical,
        [switch]$ContinueOnError
    )
    
    Write-Log "Iniciando: $StepName" "STEP"
    
    try {
        if ($DryRun) {
            Write-Log "[DRY RUN] $StepName - Simulação" "DRYRUN"
            return $true
        }
        
        & $ScriptBlock
        
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
            throw "Comando retornou código de erro: $LASTEXITCODE"
        }
        
        Write-Success "$StepName concluído com sucesso"
        return $true
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-Error "Falha em '$StepName': $errorMsg"
        
        if ($Critical -and -not $ContinueOnError) {
            throw "Etapa crítica falhou. Abortando release."
        }
        
        return $false
    }
}

function Read-YesNo {
    param(
        [string]$Prompt,
        [bool]$Default = $false
    )
    
    $defaultChar = if ($Default) { "Y" } else { "N" }
    $response = Read-Host "$Prompt [Y/n] (default: $defaultChar)"
    
    if ([string]::IsNullOrWhiteSpace($response)) {
        return $Default
    }
    
    return $response -match '^[Yy]'
}

#==============================================================================
# ETAPA 1: VERIFICAR PRÉ-REQUISITOS
#==============================================================================
function Step-VerifyPrerequisites {
    Write-Section "ETAPA 1: Verificação de Pré-Requisitos"
    
    $checks = @()
    
    # Verificar Git
    Write-Log "Verificando Git..." "INFO"
    if (Test-Command "git") {
        $gitVersion = git --version
        Write-Success "Git encontrado: $gitVersion"
        $checks += @{ Name = "Git"; Status = "OK"; Version = $gitVersion }
    }
    else {
        Write-Error "Git não encontrado. É necessário instalar o Git."
        throw "Pré-requisito obrigatório não atendido: Git"
    }
    
    # Verificar GitHub CLI (opcional)
    Write-Log "Verificando GitHub CLI..." "INFO"
    if (Test-Command "gh") {
        $ghVersion = gh --version | Select-Object -First 1
        Write-Success "GitHub CLI encontrado: $ghVersion"
        $checks += @{ Name = "GitHub CLI"; Status = "OK"; Version = $ghVersion }
        $script:HasGhCLI = $true
    }
    else {
        Write-Warning "GitHub CLI não encontrado. Release será criado via API."
        $checks += @{ Name = "GitHub CLI"; Status = "AUSENTE"; Version = "N/A" }
        $script:HasGhCLI = $false
    }
    
    # Verificar se é repositório git
    Write-Log "Verificando repositório Git..." "INFO"
    if (Test-GitRepository) {
        $repoPath = git rev-parse --show-toplevel
        Write-Success "Repositório Git válido em: $repoPath"
        $checks += @{ Name = "Repositório Git"; Status = "OK"; Version = $repoPath }
    }
    else {
        Write-Error "Diretório atual não é um repositório Git válido"
        throw "Não é possível continuar sem um repositório Git"
    }
    
    # Verificar remote origin
    Write-Log "Verificando remote origin..." "INFO"
    $remoteUrl = Get-GitRemoteUrl
    if ($remoteUrl) {
        Write-Success "Remote origin configurado: $remoteUrl"
        $checks += @{ Name = "Remote Origin"; Status = "OK"; Version = $remoteUrl }
    }
    else {
        Write-Warning "Nenhum remote origin configurado"
        $checks += @{ Name = "Remote Origin"; Status = "AUSENTE"; Version = "N/A" }
    }
    
    # Verificar credenciais Git
    Write-Log "Verificando configuração Git..." "INFO"
    $gitUser = git config user.name
    $gitEmail = git config user.email
    if ($gitUser -and $gitEmail) {
        Write-Success "Git configurado: $gitUser <$gitEmail>"
        $checks += @{ Name = "Git Config"; Status = "OK"; Version = "$gitUser <$gitEmail>" }
    }
    else {
        Write-Warning "Configuração Git incompleta (user.name ou user.email)"
        $checks += @{ Name = "Git Config"; Status = "INCOMPLETO"; Version = "N/A" }
    }
    
    # Verificar PowerShell versão
    Write-Log "Verificando versão do PowerShell..." "INFO"
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -ge 5) {
        Write-Success "PowerShell versão: $psVersion"
        $checks += @{ Name = "PowerShell"; Status = "OK"; Version = "$psVersion" }
    }
    else {
        Write-Warning "PowerShell versão antiga: $psVersion (recomendado 5.1+)"
        $checks += @{ Name = "PowerShell"; Status = "ATENÇÃO"; Version = "$psVersion" }
    }
    
    # Resumo
    Write-Host ""
    Write-Host "$($Colors.Cyan)Resumo dos Pré-Requisitos:$($Colors.Reset)"
    $checks | ForEach-Object {
        $statusColor = switch ($_.Status) {
            "OK"        { $Colors.Green }
            "AUSENTE"   { $Colors.Yellow }
            "ATENÇÃO"   { $Colors.Yellow }
            "INCOMPLETO"{ $Colors.Yellow }
            default     { $Colors.Red }
        }
        Write-Host "  $($statusColor)[$($_.Status)]$($Colors.Reset) $($_.Name): $($_.Version)"
    }
    
    return $true
}

#==============================================================================
# ETAPA 2: VERIFICAR BUILD
#==============================================================================
function Step-VerifyBuild {
    Write-Section "ETAPA 2: Verificação do Build"
    
    $cs3Path = Join-Path $PWD $Cs3SourcePath
    
    Write-Log "Procurando arquivo: $cs3Path" "INFO"
    
    if (-not (Test-Path $cs3Path)) {
        Write-Error "Arquivo MaxSeries.cs3 não encontrado em: $cs3Path"
        Write-Log "Execute o build antes de prosseguir com o release." "INFO"
        
        if (-not (Read-YesNo -Prompt "Deseja continuar mesmo assim?" -Default $false)) {
            throw "Build não encontrado. Abortando."
        }
        
        Write-Warning "Continuando sem verificação de build"
        return $false
    }
    
    $fileInfo = Get-Item $cs3Path
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Success "Arquivo MaxSeries.cs3 encontrado"
    Write-Log "  Caminho: $($fileInfo.FullName)" "INFO"
    Write-Log "  Tamanho: $fileSizeMB MB ($($fileInfo.Length) bytes)" "INFO"
    Write-Log "  Modificado: $($fileInfo.LastWriteTime)" "INFO"
    
    # Verificar se o build é recente (menos de 24 horas)
    $hoursSinceBuild = ((Get-Date) - $fileInfo.LastWriteTime).TotalHours
    if ($hoursSinceBuild -gt 24) {
        Write-Warning "O build tem mais de 24 horas ($([math]::Round($hoursSinceBuild, 1)) horas)"
        
        if (-not (Read-YesNo -Prompt "O build é antigo. Deseja continuar?" -Default $false)) {
            throw "Build antigo. Execute um novo build antes de continuar."
        }
    }
    else {
        Write-Log "Build recente ($([math]::Round($hoursSinceBuild, 1)) horas atrás)" "SUCCESS"
    }
    
    # Verificar tamanho mínimo
    if ($fileInfo.Length -lt 1000) {
        Write-Warning "Arquivo muito pequeno ($fileSizeMB MB). Verifique se o build está correto."
    }
    
    $script:Cs3File = $fileInfo
    return $true
}

#==============================================================================
# ETAPA 3: VERIFICAR TESTES
#==============================================================================
function Step-VerifyTests {
    param([switch]$Skip)
    
    if ($Skip) {
        Write-Section "ETAPA 3: Verificação de Testes (IGNORADA)"
        Write-Warning "Verificação de testes foi ignorada via parâmetro"
        return $true
    }
    
    Write-Section "ETAPA 3: Verificação de Testes"
    
    # Procurar por relatórios de teste
    $testReportPaths = @(
        "build\reports\tests\test\index.html",
        "MaxSeries\build\reports\tests\test\index.html",
        "test-results\*.xml",
        "test-automation\results\*.json"
    )
    
    $foundReport = $false
    foreach ($path in $testReportPaths) {
        $fullPath = Join-Path $PWD $path
        $matches = Get-ChildItem -Path $fullPath -ErrorAction SilentlyContinue
        if ($matches) {
            $foundReport = $true
            Write-Success "Relatório de teste encontrado: $($matches[0].FullName)"
            
            # Verificar se há falhas
            $content = Get-Content $matches[0].FullName -Raw -ErrorAction SilentlyContinue
            if ($content -match "failures=[\"']?([0-9]+)[\"']?" -or 
                $content -match "failed[^>]*>([0-9]+)<" -or
                $content -match '"failed":\s*(\d+)') {
                $failures = $matches[1]
                if ([int]$failures -gt 0) {
                    Write-Error "Testes falharam: $failures falha(s) detectada(s)"
                    if (-not (Read-YesNo -Prompt "Testes falharam. Deseja continuar mesmo assim?" -Default $false)) {
                        throw "Testes falharam. Abortando release."
                    }
                    Write-Warning "Continuando apesar das falhas nos testes"
                }
                else {
                    Write-Success "Todos os testes passaram"
                }
            }
            break
        }
    }
    
    if (-not $foundReport) {
        Write-Warning "Nenhum relatório de teste encontrado"
        
        # Verificar se existe diretório de testes
        if (Test-Path "test-automation") {
            Write-Log "Diretório de testes encontrado. Verificando manualmente..." "INFO"
            
            if (Read-YesNo -Prompt "Não foi possível verificar os testes automaticamente. Os testes passaram?" -Default $false) {
                Write-Success "Usuário confirmou que testes passaram"
            }
            else {
                if (-not (Read-YesNo -Prompt "Deseja continuar mesmo assim?" -Default $false)) {
                    throw "Verificação de testes não concluída. Abortando."
                }
                Write-Warning "Continuando sem confirmação de testes"
            }
        }
        else {
            Write-Warning "Nenhum sistema de testes detectado"
        }
    }
    
    return $true
}

#==============================================================================
# ETAPA 4: CRIAR TAG GIT
#==============================================================================
function Step-CreateGitTag {
    Write-Section "ETAPA 4: Criação da Tag Git $VersionTag"
    
    # Verificar se a tag já existe
    $existingTag = git tag -l $VersionTag 2>$null
    if ($existingTag) {
        Write-Warning "Tag $VersionTag já existe"
        
        if (-not (Read-YesNo -Prompt "Deseja recriar a tag? (isso vai deletar a tag existente)" -Default $false)) {
            throw "Tag já existe. Abortando para evitar conflitos."
        }
        
        Invoke-Step -StepName "Deletar tag local existente" -ScriptBlock {
            git tag -d $VersionTag
        } -Critical
        
        Invoke-Step -StepName "Deletar tag remota existente" -ScriptBlock {
            git push origin --delete $VersionTag 2>$null || $true
        }
    }
    
    # Criar anotação para a tag
    $tagMessage = @"
Release $VersionTag - $ReleaseTitle

PlayerEmbedAPI v5.0
- Sistema de streaming aprimorado
- Suporte a múltiplos players
- Otimizações de performance
- Correções de bugs

Gerado automaticamente em: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
    
    Invoke-Step -StepName "Criar tag Git $VersionTag" -ScriptBlock {
        git tag -a $VersionTag -m $tagMessage
    } -Critical
    
    Write-Log "Tag criada com sucesso" "SUCCESS"
    Write-Log "Mensagem da tag:" "INFO"
    $tagMessage -split "`n" | ForEach-Object { Write-Log "  $_" "INFO" }
    
    return $true
}

#==============================================================================
# ETAPA 5: FAZER COMMIT DAS ALTERAÇÕES
#==============================================================================
function Step-CommitChanges {
    Write-Section "ETAPA 5: Commit das Alterações"
    
    # Verificar status do git
    $status = git status --porcelain
    
    if (-not $status) {
        Write-Log "Nenhuma alteração pendente para commit" "INFO"
        return $true
    }
    
    Write-Log "Alterações detectadas:" "INFO"
    $status -split "`n" | ForEach-Object { Write-Log "  $_" "INFO" }
    
    # Adicionar arquivos modificados
    Invoke-Step -StepName "Adicionar arquivos ao stage" -ScriptBlock {
        git add -A
    } -Critical
    
    # Criar commit
    $commitMessage = @"
chore(release): prepare $VersionTag - $ReleaseTitle

- Atualiza plugins.json
- Prepara release do PlayerEmbedAPI v5.0
- Inclui build atualizado do MaxSeries.cs3

[skip ci]
"@
    
    Invoke-Step -StepName "Criar commit" -ScriptBlock {
        git commit -m $commitMessage
    } -Critical
    
    Write-Success "Commit criado com sucesso"
    
    # Mostrar informações do commit
    $commitHash = git rev-parse --short HEAD
    $commitInfo = git log -1 --oneline
    Write-Log "Commit: $commitInfo" "INFO"
    
    return $true
}

#==============================================================================
# ETAPA 6: PUSH PARA GITHUB
#==============================================================================
function Step-PushToGitHub {
    Write-Section "ETAPA 6: Push para GitHub"
    
    # Verificar se há remote configurado
    $remotes = git remote
    if (-not $remotes) {
        Write-Error "Nenhum remote configurado"
        throw "Não é possível fazer push sem um remote configurado"
    }
    
    Write-Log "Remotes disponíveis: $remotes" "INFO"
    
    # Push da branch atual
    $currentBranch = git branch --show-current
    Write-Log "Branch atual: $currentBranch" "INFO"
    
    Invoke-Step -StepName "Push da branch $currentBranch" -ScriptBlock {
        git push origin $currentBranch
    } -Critical
    
    Write-Success "Branch $currentBranch enviada para origin"
    
    # Push das tags
    Invoke-Step -StepName "Push das tags" -ScriptBlock {
        git push origin $VersionTag
    } -Critical
    
    Write-Success "Tag $VersionTag enviada para origin"
    
    return $true
}

#==============================================================================
# ETAPA 7: CRIAR RELEASE NO GITHUB
#==============================================================================
function Step-CreateGitHubRelease {
    param([switch]$Skip)
    
    if ($Skip) {
        Write-Section "ETAPA 7: Criação de Release no GitHub (IGNORADA)"
        Write-Warning "Criação de release ignorada via parâmetro"
        return $true
    }
    
    Write-Section "ETAPA 7: Criação de Release no GitHub"
    
    # Verificar se já existe release com esta tag
    if ($script:HasGhCLI) {
        $existingRelease = gh release view $VersionTag 2>$null
        if ($LASTEXITCODE -eq 0 -and $existingRelease) {
            Write-Warning "Release $VersionTag já existe no GitHub"
            
            if (-not (Read-YesNo -Prompt "Deseja recriar a release?" -Default $false)) {
                Write-Warning "Usando release existente"
                return $true
            }
            
            Invoke-Step -StepName "Deletar release existente" -ScriptBlock {
                gh release delete $VersionTag --yes
            }
        }
    }
    
    # Corpo do release
    $releaseNotes = @"
# $ReleaseTitle

## 🚀 Novidades

- **PlayerEmbedAPI v5.0**: Sistema completo de streaming
- Suporte aprimorado a múltiplos players de vídeo
- Otimizações de performance
- Correções de bugs reportados

## 📦 Arquivos

- `MaxSeries.cs3` - Plugin principal (formato Cloudstream)

## 🔧 Instalação

1. Baixe o arquivo `MaxSeries.cs3`
2. Instale no Cloudstream usando a opção "Instalar de arquivo"

## 📋 Notas Técnicas

- Compatível com Cloudstream v3.0+
- Requer Android 5.0+
- Tamanho: $([math]::Round($script:Cs3File.Length / 1KB, 2)) KB

---
*Release gerado automaticamente em $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
"@
    
    # Salvar release notes em arquivo temporário
    $notesFile = "release_notes_$VersionTag.md"
    $releaseNotes | Out-File -FilePath $notesFile -Encoding UTF8
    
    if ($script:HasGhCLI) {
        # Usar gh CLI
        Invoke-Step -StepName "Criar release com gh CLI" -ScriptBlock {
            gh release create $VersionTag `
                --title "$ReleaseTitle" `
                --notes-file $notesFile `
                --target $(git branch --show-current)
        } -Critical
        
        Write-Success "Release criada com sucesso via gh CLI"
    }
    else {
        # Usar API diretamente
        Write-Log "Criando release via API GitHub..." "INFO"
        
        # Obter token de forma segura
        $token = $env:GITHUB_TOKEN
        if (-not $token) {
            Write-Warning "GITHUB_TOKEN não configurado"
            Write-Log "Tentando usar gh auth token..." "INFO"
            $token = gh auth token 2>$null
        }
        
        if (-not $token) {
            Write-Error "Token de autenticação não encontrado"
            throw "Configure GITHUB_TOKEN ou faça login no gh CLI"
        }
        
        # Obter owner e repo do remote
        $remoteUrl = git remote get-url origin
        if ($remoteUrl -match "github\.com[:/]([^/]+)/([^/\.]+)") {
            $owner = $matches[1]
            $repo = $matches[2]
        }
        else {
            throw "Não foi possível extrair owner/repo do remote: $remoteUrl"
        }
        
        $apiUrl = "https://api.github.com/repos/$owner/$repo/releases"
        
        $body = @{
            tag_name = $VersionTag
            name = $ReleaseTitle
            body = $releaseNotes
            draft = $false
            prerelease = $false
            target_commitish = git rev-parse HEAD
        } | ConvertTo-Json -Depth 10
        
        try {
            $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Headers @{
                "Authorization" = "token $token"
                "Accept" = "application/vnd.github.v3+json"
                "Content-Type" = "application/json"
            } -Body $body
            
            $script:ReleaseUploadUrl = $response.upload_url -replace "{\\?name,label}", ""
            Write-Success "Release criada via API: $($response.html_url)"
        }
        catch {
            throw "Falha ao criar release via API: $($_.Exception.Message)"
        }
    }
    
    # Limpar arquivo temporário
    Remove-Item $notesFile -ErrorAction SilentlyContinue
    
    return $true
}

#==============================================================================
# ETAPA 8: UPLOAD DO ARQUIVO .CS3
#==============================================================================
function Step-UploadAsset {
    Write-Section "ETAPA 8: Upload do Arquivo .cs3"
    
    $cs3Path = $script:Cs3File.FullName
    $fileName = $script:Cs3File.Name
    
    if ($script:HasGhCLI) {
        # Usar gh CLI para upload
        Invoke-Step -StepName "Upload com gh CLI" -ScriptBlock {
            gh release upload $VersionTag "$cs3Path" --clobber
        } -Critical
        
        Write-Success "Arquivo $fileName enviado com sucesso"
    }
    else {
        # Upload via API
        Write-Log "Fazendo upload via API..." "INFO"
        
        $token = $env:GITHUB_TOKEN
        if (-not $token) {
            $token = gh auth token 2>$null
        }
        
        if (-not $script:ReleaseUploadUrl) {
            # Obter URL de upload da release existente
            $remoteUrl = git remote get-url origin
            $remoteUrl -match "github\.com[:/]([^/]+)/([^/\.]+)" | Out-Null
            $owner = $matches[1]
            $repo = $matches[2]
            
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/releases/tags/$VersionTag" -Headers @{
                "Authorization" = "token $token"
                "Accept" = "application/vnd.github.v3+json"
            }
            $script:ReleaseUploadUrl = $release.upload_url -replace "{\\?name,label}", ""
        }
        
        $uploadUrl = "$($script:ReleaseUploadUrl)?name=$fileName"
        
        $fileBytes = [System.IO.File]::ReadAllBytes($cs3Path)
        
        try {
            $response = Invoke-RestMethod -Uri $uploadUrl -Method POST -Headers @{
                "Authorization" = "token $token"
                "Accept" = "application/vnd.github.v3+json"
                "Content-Type" = "application/octet-stream"
            } -Body $fileBytes
            
            Write-Success "Arquivo enviado: $($response.browser_download_url)"
        }
        catch {
            throw "Falha no upload: $($_.Exception.Message)"
        }
    }
    
    # Verificar upload
    Write-Log "Verificando upload..." "INFO"
    $releaseInfo = gh release view $VersionTag --json assets 2>$null | ConvertFrom-Json
    $asset = $releaseInfo.assets | Where-Object { $_.name -eq $fileName }
    if ($asset) {
        Write-Success "Asset confirmado: $($asset.url)"
        Write-Log "  Download URL: $($asset.url)" "INFO"
        Write-Log "  Tamanho: $([math]::Round($asset.size / 1KB, 2)) KB" "INFO"
    }
    
    return $true
}

#==============================================================================
# ETAPA 9: ATUALIZAR PLUGINS.JSON
#==============================================================================
function Step-UpdatePluginsJson {
    Write-Section "ETAPA 9: Atualização do plugins.json"
    
    $pluginsPath = Join-Path $PWD $PluginsJsonPath
    
    if (-not (Test-Path $pluginsPath)) {
        Write-Warning "Arquivo plugins.json não encontrado em: $pluginsPath"
        
        # Tentar em CloudstreamRepo
        $altPath = Join-Path $PWD "CloudstreamRepo\plugins.json"
        if (Test-Path $altPath) {
            Write-Log "Usando arquivo alternativo: $altPath" "INFO"
            $pluginsPath = $altPath
        }
        else {
            Write-Warning "Nenhum plugins.json encontrado. Pulando esta etapa."
            return $false
        }
    }
    
    Write-Log "Lendo $pluginsPath..." "INFO"
    
    try {
        $pluginsContent = Get-Content $pluginsPath -Raw | ConvertFrom-Json
        
        # Backup do arquivo original
        $backupPath = "$pluginsPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $pluginsPath $backupPath
        Write-Log "Backup criado: $backupPath" "INFO"
        
        # Obter URL do release
        $releaseUrl = ""
        if ($script:HasGhCLI) {
            $releaseInfo = gh release view $VersionTag --json url 2>$null | ConvertFrom-Json
            $releaseUrl = $releaseInfo.url
        }
        
        # Atualizar informações do plugin (estrutura típica do Cloudstream)
        $updated = $false
        
        if ($pluginsContent.plugins) {
            foreach ($plugin in $pluginsContent.plugins) {
                if ($plugin.name -like "*MaxSeries*" -or $plugin.id -like "*maxseries*") {
                    Write-Log "Atualizando plugin: $($plugin.name)" "INFO"
                    
                    $plugin.version = $VersionTag -replace "v", ""
                    $plugin.versionCode = 253
                    $plugin.url = "https://github.com/$(git remote get-url origin | Select-String -Pattern 'github\.com[:/]([^/]+)/([^/\.]+)' | ForEach-Object { $_.Matches[0].Groups[1].Value + '/' + $_.Matches[0].Groups[2].Value })"
                    
                    if ($releaseUrl) {
                        $plugin.releaseUrl = $releaseUrl
                    }
                    
                    $updated = $true
                    Write-Success "Plugin atualizado: $($plugin.name) v$($plugin.version)"
                }
            }
        }
        
        if (-not $updated) {
            Write-Warning "Nenhum plugin MaxSeries encontrado em plugins.json"
            Write-Log "Adicionando novo entry..." "INFO"
            
            # Criar novo entry
            $newPlugin = @{
                name = "MaxSeries"
                id = "com.maxseries"
                version = $VersionTag -replace "v", ""
                versionCode = 253
                description = "PlayerEmbedAPI v5.0 - Sistema de streaming"
                url = "https://raw.githubusercontent.com/$(git remote get-url origin | Select-String -Pattern 'github\.com[:/]([^/]+)/([^/\.]+)' | ForEach-Object { $_.Matches[0].Groups[1].Value + '/' + $_.Matches[0].Groups[2].Value })/refs/tags/$VersionTag/MaxSeries.cs3"
                iconUrl = ""
                language = "pt"
            }
            
            if (-not $pluginsContent.plugins) {
                $pluginsContent | Add-Member -NotePropertyName "plugins" -NotePropertyValue @() -Force
            }
            
            $pluginsContent.plugins += $newPlugin
            $updated = $true
            Write-Success "Novo plugin adicionado"
        }
        
        # Atualizar timestamp
        $pluginsContent.lastUpdated = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        
        # Salvar arquivo atualizado
        $pluginsContent | ConvertTo-Json -Depth 10 | Out-File $pluginsPath -Encoding UTF8
        Write-Success "plugins.json atualizado: $pluginsPath"
        
        # Commit da atualização
        if ($updated) {
            Invoke-Step -StepName "Commit da atualização do plugins.json" -ScriptBlock {
                git add $pluginsPath
                git commit -m "chore: atualiza plugins.json para $VersionTag" --no-verify
            }
            
            Invoke-Step -StepName "Push da atualização" -ScriptBlock {
                git push origin $(git branch --show-current)
            }
        }
        
        return $true
    }
    catch {
        Write-Error "Falha ao atualizar plugins.json: $($_.Exception.Message)"
        Write-Log "Restaurando backup..." "INFO"
        Copy-Item $backupPath $pluginsPath -Force
        return $false
    }
}

#==============================================================================
# ETAPA 10: GERAR RELATÓRIO FINAL
#==============================================================================
function Step-GenerateReport {
    Write-Section "ETAPA 10: Relatório Final"
    
    $endTime = Get-Date
    $duration = $endTime - $script:StartTime
    
    # URL da release
    $releaseUrl = ""
    if ($script:HasGhCLI) {
        $releaseInfo = gh release view $VersionTag --json url,htmlUrl 2>$null | ConvertFrom-Json
        if ($releaseInfo) {
            $releaseUrl = $releaseInfo.htmlUrl
        }
    }
    
    $report = @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                     RELATÓRIO DE RELEASE - PlayerEmbedAPI v5.0               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 INFORMAÇÕES DO RELEASE
──────────────────────────────────────────────────────────────────────────────
  Versão:        $VersionTag
  Título:        $ReleaseTitle
  Data/Hora:     $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  Duração:       $($duration.ToString("hh\:mm\:ss"))
  Branch:        $(git branch --show-current)
  Commit:        $(git rev-parse --short HEAD)
  Release URL:   $releaseUrl

✅ ETAPAS CONCLUÍDAS COM SUCESSO ($($script:SuccessSteps.Count))
──────────────────────────────────────────────────────────────────────────────
"@
    
    if ($script:SuccessSteps.Count -gt 0) {
        $i = 1
        foreach ($step in $script:SuccessSteps) {
            $report += "`n  $i. $step"
            $i++
        }
    }
    else {
        $report += "`n  (nenhuma)"
    }
    
    $report += @"

⚠️  AVISOS ($($script:Warnings.Count))
──────────────────────────────────────────────────────────────────────────────
"@
    
    if ($script:Warnings.Count -gt 0) {
        foreach ($warning in $script:Warnings) {
            $report += "`n  • $warning"
        }
    }
    else {
        $report += "`n  (nenhum)"
    }
    
    $report += @"

❌ ERROS ($($script:Errors.Count))
──────────────────────────────────────────────────────────────────────────────
"@
    
    if ($script:Errors.Count -gt 0) {
        foreach ($error in $script:Errors) {
            $report += "`n  • $error"
        }
    }
    else {
        $report += "`n  (nenhum)"
    }
    
    $report += @"

📁 ARQUIVOS
──────────────────────────────────────────────────────────────────────────────
  Arquivo .cs3:    $($script:Cs3File.FullName)
  Tamanho:         $([math]::Round($script:Cs3File.Length / 1KB, 2)) KB
  plugins.json:    $(Join-Path $PWD $PluginsJsonPath)
  Log:             $(Join-Path $PWD $script:LogFile)

📝 PRÓXIMOS PASSOS
──────────────────────────────────────────────────────────────────────────────
  1. Verifique a release em: $releaseUrl
  2. Teste o download do arquivo .cs3
  3. Verifique se o plugins.json está correto
  4. Comunique a equipe sobre o novo release

──────────────────────────────────────────────────────────────────────────────
                          Release concluído em $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
──────────────────────────────────────────────────────────────────────────────
"@
    
    # Salvar relatório
    $reportFile = "release_report_$VersionTag.txt"
    $report | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Host $report
    Write-Log "Relatório salvo em: $reportFile" "SUCCESS"
    
    return $true
}

#==============================================================================
# FUNÇÃO PRINCIPAL
#==============================================================================
function Main {
    param(
        [switch]$SkipTests,
        [switch]$SkipGitHubRelease,
        [switch]$DryRun
    )
    
    Clear-Host
    
    Write-Header "PlayerEmbedAPI v5.0 - Release Automation"
    
    Write-Host ""
    Write-Host "$($Colors.Yellow)Configuração:$($Colors.Reset)"
    Write-Host "  Versão Tag:     $VersionTag"
    Write-Host "  Título:         $ReleaseTitle"
    Write-Host "  Caminho .cs3:   $Cs3SourcePath"
    Write-Host "  plugins.json:   $PluginsJsonPath"
    Write-Host "  Diretório:      $PWD"
    Write-Host "  Dry Run:        $DryRun"
    Write-Host ""
    
    if ($DryRun) {
        Write-Host "$($Colors.BgYellow)$($Colors.Black) MODO SIMULAÇÃO (DRY RUN) - Nenhuma alteração será feita $($Colors.Reset)"
        Write-Host ""
    }
    
    # Confirmação
    if (-not $DryRun) {
        $confirm = Read-YesNo -Prompt "Deseja iniciar o processo de release?" -Default $false
        if (-not $confirm) {
            Write-Log "Release cancelado pelo usuário" "WARNING"
            exit 0
        }
    }
    
    # Mudar para o diretório do projeto
    $projectDir = "C:\Users\KYTHOURS\Desktop\brcloudstream"
    if (Test-Path $projectDir) {
        Set-Location $projectDir
        Write-Log "Diretório de trabalho: $PWD" "INFO"
    }
    else {
        throw "Diretório do projeto não encontrado: $projectDir"
    }
    
    try {
        # ETAPA 1: Pré-requisitos
        Step-VerifyPrerequisites
        
        # ETAPA 2: Verificar Build
        Step-VerifyBuild
        
        # ETAPA 3: Verificar Testes
        Step-VerifyTests -Skip:$SkipTests
        
        # ETAPA 4: Criar Tag
        Step-CreateGitTag
        
        # ETAPA 5: Commit
        Step-CommitChanges
        
        # ETAPA 6: Push
        Step-PushToGitHub
        
        # ETAPA 7: Criar Release
        Step-CreateGitHubRelease -Skip:$SkipGitHubRelease
        
        # ETAPA 8: Upload Asset
        Step-UploadAsset
        
        # ETAPA 9: Atualizar plugins.json
        Step-UpdatePluginsJson
        
        # ETAPA 10: Relatório
        Step-GenerateReport
        
        Write-Host ""
        Write-Host "$($Colors.BgGreen)$($Colors.Black)$($Colors.Bold) ✓ RELEASE CONCLUÍDO COM SUCESSO! $($Colors.Reset)"
        Write-Host ""
        
        if ($script:Errors.Count -eq 0) {
            exit 0
        }
        else {
            Write-Warning "Release concluído com $($script:Errors.Count) erro(s)"
            exit 1
        }
    }
    catch {
        Write-Host ""
        Write-Host "$($Colors.BgRed)$($Colors.White)$($Colors.Bold) ✗ FALHA NO PROCESSO DE RELEASE $($Colors.Reset)"
        Write-Host ""
        Write-Error "Erro fatal: $($_.Exception.Message)"
        Write-Log "Stack Trace: $($_.ScriptStackTrace)" "ERROR" -NoConsole
        
        exit 1
    }
}

#==============================================================================
# EXECUÇÃO
#==============================================================================
Main -SkipTests:$SkipTests -SkipGitHubRelease:$SkipGitHubRelease -DryRun:$DryRun
