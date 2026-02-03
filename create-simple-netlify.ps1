Write-Host "=== Criando Versao Simples para Netlify ===" -ForegroundColor Green
Write-Host ""

# Criar pasta simples sem arquivos de configuracao problematicos
$simpleDir = "netlify-simple"

if (Test-Path $simpleDir) {
    Remove-Item $simpleDir -Recurse -Force
}

New-Item -ItemType Directory -Path $simpleDir | Out-Null

# Copiar apenas os arquivos essenciais
$essentialFiles = @(
    "builds/repo.json",
    "builds/plugins.json", 
    "builds/repo-alternative.json",
    "builds/plugins-minimal.json",
    "builds/*.cs3",
    "builds/*.jar"
)

foreach ($pattern in $essentialFiles) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Copy-Item $file.FullName "$simpleDir/$($file.Name)" -Force
        Write-Host "Copiado: $($file.Name)" -ForegroundColor Green
    }
}

# Criar index.html simples
$simpleIndex = @"
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🇧🇷 BRCloudStream Repository</h1>
        <p>Repositório brasileiro para Cloudstream</p>
        
        <h2>📱 URL para Cloudstream:</h2>
        <div class="url" id="repoUrl">https://SEU-SITE.netlify.app/repo.json</div>
        
        <h2>🔗 Links:</h2>
        <a href="./repo.json" class="button">repo.json</a>
        <a href="./plugins.json" class="button">plugins.json</a>
        
        <p>✅ 11 plugins disponíveis<br>
        ✅ Pronto para usar no Cloudstream</p>
    </div>
</body>
</html>
"@

Set-Content -Path "$simpleDir/index.html" -Value $simpleIndex -Encoding UTF8

# Criar ZIP simples
$simpleZip = "brcloudstream-simple.zip"

if (Test-Path $simpleZip) {
    Remove-Item $simpleZip -Force
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($simpleDir, $simpleZip)
    
    $zipSize = (Get-Item $simpleZip).Length
    $zipSizeMB = [math]::Round($zipSize / 1024 / 1024, 2)
    
    Write-Host ""
    Write-Host "✅ Versao simples criada!" -ForegroundColor Green
    Write-Host "Pasta: $simpleDir" -ForegroundColor Cyan
    Write-Host "ZIP: $simpleZip ($zipSizeMB MB)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Erro ao criar ZIP: $_" -ForegroundColor Red
}

# Listar arquivos
Write-Host ""
Write-Host "Arquivos na versao simples:" -ForegroundColor Yellow
Get-ChildItem $simpleDir | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1024, 1)
    Write-Host "  $($_.Name) - $sizeKB KB" -ForegroundColor White
}

Write-Host ""
Write-Host "=== COMO USAR ===" -ForegroundColor Green
Write-Host "1. Arraste a pasta '$simpleDir' OU o arquivo '$simpleZip' para o Netlify" -ForegroundColor Cyan
Write-Host "2. Esta versao NAO tem arquivos de configuracao problematicos" -ForegroundColor Cyan
Write-Host "3. Deve funcionar sem erros!" -ForegroundColor Cyan