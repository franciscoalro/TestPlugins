#!/usr/bin/env pwsh

Write-Host "MaxSeries v56 - Critical AnimesOnlineCC Fixes Release" -ForegroundColor Green

# Verificar se o arquivo .cs3 existe
if (-not (Test-Path "MaxSeries.cs3")) {
    Write-Host "Arquivo MaxSeries.cs3 nao encontrado!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item "MaxSeries.cs3").Length
Write-Host "Arquivo MaxSeries.cs3: $fileSize bytes" -ForegroundColor Cyan

# Commit das mudanças
Write-Host "Fazendo commit das mudancas..." -ForegroundColor Yellow
git add .
git commit -m "MaxSeries v56 - Critical AnimesOnlineCC Fixes

CORRECOES CRITICAS APLICADAS:
- Tratamento de erro robusto com try/catch
- Logs detalhados com Log.d() ao inves de println()
- Busca de imagem robusta (src, data-src, data-lazy-src)
- Uso consistente de fixUrl() e fixUrlNull()
- Melhor busca de titulo e poster
- Suporte a formato AnimesOnlineCC de episodios
- Logs de debug para facilitar troubleshooting

BASEADO NO ANIMESONLINECC FUNCIONANDO:
- Estrutura de erro handling identica
- Padroes de busca de elementos similares
- Logs detalhados para debug
- Tratamento robusto de URLs

DEVE RESOLVER: Problema de conteudo nao aparecer no CloudStream"

# Push para o repositório
Write-Host "Fazendo push para o GitHub..." -ForegroundColor Yellow
git push origin main

# Criar release no GitHub
Write-Host "Criando release v56.0..." -ForegroundColor Yellow
gh release create v56.0 MaxSeries.cs3 `
    --title "MaxSeries v56 - Critical AnimesOnlineCC Fixes" `
    --notes "MaxSeries v56 - Critical AnimesOnlineCC Fixes

CORRECOES CRITICAS APLICADAS:
- Tratamento de erro robusto: Try/catch em todas as funcoes principais
- Logs detalhados: Log.d() ao inves de println() para debug no Android
- Busca de imagem robusta: Suporte a src, data-src, data-lazy-src, data-original
- URLs consistentes: Uso de fixUrl() e fixUrlNull() em todos os lugares
- Melhor busca de elementos: Seletores mais robustos para titulo e poster
- Suporte hibrido: Funciona com formato MaxSeries e AnimesOnlineCC de episodios

BASEADO NO ANIMESONLINECC FUNCIONANDO:
- Estrutura de error handling identica ao AnimesOnlineCC
- Padroes de busca de elementos similares
- Logs detalhados para facilitar troubleshooting
- Tratamento robusto de URLs e imagens

DEVE RESOLVER:
- Problema principal: Conteudo nao aparecendo no CloudStream app
- Logs vazios: Agora com logs detalhados para debug
- Imagens quebradas: Busca robusta em multiplos atributos
- URLs malformadas: fixUrl() consistente

Site: https://www.maxseries.one/
Filtro YouTube: Ativo
Extractors: DoodStream, MegaEmbed, PlayerEmbedAPI"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Release v56.0 criado com sucesso!" -ForegroundColor Green
    Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/tag/v56.0" -ForegroundColor Cyan
    Write-Host "Arquivo: MaxSeries.cs3 ($fileSize bytes)" -ForegroundColor Cyan
} else {
    Write-Host "Erro ao criar release!" -ForegroundColor Red
    exit 1
}