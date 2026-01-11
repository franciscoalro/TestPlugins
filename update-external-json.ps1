#!/usr/bin/env pwsh
# Script para atualizar JSON externo - MaxSeries v51

$externalJsonUrl = "https://s8v3.veritasholdings.cyou/v4/ic/6pyw8t/cf-master.1767387020.txt"
$currentVersion = "51"
$currentTag = "v51.0"

Write-Host "🔄 ATUALIZANDO JSON EXTERNO - MaxSeries v$currentVersion" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "📍 URL Externa: $externalJsonUrl" -ForegroundColor Cyan

# Verificar se a URL está acessível
Write-Host "`n🔍 Verificando acesso à URL externa..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $externalJsonUrl -Method HEAD -ErrorAction Stop
    Write-Host "✅ URL acessível - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ URL não acessível: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "⚠️ Possíveis causas:" -ForegroundColor Yellow
    Write-Host "   - Servidor temporariamente indisponível" -ForegroundColor White
    Write-Host "   - Necessário autenticação/token" -ForegroundColor White
    Write-Host "   - URL mudou ou foi removida" -ForegroundColor White
    
    # Continuar mesmo assim para documentar o processo
}

# Criar payload JSON atualizado
$jsonPayload = @{
    "name" = "MaxSeries"
    "version" = $currentVersion
    "tag" = $currentTag
    "description" = "MaxSeries v$currentVersion - Anti-YouTube Filter: Filtro inteligente que ignora automaticamente links do YouTube, focando apenas em players de vídeo válidos (MegaEmbed, PlayerEmbedAPI, DoodStream)."
    "url" = "https://github.com/franciscoalro/TestPlugins/releases/download/$currentTag/MaxSeries.cs3"
    "repositoryUrl" = "https://github.com/franciscoalro/TestPlugins"
    "authors" = @("franciscoalro")
    "language" = "pt-BR"
    "tvTypes" = @("TvSeries", "Movie")
    "status" = 1
    "apiVersion" = 1
    "isAdult" = $false
    "iconUrl" = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
    "lastUpdated" = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    "features" = @(
        "Anti-YouTube Filter",
        "MegaEmbed Support", 
        "PlayerEmbedAPI Support",
        "DoodStream Support",
        "Dynamic CDN Detection"
    )
} | ConvertTo-Json -Depth 3

Write-Host "`n📝 JSON Payload preparado:" -ForegroundColor Cyan
Write-Host $jsonPayload -ForegroundColor White

# Salvar payload localmente para referência
$localJsonPath = "external_json_payload_v$currentVersion.json"
$jsonPayload | Out-File -FilePath $localJsonPath -Encoding UTF8
Write-Host "`n💾 Payload salvo localmente: $localJsonPath" -ForegroundColor Green

# Tentar atualizar o JSON externo
Write-Host "`n🚀 Tentando atualizar JSON externo..." -ForegroundColor Yellow

try {
    # Método 1: POST
    Write-Host "Tentativa 1: POST request..." -ForegroundColor Cyan
    $postResponse = Invoke-RestMethod -Uri $externalJsonUrl -Method POST -Body $jsonPayload -ContentType "application/json" -ErrorAction Stop
    Write-Host "✅ POST bem-sucedido!" -ForegroundColor Green
    Write-Host "Resposta: $postResponse" -ForegroundColor White
} catch {
    Write-Host "❌ POST falhou: $($_.Exception.Message)" -ForegroundColor Red
    
    try {
        # Método 2: PUT
        Write-Host "Tentativa 2: PUT request..." -ForegroundColor Cyan
        $putResponse = Invoke-RestMethod -Uri $externalJsonUrl -Method PUT -Body $jsonPayload -ContentType "application/json" -ErrorAction Stop
        Write-Host "✅ PUT bem-sucedido!" -ForegroundColor Green
        Write-Host "Resposta: $putResponse" -ForegroundColor White
    } catch {
        Write-Host "❌ PUT falhou: $($_.Exception.Message)" -ForegroundColor Red
        
        # Método 3: Documentar para atualização manual
        Write-Host "`n📋 ATUALIZAÇÃO MANUAL NECESSÁRIA:" -ForegroundColor Yellow
        Write-Host "=" * 40
        Write-Host "URL: $externalJsonUrl" -ForegroundColor White
        Write-Host "Método: POST ou PUT" -ForegroundColor White
        Write-Host "Content-Type: application/json" -ForegroundColor White
        Write-Host "Body: Ver arquivo $localJsonPath" -ForegroundColor White
        
        Write-Host "`n🔧 INSTRUÇÕES MANUAIS:" -ForegroundColor Cyan
        Write-Host "1. Acesse o painel de controle do servidor" -ForegroundColor White
        Write-Host "2. Navegue até a seção de JSON/API" -ForegroundColor White
        Write-Host "3. Atualize com o conteúdo de $localJsonPath" -ForegroundColor White
        Write-Host "4. Salve as alterações" -ForegroundColor White
    }
}

Write-Host "`n📊 RESUMO DA ATUALIZAÇÃO:" -ForegroundColor Green
Write-Host "=" * 40
Write-Host "Versão: v$currentVersion" -ForegroundColor White
Write-Host "Tag: $currentTag" -ForegroundColor White
Write-Host "URL Externa: $externalJsonUrl" -ForegroundColor White
Write-Host "Payload Local: $localJsonPath" -ForegroundColor White
Write-Host "Status: $(if ($postResponse -or $putResponse) { '✅ Atualizado' } else { '⚠️ Requer ação manual' })" -ForegroundColor White

Write-Host "`n🎯 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Verificar se a atualização foi aplicada" -ForegroundColor White
Write-Host "2. Testar o CloudStream com a nova versão" -ForegroundColor White
Write-Host "3. Monitorar logs para confirmar funcionamento" -ForegroundColor White

Write-Host "`n✅ Script concluído!" -ForegroundColor Green