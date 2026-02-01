# Script de upload para GitHub Releases
# Execute este script com seu token pessoal

$token = Read-Host "Digite seu token do GitHub (ghp_...)" -AsSecureString
$tokenPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))

Write-Host "`n[1/3] Verificando arquivo..." -ForegroundColor Yellow
$hash = (Get-FileHash "releases\MaxSeries.cs3" -Algorithm SHA256).Hash
Write-Host "   SHA256: $hash" -ForegroundColor White

Write-Host "`n[2/3] Criando/Verificando release v257..." -ForegroundColor Yellow

try {
    $releaseCheck = Invoke-RestMethod -Uri "https://api.github.com/repos/franciscoalro/TestPlugins/releases/tags/v257" `
        -Method Get -Headers @{ "Authorization" = "token $tokenPlain" }
    $releaseId = $releaseCheck.id
    Write-Host "   Release existe (ID: $releaseId)" -ForegroundColor Green
    
    # Deletar asset antigo
    $assetExists = $releaseCheck.assets | Where-Object { $_.name -eq "MaxSeries.cs3" }
    if ($assetExists) {
        Write-Host "   Deletando asset antigo..." -ForegroundColor Yellow
        Invoke-RestMethod -Uri "https://api.github.com/repos/franciscoalro/TestPlugins/releases/assets/$($assetExists.id)" `
            -Method Delete -Headers @{ "Authorization" = "token $tokenPlain" }
    }
} catch {
    Write-Host "   Criando novo release..." -ForegroundColor Yellow
    $body = @{
        tag_name = "v257"
        name = "MaxSeries v257"
        body = "MaxSeries v257 - PlayerEmbedAPI V8+V7 Fixes`n- R.txt: 121 bytes`n- SHA256: E1464E76...D5216"
        draft = $false
        prerelease = $false
    } | ConvertTo-Json
    
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/franciscoalro/TestPlugins/releases" `
        -Method Post -Headers @{ "Authorization" = "token $tokenPlain"; "Content-Type" = "application/json" } `
        -Body $body
    $releaseId = $release.id
}

Write-Host "`n[3/3] Fazendo upload..." -ForegroundColor Yellow
$uploadUrl = "https://uploads.github.com/repos/franciscoalro/TestPlugins/releases/$releaseId/assets?name=MaxSeries.cs3"
$fileBytes = [System.IO.File]::ReadAllBytes("releases\MaxSeries.cs3")

$response = Invoke-RestMethod -Uri $uploadUrl -Method Post `
    -Headers @{ "Authorization" = "token $tokenPlain"; "Content-Type" = "application/octet-stream" } `
    -Body $fileBytes

Write-Host "   Upload concluído!" -ForegroundColor Green
Write-Host "   URL: $($response.browser_download_url)" -ForegroundColor White

# Limpar token da memória
$tokenPlain = $null
[System.GC]::Collect()

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  UPLOAD COMPLETO!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
