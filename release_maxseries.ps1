param(
    [Parameter(Mandatory = $true)]
    [int]$Version,
    [string]$Description = $( "MaxSeries v$Version release" ),
    [switch]$SkipBuild,
    [switch]$SkipPush
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "== MaxSeries release v$Version ==" -ForegroundColor Cyan

if (-not $SkipBuild) {
    Write-Host "Building cs3..." -ForegroundColor Yellow
    .\gradlew.bat :MaxSeries:assembleDebug --no-daemon --no-build-cache
}

$cs3Src  = Join-Path $root "MaxSeries\build\MaxSeries.cs3"
$cs3Dest = Join-Path $root "MaxSeries.cs3"

if (-not (Test-Path $cs3Src)) {
    throw "cs3 não encontrado em $cs3Src. Rode o build ou use -SkipBuild apenas se já existir."
}

Copy-Item $cs3Src $cs3Dest -Force
$size = (Get-Item $cs3Dest).Length

Write-Host "cs3 copiado. Tamanho: $size bytes" -ForegroundColor Green

# Atualiza plugins.json
$pluginsPath = Join-Path $root "plugins.json"
$json = Get-Content $pluginsPath -Raw | ConvertFrom-Json
$plugin = $json[0]
$plugin.version      = $Version
$plugin.description  = $Description
$plugin.fileSize     = $size

$json | ConvertTo-Json -Depth 10 | Set-Content $pluginsPath -Encoding UTF8
Write-Host "plugins.json atualizado (versão=$Version, fileSize=$size)" -ForegroundColor Green

# Git add/commit/push
git add $cs3Dest $pluginsPath | Out-Null
$commitMsg = "Release MaxSeries v$Version"
git commit -m "$commitMsg" | Out-Null
Write-Host "Commit criado: $commitMsg" -ForegroundColor Green

if (-not $SkipPush) {
    git push
    Write-Host "Push concluído." -ForegroundColor Green
} else {
    Write-Host "Push pulado (-SkipPush)." -ForegroundColor Yellow
}

Write-Host "Release finalizado." -ForegroundColor Cyan
