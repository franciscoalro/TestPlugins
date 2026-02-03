Write-Host "=== Corrigindo URLs dos Plugins ===" -ForegroundColor Green
Write-Host ""

$netlifyUrl = "https://resilient-arithmetic-9a594e.netlify.app"

# Carregar plugins.json atual
$pluginsJsonPath = "netlify-simple/plugins.json"
$plugins = Get-Content $pluginsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "Corrigindo URLs de $($plugins.Count) plugins..." -ForegroundColor Cyan

foreach ($plugin in $plugins) {
    $oldUrl = $plugin.url
    $oldJarUrl = $plugin.jarUrl
    
    # Atualizar URLs para Netlify
    $plugin.url = "$netlifyUrl/$($plugin.internalName).cs3"
    $plugin.jarUrl = "$netlifyUrl/$($plugin.internalName).jar"
    $plugin.repositoryUrl = $netlifyUrl
    
    Write-Host "Plugin: $($plugin.name)" -ForegroundColor Yellow
    Write-Host "  CS3: $oldUrl" -ForegroundColor Red
    Write-Host "  ->   $($plugin.url)" -ForegroundColor Green
    Write-Host ""
}

# Salvar plugins.json corrigido
$pluginsJsonContent = $plugins | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($pluginsJsonPath, $pluginsJsonContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ plugins.json corrigido!" -ForegroundColor Green

# Corrigir plugins-minimal.json tambem
$pluginsMinimalPath = "netlify-simple/plugins-minimal.json"
if (Test-Path $pluginsMinimalPath) {
    $pluginsMinimal = Get-Content $pluginsMinimalPath -Raw -Encoding UTF8 | ConvertFrom-Json
    
    foreach ($plugin in $pluginsMinimal) {
        $plugin.url = "$netlifyUrl/$($plugin.internalName).cs3"
        $plugin.jarUrl = "$netlifyUrl/$($plugin.internalName).jar"
        $plugin.repositoryUrl = $netlifyUrl
    }
    
    $pluginsMinimalContent = $pluginsMinimal | ConvertTo-Json -Depth 10 -Compress:$false
    [System.IO.File]::WriteAllText($pluginsMinimalPath, $pluginsMinimalContent, [System.Text.UTF8Encoding]::new($false))
    
    Write-Host "✅ plugins-minimal.json corrigido!" -ForegroundColor Green
}

# Criar novo ZIP com URLs corrigidas
$finalZip = "brcloudstream-urls-fixed.zip"

if (Test-Path $finalZip) {
    Remove-Item $finalZip -Force
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory("netlify-simple", $finalZip)
    
    $zipSize = (Get-Item $finalZip).Length
    $zipSizeMB = [math]::Round($zipSize / 1024 / 1024, 2)
    
    Write-Host ""
    Write-Host "✅ ZIP final criado!" -ForegroundColor Green
    Write-Host "Arquivo: $finalZip ($zipSizeMB MB)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Erro ao criar ZIP: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== AGORA FAÇA O DEPLOY FINAL ===" -ForegroundColor Green
Write-Host "1. Vá para: https://app.netlify.com/sites/resilient-arithmetic-9a594e" -ForegroundColor Cyan
Write-Host "2. Clique em 'Deploys'" -ForegroundColor Cyan
Write-Host "3. Arraste o arquivo '$finalZip'" -ForegroundColor Cyan
Write-Host "4. Aguarde o deploy" -ForegroundColor Cyan
Write-Host "5. Teste no Cloudstream!" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Agora todos os URLs apontam para o Netlify!" -ForegroundColor Yellow