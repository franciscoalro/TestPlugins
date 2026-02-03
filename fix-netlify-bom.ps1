Write-Host "=== Corrigindo Problema do BOM no Netlify ===" -ForegroundColor Green
Write-Host ""

# O erro "Unknown character 65279" é o BOM (Byte Order Mark)
# Vamos recriar o netlify.toml sem BOM

$netlifyTomlPath = "cloud-deploy/netlify.toml"

# Conteudo correto sem BOM
$netlifyToml = @"
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, OPTIONS"

[[headers]]
  for = "*.json"
  [headers.values]
    Content-Type = "application/json"
    Cache-Control = "public, max-age=300"

[[headers]]
  for = "*.cs3"
  [headers.values]
    Content-Type = "application/octet-stream"
    Cache-Control = "public, max-age=3600"

[[headers]]
  for = "*.jar"
  [headers.values]
    Content-Type = "application/java-archive"
    Cache-Control = "public, max-age=3600"
"@

# Salvar sem BOM usando UTF8NoBOM
[System.IO.File]::WriteAllText($netlifyTomlPath, $netlifyToml, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ netlify.toml corrigido (sem BOM)" -ForegroundColor Green

# Verificar se o arquivo foi criado corretamente
if (Test-Path $netlifyTomlPath) {
    $bytes = [System.IO.File]::ReadAllBytes($netlifyTomlPath)
    if ($bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
        Write-Host "❌ Ainda tem BOM!" -ForegroundColor Red
    } else {
        Write-Host "✅ Sem BOM - arquivo correto!" -ForegroundColor Green
    }
}

# Recriar o ZIP sem BOM
Write-Host ""
Write-Host "Recriando ZIP corrigido..." -ForegroundColor Cyan

$zipPath = "brcloudstream-netlify-fixed.zip"

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory("cloud-deploy", $zipPath)
    
    $zipSize = (Get-Item $zipPath).Length
    $zipSizeMB = [math]::Round($zipSize / 1024 / 1024, 2)
    
    Write-Host "✅ ZIP corrigido criado!" -ForegroundColor Green
    Write-Host "Arquivo: $zipPath" -ForegroundColor Cyan
    Write-Host "Tamanho: $zipSizeMB MB" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Erro ao criar ZIP: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== SOLUCAO ALTERNATIVA ===" -ForegroundColor Green
Write-Host ""
Write-Host "Se ainda der problema, delete o netlify.toml:" -ForegroundColor Yellow
Write-Host "1. Vá na pasta cloud-deploy" -ForegroundColor Cyan
Write-Host "2. Delete o arquivo netlify.toml" -ForegroundColor Cyan
Write-Host "3. Faça upload sem esse arquivo" -ForegroundColor Cyan
Write-Host "4. O Netlify funcionará normalmente (só sem cache otimizado)" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== OPCOES DE UPLOAD ===" -ForegroundColor Green
Write-Host "1. Use o ZIP corrigido: brcloudstream-netlify-fixed.zip" -ForegroundColor Cyan
Write-Host "2. Ou arraste a pasta cloud-deploy (agora corrigida)" -ForegroundColor Cyan