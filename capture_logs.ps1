#!/usr/bin/env powershell
<#
.SYNOPSIS
    Script para capturar logs do CloudStream (PlayerEmbedAPI v5.0)
.DESCRIPTION
    Facilita a captura de logs via ADB para debug do PlayerEmbedAPI v5.0
.EXAMPLE
    .\capture_logs.ps1
    .\capture_logs.ps1 -Filter "PlayerEmbedAPI-v5"
    .\capture_logs.ps1 -SaveTo "meus_logs.txt"
#>

param(
    [string]$Filter = "PlayerEmbedAPI",
    [string]$SaveTo = "",
    [switch]$RealTime,
    [switch]$ClearBuffer
)

$ErrorActionPreference = "Stop"

function Write-Color($Text, $Color = "White") {
    Write-Host $Text -ForegroundColor $Color
}

function Test-ADB {
    try {
        $adb = Get-Command adb -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Get-DeviceStatus {
    try {
        $devices = adb devices | Select-String "device$"
        return ($devices -ne $null)
    } catch {
        return $false
    }
}

Write-Color @"
========================================
CAPTURA DE LOGS - CloudStream
PlayerEmbedAPI v5.0 Debug
========================================
"@ "Cyan"

# Verificar ADB
Write-Color "`n[1/4] Verificando ADB..." "Yellow"
if (-not (Test-ADB)) {
    Write-Color "❌ ADB não encontrado!" "Red"
    Write-Color "Instale o Android SDK Platform Tools:" "Yellow"
    Write-Color "https://developer.android.com/studio/releases/platform-tools" "Gray"
    exit 1
}
Write-Color "✅ ADB encontrado" "Green"

# Verificar dispositivo
Write-Color "`n[2/4] Verificando dispositivo..." "Yellow"
if (-not (Get-DeviceStatus)) {
    Write-Color "❌ Nenhum dispositivo conectado!" "Red"
    Write-Color "Certifique-se de que:" "Yellow"
    Write-Color "  - USB está conectado" "Gray"
    Write-Color "  - Debug USB está ativado" "Gray"
    Write-Color "  - Permissão de debug foi concedida" "Gray"
    exit 1
}
Write-Color "✅ Dispositivo conectado" "Green"

# Limpar buffer se solicitado
if ($ClearBuffer) {
    Write-Color "`n[3/4] Limpando buffer de logs..." "Yellow"
    adb logcat -c
    Write-Color "✅ Buffer limpo" "Green"
}

# Preparar comando
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if ($SaveTo -eq "") {
    $SaveTo = "cloudstream_logs_$timestamp.txt"
}

Write-Color "`n[4/4] Configuração:" "Yellow"
Write-Color "  Filtro: $Filter" "Gray"
Write-Color "  Saída: $SaveTo" "Gray"
Write-Color "  Modo: $(if ($RealTime) { 'Tempo real' } else { 'Snapshot' })" "Gray"

Write-Color "`n========================================" "Cyan"
Write-Color "INICIANDO CAPTURA..." "Green"
Write-Color "Pressione Ctrl+C para parar" "Yellow"
Write-Color "========================================`n" "Cyan"

try {
    if ($RealTime) {
        # Modo tempo real
        adb logcat -s "${Filter}:D" | Tee-Object -FilePath $SaveTo
    } else {
        # Modo snapshot
        adb logcat -d -s "${Filter}:D" | Tee-Object -FilePath $SaveTo
        Write-Color "`n✅ Logs salvos em: $SaveTo" "Green"
        
        # Análise rápida
        $content = Get-Content $SaveTo -Raw
        
        Write-Color "`n📊 Análise Rápida:" "Cyan"
        
        if ($content -match "PlayerEmbedAPI-v5") {
            Write-Color "  ✅ PlayerEmbedAPI v5.0 detectado nos logs" "Green"
        } else {
            Write-Color "  ⚠️  PlayerEmbedAPI v5.0 NÃO encontrado" "Yellow"
        }
        
        if ($content -match "SUCESSO") {
            $count = ([regex]::Matches($content, "SUCESSO")).Count
            Write-Color "  ✅ Extrações bem-sucedidas: $count" "Green"
        }
        
        if ($content -match "Falhou|Erro|ERROR") {
            Write-Color "  ❌ Erros detectados (verifique o log)" "Red"
        }
        
        if ($content -match "Estratégia 1.*API") {
            Write-Color "  ✅ Estratégia 1 (API) foi tentada" "Green"
        }
        
        if ($content -match "ShortIcu") {
            Write-Color "  ℹ️  Fallback para ShortIcu utilizado" "Yellow"
        }
        
        if ($content -match "WebView") {
            Write-Color "  ℹ️  Fallback para WebView utilizado" "Yellow"
        }
    }
} catch {
    Write-Color "`n❌ Erro: $_" "Red"
}

Write-Color "`n========================================" "Cyan"
Write-Color "Para análise detalhada:" "Gray"
Write-Color "  python analyze_logs.py $SaveTo" "Gray"
Write-Color "========================================" "Cyan"
