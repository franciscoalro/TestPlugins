# Script de Deploy para GitHub - BRCloudStream
# Este script executa o deploy dos plugins para o repositório CloudstreamRepo

param(
    [string]$Versao = "v256",
    [switch]$UsarGitHubCLI = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY BRCloudStream - GitHub       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Não está em um repositório git!" -ForegroundColor Red
    exit 1
}

# Verificar repositório remoto
$remote = git remote -v
Write-Host "Repositório configurado:" -ForegroundColor Yellow
Write-Host $remote
Write-Host ""

# Verificar branch atual
$branch = git branch --show-current
Write-Host "Branch atual: $branch" -ForegroundColor Yellow
Write-Host ""

# Verificar se há alterações não commitadas
$status = git status --porcelain
if ($status) {
    Write-Host "AVISO: Existem alterações não commitadas:" -ForegroundColor Yellow
    Write-Host $status
    Write-Host ""
    
    $commit = Read-Host "Deseja fazer commit das alterações? (s/n)"
    if ($commit -eq "s") {
        git add .
        git commit -m "Pre-deploy changes $(Get-Format-Date)"
    }
}

# Verificar se existem arquivos .cs3 para deploy
Write-Host "1. Verificando arquivos .cs3..." -ForegroundColor Yellow
$cs3Files = Get-ChildItem -Path "builds/*.cs3" -ErrorAction SilentlyContinue
if ($cs3Files.Count -eq 0) {
    Write-Host "   Nenhum arquivo .cs3 encontrado na pasta builds/" -ForegroundColor Red
    Write-Host "   Executando build primeiro..." -ForegroundColor Gray
    
    # Build
    .\gradlew.bat build --no-daemon -x test -x lint
    
    # Copiar arquivos
    New-Item -ItemType Directory -Force -Path "builds" | Out-Null
    Get-ChildItem -Path "*/build/outputs/aar/*-release.aar" | ForEach-Object {
        $name = $_.Name -replace "-release.aar", ".cs3"
        Copy-Item $_.FullName -Destination "builds/$name" -Force
    }
}

Write-Host "   Arquivos encontrados:" -ForegroundColor Green
$cs3Files | ForEach-Object { Write-Host "   - $($_.Name)" }
Write-Host ""

# Verificar GitHub CLI
Write-Host "2. Verificando GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    Write-Host "   GitHub CLI encontrado!" -ForegroundColor Green
    gh --version | Select-Object -First 1
    
    # Verificar autenticação
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Autenticado com GitHub!" -ForegroundColor Green
        
        # Trigger workflow
        Write-Host ""
        Write-Host "3. Disparando workflow de deploy..." -ForegroundColor Yellow
        gh workflow run build.yml --ref main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Workflow disparado com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Acompanhe a execução em:" -ForegroundColor Cyan
            Write-Host "https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor White
        } else {
            Write-Host "   Erro ao disparar workflow" -ForegroundColor Red
        }
    } else {
        Write-Host "   Não autenticado. Execute: gh auth login" -ForegroundColor Red
    }
} else {
    Write-Host "   GitHub CLI não instalado" -ForegroundColor Yellow
    Write-Host "   Instale em: https://cli.github.com/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Alternativa: Push direto via git" -ForegroundColor Yellow
    
    # Push para trigger do workflow
    Write-Host "3. Fazendo push para GitHub..." -ForegroundColor Yellow
    
    # Criar tag se especificado
    if ($Versao) {
        Write-Host "   Criando tag $Versao..." -ForegroundColor Gray
        git tag -f $Versao
        git push origin $Versao --force
    }
    
    # Push da branch
    git push origin $branch
    
    Write-Host "   Push realizado! Workflow será executado automaticamente." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY INICIADO!                    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs do repositório:" -ForegroundColor Yellow
Write-Host "  Repo:  https://github.com/franciscoalro/TestPlugins" -ForegroundColor White
Write-Host "  Actions: https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor White
Write-Host ""
Write-Host "Após o workflow completar, os plugins estarão em:" -ForegroundColor Yellow
Write-Host "  https://github.com/franciscoalro/CloudstreamRepo" -ForegroundColor White
Write-Host ""
Write-Host "URL para CloudStream:" -ForegroundColor Yellow
Write-Host "  https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json" -ForegroundColor Green
Write-Host ""
