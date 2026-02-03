Write-Host "=== Deploy no Netlify - Guia Completo ===" -ForegroundColor Green
Write-Host ""

# Verificar se a pasta cloud-deploy existe
if (-not (Test-Path "cloud-deploy")) {
    Write-Host "Pasta cloud-deploy nao encontrada!" -ForegroundColor Red
    Write-Host "Execute primeiro: ./create-cloud-alternatives.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Pasta cloud-deploy encontrada" -ForegroundColor Green
Write-Host ""

# Criar arquivo _redirects para Netlify
$redirects = @"
# Redirects para compatibilidade
/plugins /plugins.json 200
/repo /repo.json 200
"@

Set-Content -Path "cloud-deploy/_redirects" -Value $redirects -Encoding UTF8

# Otimizar netlify.toml
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

Set-Content -Path "cloud-deploy/netlify.toml" -Value $netlifyToml -Encoding UTF8

Write-Host "Arquivos do Netlify otimizados" -ForegroundColor Green
Write-Host ""

# Listar arquivos finais
Write-Host "=== Arquivos prontos para Netlify ===" -ForegroundColor Cyan
$totalSize = 0
Get-ChildItem "cloud-deploy" | Sort-Object Name | ForEach-Object {
    if (-not $_.PSIsContainer) {
        $sizeKB = [math]::Round($_.Length / 1024, 1)
        $totalSize += $_.Length
        Write-Host "  $($_.Name) - $sizeKB KB" -ForegroundColor Yellow
    }
}

$totalSizeMB = [math]::Round($totalSize / 1024 / 1024, 2)
Write-Host ""
Write-Host "Total: $totalSizeMB MB" -ForegroundColor Green
Write-Host ""

Write-Host "=== COMO FAZER DEPLOY NO NETLIFY ===" -ForegroundColor Green
Write-Host ""

Write-Host "PASSO A PASSO:" -ForegroundColor Cyan
Write-Host "1. Acesse: https://netlify.com" -ForegroundColor White
Write-Host "2. Clique em 'Sign up' (criar conta) ou 'Log in' (entrar)" -ForegroundColor White
Write-Host "3. Faca login com GitHub, Google ou email" -ForegroundColor White
Write-Host "4. Na dashboard, procure 'Want to deploy a new site without connecting to Git?'" -ForegroundColor White
Write-Host "5. Clique em 'Browse to upload'" -ForegroundColor White
Write-Host "6. Selecione TODA a pasta 'cloud-deploy' e arraste para o site" -ForegroundColor White
Write-Host "7. Aguarde o upload e deploy (alguns minutos)" -ForegroundColor White
Write-Host ""

Write-Host "=== APOS O DEPLOY ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. O Netlify gerara uma URL como:" -ForegroundColor Yellow
Write-Host "   https://NOME-ALEATORIO.netlify.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Voce pode personalizar o nome em:" -ForegroundColor Yellow
Write-Host "   Site settings > Change site name" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Sua URL final para o Cloudstream sera:" -ForegroundColor Yellow
Write-Host "   https://SEU-NOME.netlify.app/repo.json" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== TESTE APOS DEPLOY ===" -ForegroundColor Green
Write-Host ""
Write-Host "Teste estas URLs no navegador:" -ForegroundColor Yellow
Write-Host "- https://SEU-SITE.netlify.app/repo.json" -ForegroundColor Cyan
Write-Host "- https://SEU-SITE.netlify.app/plugins.json" -ForegroundColor Cyan
Write-Host "- https://SEU-SITE.netlify.app/MaxSeries.cs3" -ForegroundColor Cyan
Write-Host "- https://SEU-SITE.netlify.app (pagina principal)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== VANTAGENS DO NETLIFY ===" -ForegroundColor Green
Write-Host "- Gratuito ate 100GB de trafego/mes" -ForegroundColor Green
Write-Host "- HTTPS automatico" -ForegroundColor Green
Write-Host "- CDN global (rapido no mundo todo)" -ForegroundColor Green
Write-Host "- Headers CORS configurados" -ForegroundColor Green
Write-Host "- Cache otimizado" -ForegroundColor Green
Write-Host ""

Write-Host "PRONTO! Agora faca o upload da pasta 'cloud-deploy' no Netlify!" -ForegroundColor Green