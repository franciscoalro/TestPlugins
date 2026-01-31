#requires -Version 5.1

<#
.SYNOPSIS
    Faz upload do MaxSeries.cs3 para o GitHub Releases (v256)
.DESCRIPTION
    Cria a release v256 se não existir e faz upload do arquivo CS3.
    Verifica se existe um GitHub token configurado (GH_TOKEN ou GITHUB_TOKEN).
.EXAMPLE
    .\upload-to-github-releases.ps1
    .\upload-to-github-releases.ps1 -Token "ghp_xxxxxxxx"
    .\upload-to-github-releases.ps1 -FilePath "C:\outro\caminho\MaxSeries.cs3"
#>
[CmdletBinding()]
param(
    [Parameter(HelpMessage = "GitHub Personal Access Token. Usa GH_TOKEN ou GITHUB_TOKEN por padrão.")]
    [string]$Token = $env:GH_TOKEN,
    
    [Parameter(HelpMessage = "Caminho completo para o arquivo MaxSeries.cs3")]
    [string]$FilePath = "C:\Users\KYTHOURS\Desktop\brcloudstream\releases\MaxSeries.cs3",
    
    [Parameter(HelpMessage = "Owner do repositório no GitHub")]
    [string]$Owner = "franciscoalro",
    
    [Parameter(HelpMessage = "Nome do repositório no GitHub")]
    [string]$Repo = "TestPlugins",
    
    [Parameter(HelpMessage = "Tag da release (ex: v256)")]
    [string]$TagName = "v256",
    
    [Parameter(HelpMessage = "Nome da release")]
    [string]$ReleaseName = "MaxSeries v256",
    
    [Parameter(HelpMessage = "Descrição da release em Markdown")]
    [string]$ReleaseBody = @"
## MaxSeries v256 - PlayerEmbedAPI V8+V7 Fixes

### 🚀 Melhorias
- PlayerEmbedAPI V8: 12 padrões de URL (Pure HTTP)
- PlayerEmbedAPI V7: Memory leak corrigido, cleanup thread-safe
- Timeout aumentado: 15s → 25s
- Max attempts: 3 → 5

### 📝 Notas
- Build: Android SDK D:\Android
- Tamanho: ~638 KB
- Compatibilidade: CloudStream 3.x+
"@
)

#==============================================================================
# Configuração de cores para saída
#==============================================================================
$Colors = @{
    Success = "Green"
    Error   = "Red"
    Warning = "Yellow"
    Info    = "Cyan"
    Step    = "Magenta"
}

#==============================================================================
# Funções Auxiliares
#==============================================================================

function Write-Step {
    param([string]$Message)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host "▶ $Message" -ForegroundColor $Colors.Step
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor $Colors.Success
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor $Colors.Error
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor $Colors.Info
}

function Show-Header {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║           GitHub Releases Uploader - MaxSeries.cs3             ║" -ForegroundColor Cyan
    Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║  Owner:  franciscoalro                                         ║" -ForegroundColor White
    Write-Host "║  Repo:   TestPlugins                                           ║" -ForegroundColor White
    Write-Host "║  Tag:    v256                                                  ║" -ForegroundColor White
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

#==============================================================================
# Verificação 1: Token do GitHub
#==============================================================================
function Test-GitHubToken {
    Write-Step "Verificando GitHub Token..."
    
    # Verifica se o token foi passado via parâmetro ou env
    if ([string]::IsNullOrWhiteSpace($Token)) {
        # Tenta usar GITHUB_TOKEN como fallback
        $Token = $env:GITHUB_TOKEN
    }
    
    if ([string]::IsNullOrWhiteSpace($Token)) {
        Write-ErrorMsg "GitHub Token não encontrado!"
        Write-Host ""
        Write-Host "Para usar este script, configure o token de uma das seguintes formas:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  1. Variável de ambiente (recomendado):" -ForegroundColor White
        Write-Host "     `$env:GH_TOKEN = 'ghp_seu_token_aqui'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Parâmetro direto:" -ForegroundColor White
        Write-Host "     .\upload-to-github-releases.ps1 -Token 'ghp_seu_token_aqui'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Como criar um token:" -ForegroundColor Yellow
        Write-Host "  → https://github.com/settings/tokens" -ForegroundColor Cyan
        Write-Host "  → Scopes necessários: 'repo' (para repositórios privados)" -ForegroundColor Gray
        Write-Host ""
        return $false
    }
    
    # Verifica formato do token
    if (-not ($Token -match '^ghp_[a-zA-Z0-9]{36}$' -or 
              $Token -match '^github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}$' -or
              $Token -match '^[a-f0-9]{40}$')) {
        Write-WarningMsg "Formato do token parece invalido. Token deve comecar com 'ghp_' ou 'github_pat_'"
    }
    
    # Mascara o token para exibição
    $maskedToken = if ($Token.Length -gt 8) { 
        $Token.Substring(0, 4) + "****" + $Token.Substring($Token.Length - 4) 
    } else { 
        "****" 
    }
    
    Write-Success "Token encontrado: $maskedToken"
    return $true
}

#==============================================================================
# Verificação 2: Arquivo CS3
#==============================================================================
function Test-CS3File {
    Write-Step "Verificando arquivo MaxSeries.cs3..."
    
    # Resolve o caminho absoluto
    $resolvedPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($FilePath)
    
    if (-not (Test-Path -Path $resolvedPath -PathType Leaf)) {
        Write-ErrorMsg "Arquivo não encontrado!"
        Write-Info "Caminho esperado: $resolvedPath"
        
        # Sugere caminhos alternativos
        $possiblePaths = @(
            "C:\Users\$env:USERNAME\Desktop\brcloudstream\releases\MaxSeries.cs3",
            "C:\Users\$env:USERNAME\Downloads\MaxSeries.cs3",
            ".\releases\MaxSeries.cs3",
            ".\MaxSeries.cs3"
        )
        
        Write-Host ""
        Write-Host "Possíveis locais (verificados):" -ForegroundColor Yellow
        foreach ($path in $possiblePaths) {
            $exists = Test-Path -Path $path -PathType Leaf
            $status = if ($exists) { "[ENCONTRADO]" } else { "[não existe]" }
            $color = if ($exists) { "Green" } else { "Gray" }
            Write-Host "  $status $path" -ForegroundColor $color
        }
        
        return $null
    }
    
    $fileInfo = Get-Item -Path $resolvedPath
    $fileSizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Success "Arquivo encontrado!"
    Write-Info "Caminho: $($fileInfo.FullName)"
    Write-Info "Tamanho: $fileSizeKB KB (${fileSizeMB} MB)"
    Write-Info "Modificado: $($fileInfo.LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss'))"
    
    return $fileInfo.FullName
}

#==============================================================================
# Verificação 3: Testar conectividade com API do GitHub
#==============================================================================
function Test-GitHubApi {
    Write-Step "Testando conectividade com API do GitHub..."
    
    try {
        $headers = @{
            "Authorization" = "Bearer $Token"
            "Accept"        = "application/vnd.github+json"
            "X-GitHub-Api-Version" = "2022-11-28"
        }
        
        $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method GET -ErrorAction Stop
        
        Write-Success "Conectado como: $($response.login)"
        Write-Info "Rate limit disponível"
        
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response?.StatusCode.value__
        
        switch ($statusCode) {
            401 {
                Write-ErrorMsg "Token invalido ou expirado (401 Unauthorized)"
                Write-Info "Verifique se o token esta correto e nao expirou"
            }
            403 {
                Write-ErrorMsg "Acesso negado (403)"
                Write-Info "Verifique se o token tem permissao 'repo'"
            }
            default {
                Write-ErrorMsg "Erro ao conectar: $($_.Exception.Message)"
            }
        }
        
        return $false
    }
}

#==============================================================================
# Verificar/Criar Release
#==============================================================================
function Get-OrCreateRelease {
    param([string]$Token)
    
    Write-Step "Verificando release '$TagName'..."
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept"        = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    
    $apiUrl = "https://api.github.com/repos/$Owner/$Repo/releases/tags/$TagName"
    
    try {
        # Tenta obter a release existente
        $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method GET -ErrorAction Stop
        
        Write-Success "Release '$TagName' já existe!"
        Write-Info "ID: $($release.id)"
        Write-Info "URL: $($release.html_url)"
        
        return $release
    }
    catch {
        $statusCode = $_.Exception.Response?.StatusCode.value__
        
        if ($statusCode -eq 404) {
            Write-WarningMsg "Release '$TagName' não encontrada. Criando..."
            
            return New-GitHubRelease -Token $Token
        }
        else {
            Write-ErrorMsg "Erro ao verificar release: $($_.Exception.Message)"
            return $null
        }
    }
}

function New-GitHubRelease {
    param([string]$Token)
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept"        = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
        "Content-Type"  = "application/json"
    }
    
    $body = @{
        tag_name         = $TagName
        name             = $ReleaseName
        body             = $ReleaseBody
        draft            = $false
        prerelease       = $false
        generate_release_notes = $false
    } | ConvertTo-Json -Depth 10
    
    $apiUrl = "https://api.github.com/repos/$Owner/$Repo/releases"
    
    try {
        Write-Info "Criando release '$TagName'..."
        
        $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method POST -Body $body -ErrorAction Stop
        
        Write-Success "Release criada com sucesso!"
        Write-Info "ID: $($release.id)"
        Write-Info "URL: $($release.html_url)"
        
        return $release
    }
    catch {
        $statusCode = $_.Exception.Response?.StatusCode.value__
        $errorMessage = $_.Exception.Message
        
        # Tenta extrair mensagem de erro detalhada
        try {
            $errorBody = $_.ErrorDetails?.Message
            if ($errorBody) {
                $errorJson = $errorBody | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($errorJson.message) {
                    $errorMessage = $errorJson.message
                }
            }
        }
        catch { }
        
        Write-ErrorMsg "Falha ao criar release - Codigo: $statusCode"
        Write-Info "Erro: $errorMessage"
        
        return $null
    }
}

#==============================================================================
# Upload do Asset
#==============================================================================
function Upload-ReleaseAsset {
    param(
        [string]$Token,
        [PSCustomObject]$Release,
        [string]$FilePath
    )
    
    Write-Step "Fazendo upload de MaxSeries.cs3..."
    
    $fileName = [System.IO.Path]::GetFileName($FilePath)
    $fileInfo = Get-Item -Path $FilePath
    $fileSize = $fileInfo.Length
    
    Write-Info "Arquivo: $fileName"
    Write-Info "Tamanho: $([math]::Round($fileSize / 1KB, 2)) KB"
    
    # Prepara os headers para upload
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept"        = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
        "Content-Type"  = "application/octet-stream"
    }
    
    # URL de upload
    $uploadUrl = "https://uploads.github.com/repos/$Owner/$Repo/releases/$($Release.id)/assets?name=$fileName"
    
    try {
        # Lê o arquivo como bytes
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        
        Write-Info "Enviando arquivo..."
        
        # Faz o upload
        $asset = Invoke-RestMethod -Uri $uploadUrl -Headers $headers -Method POST -Body $fileBytes -ErrorAction Stop
        
        Write-Success "Upload concluído com sucesso!"
        Write-Info "Asset ID: $($asset.id)"
        Write-Info "Download URL: $($asset.browser_download_url)"
        
        return $asset
    }
    catch {
        $statusCode = $_.Exception.Response?.StatusCode.value__
        $errorMessage = $_.Exception.Message
        
        # Tenta extrair mensagem de erro detalhada
        try {
            $errorBody = $_.ErrorDetails?.Message
            if ($errorBody) {
                $errorJson = $errorBody | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($errorJson.message) {
                    $errorMessage = $errorJson.message
                }
            }
        }
        catch { }
        
        Write-ErrorMsg "Falha no upload - Codigo: $statusCode"
        Write-Info "Erro: $errorMessage"
        
        # Dicas específicas por código de erro
        switch ($statusCode) {
            422 {
                Write-WarningMsg "Arquivo pode já existir na release"
                Write-Info "Verifique em: $($Release.html_url)"
            }
            413 {
                Write-WarningMsg "Arquivo muito grande"
            }
        }
        
        return $null
    }
}

#==============================================================================
# Verificar asset existente
#==============================================================================
function Test-AssetExists {
    param(
        [PSCustomObject]$Release,
        [string]$FileName
    )
    
    $existingAsset = $Release.assets | Where-Object { $_.name -eq $FileName }
    
    if ($existingAsset) {
        Write-WarningMsg "Asset '$FileName' já existe na release!"
        Write-Info "Asset ID: $($existingAsset.id)"
        Write-Info "Criado em: $($existingAsset.created_at)"
        Write-Info "Download: $($existingAsset.browser_download_url)"
        
        return $true
    }
    
    return $false
}

#==============================================================================
# Função Principal
#==============================================================================
function Main {
    Show-Header
    
    Write-Host "Parâmetros configurados:" -ForegroundColor White
    Write-Info "Owner: $Owner"
    Write-Info "Repo: $Repo"
    Write-Info "Tag: $TagName"
    Write-Info "Arquivo: $FilePath"
    Write-Host ""
    
    # Verificação 1: Token
    if (-not (Test-GitHubToken)) {
        exit 1
    }
    
    # Verificação 2: Arquivo
    $resolvedFilePath = Test-CS3File
    if (-not $resolvedFilePath) {
        exit 1
    }
    
    # Verificação 3: API
    if (-not (Test-GitHubApi)) {
        exit 1
    }
    
    # Verificar/Criar Release
    $release = Get-OrCreateRelease -Token $Token
    if (-not $release) {
        exit 1
    }
    
    # Verificar se asset já existe
    $fileName = [System.IO.Path]::GetFileName($resolvedFilePath)
    if (Test-AssetExists -Release $release -FileName $fileName) {
        Write-Host ""
        Write-Host "Deseja sobrescrever o asset existente? (S/N): " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        
        if ($response -ne 'S' -and $response -ne 's') {
            Write-Info "Upload cancelado pelo usuário."
            exit 0
        }
        
        # Deleta o asset existente (opcional, GitHub sobrescreve automaticamente)
        Write-WarningMsg "Continuando upload (GitHub pode rejeitar se já existir)..."
    }
    
    # Upload do asset
    $asset = Upload-ReleaseAsset -Token $Token -Release $release -FilePath $resolvedFilePath
    if (-not $asset) {
        exit 1
    }
    
    # Resumo final
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                      ✅ UPLOAD CONCLUÍDO                       ║" -ForegroundColor Green
    Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║  Release:  $($Release.html_url.PadRight(47)) ║" -ForegroundColor White
    Write-Host "║  Download: $($asset.browser_download_url.PadRight(47)) ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Success "MaxSeries.cs3 foi enviado com sucesso para v256!"
    Write-Host ""
}

#==============================================================================
# Execução
#==============================================================================
Main
