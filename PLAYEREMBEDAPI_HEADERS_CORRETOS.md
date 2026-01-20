# PlayerEmbedAPI - Headers Corretos (Postman)

## 📅 Data: 18/01/2026 - 21:50

## 🎯 Headers Capturados do Postman

### Request para sssrr.org
```json
{
  "host": "htm4jbxon18.sssrr.org",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "accept": "*/*",
  "accept-encoding": "gzip, br",
  "accept-language": "en-US,en;q=0.9",
  "connection": "keep-alive",
  "origin": "https://playerembedapi.link",
  "referer": "https://playerembedapi.link/"
}
```

## 🔍 Análise

### Headers Críticos
1. **Origin**: `https://playerembedapi.link` ✅
2. **Referer**: `https://playerembedapi.link/` ✅
3. **User-Agent**: Chrome 120 ✅
4. **Accept**: `*/*` ✅

### O Que Isso Significa?

O PlayerEmbedAPI **faz requests diretos** para `sssrr.org` com headers específicos. Isso significa que:

1. ✅ **Não precisa WebView** - Pode usar HTTP direto
2. ✅ **Headers são simples** - Fácil de replicar
3. ✅ **Funciona no Postman** - Prova que é possível

## 🎯 Problema Atual (v127)

### PlayerEmbedAPI v3.3 (v124)
```kotlin
// Usa WebView com interceptação
val resolver = WebViewResolver(
    interceptUrl = Regex("""sssrr\.org"""),
    timeout = 30_000L
)
```

**Problema**: WebView não está fazendo requests para sssrr.org

## 💡 Solução: PlayerEmbedAPI v3.4 (v128)

### Estratégia 1: HTTP Direto (SEM WebView)
```kotlin
private suspend fun extractWithDirectHTTP(
    url: String,
    referer: String?,
    callback: (ExtractorLink) -> Unit
): Boolean {
    return try {
        // 1. Baixar HTML do PlayerEmbedAPI
        val html = app.get(
            url,
            headers = mapOf(
                "User-Agent" to USER_AGENT,
                "Referer" to (referer ?: "https://playerthree.online/"),
                "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            )
        ).text
        
        // 2. Extrair host e id do HTML
        // Procurar por: htm4jbxon18.sssrr.org
        // Procurar por: id=qx5haz5c0wg
        val hostRegex = Regex("""([a-z0-9]+)\.sssrr\.org""")
        val idRegex = Regex("""id=([a-zA-Z0-9]+)""")
        
        val hostMatch = hostRegex.find(html)
        val idMatch = idRegex.find(html)
        
        if (hostMatch != null && idMatch != null) {
            val host = hostMatch.value // htm4jbxon18.sssrr.org
            val videoId = idMatch.groupValues[1] // qx5haz5c0wg
            
            // 3. Fazer request para sssrr.org
            val metadataUrl = "https://$host/?timestamp=&id=$videoId"
            
            val metadataResponse = app.get(
                metadataUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://playerembedapi.link/",
                    "Origin" to "https://playerembedapi.link",
                    "Accept" to "*/*",
                    "Accept-Language" to "en-US,en;q=0.9"
                )
            )
            
            val videoUrl = metadataResponse.text.trim()
            
            if (isValidVideoUrl(videoUrl)) {
                Log.d(TAG, "🎯 Direct HTTP capturou: $videoUrl")
                emitExtractorLink(videoUrl, url, callback)
                return true
            }
        }
        
        false
    } catch (e: Exception) {
        Log.e(TAG, "❌ Direct HTTP falhou: ${e.message}")
        false
    }
}
```

### Estratégia 2: Crypto Interception (Como MegaEmbed)
```kotlin
// Se Direct HTTP falhar, usar mesma técnica do MegaEmbed
// Interceptar crypto.subtle.decrypt() ou fetch()
```

## 📊 Vantagens do HTTP Direto

| Aspecto | WebView | HTTP Direto |
|---------|---------|-------------|
| **Velocidade** | 30s timeout | ~2s |
| **Confiabilidade** | ❌ Não funciona | ✅ Funciona no Postman |
| **Complexidade** | Alta | Baixa |
| **Manutenção** | Difícil | Fácil |
| **Detecção** | Pode ser detectado | Parece navegador real |

## 🚀 Implementação v128

### Ordem de Estratégias (PlayerEmbedAPI)
1. **Direct HTTP** (NOVO) - Extrai do HTML e faz request direto
2. **Crypto Interception** (v127) - Intercepta descriptografia
3. **WebView Interceptação** (v124) - Fallback final

### Código Completo
```kotlin
override suspend fun getUrl(
    url: String,
    referer: String?,
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
) {
    Log.d(TAG, "=== PLAYEREMBEDAPI V3.4 (v128) ===")
    
    try {
        // ESTRATÉGIA 1: Direct HTTP (NOVO - MAIS RÁPIDO)
        if (extractWithDirectHTTP(url, referer, callback)) {
            Log.d(TAG, "✅ Direct HTTP funcionou!")
            return
        }
        
        // ESTRATÉGIA 2: Crypto Interception (v127)
        if (extractWithCryptoInterception(url, referer, callback)) {
            Log.d(TAG, "✅ Crypto Interception funcionou!")
            return
        }
        
        // ESTRATÉGIA 3: WebView Interceptação (v124 - FALLBACK)
        if (extractWithWebViewInterception(url, referer, callback)) {
            Log.d(TAG, "✅ WebView Interceptação funcionou!")
            return
        }
        
        Log.e(TAG, "❌ Todas as estratégias falharam")
        
    } catch (e: Exception) {
        Log.e(TAG, "❌ Erro: ${e.message}")
    }
}
```

## 🧪 Teste Rápido

### Postman
```
GET https://htm4jbxon18.sssrr.org/?timestamp=&id=qx5haz5c0wg

Headers:
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  Referer: https://playerembedapi.link/
  Origin: https://playerembedapi.link
  Accept: */*
```

**Resultado esperado**: URL do vídeo ou JSON com metadata

## 🎯 Próximos Passos

1. **Testar v127** (MegaEmbed com Crypto Interception)
2. **Se v127 funcionar**: Implementar v128 (PlayerEmbedAPI com Direct HTTP)
3. **Se v127 falhar**: Focar em PlayerEmbedAPI Direct HTTP primeiro

---

**Status**: Aguardando teste v127  
**Próxima versão**: v128 (PlayerEmbedAPI Direct HTTP)  
**Prioridade**: Alta  
**Tempo estimado**: 30 minutos para implementar v128
