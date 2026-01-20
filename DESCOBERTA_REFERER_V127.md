# DESCOBERTA CRÍTICA: MegaEmbed Precisa de Referer

## 📅 Data: 18/01/2026 - 21:25

## 🚨 PROBLEMA IDENTIFICADO

Usuário reportou:
> "https://megaembed.link/#3wnuij esse link não encontra a fonte do vídeo se digitar direto"

## 🔍 ANÁLISE

### O Que Isso Significa?

1. **MegaEmbed verifica Referer**
   - Se abrir direto no navegador: ❌ Não funciona
   - Se abrir via iframe do playerthree: ✅ Funciona

2. **Proteção Anti-Hotlink**
   - Site bloqueia acesso direto
   - Precisa vir de domínio autorizado
   - Provavelmente: `playerthree.online` ou `maxseries.one`

3. **Implicações para CloudStream**
   ```kotlin
   // ANTES (v126) - Pode estar faltando Referer correto
   app.get(url, headers = mapOf(
       "Referer" to "https://megaembed.link/"  // ❌ ERRADO!
   ))
   
   // DEPOIS (v127) - Referer correto
   app.get(url, headers = mapOf(
       "Referer" to "https://playerthree.online/"  // ✅ CORRETO!
   ))
   ```

## 🧪 TESTE PARA VALIDAR

### Opção 1: Teste HTML Local
Criei `test-megaembed-referer.html`:
1. Abrir arquivo no navegador
2. Abrir DevTools (F12) → Network tab
3. Clicar em "Carregar Player"
4. Verificar se API `/api/v1/info?id=3wnuij` é chamada
5. Verificar se URL .txt aparece

### Opção 2: Teste com cURL
```bash
# Teste 1: SEM Referer (deve falhar)
curl -v "https://megaembed.link/api/v1/info?id=3wnuij"

# Teste 2: COM Referer errado (deve falhar)
curl -v "https://megaembed.link/api/v1/info?id=3wnuij" \
  -H "Referer: https://megaembed.link/"

# Teste 3: COM Referer correto (deve funcionar)
curl -v "https://megaembed.link/api/v1/info?id=3wnuij" \
  -H "Referer: https://playerthree.online/"

# Teste 4: COM Referer alternativo (testar)
curl -v "https://megaembed.link/api/v1/info?id=3wnuij" \
  -H "Referer: https://maxseries.one/"
```

### Opção 3: Teste no Postman
```
GET https://megaembed.link/api/v1/info?id=3wnuij

Headers:
  Referer: https://playerthree.online/
  Origin: https://playerthree.online
  User-Agent: Mozilla/5.0...
```

## 🎯 CORREÇÃO v127

### MegaEmbed - Referer Correto

```kotlin
// MegaEmbedExtractorV5.kt v127

override suspend fun getUrl(
    url: String,
    referer: String?,  // ← USAR ESTE REFERER!
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
) {
    Log.d(TAG, "=== MEGAEMBED V5 (v127) ===")
    Log.d(TAG, "URL: $url")
    Log.d(TAG, "Referer recebido: $referer")  // ← IMPORTANTE!
    
    // Usar referer recebido (playerthree.online)
    // NÃO usar megaembed.link como referer!
    val correctReferer = referer ?: "https://playerthree.online/"
    
    try {
        val videoId = extractVideoId(url)
        if (videoId == null) {
            Log.e(TAG, "VideoId não encontrado")
            return
        }
        
        Log.d(TAG, "VideoId: $videoId")
        Log.d(TAG, "Usando Referer: $correctReferer")  // ← LOG
        
        // ESTRATÉGIA 0: Direct API com Referer correto
        if (extractWithDirectAPI(videoId, correctReferer, callback)) {
            return
        }
        
        // ... outras estratégias
        
    } catch (e: Exception) {
        Log.e(TAG, "Erro: ${e.message}")
    }
}

private suspend fun extractWithDirectAPI(
    videoId: String,
    referer: String,  // ← Referer correto
    callback: (ExtractorLink) -> Unit
): Boolean {
    return try {
        val apiUrl = "https://megaembed.link/api/v1/info?id=$videoId"
        Log.d(TAG, "Direct API: $apiUrl")
        Log.d(TAG, "Referer: $referer")  // ← LOG
        
        val response = app.get(
            apiUrl,
            headers = mapOf(
                "User-Agent" to USER_AGENT,
                "Referer" to referer,  // ← USAR REFERER CORRETO!
                "Origin" to extractOrigin(referer),  // ← Extrair origin do referer
                "Accept" to "application/json, text/plain, */*"
            )
        )
        
        val json = response.text
        Log.d(TAG, "API Response: ${json.take(200)}...")
        
        // ... resto do código
        
    } catch (e: Exception) {
        Log.e(TAG, "Direct API falhou: ${e.message}")
        false
    }
}

private fun extractOrigin(referer: String): String {
    return try {
        val url = java.net.URL(referer)
        "${url.protocol}://${url.host}"
    } catch (e: Exception) {
        "https://playerthree.online"
    }
}
```

### PlayerEmbedAPI - Referer Correto

```kotlin
// PlayerEmbedAPIExtractor.kt v127

override suspend fun getUrl(
    url: String,
    referer: String?,  // ← USAR ESTE!
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
) {
    Log.d(TAG, "=== PLAYEREMBEDAPI V3 (v127) ===")
    Log.d(TAG, "URL: $url")
    Log.d(TAG, "Referer recebido: $referer")
    
    val correctReferer = referer ?: "https://playerthree.online/"
    
    try {
        val response = app.get(
            url,
            headers = mapOf(
                "User-Agent" to USER_AGENT,
                "Referer" to correctReferer,  // ← CORRETO!
                "Origin" to extractOrigin(correctReferer),
                "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            )
        )
        
        // ... resto do código
        
    } catch (e: Exception) {
        Log.e(TAG, "Erro: ${e.message}")
    }
}
```

## 🔍 VERIFICAR NO CÓDIGO ATUAL

Vamos verificar se v126 está usando Referer correto:

```kotlin
// MaxSeriesProvider.kt - Como chama os extractors?

suspend fun loadLinks(
    data: String,
    isCasting: Boolean,
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
): Boolean {
    val url = parseJson<LinkData>(data).url
    
    // Qual referer está sendo passado aqui?
    loadExtractor(
        url,
        referer = ???,  // ← VERIFICAR ISTO!
        subtitleCallback,
        callback
    )
}
```

## 📊 POSSÍVEIS CENÁRIOS

### Cenário 1: Referer está correto
- v126 já usa `playerthree.online`
- Problema é outro (descriptografia)
- Solução: Interceptação crypto.subtle

### Cenário 2: Referer está errado
- v126 usa `megaembed.link` como referer
- API bloqueia request
- Solução: Corrigir referer para `playerthree.online`

### Cenário 3: Referer está null
- v126 não passa referer
- API bloqueia request
- Solução: Passar referer correto

## 🎯 AÇÃO IMEDIATA

### 1. Testar com cURL
```bash
curl -v "https://megaembed.link/api/v1/info?id=3wnuij" \
  -H "Referer: https://playerthree.online/" \
  -H "Origin: https://playerthree.online" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**Resultado esperado**:
- Se retornar HEX: ✅ Referer está OK, problema é descriptografia
- Se retornar erro 403/401: ❌ Referer está bloqueado
- Se retornar HTML: ❌ Referer está errado

### 2. Verificar código v126
```kotlin
// Procurar por:
// 1. Como MaxSeriesProvider chama extractors
// 2. Qual referer está sendo passado
// 3. Se está usando referer do episódio ou hardcoded
```

### 3. Implementar v127 com correção
```kotlin
// Se referer estiver errado:
// - Corrigir para usar referer do episódio
// - Ou hardcode "https://playerthree.online/"

// Se referer estiver correto:
// - Implementar interceptação crypto.subtle
```

## 🚀 PRÓXIMO PASSO

**Testar com cURL AGORA** para confirmar se problema é Referer ou descriptografia!

```bash
# Cole este comando no terminal:
curl -v "https://megaembed.link/api/v1/info?id=3wnuij" \
  -H "Referer: https://playerthree.online/" \
  -H "Origin: https://playerthree.online" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

---

**Status**: Aguardando teste cURL  
**Prioridade**: CRÍTICA  
**Impacto**: Pode resolver problema sem precisar interceptação!
