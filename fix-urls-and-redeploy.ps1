# Corrige URLs para usar formato refs/heads/main (igual saimuelrepo)
param([string]$Message = "Fix URLs format")

Write-Host "=== Corrigindo URLs para formato refs/heads/main ===" -ForegroundColor Cyan

# Ler plugins.json
$plugins = Get-Content "builds/plugins.json" | ConvertFrom-Json

foreach ($plugin in $plugins) {
    # Atualizar URLs para usar refs/heads/main
    $plugin.jarUrl = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/$($plugin.internalName).jar"
    $plugin.url = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/$($plugin.internalName).cs3"
    $plugin.repositoryUrl = "https://github.com/franciscoalro/CloudstreamRepo"
    Write-Host "Atualizado: $($plugin.internalName)" -ForegroundColor Gray
}

$plugins | ConvertTo-Json -Depth 10 | Set-Content "builds/plugins.json" -Encoding UTF8
Write-Host "plugins.json atualizado" -ForegroundColor Green

# Atualizar repo.json
$repo = Get-Content "repo.json" | ConvertFrom-Json
$repo.pluginLists[0] = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/refs/heads/main/builds/plugins.json"
$repo | ConvertTo-Json -Depth 10 | Set-Content "repo.json" -Encoding UTF8
Write-Host "repo.json atualizado" -ForegroundColor Green

# Commit
git add builds/plugins.json repo.json
git commit -m "Fix URLs: use refs/heads/main format like saimuelrepo" 2>$null

# Deploy
powershell -ExecutionPolicy Bypass -File deploy-to-cloudstream-manual.ps1 -Message $Message
