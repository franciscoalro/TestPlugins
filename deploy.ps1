# ============================================================================
# MaxSeries Auto-Deploy Script
# ============================================================================
# Automatiza TODO o processo de deploy de uma nova versão:
# 1. Build do plugin
# 2. Cálculo de SHA256
# 3. Atualização de JSONs (plugins.json, plugins-simple.json, providers.json)
# 4. Commit e Push para GitHub
# 5. Criação automática de Release no GitHub
# ============================================================================

param(
    [string]$PluginName = "MaxSeries",
    [switch]$SkipBuild = $false,
    [switch]$SkipRelease = $false
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  MaxSeries Auto-Deploy Script v1.0" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================================
# STEP 1: Detectar versão do build.gradle.kts
# ============================================================================
Write-Info "STEP 1: Detectando versão atual..."

$buildGradlePath = ".\$PluginName\build.gradle.kts"
if (-not (Test-Path $buildGradlePath)) {
    Write-Error "Arquivo não encontrado: $buildGradlePath"
    exit 1
}

$buildContent = Get-Content $buildGradlePath -Raw
if ($buildContent -match 'version\s*=\s*(\d+)') {
    $version = [int]$matches[1]
    Write-Success "Versão detectada: v$version"
} else {
    Write-Error "Não foi possível detectar a versão em $buildGradlePath"
    exit 1
}

# Extrair descrição
if ($buildContent -match 'description\s*=\s*"([^"]+)"') {
    $description = $matches[1]
    Write-Info "Descrição: $description"
} else {
    Write-Warning "Descrição não encontrada, usando padrão"
    $description = "$PluginName v$version"
}

# ============================================================================
# STEP 2: Build do plugin
# ============================================================================
if (-not $SkipBuild) {
    Write-Info "STEP 2: Compilando plugin..."
    
    # Parar daemon para evitar problemas de memória
    Write-Info "Parando Gradle daemon..."
    .\gradlew.bat --stop | Out-Null
    
    Write-Info "Iniciando build (sem daemon)..."
    $buildOutput = .\gradlew.bat ${PluginName}:make --no-daemon 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build falhou!"
        Write-Host $buildOutput
        exit 1
    }
    
    Write-Success "Build concluído com sucesso!"
} else {
    Write-Warning "Build pulado (--SkipBuild)"
}

# ============================================================================
# STEP 3: Verificar arquivo .cs3 e calcular SHA256
# ============================================================================
Write-Info "STEP 3: Calculando SHA256..."

$cs3Path = ".\$PluginName\build\$PluginName.cs3"
if (-not (Test-Path $cs3Path)) {
    Write-Error "Arquivo não encontrado: $cs3Path"
    exit 1
}

$fileSize = (Get-Item $cs3Path).Length
$sha256 = (Get-FileHash -Algorithm SHA256 $cs3Path).Hash

Write-Success "Arquivo: $cs3Path"
Write-Info "Tamanho: $fileSize bytes"
Write-Info "SHA256: $sha256"

# ============================================================================
# STEP 4: Atualizar JSONs
# ============================================================================
Write-Info "STEP 4: Atualizando arquivos JSON..."

$releaseUrl = "https://github.com/franciscoalro/TestPlugins/releases/download/v$version/$PluginName.cs3"

# Função para atualizar JSON
function Update-PluginJson {
    param(
        [string]$JsonPath,
        [string]$PluginName,
        [int]$Version,
        [string]$Description,
        [string]$Url,
        [long]$FileSize,
        [string]$Sha256
    )
    
    if (-not (Test-Path $JsonPath)) {
        Write-Warning "Arquivo não encontrado: $JsonPath (pulando)"
        return
    }
    
    $json = Get-Content $JsonPath -Raw | ConvertFrom-Json
    
    foreach ($plugin in $json) {
        if ($plugin.name -eq $PluginName -or $plugin.internalName -eq $PluginName) {
            $plugin.version = $Version
            $plugin.description = $Description
            $plugin.url = $Url
            
            # Adicionar SHA256 e fileSize se existirem no objeto
            if ($plugin.PSObject.Properties.Name -contains "sha256") {
                $plugin.sha256 = $Sha256
            }
            if ($plugin.PSObject.Properties.Name -contains "fileSize") {
                $plugin.fileSize = $FileSize
            }
            
            Write-Success "Atualizado: $JsonPath"
            break
        }
    }
    
    # Salvar com formatação bonita
    $json | ConvertTo-Json -Depth 10 | Set-Content $JsonPath -Encoding UTF8
}

# Atualizar todos os JSONs
Update-PluginJson -JsonPath ".\plugins.json" -PluginName $PluginName -Version $version -Description $description -Url $releaseUrl -FileSize $fileSize -Sha256 $sha256
Update-PluginJson -JsonPath ".\plugins-simple.json" -PluginName $PluginName -Version $version -Description $description -Url $releaseUrl -FileSize $fileSize -Sha256 $sha256
Update-PluginJson -JsonPath ".\providers.json" -PluginName $PluginName -Version $version -Description $description -Url $releaseUrl -FileSize $fileSize -Sha256 $sha256

# ============================================================================
# STEP 5: Git commit e push
# ============================================================================
Write-Info "STEP 5: Fazendo commit e push..."

git add "$PluginName/build.gradle.kts" "$PluginName/src/" "plugins.json" "plugins-simple.json" "providers.json" 2>&1 | Out-Null

$commitMessage = "$PluginName v$version: $description"
git commit -m $commitMessage 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Commit criado: $commitMessage"
    
    Write-Info "Enviando para GitHub..."
    git push 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Push concluído!"
    } else {
        Write-Error "Falha no push"
        exit 1
    }
} else {
    Write-Warning "Nenhuma mudança para commit (ou commit falhou)"
}

# ============================================================================
# STEP 6: Criar Release no GitHub
# ============================================================================
if (-not $SkipRelease) {
    Write-Info "STEP 6: Criando release no GitHub..."
    
    # Verificar se gh CLI está instalado
    $ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
    
    if ($ghInstalled) {
        Write-Info "Criando release v$version..."
        
        $releaseNotes = @"
## $PluginName v$version

$description

### 📦 Instalação
1. Abra CloudStream
2. Configurações → Extensões
3. Adicione o repositório: \`https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json\`
4. Atualize a extensão $PluginName

### 📊 Detalhes Técnicos
- **Versão**: $version
- **Tamanho**: $fileSize bytes
- **SHA256**: \`$sha256\`

### 🔗 Links
- [Download Direto]($releaseUrl)
- [Código Fonte](https://github.com/franciscoalro/TestPlugins/tree/main/$PluginName)
"@
        
        # Criar release
        gh release create "v$version" `
            "$cs3Path" `
            --title "$PluginName v$version" `
            --notes $releaseNotes `
            --repo franciscoalro/TestPlugins
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Release v$version criada com sucesso!"
            Write-Info "URL: https://github.com/franciscoalro/TestPlugins/releases/tag/v$version"
        } else {
            Write-Error "Falha ao criar release"
            exit 1
        }
    } else {
        Write-Warning "GitHub CLI (gh) não está instalado!"
        Write-Info "Para instalar: winget install GitHub.cli"
        Write-Info ""
        Write-Info "Ou crie a release manualmente em:"
        Write-Info "https://github.com/franciscoalro/TestPlugins/releases/new"
        Write-Info ""
        Write-Info "Tag: v$version"
        Write-Info "Arquivo: $cs3Path"
    }
} else {
    Write-Warning "Criação de release pulada (--SkipRelease)"
}

# ============================================================================
# RESUMO FINAL
# ============================================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Success "Versão: v$version"
Write-Success "Descrição: $description"
Write-Success "SHA256: $sha256"
Write-Success "Tamanho: $fileSize bytes"
Write-Host ""
Write-Info "Próximos passos:"
Write-Info "1. Aguarde alguns minutos para o GitHub processar"
Write-Info "2. Abra CloudStream no dispositivo"
Write-Info "3. Vá em Configurações → Extensões → Atualizar"
Write-Info "4. Atualize o plugin $PluginName para v$version"
Write-Host ""
Write-Success "Pronto para usar! 🚀"
Write-Host ""
