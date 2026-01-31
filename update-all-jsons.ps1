# Script para atualizar todos os JSONs para nova versão
# Uso: .\update-all-jsons.ps1 -Version 256 -Tag "v256"

param(
    [int]$Version = 256,
    [string]$Tag = "v256",
    [string]$Description = "MaxSeries v256 - PlayerEmbedAPI V8+V7 Fixes (Pure HTTP + WebView Optimized, Timeout 25s, 12 URL Patterns)",
    [int]$FileSize = 654000
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZANDO JSONS PARA v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$UpdateCount = 0

# Função para atualizar JSON
def Update-JsonFile($FilePath, $JsonContent) {
    $JsonContent | ConvertTo-Json -Depth 10 | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Atualizado: $FilePath" -ForegroundColor Green
    $script:UpdateCount++
}

# 1. plugins.json
$pluginsPath = "plugins.json"
if (Test-Path $pluginsPath) {
    Write-Host "`n📝 Processando $pluginsPath..." -ForegroundColor Yellow
    $content = Get-Content $pluginsPath -Raw | ConvertFrom-Json
    $maxseries = $content | Where-Object { $_.name -eq "MaxSeries" }
    if ($maxseries) {
        $maxseries.version = $Version
        $maxseries.url = "https://github.com/franciscoalro/TestPlugins/releases/download/$Tag/MaxSeries.cs3"
        $maxseries.fileSize = $FileSize
        $maxseries.description = $Description
        Update-JsonFile $pluginsPath $content
    }
}

# 2. plugins-complete.json
$pluginsCompletePath = "plugins-complete.json"
if (Test-Path $pluginsCompletePath) {
    Write-Host "`n📝 Processando $pluginsCompletePath..." -ForegroundColor Yellow
    $content = Get-Content $pluginsCompletePath -Raw | ConvertFrom-Json
    $maxseries = $content | Where-Object { $_.name -eq "MaxSeries" }
    if ($maxseries) {
        $maxseries.version = $Version
        $maxseries.url = "https://github.com/franciscoalro/TestPlugins/releases/download/$Tag/MaxSeries.cs3"
        $maxseries.description = $Description
        Update-JsonFile $pluginsCompletePath $content
    }
}

# 3. repo.json
$repoPath = "repo.json"
if (Test-Path $repoPath) {
    Write-Host "`n📝 Processando $repoPath..." -ForegroundColor Yellow
    $content = Get-Content $repoPath -Raw | ConvertFrom-Json
    $content.description = "Repositorio completo de extensoes brasileiras para Cloudstream - MaxSeries v$Version (PlayerEmbedAPI V8+V7 Fixes)"
    Update-JsonFile $repoPath $content
}

# 4. repo-complete.json
$repoCompletePath = "repo-complete.json"
if (Test-Path $repoCompletePath) {
    Write-Host "`n📝 Processando $repoCompletePath..." -ForegroundColor Yellow
    $content = Get-Content $repoCompletePath -Raw | ConvertFrom-Json
    $content.description = "Repositório completo de extensões brasileiras para Cloudstream - MaxSeries v$Version com PlayerEmbedAPI V8+V7 Fixes"
    Update-JsonFile $repoCompletePath $content
}

# 5. plugins-simple.json
$pluginsSimplePath = "plugins-simple.json"
if (Test-Path $pluginsSimplePath) {
    Write-Host "`n📝 Processando $pluginsSimplePath..." -ForegroundColor Yellow
    $content = Get-Content $pluginsSimplePath -Raw | ConvertFrom-Json
    if ($content -is [System.Array]) {
        $maxseries = $content | Where-Object { $_.name -eq "MaxSeries" }
    } else {
        $maxseries = $content.MaxSeries
    }
    if ($maxseries) {
        $maxseries.version = $Version
        $maxseries.url = "https://github.com/franciscoalro/TestPlugins/releases/download/$Tag/MaxSeries.cs3"
        $maxseries.description = $Description
        Update-JsonFile $pluginsSimplePath $content
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  $UpdateCount ARQUIVOS ATUALIZADOS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nVersão: v$Version" -ForegroundColor White
Write-Host "Tag: $Tag" -ForegroundColor White
Write-Host "Descrição: $Description" -ForegroundColor Gray
