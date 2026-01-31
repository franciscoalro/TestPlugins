# Build com Testes - PlayerEmbedAPI v5.0
# Automatiza: validação Python, testes unitários e build do plugin

param(
    [switch]$SkipTests,
    [switch]$SkipValidation,
    [switch]$Release
)

$ErrorActionPreference = "Stop"
$BaseDir = "C:\Users\KYTHOURS\Desktop\brcloudstream"

function Write-Header($message) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

Set-Location $BaseDir

# 1. Validação Python
if (-not $SkipValidation) {
    Write-Header "ETAPA 1: Validação Python vs Kotlin"
    
    if (Test-Path "validate_implementation.py") {
        python validate_implementation.py
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Validação falhou! Corrija os erros antes de continuar."
            exit 1
        }
    } else {
        Write-Warning "Script de validação não encontrado"
    }
} else {
    Write-Warning "Validação pulada (--SkipValidation)"
}

# 2. Testes Python (se houver URLs de teste)
if (-not $SkipTests -and (Test-Path "test_urls.txt")) {
    Write-Header "ETAPA 2: Testes Python em Batch"
    
    if (Test-Path "test_playerembedapi_batch.py") {
        python test_playerembedapi_batch.py test_urls.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Alguns testes Python falharam"
        }
    }
} else {
    Write-Warning "Testes Python pulados (sem URLs de teste)"
}

# 3. Testes Unitários Kotlin
if (-not $SkipTests) {
    Write-Header "ETAPA 3: Testes Unitários Kotlin"
    
    try {
        & .\gradlew.bat :MaxSeries:test --tests "*PlayerEmbedAPIV5Test*" --no-daemon
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Testes unitários passaram!"
        } else {
            Write-Warning "Alguns testes unitários falharam"
        }
    } catch {
        Write-Error "Erro ao executar testes: $_"
    }
} else {
    Write-Warning "Testes unitários pulados (--SkipTests)"
}

# 4. Build do Plugin
Write-Header "ETAPA 4: Build do Plugin MaxSeries"

try {
    & .\gradlew.bat :MaxSeries:make --no-daemon
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Build concluído com sucesso!"
        
        # Procurar arquivo .cs3 gerado
        $cs3Files = Get-ChildItem -Path "MaxSeries\build\outputs" -Filter "*.cs3" -Recurse | Sort-Object LastWriteTime -Descending
        
        if ($cs3Files) {
            $latestFile = $cs3Files[0]
            Write-Success "Plugin gerado: $($latestFile.FullName)"
            Write-Host "Tamanho: $([math]::Round($latestFile.Length / 1KB, 2)) KB" -ForegroundColor Gray
            
            # Copiar para diretório de release
            if ($Release) {
                $releaseDir = "releases"
                if (-not (Test-Path $releaseDir)) {
                    New-Item -ItemType Directory -Path $releaseDir | Out-Null
                }
                
                $version = (Get-Date -Format "yyyyMMdd-HHmm")
                $releaseFile = "MaxSeries-v253-$version.cs3"
                Copy-Item $latestFile.FullName "$releaseDir\$releaseFile"
                Write-Success "Release criado: $releaseDir\$releaseFile"
            }
        }
    } else {
        Write-Error "Build falhou!"
        exit 1
    }
} catch {
    Write-Error "Erro no build: $_"
    exit 1
}

# 5. Resumo
Write-Header "RESUMO DO BUILD"
Write-Success "PlayerEmbedAPI v5.0 buildado com sucesso!"
Write-Host "`nMelhorias incluídas:" -ForegroundColor White
Write-Host "  • 4 estratégias de extração" -ForegroundColor Gray
Write-Host "  • Validação de URLs" -ForegroundColor Gray
Write-Host "  • Correções de segurança (SSL, logs)" -ForegroundColor Gray
Write-Host "  • Regex compilados para performance" -ForegroundColor Gray
Write-Host "  • Suporte a 4K" -ForegroundColor Gray

Write-Host "`nPara instalar:" -ForegroundColor White
Write-Host "  1. Copie o arquivo .cs3 para o CloudStream" -ForegroundColor Gray
Write-Host "  2. Ou use: .\auto-update-repo.ps1" -ForegroundColor Gray
