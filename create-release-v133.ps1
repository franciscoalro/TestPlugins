# Script para criar release v133.0 no GitHub
# Regex Template URL para Extração Dinâmica

$ErrorActionPreference = "Stop"

Write-Host "=== Criando Release v133.0 ===" -ForegroundColor Cyan

$cs3File = "MaxSeries\build\MaxSeries.cs3"
if (-not (Test-Path $cs3File)) {
    Write-Host "ERRO: Arquivo $cs3File não encontrado" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $cs3File).Length
$fileSizeKB = [math]::Round($fileSize / 1KB, 2)

Write-Host "Arquivo: $cs3File ($fileSizeKB KB)" -ForegroundColor Green

$releaseNotes = @"
# 🔍 MaxSeries v133 - Regex Template URL

**Data:** 20 de Janeiro de 2026  
**Tipo:** Enhancement

---

## 🎯 RESUMO

**Objetivo:** Extrair dados dinâmicos das URLs automaticamente  
**Método:** Regex template URL  
**Benefício:** Descoberta automática de novos CDNs

---

## 🆕 NOVA FUNCIONALIDADE

### Regex Template URL

**Template:**
``````
https://{HOST}/v4/{CLUSTER}/{VIDEO_ID}/{FILE_NAME}
``````

**Regex:**
``````kotlin
Regex("""https?://([^/]+)/v4/([^/]+)/([^/]+)/([^?]+)""")
              ↓        ↓        ↓        ↓
            HOST    CLUSTER  VIDEO_ID  FILE_NAME
``````

---

## 📊 EXTRAÇÃO AUTOMÁTICA

### Exemplo

**URL:**
``````
https://spuc.alphastrahealth.store/v4/il/n3kh5r/index-f1-v1-a1.txt
``````

**Extraído:**
``````kotlin
UrlData(
    host = "spuc.alphastrahealth.store",
    cluster = "il",
    videoId = "n3kh5r",
    fileName = "index-f1-v1-a1.txt"
)
``````

---

## 📝 LOGS MELHORADOS

### Antes (v132)
``````
D/MegaEmbedV7: ✅ WebView descobriu: https://...
``````

### Depois (v133)
``````
D/MegaEmbedV7: ✅ WebView descobriu: https://...
D/MegaEmbedV7: 📊 Dados extraídos: host=..., cluster=..., videoId=..., file=...
D/MegaEmbedV7: 🆕 Novo CDN descoberto: ... (cluster: ...)
``````

---

## 🎯 BENEFÍCIOS

- ✅ Descoberta automática de novos CDNs
- ✅ Logs detalhados com dados estruturados
- ✅ Base para melhorias futuras
- ✅ Sistema mais inteligente

---

## 🔄 COMPATIBILIDADE

**Mantém:**
- ✅ 12 CDNs conhecidos
- ✅ 4 variações de arquivo
- ✅ ~95% taxa de sucesso

**Adiciona:**
- ✅ Extração automática de dados
- ✅ Detecção de novos CDNs
- ✅ Logs estruturados

---

## 📦 INSTALAÇÃO

1. CloudStream → Settings → Extensions
2. Atualizar MaxSeries para v133

---

**Desenvolvido por:** franciscoalro  
**Implementado por:** Kiro AI  
**Data:** 20 de Janeiro de 2026

---

## 📝 Changelog Completo

Ver: [release-notes-v133.md](https://github.com/franciscoalro/TestPlugins/blob/main/release-notes-v133.md)
"@

Write-Host "`nCriando release v133.0..." -ForegroundColor Yellow

try {
    gh release create v133.0 `
        --title "v133.0 - Regex Template URL" `
        --notes $releaseNotes `
        $cs3File
    
    Write-Host "`n✅ Release v133.0 criada com sucesso!" -ForegroundColor Green
    Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/tag/v133.0" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Erro ao criar release: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Concluído ===" -ForegroundColor Green
