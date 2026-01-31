#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script de Build e Verificação do PlayerEmbedAPI v5.0 para o projeto brcloudstream

.DESCRIPTION
    Este script automatiza o processo de build do projeto MaxSeries e verifica
    a geração do arquivo .cs3 do PlayerEmbedAPI v5.0.

.AUTHOR
    Build Automation Script
.VERSION
    1.0.0
#>

# Configurações
$ErrorActionPreference = "Stop"
$projectDir = "C:\Users\KYTHOURS\Desktop\brcloudstream"
$moduleName = "MaxSeries"
$targetVersion = "5.0"
$minFileSizeKB = 50  # Tamanho mínimo esperado em KB

# Cores para output
$colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor $colors.Header
    Write-Host "  $Message" -ForegroundColor $colors.Header
    Write-Host "=" * 70 -ForegroundColor $colors.Header
}

function Write-Step {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] » $Message" -ForegroundColor $colors.Info
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor $colors.Success
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor $colors.Error
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor $colors.Warning
}

function Format-FileSize {
    param([long]$Size)
    if ($Size -gt 1MB) {
        return "{0:N2} MB" -f ($Size / 1MB)
    } elseif ($Size -gt 1KB) {
        return "{0:N2} KB" -f ($Size / 1KB)
    } else {
        return "$Size bytes"
    }
}

# ============================================
# 1. VERIFICAÇÃO DE PRÉ-REQUISITOS
# ============================================

Write-Header "PLAYEREMBEDAPI v5.0 - BUILD E VERIFICAÇÃO"

Write-Step "Verificando pré-requisitos..."

$prereqs = @{
    Java = @{ Cmd = "java"; Args = "-version"; Required = $true }
    GradleWrapper = @{ Cmd = "$projectDir\gradlew.bat"; Args = "--version"; Required = $true }
    Git = @{ Cmd = "git"; Args = "--version"; Required = $false }
}

$prereqResults = @{}

foreach ($prereq in $prereqs.GetEnumerator()) {
    $name = $prereq.Key
    $config = $prereq.Value
    
    try {
        $null = & $config.Cmd $config.Args 2>&1
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
            Write-Success "$name encontrado"
            $prereqResults[$name] = $true
        } else {
            throw "Exit code: $LASTEXITCODE"
        }
    } catch {
        $prereqResults[$name] = $false
        if ($config.Required) {
            Write-Error "$name não encontrado ou não funcional"
        } else {
            Write-Warning "$name não encontrado (opcional)"
        }
    }
}

# Verificar Java versão
if ($prereqResults.Java) {
    try {
        $javaVersion = & java -version 2>&1 | Select-String -Pattern '"([0-9._]+)"' | ForEach-Object { $_.Matches.Groups[1].Value }
        if ($javaVersion -match "^(1\.8|11|17|21)" -or [int]($javaVersion -split '\.')[0] -ge 11) {
            Write-Success "Java versão compatível: $javaVersion"
        } else {
            Write-Warning "Java versão pode não ser compatível: $javaVersion (recomendado: 11+)"
        }
    } catch {
        Write-Warning "Não foi possível verificar a versão do Java"
    }
} else {
    Write-Error "Java é obrigatório para o build. Instale o JDK 11 ou superior."
    exit 1
}

# Verificar estrutura do projeto
Write-Step "Verificando estrutura do projeto..."

$requiredPaths = @(
    "$projectDir\$moduleName",
    "$projectDir\$moduleName\build.gradle.kts",
    "$projectDir\$moduleName\src\main\kotlin\com\franciscoalro\maxseries\MaxSeriesProvider.kt",
    "$projectDir\gradlew.bat",
    "$projectDir\build.gradle.kts",
    "$projectDir\settings.gradle.kts"
)

$structureOk = $true
foreach ($path in $requiredPaths) {
    if (Test-Path $path) {
        Write-Success "$(Split-Path $path -Leaf) encontrado"
    } else {
        Write-Error "Arquivo/Pasta não encontrado: $path"
        $structureOk = $false
    }
}

if (-not $structureOk) {
    Write-Error "Estrutura do projeto incompleta. Abortando."
    exit 1
}

# ============================================
# 2. LIMPAR BUILD ANTERIOR
# ============================================

Write-Header "LIMPANDO BUILD ANTERIOR"

Write-Step "Removendo arquivos de build antigos..."

$buildPaths = @(
    "$projectDir\$moduleName\build",
    "$projectDir\build",
    "$projectDir\.gradle\buildOutputCleanup"
)

$cleanedCount = 0
foreach ($path in $buildPaths) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Success "Removido: $(Split-Path $path -Leaf)"
            $cleanedCount++
        } catch {
            Write-Warning "Não foi possível remover: $(Split-Path $path -Leaf)"
        }
    }
}

if ($cleanedCount -eq 0) {
    Write-Warning "Nenhum diretório de build encontrado para limpar"
} else {
    Write-Success "$cleanedCount diretório(s) de build limpo(s)"
}

# Limpar arquivos .cs3 antigos na raiz do módulo
$oldCs3Files = Get-ChildItem -Path "$projectDir\$moduleName" -Filter "*.cs3" -ErrorAction SilentlyContinue
if ($oldCs3Files) {
    foreach ($file in $oldCs3Files) {
        Remove-Item -Path $file.FullName -Force
        Write-Success "Removido arquivo antigo: $($file.Name)"
    }
}

# ============================================
# 3. COMPILAR O PROJETO
# ============================================

Write-Header "COMPILANDO PROJETO MAXSERIES"

Write-Step "Iniciando build com Gradle (pode levar alguns minutos)..."
Write-Host ""

Set-Location $projectDir

# Registrar tempo de início
$buildStartTime = Get-Date

# Executar o build
try {
    # Usar --no-daemon para evitar problemas com daemon preso
    $buildOutput = & .\gradlew.bat $moduleName`:make --no-daemon --console=plain 2>&1
    $buildExitCode = $LASTEXITCODE
    
    # Mostrar output relevante
    $relevantLines = $buildOutput | Select-String -Pattern "(BUILD|Task|error|warning|success|cs3)" -CaseSensitive:$false | Select-Object -Last 30
    if ($relevantLines) {
        foreach ($line in $relevantLines) {
            Write-Host "  $line" -ForegroundColor Gray
        }
    }
    
    if ($buildExitCode -eq 0) {
        Write-Host ""
        Write-Success "Build concluído com sucesso!"
    } else {
        throw "Gradle exit code: $buildExitCode"
    }
} catch {
    Write-Host ""
    Write-Error "Falha no build: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "  Output completo:" -ForegroundColor Yellow
    $buildOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    exit 1
}

# Calcular tempo de build
$buildEndTime = Get-Date
$buildDuration = $buildEndTime - $buildStartTime
Write-Success "Tempo de build: $($buildDuration.ToString('mm\:ss'))"

# ============================================
# 4. VERIFICAR SE O .CS3 FOI GERADO
# ============================================

Write-Header "VERIFICANDO ARQUIVO .CS3 GERADO"

Write-Step "Procurando arquivo .cs3..."

# Procurar em várias localizações possíveis
$searchPaths = @(
    "$projectDir\$moduleName\build\outputs\cs3",
    "$projectDir\$moduleName\build\libs",
    "$projectDir\$moduleName\build",
    "$projectDir\$moduleName",
    "$projectDir\build\outputs\cs3",
    "$projectDir\build\libs"
)

$foundCs3 = $null
foreach ($searchPath in $searchPaths) {
    if (Test-Path $searchPath) {
        $cs3Files = Get-ChildItem -Path $searchPath -Filter "*.cs3" -Recurse -ErrorAction SilentlyContinue | 
                    Where-Object { $_.Name -like "*$moduleName*" -or $_.Name -eq "$moduleName.cs3" } |
                    Sort-Object LastWriteTime -Descending |
                    Select-Object -First 1
        
        if ($cs3Files) {
            $foundCs3 = $cs3Files
            break
        }
    }
}

# Também procurar na raiz do projeto
if (-not $foundCs3) {
    $rootCs3 = Get-ChildItem -Path $projectDir -Filter "$moduleName.cs3" -ErrorAction SilentlyContinue | 
               Sort-Object LastWriteTime -Descending | 
               Select-Object -First 1
    if ($rootCs3) {
        $foundCs3 = $rootCs3
    }
}

if ($foundCs3) {
    Write-Success "Arquivo .cs3 encontrado: $($foundCs3.FullName)"
    $cs3Generated = $true
} else {
    Write-Error "Arquivo .cs3 não encontrado!"
    Write-Warning "Verifique se o build foi concluído corretamente"
    $cs3Generated = $false
}

# ============================================
# 5. VERIFICAR O TAMANHO DO ARQUIVO
# ============================================

Write-Header "VERIFICANDO TAMANHO DO ARQUIVO"

if ($foundCs3) {
    $fileSize = $foundCs3.Length
    $formattedSize = Format-FileSize -Size $fileSize
    $fileSizeKB = [math]::Round($fileSize / 1KB, 2)
    
    Write-Step "Analisando arquivo: $($foundCs3.Name)"
    Write-Host ""
    Write-Host "  📄 Nome:        $($foundCs3.Name)" -ForegroundColor White
    Write-Host "  📁 Caminho:     $($foundCs3.FullName)" -ForegroundColor White
    Write-Host "  📊 Tamanho:     $formattedSize ($fileSizeKB KB)" -ForegroundColor White
    Write-Host "  📅 Modificado:  $($foundCs3.LastWriteTime)" -ForegroundColor White
    Write-Host ""
    
    # Verificar se o tamanho é adequado
    if ($fileSizeKB -ge $minFileSizeKB) {
        Write-Success "Tamanho do arquivo está dentro do esperado (>= $minFileSizeKB KB)"
        $sizeCheck = $true
    } else {
        Write-Warning "Tamanho do arquivo menor que o esperado ($fileSizeKB KB < $minFileSizeSizeKB KB)"
        $sizeCheck = $false
    }
    
    # Verificar se o arquivo não está vazio/corrompido
    if ($fileSize -eq 0) {
        Write-Error "Arquivo está vazio!"
        $sizeCheck = $false
    } elseif ($fileSize -lt 1024) {
        Write-Warning "Arquivo muito pequeno, pode estar corrompido"
        $sizeCheck = $false
    }
    
    # Verificar extensão
    if ($foundCs3.Extension -ne ".cs3") {
        Write-Warning "Extensão do arquivo não é .cs3"
    }
} else {
    Write-Error "Não foi possível verificar o tamanho - arquivo não encontrado"
    $sizeCheck = $false
}

# ============================================
# 6. CRIAR RESUMO DO BUILD
# ============================================

Write-Header "RESUMO DO BUILD"

$summaryData = @{
    "Data/Hora" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "Versão" = $targetVersion
    "Módulo" = $moduleName
    "Diretório" = $projectDir
    "Java OK" = $prereqResults.Java
    "Gradle OK" = $prereqResults.GradleWrapper
    "Estrutura OK" = $structureOk
    "Build OK" = ($buildExitCode -eq 0)
    "CS3 Gerado" = $cs3Generated
    "Tamanho OK" = $sizeCheck
    "Tempo de Build" = $buildDuration.ToString('mm\:ss')
}

if ($foundCs3) {
    $summaryData["Arquivo"] = $foundCs3.Name
    $summaryData["Tamanho"] = Format-FileSize -Size $foundCs3.Length
    $summaryData["Caminho"] = $foundCs3.FullName
}

# Exibir resumo visual
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $colors.Header
Write-Host "  │                     RESUMO DO BUILD                         │" -ForegroundColor $colors.Header
Write-Host "  ├─────────────────────────────────────────────────────────────┤" -ForegroundColor $colors.Header

foreach ($item in $summaryData.GetEnumerator()) {
    $key = $item.Key.PadRight(15)
    $value = $item.Value
    
    if ($value -is [bool]) {
        $status = if ($value) { "✓ SIM" } else { "✗ NÃO" }
        $color = if ($value) { $colors.Success } else { $colors.Error }
    } else {
        $status = $value.ToString()
        $color = "White"
    }
    
    Write-Host "  │  $key : " -NoNewline -ForegroundColor Gray
    Write-Host "$status".PadRight(35) -NoNewline -ForegroundColor $color
    Write-Host "│" -ForegroundColor $colors.Header
}

Write-Host "  └─────────────────────────────────────────────────────────────┘" -ForegroundColor $colors.Header

# Determinar status geral
$allChecks = @(
    $prereqResults.Java,
    $prereqResults.GradleWrapper,
    $structureOk,
    ($buildExitCode -eq 0),
    $cs3Generated,
    $sizeCheck
)

$passedChecks = ($allChecks | Where-Object { $_ -eq $true }).Count
$totalChecks = $allChecks.Count

Write-Host ""
if ($passedChecks -eq $totalChecks) {
    Write-Success "TODAS AS VERIFICAÇÕES PASSARAM ($passedChecks/$totalChecks)"
    $overallStatus = "SUCESSO"
} else {
    Write-Error "ALGUMAS VERIFICAÇÕES FALHARAM ($passedChecks/$totalChecks)"
    $overallStatus = "FALHA"
}

# Criar arquivo de log do build
$logFile = "$projectDir\build_v5_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$logContent = @"
================================================================================
BUILD LOG - PlayerEmbedAPI v5.0
================================================================================
Data/Hora: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Status: $overallStatus

--- PRÉ-REQUISITOS ---
Java: $($prereqResults.Java)
Gradle: $($prereqResults.GradleWrapper)

--- ESTRUTURA ---
OK: $structureOk

--- BUILD ---
Tempo: $($buildDuration.ToString('mm\:ss'))
Exit Code: $buildExitCode

--- ARQUIVO GERADO ---
$(if ($foundCs3) { @"
Nome: $($foundCs3.Name)
Caminho: $($foundCs3.FullName)
Tamanho: $(Format-FileSize -Size $foundCs3.Length)
Modificado: $($foundCs3.LastWriteTime)
"@ } else { "Nenhum arquivo .cs3 encontrado" })

--- VERIFICAÇÕES ---
CS3 Gerado: $cs3Generated
Tamanho OK: $sizeCheck
Verificações Passadas: $passedChecks/$totalChecks

--- DETALHES DO BUILD ---
$($buildOutput -join "`n")
================================================================================
"@

$logContent | Out-File -FilePath $logFile -Encoding UTF8
Write-Host ""
Write-Success "Log salvo em: $logFile"

# ============================================
# FINALIZAÇÃO
# ============================================

Write-Header "BUILD FINALIZADO"

if ($overallStatus -eq "SUCESSO") {
    Write-Host ""
    Write-Host "  🎉 BUILD CONCLUÍDO COM SUCESSO! 🎉" -ForegroundColor $colors.Success
    Write-Host ""
    Write-Host "  Próximos passos:" -ForegroundColor $colors.Info
    Write-Host "  1. O arquivo .cs3 está pronto em: $($foundCs3.FullName)" -ForegroundColor White
    Write-Host "  2. Copie o arquivo para seu dispositivo Android" -ForegroundColor White
    Write-Host "  3. Instale no CloudStream através de 'Instalar de arquivo'" -ForegroundColor White
    Write-Host "  4. Teste o PlayerEmbedAPI v5.0" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host ""
    Write-Host "  ❌ BUILD FALHOU ❌" -ForegroundColor $colors.Error
    Write-Host ""
    Write-Host "  Verifique os erros acima e tente novamente." -ForegroundColor $colors.Warning
    Write-Host "  Para mais detalhes, consulte o log: $logFile" -ForegroundColor $colors.Warning
    Write-Host ""
    exit 1
}
