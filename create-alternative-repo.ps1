Write-Host "=== Criando Repositorio Alternativo ===" -ForegroundColor Green
Write-Host ""

# Criar uma versao ainda mais compativel do repositorio
$pluginsJsonPath = "builds/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json

# Criar versao minimalista do plugins.json
$minimalPlugins = @()

foreach ($plugin in $plugins) {
    $minimalPlugin = @{
        "name" = $plugin.name
        "internalName" = $plugin.internalName
        "version" = $plugin.version
        "url" = $plugin.url
        "jarUrl" = $plugin.jarUrl
        "apiVersion" = 1
        "status" = 1
        "language" = "pt"
        "authors" = @("franciscoalro")
        "tvTypes" = $plugin.tvTypes
        "fileSize" = $plugin.fileSize
        "description" = $plugin.description
        "iconUrl" = $plugin.iconUrl
        "repositoryUrl" = "https://github.com/franciscoalro/CloudstreamRepo"
    }
    
    $minimalPlugins += $minimalPlugin
}

# Salvar versao minimalista
$minimalJson = $minimalPlugins | ConvertTo-Json -Depth 10 -Compress
[System.IO.File]::WriteAllText("builds/plugins-minimal.json", $minimalJson, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ plugins-minimal.json criado" -ForegroundColor Green

# Criar repo alternativo
$alternativeRepo = @{
    "name" = "BRCloudStream Repo (Alternative)"
    "iconUrl" = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/icon.png"
    "description" = "Repositorio brasileiro - versao alternativa"
    "manifestVersion" = 1
    "pluginLists" = @(
        "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins-minimal.json"
    )
}

$repoJson = $alternativeRepo | ConvertTo-Json -Depth 10 -Compress
[System.IO.File]::WriteAllText("builds/repo-alternative.json", $repoJson, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ repo-alternative.json criado" -ForegroundColor Green

Write-Host ""
Write-Host "=== URLs Alternativas ===" -ForegroundColor Cyan
Write-Host "Principal: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json" -ForegroundColor Green
Write-Host "Alternativa: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo-alternative.json" -ForegroundColor Yellow

Write-Host ""
Write-Host "Use a URL alternativa se a principal nao funcionar!" -ForegroundColor Yellow