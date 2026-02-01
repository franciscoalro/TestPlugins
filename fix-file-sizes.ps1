# Corrige os fileSize em plugins.json para corresponder aos tamanhos reais dos arquivos .jar

Write-Host "=== Corrigindo fileSize em plugins.json ===" -ForegroundColor Cyan

$pluginsPath = "builds/plugins.json"

if (-not (Test-Path $pluginsPath)) {
    Write-Host "❌ Arquivo $pluginsPath não encontrado!" -ForegroundColor Red
    exit 1
}

# Ler plugins.json
$plugins = Get-Content $pluginsPath | ConvertFrom-Json

$updated = 0
foreach ($plugin in $plugins) {
    $jarFile = "builds/$($plugin.internalName).jar"
    
    if (Test-Path $jarFile) {
        $actualSize = (Get-Item $jarFile).Length
        $oldSize = $plugin.fileSize
        
        if ($actualSize -ne $oldSize) {
            Write-Host "Atualizando $($plugin.internalName): $oldSize -> $actualSize bytes" -ForegroundColor Yellow
            $plugin.fileSize = $actualSize
            $updated++
        } else {
            Write-Host "✅ $($plugin.internalName): $actualSize bytes (correto)" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  $($plugin.internalName): .jar não encontrado em $jarFile" -ForegroundColor Red
    }
}

# Salvar arquivo atualizado
if ($updated -gt 0) {
    $plugins | ConvertTo-Json -Depth 10 | Set-Content $pluginsPath -Encoding UTF8
    Write-Host "`n✅ $updated plugin(s) atualizado(s)!" -ForegroundColor Green
} else {
    Write-Host "`n✅ Todos os fileSize estão corretos!" -ForegroundColor Green
}

# Mostrar resumo
Write-Host "`n=== Resumo ===" -ForegroundColor Cyan
foreach ($plugin in $plugins) {
    Write-Host "$($plugin.internalName): $($plugin.fileSize) bytes" -ForegroundColor Gray
}
