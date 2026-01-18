# MegaEmbed - Solução do Problema (ATUALIZADO)

## 🔍 Problema Identificado

O player MegaEmbed usa **criptografia AES-CBC** para proteger as URLs dos vídeos:

1. **Token Longo**: A API `/api/v1/player?t={token}` requer um token de ~512 caracteres hex
2. **Resposta Criptografada**: A resposta é um hex string de 2500 bytes criptografado com AES-CBC
3. **Chave Desconhecida**: A chave de descriptografia está hardcoded no JavaScript ou derivada do video ID

## 📊 Fluxo Completo Descoberto (Burp Suite)

```
1. Usuário clica no episódio
   → GET https://playerthree.online/episodio/255703

2. Seleciona player MegaEmbed
   → GET https://megaembed.link/

3. JavaScript carrega e lê location.hash
   → Video ID: location.hash.split('#')[1]

4. Gera token longo (~512 chars hex)
   → Algoritmo desconhecido (precisa reverse engineering)

5. Chama API com token
   → GET /api/v1/player?t=3772aacff2bd31142eec3d5b0f291f4e...

6. Resposta criptografada (2500 bytes hex)
   → AES-CBC encrypted data

7. JavaScript descriptografa com chave hardcoded
   → Chave: desconhecida (16/32 bytes)
   → IV: desconhecido (16 bytes)

8. Resultado: JSON com URL do m3u8
   → {"url": "https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt"}
```

## 🔐 Detalhes da Criptografia

### Resposta da API
- **Formato**: Hex string (5000 caracteres = 2500 bytes)
- **Algoritmo**: AES-CBC (confirmado no JS)
- **Entropia**: 7.92 bits/byte (alta = criptografado)
- **Content-Type**: `application/octet-stream`

### Chaves Testadas (FALHARAM)
```
1077efecc0b24d02ace33c1e52e2fb4b  # CENC (DRM)
e2719d58a985b3c9781ab030af78d30e  # CLEARKEY (DRM)
9a04f07998404286ab92e65be0885f95  # PLAYREADY (DRM)
edef8ba979d64acea3c827dcd51d21ed  # WIDEVINE (DRM)
```

Essas são chaves de DRM (HLS encryption), não a chave do MegaEmbed.

### Código JavaScript Relevante
```javascript
// Geração do token (ofuscado)
location.hash[g(600)](g(800))[1]  // = location.hash.split('#')[1]

// Descriptografia (encontrado no JS)
crypto.subtle.importKey("raw", this.key, {name: "AES-CBC"}, false, ["encrypt", "decrypt"])

// Modo de criptografia
switch(n) {
  case En.cbc: return "AES-CBC";
  case En.ctr: return "AES-CTR";
}
```

## 🎯 APIs Descobertas

```javascript
// Do arquivo index-CZ_ja_1t.js
api/v1/player?t=     // Requer token ❌
api/v1/video?id=     // Retorna vazio ❌
api/v1/info?id=      // Retorna vazio ❌
api/v1/download?id=  // Não testado
api/v1/folder?id=    // Não testado
api/v1/log?t=        // Analytics
```

## ✅ Solução Recomendada

### Opção 1: Priorizar Outros Players (RECOMENDADO)

No `MaxSeriesProvider.kt`, mantenha MegaEmbed como **última prioridade**:

```kotlin
val serverPriority = mapOf(
    "playerembedapi" to 1,  // MP4 direto ✅
    "myvidplay" to 2,       // MP4 direto ✅
    "streamtape" to 3,      // MP4 direto ✅
    "dood" to 4,            // HLS/MP4 ✅
    "mixdrop" to 5,         // HLS/MP4 ✅
    "filemoon" to 6,        // MP4 ✅
    "uqload" to 7,          // MP4 ✅
    "vidcloud" to 8,        // HLS ✅
    "upstream" to 9,        // MP4 ✅
    "megaembed" to 10       // Requer WebView ⚠️
)
```

### Opção 2: Usar WebView (Complexo)

Se realmente precisar do MegaEmbed, use WebView:

```kotlin
// Em MegaEmbedExtractor.kt
suspend fun extract(url: String): List<ExtractorLink> {
    return suspendCoroutine { continuation ->
        val webView = WebView(context)
        webView.settings.javaScriptEnabled = true
        
        // Interceptar requisições
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val url = request.url.toString()
                
                // Capturar chamada à API
                if (url.contains("/api/v1/player")) {
                    // Extrair resposta JSON
                    // Parsear URL do m3u8
                    continuation.resume(links)
                }
                
                return super.shouldInterceptRequest(view, request)
            }
        }
        
        webView.loadUrl(url)
    }
}
```

### Opção 3: Reverse Engineering do Token (Avançado)

Analisar o JavaScript minificado para descobrir como o token é gerado:

```bash
# Baixar e beautify o JS
curl https://megaembed.link/assets/index-CZ_ja_1t.js > megaembed.min.js
npx js-beautify megaembed.min.js > megaembed.js

# Procurar função de geração de token
grep -A 20 "player.*token" megaembed.js
grep -A 20 "location.hash" megaembed.js
```

## 📝 Implementação Atual no MaxSeries

O provider atual já está configurado corretamente:

```kotlin
// MaxSeriesProvider.kt v103
// MegaEmbed é PRIORIDADE 10 (última opção)
// Outros players funcionam melhor
```

## 🧪 Testes Realizados

```bash
# Teste 1: API direta (FALHOU)
curl "https://megaembed.link/api/v1/player?t=xez5rx"
# Resposta: {"error": "Token is invalid"}

# Teste 2: API video (VAZIO)
curl "https://megaembed.link/api/v1/video?id=xez5rx"
# Resposta: vazio

# Teste 3: Página HTML (JS SPA)
curl "https://megaembed.link/#xez5rx"
# Resposta: HTML com <script src="/assets/index-CZ_ja_1t.js">
```

## 💡 Conclusão

**NÃO VALE A PENA** implementar suporte completo ao MegaEmbed porque:

1. ✅ Outros 9 players funcionam perfeitamente
2. ⚠️ MegaEmbed requer WebView (pesado, lento)
3. ⚠️ Token muda frequentemente (manutenção constante)
4. ⚠️ Pode quebrar a qualquer momento

**Mantenha MegaEmbed como fallback** e priorize os players que retornam MP4/HLS direto.

## 📚 Arquivos Criados

- `analyze-js-response.py` - Analisa respostas JS
- `extract-megaembed-real.py` - Tentativas de extração
- `download-megaembed-js.py` - Download do JS principal
- `megaembed-api-extractor.py` - Testa APIs descobertas
- `megaembed_index.js` - JavaScript completo (880KB)

## 🔗 Referências

- Burp Suite capture: `logsburpsuit/megaembed_burp_export.xml`
- Player HTML: `megaembed_page_dump.html`
- JavaScript: `megaembed_index.js` (880KB)
