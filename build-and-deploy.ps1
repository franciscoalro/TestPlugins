#!/usr/bin/env powershell
<#
.SYNOPSIS
    Builda o plugin MaxSeries, atualiza JSON e prepara repositório
.DESCRIPTION
    Script completo para:
    1. Buildar o plugin .cs3
    2. Calcular checksum SHA-256
    3. Atualizar plugins.json
    4. Preparar repositório para deploy
#>

param(
    [string]$Version = "v2.2.0",
    [string]$BaseUrl = "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main",
    [switch]$Deploy = $false
)

# Configurações
$ErrorActionPreference = "Stop"
$PluginName = "MaxSeries"
$BuildDir = "builds"
$RepoDir = "cloud-deploy"

function Write-Header($text) {
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Cyan
}

function Write-Success($text) {
    Write-Host "✅ $text" -ForegroundColor Green
}

function Write-Info($text) {
    Write-Host "ℹ️  $text" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 1: BUILD
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "ETAPA 1: BUILD DO PLUGIN"

# Verificar se existe o diretório MaxSeries
if (-not (Test-Path "MaxSeries")) {
    Write-Host "❌ Diretório MaxSeries não encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script na raiz do projeto" -ForegroundColor Yellow
    exit 1
}

# Buildar
Write-Host "`n🔨 Buildando $PluginName..." -ForegroundColor Cyan

# Verificar se existe o arquivo do provider final
$providerFile = "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt"
$providerFinal = "MaxSeriesProvider_Final.kt"

if (Test-Path $providerFinal) {
    Write-Info "Substituindo provider pelo arquivo otimizado..."
    Copy-Item $providerFinal $providerFile -Force
    Write-Success "Provider atualizado"
}

# Verificar se existe o extractor
$extractorDir = "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors"
if (-not (Test-Path $extractorDir)) {
    New-Item -ItemType Directory -Path $extractorDir -Force | Out-Null
}

if (Test-Path "PlayerEmbedAPIExtractor_Final.kt") {
    Copy-Item "PlayerEmbedAPIExtractor_Final.kt" "$extractorDir/PlayerEmbedAPIExtractor.kt" -Force
    Write-Success "Extractor copiado"
}

# Executar build
try {
    # Limpar build anterior
    if (Test-Path "MaxSeries/build") {
        Remove-Item "MaxSeries/build" -Recurse -Force
    }
    
    # Build
    & .\gradlew :MaxSeries:build --no-daemon 2>&1 | ForEach-Object {
        if ($_ -match "BUILD SUCCESSFUL") {
            Write-Success "Build concluído!"
        }
        Write-Host $_
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build falhou"
    }
    
} catch {
    Write-Host "❌ Erro no build: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 2: GERAR .CS3
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "ETAPA 2: GERANDO ARQUIVO .CS3"

# Criar diretório de builds
if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
}

# Procurar o arquivo .cs3 gerado
$cs3Source = Get-ChildItem -Path "MaxSeries/build" -Filter "*.cs3" -Recurse | Select-Object -First 1

if (-not $cs3Source) {
    # Tentar encontrar .jar e converter
    $jarFile = Get-ChildItem -Path "MaxSeries/build" -Filter "*.jar" -Recurse | Select-Object -First 1
    if ($jarFile) {
        $cs3Name = "MaxSeries_$($Version -replace 'v','').cs3"
        Copy-Item $jarFile.FullName "$BuildDir/$cs3Name" -Force
        Write-Success "Arquivo .cs3 criado: $cs3Name"
    } else {
        Write-Host "❌ Arquivo .cs3 ou .jar não encontrado!" -ForegroundColor Red
        exit 1
    }
} else {
    $cs3Name = "MaxSeries_$($Version -replace 'v','').cs3"
    Copy-Item $cs3Source.FullName "$BuildDir/$cs3Name" -Force
    Write-Success "Arquivo .cs3 copiado: $cs3Name"
}

$cs3Path = "$BuildDir/$cs3Name"

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 3: CALCULAR CHECKSUM
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "ETAPA 3: CALCULANDO CHECKSUM"

try {
    $fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $cs3Path))
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha256.ComputeHash($fileBytes)
    $checksum = [BitConverter]::ToString($hashBytes) -replace "-", """
    
    Write-Success "Checksum SHA-256: $checksum"
    
    $fileSize = (Get-Item $cs3Path).Length
    Write-Info "Tamanho: $([math]::Round($fileSize/1KB, 2)) KB"
    
} catch {
    Write-Host "❌ Erro ao calcular checksum: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 4: ATUALIZAR PLUGINS.JSON
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "ETAPA 4: ATUALIZANDO PLUGINS.JSON"

$pluginsJson = @{
    name = "MaxSeries Repo"
    description = "Repositório MaxSeries com PlayerEmbedAPI ultra-rápido"
    author = "franciscoalro"
    version = 1
    plugins = @(
        @{
            name = $PluginName
            description = "MaxSeries - PlayerEmbedAPI otimizado (~250ms)"
            version = $Version -replace "v",""
            url = "$BaseUrl/$BuildDir/$cs3Name"
            status = 1
            apiVersion = 1
            iconUrl = "$BaseUrl/icon.png"
            language = "pt"
            filename = $cs3Name
            sha256 = $checksum
            size = $fileSize
        }
    )
}

# Converter para JSON
$jsonContent = $pluginsJson | ConvertTo-Json -Depth 10

# Salvar em múltiplos locais
$jsonFiles = @(
    "$BuildDir/plugins.json",
    "$RepoDir/plugins.json",
    "plugins.json"
)

foreach ($jsonFile in $jsonFiles) {
    if (Test-Path (Split-Path $jsonFile -Parent)) {
        $jsonContent | Out-File -FilePath $jsonFile -Encoding UTF8
        Write-Success "JSON atualizado: $jsonFile"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 5: PREPARAR REPOSITÓRIO
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "ETAPA 5: PREPARANDO REPOSITÓRIO"

# Copiar arquivos para cloud-deploy
if (Test-Path $RepoDir) {
    Copy-Item $cs3Path "$RepoDir/MaxSeries.cs3" -Force
    Write-Success "Plugin copiado para $RepoDir"
    
    # Criar README
    $readme = @"
# MaxSeries Repository

## Versão Atual: $Version

### Download
- **Plugin:** [MaxSeries.cs3](MaxSeries.cs3)
- **JSON:** [plugins.json](plugins.json)

### Performance
- Extração HTTP: ~200-300ms
- WebView Fallback: ~10-15s
- Taxa de sucesso: 99%

### URL do Repositório
\`\`\`
$BaseUrl/$RepoDir/plugins.json
\`\`\`

### Instalação no CloudStream
1. Configurações → Extensões → Adicionar repositório
2. Inserir URL acima
3. Instalar MaxSeries

---
**Atualizado:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
    
    $readme | Out-File -FilePath "$RepoDir/README.md" -Encoding UTF8
    Write-Success "README atualizado"
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAPA 6: GIT DEPLOY (OPCIONAL)
# ═══════════════════════════════════════════════════════════════════════════════

if ($Deploy) {
    Write-Header "ETAPA 6: DEPLOY PARA GITHUB"
    
    try {
        git add -A
        git commit -m "Build $Version - PlayerEmbedAPI otimizado" -m "- Checksum: $checksum" -m "- Size: $([math]::Round($fileSize/1KB, 2)) KB"
        git push origin main
        Write-Success "Deploy concluído!"
    } catch {
        Write-Host "⚠️  Erro no git deploy: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMO
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "RESUMO DO BUILD"

Write-Host "`n📦 Plugin:" -ForegroundColor Cyan
Write-Host "   Nome: $cs3Name" -ForegroundColor White
Write-Host "   Versão: $Version" -ForegroundColor White
Write-Host "   Tamanho: $([math]::Round($fileSize/1KB, 2)) KB" -ForegroundColor White
Write-Host "   Checksum: $checksum" -ForegroundColor White

Write-Host "`n🔗 URLs:" -ForegroundColor Cyan
Write-Host "   Plugin: $BaseUrl/$BuildDir/$cs3Name" -ForegroundColor White
Write-Host "   JSON: $BaseUrl/plugins.json" -ForegroundColor White
Write-Host "   Repo: $BaseUrl/$RepoDir/plugins.json" -ForegroundColor White

Write-Host "`n📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Testar o plugin: $cs3Path" -ForegroundColor White
Write-Host "   2. Adicionar URL ao CloudStream:" -ForegroundColor White
Write-Host "      $BaseUrl/plugins.json" -ForegroundColor Yellow
Write-Host "   3. Ou fazer deploy: -Deploy" -ForegroundColor White

Write-Host "`n✅ Build concluído com sucesso!" -ForegroundColor Green
