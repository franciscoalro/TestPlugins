#requires -Version 5.1
<#
.SYNOPSIS
    Script de release para o PlayerEmbedAPI v5.0 no GitHub
.DESCRIPTION
    Realiza commit e push da versão v5.0 do PlayerEmbedAPI com todas as melhorias
    e arquivos atualizados.
.NOTES
    Versão: 5.0
    Data: 2026-01-31
    Autor: Automated Release Script
#>

[CmdletBinding()]
param(
    [string]$CommitMessage = @"
feat: PlayerEmbedAPI v5.0 - Enhanced Detection & Security

- 4 estratégias de extração (API, ShortIcu, Regex, WebView)
- Suporte a 4K (360p/480p/720p/1080p/2160p)
- Correções de segurança (SSL, logs)
- Regex compilados para performance
- Testes unitários

Versão: 253
"@
)

# Configuração de codificação para suportar caracteres especiais
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Cores para output
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

function Write-Status {
    param([string]$Message, [string]$Color = $ColorInfo)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# ============================================================================
# INÍCIO DO SCRIPT
# ============================================================================

Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════════════════╗
║           PlayerEmbedAPI v5.0 - GitHub Release Script               ║
╚══════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor $ColorInfo

# Verificar se estamos no diretório correto
$RepoPath = "C:\Users\KYTHOURS\Desktop\brcloudstream"
if (-not (Test-Path $RepoPath)) {
    Write-Status "ERRO: Diretório do repositório não encontrado: $RepoPath" $ColorError
    exit 1
}

Set-Location $RepoPath
Write-Status "Diretório do repositório: $RepoPath" $ColorInfo

# Verificar se é um repositório git
if (-not (Test-Path ".git")) {
    Write-Status "ERRO: Este diretório não é um repositório Git!" $ColorError
    exit 1
}

# Verificar se git está disponível
if (-not (Test-Command "git")) {
    Write-Status "ERRO: Git não encontrado no PATH!" $ColorError
    exit 1
}

Write-Status "✓ Git encontrado" $ColorSuccess

# ============================================================================
# PASSO 1: Verificar status do Git
# ============================================================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo
Write-Status "PASSO 1: Verificando status do Git..." $ColorInfo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo

try {
    $gitStatus = git status --short 2>&1
    $gitBranch = git branch --show-current 2>&1
    
    Write-Status "Branch atual: $gitBranch" $ColorInfo
    
    if ([string]::IsNullOrWhiteSpace($gitStatus)) {
        Write-Status "⚠ Nenhuma alteração detectada no working directory" $ColorWarning
    } else {
        Write-Status "Arquivos modificados/pendentes:" $ColorWarning
        $gitStatus | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorWarning }
    }
    
    # Verificar se há commits pendentes de push
    $unpushed = git log @{u}..HEAD --oneline 2>&1
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($unpushed)) {
        Write-Status "⚠ Commits pendentes de push:" $ColorWarning
        $unpushed | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorWarning }
    }
} catch {
    Write-Status "ERRO ao verificar status: $_" $ColorError
    exit 1
}

# ============================================================================
# PASSO 2: Adicionar arquivos ao staging
# ============================================================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo
Write-Status "PASSO 2: Adicionando arquivos ao staging..." $ColorInfo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo

# Lista de arquivos importantes para o v5.0
$importantFiles = @(
    "app/src/main/java/com/lagradost/cloudstream3/extractors/PlayerEmbedAPIExtractorV5.kt",
    "app/src/main/java/com/lagradost/cloudstream3/extractors/PlayerEmbedAPIWebViewExtractorV5.kt",
    "app/src/test/java/com/lagradost/cloudstream3/PlayerEmbedAPIV5Test.kt",
    "app/src/main/java/com/lagradost/cloudstream3/providers/MaxSeriesProvider.kt",
    "app/src/main/java/com/lagradost/cloudstream3/utils/LinkDecryptor.kt",
    "app/build.gradle.kts",
    "CHANGELOG_PLAYEREMBEDAPI_V5.md"
)

# Adicionar arquivos Python de teste (usando padrão)
$pythonTestFiles = Get-ChildItem -Path "." -Filter "*.py" -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -match "test|extract|player|embed" } |
    Select-Object -ExpandProperty FullName

Write-Status "Arquivos importantes para incluir:" $ColorInfo

# Verificar e adicionar cada arquivo importante
$filesAdded = 0
foreach ($file in $importantFiles) {
    if (Test-Path $file) {
        Write-Status "  ✓ $file" $ColorSuccess
        git add "$file" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $filesAdded++
        }
    } else {
        Write-Status "  ✗ $file (não encontrado)" $ColorWarning
    }
}

# Adicionar scripts Python
Write-Status "Scripts Python relacionados:" $ColorInfo
foreach ($file in $pythonTestFiles) {
    $relativePath = $file.Replace($RepoPath, "").TrimStart("\", "/")
    Write-Status "  ✓ $relativePath" $ColorSuccess
    git add "$relativePath" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $filesAdded++
    }
}

# Adicionar todos os outros arquivos modificados
Write-Status "Adicionando demais arquivos modificados..." $ColorInfo
git add -A 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Status "ERRO: Falha ao adicionar arquivos!" $ColorError
    exit 1
}

Write-Status "✓ Arquivos adicionados ao staging ($filesAdded+ arquivos principais)" $ColorSuccess

# Verificar o que foi staged
Write-Status "Arquivos no staging:" $ColorInfo
git diff --cached --name-only | ForEach-Object { Write-Host "  → $_" -ForegroundColor $ColorInfo }

# ============================================================================
# PASSO 3: Criar o commit
# ============================================================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo
Write-Status "PASSO 3: Criando commit..." $ColorInfo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo

# Salvar mensagem em arquivo temporário para preservar formatação
$tempFile = [System.IO.Path]::GetTempFileName()
$CommitMessage | Set-Content -Path $tempFile -Encoding UTF8

try {
    Write-Status "Mensagem do commit:" $ColorInfo
    Write-Host "---" -ForegroundColor DarkGray
    Write-Host $CommitMessage -ForegroundColor White
    Write-Host "---" -ForegroundColor DarkGray
    
    # Criar commit usando arquivo
    git commit -F $tempFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✓ Commit criado com sucesso!" $ColorSuccess
        
        # Mostrar informações do commit
        $commitHash = git rev-parse --short HEAD
        $commitInfo = git log -1 --oneline
        Write-Status "Commit: $commitInfo" $ColorSuccess
    } else {
        Write-Status "⚠ Nenhuma alteração para commit ou commit já existente" $ColorWarning
    }
} catch {
    Write-Status "ERRO ao criar commit: $_" $ColorError
    exit 1
} finally {
    # Limpar arquivo temporário
    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
    }
}

# ============================================================================
# PASSO 4: Push para o GitHub
# ============================================================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo
Write-Status "PASSO 4: Enviando para o GitHub..." $ColorInfo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo

# Identificar o branch principal
$mainBranch = git branch --show-current
$remoteBranches = git branch -r | ForEach-Object { $_.Trim() }

# Verificar se existe remote origin
$remote = git remote -v 2>&1
if ([string]::IsNullOrWhiteSpace($remote)) {
    Write-Status "ERRO: Nenhum remote configurado!" $ColorError
    Write-Status "Adicione um remote com: git remote add origin <URL>" $ColorWarning
    exit 1
}

Write-Status "Remote configurado:" $ColorInfo
$remote | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }

# Fazer o push
Write-Status "Enviando para o branch '$mainBranch'..." $ColorInfo

$pushOutput = git push -u origin $mainBranch 2>&1
$pushExitCode = $LASTEXITCODE

Write-Host $pushOutput -ForegroundColor DarkGray

# ============================================================================
# PASSO 5: Verificar se o push foi bem-sucedido
# ============================================================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo
Write-Status "PASSO 5: Verificando resultado..." $ColorInfo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $ColorInfo

if ($pushExitCode -eq 0) {
    Write-Status "✅ PUSH REALIZADO COM SUCESSO!" $ColorSuccess
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor $ColorSuccess
    Write-Host "              PlayerEmbedAPI v5.0 - Release Completo" -ForegroundColor $ColorSuccess
    Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor $ColorSuccess
    
    # Informações do commit
    $latestCommit = git log -1 --pretty=format:"%h - %s (%cr)" 2>&1
    Write-Status "Último commit: $latestCommit" $ColorInfo
    
    # Verificar status remoto
    $remoteUrl = git remote get-url origin 2>&1
    Write-Status "Repositório remoto: $remoteUrl" $ColorInfo
    
    Write-Host ""
    Write-Status "Arquivos incluídos no release:" $ColorInfo
    git ls-tree -r HEAD --name-only | Where-Object { 
        $_ -match "PlayerEmbedAPI|MaxSeriesProvider|LinkDecryptor|build\.gradle|CHANGELOG|\.py$" 
    } | ForEach-Object { Write-Host "  📄 $_" -ForegroundColor $ColorInfo }
    
    Write-Host ""
    Write-Status "Próximos passos:" $ColorWarning
    Write-Host "  1. Verifique no GitHub se o push foi recebido" -ForegroundColor White
    Write-Host "  2. Crie uma release/tag v5.0 se necessário" -ForegroundColor White
    Write-Host "  3. Execute os testes para validar a implementação" -ForegroundColor White
    
    exit 0
} else {
    Write-Status "❌ FALHA NO PUSH!" $ColorError
    Write-Host ""
    Write-Status "Possíveis causas:" $ColorError
    Write-Host "  • Problemas de autenticação com o GitHub" -ForegroundColor White
    Write-Host "  • Conflitos de merge pendentes" -ForegroundColor White
    Write-Host "  • Branch protegida ou sem permissão de escrita" -ForegroundColor White
    Write-Host "  • Problemas de conectividade de rede" -ForegroundColor White
    
    Write-Host ""
    Write-Status "Tentativas de resolução:" $ColorWarning
    Write-Host "  1. Verifique suas credenciais do GitHub" -ForegroundColor White
    Write-Host "  2. Execute: git pull origin $mainBranch" -ForegroundColor White
    Write-Host "  3. Resolva conflitos se houver" -ForegroundColor White
    Write-Host "  4. Tente novamente" -ForegroundColor White
    
    exit 1
}
