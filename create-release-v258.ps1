# Script para criar release v258 com o .cs3 do GitHub Actions
# Requer: gh (GitHub CLI) instalado e autenticado

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Criar Release v258 - MaxSeries" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gh está instalado
try {
    $ghVersion = gh --version 2>$null
    Write-Host "GitHub CLI encontrado: $($ghVersion[0])" -ForegroundColor Green
} catch {
    Write-Host "ERRO: GitHub CLI (gh) nao esta instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
try {
    $user = gh api user -q .login 2>$null
    Write-Host "Autenticado como: $user" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Nao autenticado no GitHub CLI!" -ForegroundColor Red
    Write-Host "Execute: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Definir variáveis
$repo = "franciscoalro/TestPlugins"
$version = "v258"
$artifactName = "Cloudstream-Plugins"
$runId = "21554293558"  # Build #684

Write-Host ""
Write-Host "Download do artifact do GitHub Actions..." -ForegroundColor Yellow
Write-Host "Run ID: $runId" -ForegroundColor Gray

# Criar diretório temporário
$tempDir = "temp_release_$version"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

# Baixar artifact
try {
    Write-Host "Baixando artifact..." -ForegroundColor Yellow
    gh run download $runId --name $artifactName --repo $repo
    Write-Host "Artifact baixado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao baixar artifact: $_" -ForegroundColor Red
    Set-Location ..
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    exit 1
}

# Listar arquivos baixados
Write-Host ""
Write-Host "Arquivos baixados:" -ForegroundColor Cyan
Get-ChildItem -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Gray }

# Encontrar o arquivo .cs3
$cs3File = Get-ChildItem -Recurse -Filter "*.cs3" | Select-Object -First 1

if (-not $cs3File) {
    Write-Host "ERRO: Arquivo .cs3 nao encontrado no artifact!" -ForegroundColor Red
    Set-Location ..
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "Arquivo .cs3 encontrado: $($cs3File.Name)" -ForegroundColor Green
Write-Host "Tamanho: $([math]::Round($cs3File.Length/1024, 2)) KB" -ForegroundColor Gray

# Renomear para MaxSeries.cs3 se necessário
$targetFile = "MaxSeries.cs3"
if ($cs3File.Name -ne $targetFile) {
    Copy-Item $cs3File.FullName $targetFile -Force
    Write-Host "Arquivo renomeado para: $targetFile" -ForegroundColor Yellow
} else {
    $targetFile = $cs3File.FullName
}

# Verificar se release já existe
try {
    $existingRelease = gh release view $version --repo $repo 2>$null
    if ($existingRelease) {
        Write-Host ""
        Write-Host "Release $version ja existe!" -ForegroundColor Yellow
        $deleteOld = Read-Host "Deseja excluir a release existente e criar nova? (s/n)"
        if ($deleteOld -eq "s" -or $deleteOld -eq "S") {
            Write-Host "Excluindo release antiga..." -ForegroundColor Yellow
            gh release delete $version --repo $repo --yes
            Write-Host "Release antiga excluida!" -ForegroundColor Green
        } else {
            Write-Host "Operacao cancelada pelo usuario." -ForegroundColor Yellow
            Set-Location ..
            Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
            exit 0
        }
    }
} catch {
    # Release não existe, pode continuar
}

# Criar release
Write-Host ""
Write-Host "Criando release $version..." -ForegroundColor Yellow

$releaseNotes = @"
# MaxSeries v258 - BOM Fix & Clean Build

## Correcoes
- Removido BOM UTF-8 dos arquivos de configuracao
- Adicionado campo 'internalName' obrigatorio
- Adicionado campo 'apiVersion' obrigatorio
- Encoding UTF-8 sem BOM para compatibilidade com CloudStream

## Como usar
1. Adicione o repositorio no CloudStream:
   \`https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json\`

2. Instale o MaxSeries v258

3. Aproveite!

## Arquivos
- MaxSeries.cs3 (v258)
- Compativel com CloudStream 3.x
"@

try {
    gh release create $version `
        --repo $repo `
        --title "MaxSeries v258 - BOM Fix" `
        --notes $releaseNotes `
        $targetFile
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Release $version criada com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL da Release:" -ForegroundColor Cyan
    gh release view $version --repo $repo --json url -q .url
} catch {
    Write-Host "ERRO ao criar release: $_" -ForegroundColor Red
    Set-Location ..
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    exit 1
}

# Limpar
Set-Location ..
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "Arquivos temporarios removidos." -ForegroundColor Gray
Write-Host ""
Write-Host "Pronto! O repositorio esta atualizado para v258." -ForegroundColor Green
