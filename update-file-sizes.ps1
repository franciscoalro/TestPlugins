Write-Host "=== Atualizando Tamanhos dos Arquivos ===" -ForegroundColor Green
Write-Host ""

$pluginsJsonPath = "builds/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json

$updated = $false

foreach ($plugin in $plugins) {
    $cs3File = "builds/$($plugin.internalName).cs3"
    
    if (Test-Path $cs3File) {
        $actualSize = (Get-Item $cs3File).Length
        $currentSize = $plugin.fileSize
        
        if ($actualSize -ne $currentSize) {
            Write-Host "Atualizando $($plugin.internalName): $currentSize -> $actualSize bytes" -ForegroundColor Yellow
            $plugin.fileSize = $actualSize
            $updated = $true
        } else {
            Write-Host "$($plugin.internalName): Tamanho correto ($actualSize bytes)" -ForegroundColor Green
        }
    }
}

if ($updated) {
    # Salvar o plugins.json atualizado
    $plugins | ConvertTo-Json -Depth 10 | Set-Content $pluginsJsonPath -Encoding UTF8
    
    # Copiar para a raiz tambem
    Copy-Item $pluginsJsonPath "plugins.json" -Force
    
    Write-Host ""
    Write-Host "✅ plugins.json atualizado com os novos tamanhos!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✅ Todos os tamanhos ja estavam corretos!" -ForegroundColor Green
}