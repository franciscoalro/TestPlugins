Write-Host "=== Deploy no Netlify - Guia Completo ===" -ForegroundColor Green
Write-Host ""

# Verificar se a pasta cloud-deploy existe
if (-not (Test-Path "cloud-deploy")) {
    Write-Host "❌ Pasta cloud-deploy nao encontrada!" -ForegroundColor Red
    Write-Host "Execute primeiro: ./create-cloud-alternatives.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Pasta cloud-deploy encontrada" -ForegroundColor Green
Write-Host ""

# Criar arquivo _redirects para Netlify (importante para SPAs)
$redirects = @"
# Redirects para compatibilidade
/plugins /plugins.json 200
/repo /repo.json 200

# Headers para CORS
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, OPTIONS
  Access-Control-Allow-Headers: Content-Type
"@

Set-Content -Path "cloud-deploy/_redirects" -Value $redirects -Encoding UTF8

# Otimizar netlify.toml
$netlifyToml = @"
[build]
  publish = "."

[build.environment]
  NODE_VERSION = "18"

[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type"

[[headers]]
  for = "*.json"
  [headers.values]
    Content-Type = "application/json; charset=utf-8"
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

[[redirects]]
  from = "/plugins"
  to = "/plugins.json"
  status = 200

[[redirects]]
  from = "/repo"
  to = "/repo.json"
  status = 200
"@

Set-Content -Path "cloud-deploy/netlify.toml" -Value $netlifyToml -Encoding UTF8

# Criar arquivo de configuracao adicional
$packageJson = @{
    "name" = "brcloudstream-repo"
    "version" = "1.0.0"
    "description" = "Repositorio brasileiro para Cloudstream"
    "scripts" = @{
        "build" = "echo 'Build completed'"
    }
}

$packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path "cloud-deploy/package.json" -Encoding UTF8

Write-Host "✅ Arquivos do Netlify otimizados" -ForegroundColor Green
Write-Host ""

# Listar arquivos finais
Write-Host "=== Arquivos prontos para Netlify ===" -ForegroundColor Cyan
$totalSize = 0
Get-ChildItem "cloud-deploy" | Sort-Object Name | ForEach-Object {
    if (-not $_.PSIsContainer) {
        $sizeKB = [math]::Round($_.Length / 1024, 1)
        $totalSize += $_.Length
        
        $icon = switch ($_.Extension) {
            ".json" { "📄" }
            ".cs3" { "📦" }
            ".jar" { "☕" }
            ".html" { "🌐" }
            ".toml" { "⚙️" }
            ".md" { "📝" }
            default { "📄" }
        }
        
        Write-Host "  $icon $($_.Name) - $sizeKB KB" -ForegroundColor Yellow
    }
}

$totalSizeMB = [math]::Round($totalSize / 1024 / 1024, 2)
Write-Host ""
Write-Host "📊 Total: $totalSizeMB MB" -ForegroundColor Green
Write-Host ""

Write-Host "=== COMO FAZER DEPLOY NO NETLIFY ===" -ForegroundColor Green
Write-Host ""

Write-Host "MÉTODO 1 - Drag & Drop (Mais Fácil):" -ForegroundColor Cyan
Write-Host "1. Acesse: https://netlify.com" -ForegroundColor White
Write-Host "2. Clique em 'Sign up' ou 'Log in'" -ForegroundColor White
Write-Host "3. Faça login com GitHub, Google ou email" -ForegroundColor White
Write-Host "4. Na dashboard, procure por 'Want to deploy a new site without connecting to Git?'" -ForegroundColor White
Write-Host "5. Clique em 'Browse to upload'" -ForegroundColor White
Write-Host "6. Selecione TODA a pasta 'cloud-deploy' e arraste para o site" -ForegroundColor White
Write-Host "7. Aguarde o upload e deploy" -ForegroundColor White
Write-Host ""

Write-Host "MÉTODO 2 - Via Git (Recomendado para atualizações):" -ForegroundColor Cyan
Write-Host "1. Crie um repositório no GitHub com os arquivos da pasta 'cloud-deploy'" -ForegroundColor White
Write-Host "2. No Netlify, clique em 'New site from Git'" -ForegroundColor White
Write-Host "3. Conecte com GitHub e selecione o repositório" -ForegroundColor White
Write-Host "4. Configure:" -ForegroundColor White
Write-Host "   - Build command: (deixe vazio)" -ForegroundColor Gray
Write-Host "   - Publish directory: (deixe vazio ou '.')" -ForegroundColor Gray
Write-Host "5. Clique em 'Deploy site'" -ForegroundColor White
Write-Host ""

Write-Host "=== APÓS O DEPLOY ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. O Netlify gerará uma URL como:" -ForegroundColor Yellow
Write-Host "   https://NOME-ALEATORIO.netlify.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Você pode personalizar o nome em:" -ForegroundColor Yellow
Write-Host "   Site settings > Change site name" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Sua URL final para o Cloudstream será:" -ForegroundColor Yellow
Write-Host "   https://SEU-NOME.netlify.app/repo.json" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== TESTE APÓS DEPLOY ===" -ForegroundColor Green
Write-Host ""
Write-Host "Teste estas URLs no navegador:" -ForegroundColor Yellow
Write-Host "✅ https://SEU-SITE.netlify.app/repo.json" -ForegroundColor Cyan
Write-Host "✅ https://SEU-SITE.netlify.app/plugins.json" -ForegroundColor Cyan
Write-Host "✅ https://SEU-SITE.netlify.app/MaxSeries.cs3" -ForegroundColor Cyan
Write-Host "✅ https://SEU-SITE.netlify.app (página principal)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== VANTAGENS DO NETLIFY ===" -ForegroundColor Green
Write-Host "✅ Gratuito até 100GB de tráfego/mês" -ForegroundColor Green
Write-Host "✅ HTTPS automático" -ForegroundColor Green
Write-Host "✅ CDN global (rápido no mundo todo)" -ForegroundColor Green
Write-Host "✅ Deploy automático via Git" -ForegroundColor Green
Write-Host "✅ Headers CORS configurados" -ForegroundColor Green
Write-Host "✅ Cache otimizado" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 PRONTO! Agora faça o upload da pasta 'cloud-deploy' no Netlify!" -ForegroundColor Green