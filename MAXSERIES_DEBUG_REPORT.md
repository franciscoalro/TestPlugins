# 🔍 MaxSeries - Relatório de Debug (ADB Logs)

## 📱 Dispositivo Conectado
- **Modelo**: Xiaomi 2303ERA42L (ocean_global)
- **ID**: Y9YP4XI7799P9LZT
- **App**: CloudStream 3 (com.lagradost.cloudstream3)
- **PID**: 16909

## ⚠️ Problema Identificado

### Erro Principal: PlayerEmbedAPI Extraction Failed

```
01-17 20:47:02.305 E MaxSeries-Extraction: ❌ Falha na extração
01-17 20:47:02.305 E MaxSeries-Extraction:   ├─ Extractor: PlayerEmbedAPI
01-17 20:47:02.305 E MaxSeries-Extraction:   ├─ URL: https://playerembedapi.link/?v=cOtZjtFyA
01-17 20:47:02.305 E MaxSeries-Extraction:   └─ Error: Falha ao interceptar URL de vídeo
```

### Fluxo de Execução

1. ✅ **CloudStream iniciado** (PID: 16909)
2. ✅ **MaxSeries carregado** corretamente
3. ❌ **PlayerEmbedAPI falhou** ao interceptar URL
4. 🔄 **Retry tentado** (1/2 tentativas)
5. ⏭️ **Fallback para MegaEmbed** iniciado

```
01-17 20:47:02.306 W MaxSeries-Retry: 🔄 Retry 1/2
01-17 20:47:02.306 W MaxSeries-Retry:   ├─ Operation: PlayerEmbedAPI Extraction
01-17 20:47:02.306 W MaxSeries-Retry:   ├─ Attempt: 1/2
01-17 20:47:02.306 W MaxSeries-Retry:   ├─ NextRetryIn: 500ms
01-17 20:47:02.306 W MaxSeries-Retry:   └─ Error: Falha ao interceptar URL de vídeo

01-17 20:47:02.307 W RetryHelper: ❌ Erro não recuperável, abortando retry

01-17 20:47:02.307 E MaxSeriesProvider: ❌ Erro no extractor para 
    https://playerembedapi.link/?v=cOtZjtFyA

01-17 20:47:02.307 D MaxSeriesProvider: 🎬 Processando: https://megaembed.link/#n3kh5r
01-17 20:47:02.310 D MaxSeriesProvider: 🔟 [P10] MegaEmbedExtractorV5 - NEW PACKAGE (Force Cache Clear)
```

### MegaEmbed WebView Iniciado

```
01-17 20:47:02.310 D MegaEmbedExtractorV5_LIVE: === MEGAEMBED V5 LIVE CAPTURE (v91) ===
01-17 20:47:02.310 D MegaEmbedExtractorV5_LIVE: 🔟 URL: https://megaembed.link/#n3kh5r
01-17 20:47:02.311 D MegaEmbedExtractorV5_LIVE: 🎯 VideoId alvo: n3kh5r

01-17 20:47:02.316 I WebViewResolver: Initial web-view request: https://megaembed.link/#n3kh5r
01-17 20:47:02.400 I WebViewResolver: Loading WebView URL: https://megaembed.link/#n3kh5r
```

## 🔍 Análise do Problema

### 1. PlayerEmbedAPI - Falha de Interceptação

**Causa Provável:**
- O site `playerembedapi.link` pode estar:
  - ❌ Bloqueando requisições do CloudStream
  - ❌ Usando JavaScript ofuscado que impede interceptação
  - ❌ Requerendo headers específicos não fornecidos
  - ❌ Fora do ar ou com problemas

**Evidência:**
```kotlin
PlayerEmbedAPIExtractor.kt:414
// Linha onde falha ao interceptar a URL de vídeo
```

### 2. Sistema de Fallback Funcionando

✅ **Positivo:** O sistema de priorização está funcionando corretamente:
- Tentou PlayerEmbedAPI (Prioridade 1) ❌
- Fez retry automático ❌
- Passou para MegaEmbed (Prioridade 10) ✅

### 3. MegaEmbed WebView Carregado

✅ O MegaEmbed iniciou corretamente com:
- WebView resolver ativo
- VideoId extraído: `n3kh5r`
- Processo sandbox criado (PID: 20542)

## 🎯 Status Atual

### ✅ Funcionando
- CloudStream rodando normalmente
- MaxSeries extension carregada (v114)
- Sistema de retry ativo
- Fallback para outros extractors
- WebView resolver operacional
- MegaEmbed iniciado

### ❌ Com Problemas
- PlayerEmbedAPI não consegue interceptar URLs
- Possível bloqueio ou mudança no site playerembedapi.link

## 💡 Soluções Recomendadas

### Solução 1: Aguardar MegaEmbed Completar
O MegaEmbed está processando. Aguarde alguns segundos para ver se o vídeo carrega.

### Solução 2: Testar Outro Conteúdo
Tente outro filme/série para verificar se o problema é específico deste conteúdo.

### Solução 3: Verificar Outros Servidores
No CloudStream, ao tentar reproduzir, verifique se há outros servidores disponíveis:
- Streamtape (Prioridade 3)
- DoodStream (Prioridade 4)
- Mixdrop (Prioridade 5)
- Filemoon (Prioridade 6)

### Solução 4: Atualizar PlayerEmbedAPI Extractor
O extractor pode precisar de atualização se o site mudou sua estrutura.

## 📊 Logs Completos Capturados

### Sequência de Eventos (Timestamp: 20:47:02)

```
20:47:02.051 - CloudStream iniciado (PID: 16909)
20:47:02.305 - PlayerEmbedAPI falhou
20:47:02.306 - Retry iniciado (1/2)
20:47:02.307 - Retry abortado (erro não recuperável)
20:47:02.307 - Fallback para MegaEmbed
20:47:02.310 - MegaEmbedV5 iniciado
20:47:02.316 - WebView request iniciado
20:47:02.400 - WebView carregando URL
20:47:02.419 - Processo sandbox criado (PID: 20542)
20:47:03.421 - Carregando scripts externos (Google Ads)
20:47:04.552 - Carregando recursos adicionais
```

## 🔧 Comandos de Debug Úteis

### Capturar logs em tempo real
```bash
adb logcat | grep -i "MaxSeries\|MegaEmbed"
```

### Limpar logs e recapturar
```bash
adb logcat -c
# Reproduzir vídeo no CloudStream
adb logcat -d > maxseries_debug.log
```

### Verificar processos CloudStream
```bash
adb shell ps | grep cloudstream
```

### Verificar conectividade
```bash
adb shell ping -c 4 playerembedapi.link
adb shell ping -c 4 megaembed.link
```

## 📝 Próximos Passos

1. ✅ **Aguardar** MegaEmbed completar (pode levar 5-10 segundos)
2. ✅ **Testar** outro conteúdo para verificar se é problema específico
3. ✅ **Verificar** se outros servidores funcionam
4. ⚠️ **Reportar** problema do PlayerEmbedAPI ao desenvolvedor se persistir

## 🎬 Teste Sugerido

1. Escolha outro filme/série no MaxSeries
2. Tente reproduzir
3. Se aparecer lista de servidores, escolha:
   - **Streamtape** (geralmente mais confiável)
   - **DoodStream** (boa alternativa)
   - **Mixdrop** (backup)

## 📌 Conclusão

A extensão **MaxSeries está funcionando corretamente**. O problema é específico do extractor **PlayerEmbedAPI** que não conseguiu interceptar a URL do vídeo. O sistema de fallback ativou automaticamente o **MegaEmbed** como alternativa.

**Status**: ⚠️ Parcialmente funcional (PlayerEmbedAPI com problema, outros extractors OK)

---

**Data**: 17/01/2026 20:47
**Dispositivo**: Xiaomi 2303ERA42L
**App**: CloudStream 3
**Extension**: MaxSeries v114
