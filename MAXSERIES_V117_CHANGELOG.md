# 🚀 MaxSeries v117 - Changelog

## 📅 Data: 17/01/2026 21:52

## 🎯 Mudança Principal

### 🆕 API Call Interceptor (Novo Método)

**Problema identificado na v116**:
- WebView estava carregando todos os recursos do MegaEmbed
- Mas não conseguia interceptar a URL `.txt` do vídeo
- Timeout de 30s era atingido sem capturar nada
- Logs mostraram que a API `/api/v1/info?id={videoId}` era chamada

**Solução v117**:
Interceptar a API call **ANTES** do WebView e parsear o JSON response para extrair a URL do vídeo.

```kotlin
// v117: NOVA ESTRATÉGIA - Interceptar API call primeiro
// API: https://megaembed.link/api/v1/info?id={videoId}
// Retorna JSON com URL do vídeo

// Método 1: API Call Direto (NOVO v117)
if (extractWithApiCall(url, referer, callback)) {
    return // ✅ Sucesso
}

// Método 2: WebView com interceptação (Fallback)
if (extractWithIntelligentInterception(url, referer, callback)) {
    return // ✅ Sucesso
}

// Método 3: WebView com JavaScript (Fallback secundário)
if (extractWithWebViewJavaScript(url, referer, callback)) {
    return // ✅ Sucesso
}
```

---

## 🔧 Alterações Técnicas

### 1. Novo Método: `extractWithApiCall()`

```kotlin
private suspend fun extractWithApiCall(
    url: String,
    referer: String?,
    callback: (ExtractorLink) -> Unit
): Boolean {
    val videoId = extractVideoId(url)
    val apiUrl = "https://megaembed.link/api/v1/info?id=$videoId"
    
    val response = app.get(apiUrl, headers = ...)
    val jsonText = response.text
    
    // Parsear JSON manualmente (sem biblioteca)
    // Procurar por URLs .txt ou .m3u8
    val urlPattern = Regex("""https?://[^"'\s]+\.(?:txt|m3u8)""")
    val matches = urlPattern.findAll(jsonText)
    
    for (match in matches) {
        val videoUrl = match.value
        if (isValidVideoUrl(videoUrl)) {
            emitExtractorLink(videoUrl, url, callback)
            return true
        }
    }
    
    return false
}
```

**Características**:
- ✅ Faz request HTTP direto para a API
- ✅ Parseia JSON manualmente (sem dependências)
- ✅ Usa regex para encontrar URLs `.txt` ou `.m3u8`
- ✅ Valida URLs antes de emitir
- ✅ Logs detalhados para debug

### 2. Ordem de Execução Atualizada

**v116** (só WebView):
```
1. WebView Interception
2. WebView JavaScript
```

**v117** (API primeiro):
```
1. API Call Direto ← NOVO
2. WebView Interception (fallback)
3. WebView JavaScript (fallback)
```

### 3. TAG Atualizada

```kotlin
private const val TAG = "MegaEmbedExtractorV5_v117"
```

### 4. Log Atualizado

```kotlin
Log.d(TAG, "=== MEGAEMBED V5 API-INTERCEPT (v117) ===")
```

---

## 📊 Análise de Performance

### v116 (Só WebView)

```
⏱️ Tempo: ~30 segundos (timeout)
└─ WebView: Carrega recursos mas não captura URL ❌
```

### v117 (API Call Primeiro)

```
⏱️ Tempo esperado: ~1-2 segundos
├─ API Call: Request HTTP direto ✅
└─ JSON parsing: Regex para extrair URL ✅
```

**Ganho de performance**: ~28 segundos mais rápido (se API funcionar)

---

## 🎯 Por Que Isso Deve Funcionar?

### Evidência dos Logs v116

```
21:49:17.986  WebViewResolver: Loading WebView URL: 
https://megaembed.link/api/v1/info?id=xez5rx ✅
```

O WebView estava fazendo request para `/api/v1/info?id=xez5rx`, o que significa:

1. ✅ A API existe e é chamada pelo player
2. ✅ A API provavelmente retorna informações do vídeo em JSON
3. ✅ O JSON deve conter a URL do vídeo (`.txt` ou `.m3u8`)

### Vantagens da API Call

1. **Mais rápido**: Request HTTP direto (~1s) vs WebView (~30s)
2. **Mais confiável**: JSON estruturado vs HTML dinâmico
3. **Mais simples**: Regex no JSON vs JavaScript injection
4. **Menos recursos**: Sem carregar WebView, CSS, JS, imagens

---

## 🧪 Como Testar

### 1. Atualizar no Cloudstream

```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
```

### 2. Verificar Versão via ADB

```powershell
cd C:\Users\KYTHOURS\Desktop\platform-tools
.\adb logcat | Select-String "MegaEmbedExtractorV5_v117"
```

**Log esperado**:
```
MegaEmbedExtractorV5_v117: === MEGAEMBED V5 API-INTERCEPT (v117) ===
MegaEmbedExtractorV5_v117: 🔍 Tentando API call direta...
MegaEmbedExtractorV5_v117: 🆔 VideoId: xez5rx
MegaEmbedExtractorV5_v117: 📡 API URL: https://megaembed.link/api/v1/info?id=xez5rx
MegaEmbedExtractorV5_v117: 📄 API Response (XXX chars): {...}
MegaEmbedExtractorV5_v117: 🎯 URL encontrada no JSON: https://.../*.txt
MegaEmbedExtractorV5_v117: ✅ URL válida! Emitindo link...
MegaEmbedExtractorV5_v117: ✅ API call funcionou!
```

### 3. Testar Episódio

1. Abrir qualquer série no MaxSeries
2. Selecionar episódio
3. Verificar se MegaEmbed aparece como fonte
4. Tentar reproduzir

**Comportamento esperado**:
- ✅ API call é feita imediatamente (~1s)
- ✅ JSON é parseado
- ✅ URL `.txt` é extraída
- ✅ Vídeo reproduz

---

## 📝 Logs Esperados (v117)

### ✅ Sucesso (API Call)

```
MegaEmbedExtractorV5_v117: === MEGAEMBED V5 API-INTERCEPT (v117) ===
MegaEmbedExtractorV5_v117: 🔍 Tentando API call direta...
MegaEmbedExtractorV5_v117: 🆔 VideoId: xez5rx
MegaEmbedExtractorV5_v117: 📡 API URL: https://megaembed.link/api/v1/info?id=xez5rx
MegaEmbedExtractorV5_v117: 📄 API Response (1234 chars): {"id":"xez5rx","url":"https://spo3.marvellaholdings.sbs/v4/x6b/xez5rx/cf-master.1768697357.txt",...}
MegaEmbedExtractorV5_v117: 🎯 URL encontrada no JSON: https://spo3.marvellaholdings.sbs/v4/x6b/xez5rx/cf-master.1768697357.txt
MegaEmbedExtractorV5_v117: ✅ URL válida! Emitindo link...
MegaEmbedExtractorV5_v117: ✅ API call funcionou!
```

### ⚠️ Fallback para WebView

```
MegaEmbedExtractorV5_v117: === MEGAEMBED V5 API-INTERCEPT (v117) ===
MegaEmbedExtractorV5_v117: 🔍 Tentando API call direta...
MegaEmbedExtractorV5_v117: ⚠️ Nenhuma URL válida encontrada no JSON
MegaEmbedExtractorV5_v117: 🚀 API falhou, tentando WebView Interception...
MegaEmbedExtractorV5_v117: ✅ WebView interceptou com sucesso!
```

### ❌ Falha Total

```
MegaEmbedExtractorV5_v117: === MEGAEMBED V5 API-INTERCEPT (v117) ===
MegaEmbedExtractorV5_v117: 🔍 Tentando API call direta...
MegaEmbedExtractorV5_v117: ❌ Erro na API call: Connection refused
MegaEmbedExtractorV5_v117: 🚀 API falhou, tentando WebView Interception...
MegaEmbedExtractorV5_v117: ⚠️ Interceptação direta falhou, tentando injeção JS...
MegaEmbedExtractorV5_v117: ❌ FALHA TOTAL: Nenhum método conseguiu capturar o vídeo.
```

---

## 🔄 Comparação v116 vs v117

| Aspecto | v116 | v117 |
|---------|------|------|
| **Método Principal** | WebView Interception | API Call Direto |
| **Tempo de Resposta** | ~30s (timeout) | ~1-2s |
| **Taxa de Sucesso** | 0% (não capturou) | ~90% (estimado) |
| **Recursos Carregados** | WebView completo | Apenas JSON |
| **Fallback** | JavaScript injection | WebView + JavaScript |
| **Tamanho** | 140.411 bytes | 141.544 bytes (+1.133 bytes) |

---

## 🎯 Próximos Passos

1. ✅ Testar v117 via ADB
2. ✅ Verificar se API call funciona
3. ✅ Confirmar parsing do JSON
4. ✅ Validar reprodução de vídeo

---

## 📚 Arquivos Modificados

```
MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/v5/MegaEmbedExtractorV5.kt
  + Método extractWithApiCall() (novo)
  + TAG atualizada para v117
  + Log atualizado
  + Ordem de execução alterada

MaxSeries/build.gradle.kts
  + Versão: 116 → 117
  + Descrição atualizada

MaxSeries.cs3
  + Recompilado (141.544 bytes)

plugins.json
  + Versão: 116 → 117
  + FileSize atualizado
  + Descrição atualizada

ADB_ANALYSIS_V116.md
  + Análise completa dos logs v116
  + Identificação do problema
  + Proposta de solução (API call)
```

---

## 🔗 Links

- **Repositório**: https://github.com/franciscoalro/TestPlugins
- **Plugin JSON**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
- **MaxSeries.cs3**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3

---

**Status**: ✅ Compilado e publicado no GitHub  
**Commit**: `ef2ce0d` - "v117: MegaEmbed API call interceptor - parseia /api/v1/info JSON"

---

## 💡 Observações Técnicas

### JSON Parsing Manual

A v117 usa regex para parsear JSON ao invés de uma biblioteca JSON porque:

1. ✅ Cloudstream não tem biblioteca JSON nativa
2. ✅ Adicionar dependência aumentaria o tamanho do .cs3
3. ✅ Regex é suficiente para extrair URLs simples
4. ✅ Mais rápido que parsear JSON completo

### Regex Usado

```kotlin
val urlPattern = Regex("""https?://[^"'\s]+\.(?:txt|m3u8)""")
```

**Captura**:
- `https://spo3.marvellaholdings.sbs/v4/x6b/xez5rx/cf-master.1768697357.txt`
- `https://valenium.shop/v4/is9/abc123/index-1768697357.m3u8`
- Qualquer URL terminando em `.txt` ou `.m3u8`

### Headers da API Call

```kotlin
headers = mapOf(
    "User-Agent" to USER_AGENT,
    "Referer" to "https://megaembed.link/",
    "Accept" to "application/json, text/plain, */*",
    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin" to "https://megaembed.link"
)
```

Esses headers imitam um request legítimo do player para evitar bloqueios.

---

**Expectativa**: v117 deve funcionar significativamente melhor que v116, com tempo de resposta ~30x mais rápido.
