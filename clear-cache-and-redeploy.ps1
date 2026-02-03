# Limpa cache e faz redeploy
param([string]$CacheBustReason = "Cache clear")

Write-Host "=== Limpando Cache e Redeploy ===" -ForegroundColor Cyan

# Limpar URLs (remover cache-busting)
$plugins = Get-Content "builds/plugins.json" | ConvertFrom-Json

foreach ($plugin in $plugins) {
    # Remover query params
    $plugin.jarUrl = $plugin.jarUrl -replace "\?v=.*", ""
    $plugin.url = $plugin.url -replace "\?v=.*", ""
    $plugin.iconUrl = $plugin.iconUrl -replace "\?v=.*", ""
}

$plugins | ConvertTo-Json -Depth 10 | Set-Content "builds/plugins.json" -Encoding UTF8
Write-Host "URLs limpas (sem cache-busting)" -ForegroundColor Green

# Atualizar repo.json (sem cache-busting)
$repo = Get-Content "repo.json" | ConvertFrom-Json
$repo.pluginLists[0] = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json"
$repo | ConvertTo-Json -Depth 10 | Set-Content "repo.json" -Encoding UTF8
Write-Host "repo.json atualizado" -ForegroundColor Green

# Commit local
git add builds/plugins.json repo.json
git commit -m "Clean URLs for cache bust: $CacheBustReason" 2>$null

# Deploy
powershell -ExecutionPolicy Bypass -File deploy-to-cloudstream-manual.ps1 -Message $CacheBustReason
