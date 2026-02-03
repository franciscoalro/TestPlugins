Write-Host "=== Correcao Rapida ===" -ForegroundColor Green

$netlifyUrl = "https://resilient-arithmetic-9a594e.netlify.app"

# Corrigir repo.json
$repoJson = @{
    "name" = "BRCloudStream Repo"
    "iconUrl" = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/icon.png"
    "description" = "Repositorio brasileiro com filmes, series, animes, doramas, novelas e TV ao vivo"
    "manifestVersion" = 1
    "pluginLists" = @(
        "$netlifyUrl/plugins.json"
    )
}

$repoJsonContent = $repoJson | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText("netlify-simple/repo.json", $repoJsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "repo.json corrigido" -ForegroundColor Green

# Criar ZIP
$correctedZip = "brcloudstream-netlify-final.zip"
if (Test-Path $correctedZip) { Remove-Item $correctedZip -Force }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory("netlify-simple", $correctedZip)

Write-Host "ZIP criado: $correctedZip" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Va para: https://app.netlify.com/sites/resilient-arithmetic-9a594e" -ForegroundColor Cyan
Write-Host "2. Clique em 'Deploys'" -ForegroundColor Cyan
Write-Host "3. Arraste o arquivo '$correctedZip'" -ForegroundColor Cyan