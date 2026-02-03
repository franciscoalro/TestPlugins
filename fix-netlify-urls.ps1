Write-Host "=== Corrigindo URLs para Netlify ===" -ForegroundColor Green
Write-Host ""

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

# Salvar repo.json corrigido
$repoJsonContent = $repoJson | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText("netlify-simple/repo.json", $repoJsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ repo.json corrigido para apontar para Netlify" -ForegroundColor Green

# Corrigir plugins.json para usar URLs do Netlify
$pluginsJsonPath = "netlify-simple/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($plugin in $plugins) {
    $plugin.url = "$netlifyUrl/$($plugin.internalName).cs3"
    $plugin.jarUrl = "$netlifyUrl/$($plugin.internalName).jar"
    $plugin.repositoryUrl = $netlifyUrl
}

# Salvar plugins.json corrigido
$pluginsJsonContent = $plugins | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($pluginsJsonPath, $pluginsJsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ plugins.json corrigido para usar URLs do Netlify" -ForegroundColor Green

# Corrigir repo-alternative.json
$repoAltJson = @{
    "name" = "BRCloudStream Repo (Alternative)"
    "iconUrl" = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/icon.png"
    "description" = "Repositorio brasileiro - versao alternativa"
    "manifestVersion" = 1
    "pluginLists" = @(
        "$netlifyUrl/plugins-minimal.json"
    )
}

$repoAltJsonContent = $repoAltJson | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText("netlify-simple/repo-alternative.json", $repoAltJsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ repo-alternative.json corrigido" -ForegroundColor Green

# Corrigir plugins-minimal.json
$pluginsMinimalPath = "netlify-simple/plugins-minimal.json"
$pluginsMinimal = Get-Content $pluginsMinimalPath -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($plugin in $pluginsMinimal) {
    $plugin.url = "$netlifyUrl/$($plugin.internalName).cs3"
    $plugin.jarUrl = "$netlifyUrl/$($plugin.internalName).jar"
    $plugin.repositoryUrl = $netlifyUrl
}

$pluginsMinimalContent = $pluginsMinimal | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($pluginsMinimalPath, $pluginsMinimalContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ plugins-minimal.json corrigido" -ForegroundColor Green

# Atualizar index.html
$indexHtml = @"
<!DOCTYPE html>
<html>
<head>
    <title>BRCloudStream Repository</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
        .container { max-width: 600px; margin: 0 auto; text-align: center; }
        .url { background: #333; padding: 15px; margin: 20px 0; border-radius: 5px; font-family: monospace; word-break: break-all; }
        .button { background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
        .copy-btn { background: #2196F3; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🇧🇷 BRCloudStream Repository</h1>
        <p>Repositório brasileiro para Cloudstream</p>
        
        <h2>📱 URL para Cloudstream:</h2>
        <div class="url" id="repoUrl">$netlifyUrl/repo.json</div>
        <button class="copy-btn" onclick="copyUrl()">Copiar URL</button>
        
        <h2>🔗 Links:</h2>
        <a href="./repo.json" class="button">repo.json</a>
        <a href="./plugins.json" class="button">plugins.json</a>
        <a href="./repo-alternative.json" class="button">alternativo</a>
        
        <p>✅ 11 plugins disponíveis<br>
        ✅ Hospedado no Netlify<br>
        ✅ Pronto para usar no Cloudstream</p>
        
        <h3>🎮 Plugins Incluídos:</h3>
        <p>MaxSeries • AnimesOnlineCC • Doramas • NovelasFlix<br>
        DonghuaNoSekai • EmbedCanais • MegaFlix • NetCine<br>
        OverFlix • PobreFlix • Vizer</p>
    </div>
    
    <script>
        function copyUrl() {
            const url = document.getElementById('repoUrl').textContent;
            navigator.clipboard.writeText(url).then(() => {
                alert('URL copiada para a área de transferência!');
            });
        }
    </script>
</body>
</html>
"@

Set-Content -Path "netlify-simple/index.html" -Value $indexHtml -Encoding UTF8

Write-Host "✅ index.html atualizado" -ForegroundColor Green

# Criar novo ZIP corrigido
$correctedZip = "brcloudstream-netlify-corrected.zip"

if (Test-Path $correctedZip) {
    Remove-Item $correctedZip -Force
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory("netlify-simple", $correctedZip)
    
    $zipSize = (Get-Item $correctedZip).Length
    $zipSizeMB = [math]::Round($zipSize / 1024 / 1024, 2)
    
    Write-Host ""
    Write-Host "✅ ZIP corrigido criado!" -ForegroundColor Green
    Write-Host "Arquivo: $correctedZip ($zipSizeMB MB)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Erro ao criar ZIP: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== PRÓXIMOS PASSOS ===" -ForegroundColor Green
Write-Host "1. Vá para o Netlify: https://app.netlify.com/sites/resilient-arithmetic-9a594e" -ForegroundColor Cyan
Write-Host "2. Clique em 'Deploys'" -ForegroundColor Cyan
Write-Host "3. Arraste o arquivo '$correctedZip' para fazer novo deploy" -ForegroundColor Cyan
Write-Host "4. Aguarde o deploy" -ForegroundColor Cyan
Write-Host "5. Teste a URL: $netlifyUrl/repo.json" -ForegroundColor Cyan