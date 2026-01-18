# PlayerEmbedAPI - Guia de Implementação para MaxSeries

## ✅ Problema Resolvido!

Descobrimos como extrair URLs de vídeo do PlayerEmbedAPI usando automação de navegador.

## Descoberta Principal

**URL do vídeo**: `https://storage.googleapis.com/mediastorage/{timestamp}/{random_id}/{video_id}.mp4`

Exemplo real capturado:
```
https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4
```

## Como Funciona

1. PlayerEmbedAPI carrega a página com dados encriptados
2. JavaScript descriptografa os dados usando AES-CTR
3. JWPlayer é inicializado com a URL do vídeo
4. Vídeo é carregado do Google Cloud Storage

## Solução: Automação de Navegador

### Opção 1: WebView (Recomendado para CloudStream)

CloudStream já suporta WebView. Implementação em Kotlin:

```kotlin
suspend fun extractPlayerEmbedAPI(url: String): List<ExtractorLink> {
    val videoUrls = mutableListOf<String>()
    
    // Usar WebView para carregar a página
    val webView = WebView(context)
    webView.settings.javaScriptEnabled = true
    
    // Interceptar requisições de rede
    webView.webViewClient = object : WebViewClient() {
        override fun shouldInterceptRequest(
            view: WebView?,
            request: WebResourceRequest?
        ): WebResourceResponse? {
            val url = request?.url?.toString() ?: return null
            
            // Capturar URLs de vídeo
            if (url.contains(".mp4") || url.contains(".m3u8")) {
                if (url.contains("storage.googleapis.com") || 
                    url.contains("sssrr.org")) {
                    videoUrls.add(url)
                    Log.d("PlayerEmbedAPI", "Video URL found: $url")
                }
            }
            
            return super.shouldInterceptRequest(view, request)
        }
        
        override fun onPageFinished(view: WebView?, url: String?) {
            super.onPageFinished(view, url)
            
            // Tentar extrair do JWPlayer também
            view?.evaluateJavascript("""
                (function() {
                    try {
                        if (typeof jwplayer !== 'undefined') {
                            var player = jwplayer();
                            if (player && typeof player.getConfig === 'function') {
                                var config = player.getConfig();
                                return config.file || 
                                       (config.sources && config.sources[0] && config.sources[0].file) ||
                                       null;
                            }
                        }
                        return null;
                    } catch(e) {
                        return null;
                    }
                })();
            """) { result ->
                if (result != null && result != "null") {
                    val cleanUrl = result.trim('"')
                    if (cleanUrl.isNotEmpty()) {
                        videoUrls.add(cleanUrl)
                        Log.d("PlayerEmbedAPI", "Video URL from JWPlayer: $cleanUrl")
                    }
                }
            }
        }
    }
    
    // Carregar a página
    webView.loadUrl(url)
    
    // Esperar o vídeo carregar (ajustar timeout conforme necessário)
    delay(5000)
    
    // Retornar links extraídos
    return videoUrls.distinct().map { videoUrl ->
        ExtractorLink(
            source = "PlayerEmbedAPI",
            name = "PlayerEmbedAPI",
            url = videoUrl,
            referer = url,
            quality = Qualities.Unknown.value,
            isM3u8 = videoUrl.contains(".m3u8")
        )
    }
}
```

### Opção 2: Playwright (Para testes/desenvolvimento)

Script Python para testar e validar:

```python
from playwright.sync_api import sync_playwright

def extract_playerembedapi(player_url):
    """
    Extrai URL de vídeo do PlayerEmbedAPI
    
    Args:
        player_url: URL do player (ex: https://playerembedapi.link/?v=kBJLtxCD3)
    
    Returns:
        str: URL do vídeo ou None
    """
    video_url = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Interceptar requisições de rede
        def handle_response(response):
            nonlocal video_url
            url = response.url
            if '.mp4' in url and response.status in [200, 206]:
                if 'storage.googleapis.com' in url:
                    video_url = url
                    print(f"[+] Video URL: {url}")
        
        page.on('response', handle_response)
        
        # Carregar página
        page.goto(player_url, wait_until='networkidle', timeout=30000)
        
        # Esperar um pouco mais
        page.wait_for_timeout(3000)
        
        browser.close()
    
    return video_url

# Uso
video_url = extract_playerembedapi("https://playerembedapi.link/?v=kBJLtxCD3")
print(f"Video URL: {video_url}")
```

## Integração no MaxSeries Provider

### 1. Adicionar ao MaxSeriesProvider.kt

```kotlin
// No arquivo MaxSeriesProvider.kt

override suspend fun loadLinks(
    data: String,
    isCasting: Boolean,
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
): Boolean {
    val doc = app.get(data).document
    
    // ... código existente para outros players ...
    
    // Adicionar PlayerEmbedAPI
    doc.select("div.player-container iframe").forEach { iframe ->
        val iframeUrl = iframe.attr("src")
        
        if (iframeUrl.contains("playerembedapi.link")) {
            Log.d("MaxSeries", "Found PlayerEmbedAPI: $iframeUrl")
            
            try {
                val links = extractPlayerEmbedAPI(iframeUrl)
                links.forEach { link ->
                    callback(link)
                }
            } catch (e: Exception) {
                Log.e("MaxSeries", "Error extracting PlayerEmbedAPI: ${e.message}")
            }
        }
    }
    
    return true
}
```

### 2. Adicionar Permissões (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 3. Adicionar Dependências (build.gradle)

Se usar WebView, não precisa de dependências extras (já está no Android).

## Padrões de URL Descobertos

### PlayerEmbedAPI
```
https://playerembedapi.link/?v={VIDEO_ID}
```

### Google Cloud Storage (vídeo final)
```
https://storage.googleapis.com/mediastorage/{TIMESTAMP}/{RANDOM_ID}/{VIDEO_ID}.mp4
```

Características:
- **TIMESTAMP**: Unix timestamp (ex: 1768755384966)
- **RANDOM_ID**: String aleatória (ex: az8sfdbewst)
- **VIDEO_ID**: ID numérico do vídeo (ex: 81347747)

## Headers Necessários

Para reproduzir o vídeo, use:

```kotlin
val headers = mapOf(
    "Referer" to "https://playerembedapi.link/",
    "Origin" to "https://playerembedapi.link",
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

## Prioridade de Extratores

Recomendo esta ordem no MaxSeries:

```kotlin
val extractorPriority = listOf(
    "Doodstream",           // 1 - Mais rápido (HTTP direto)
    "PlayerEmbedAPI",       // 2 - Confiável (Google Cloud Storage)
    "PlayerThree",          // 3 - Backup
    "MyVidPlay",            // 4 - Backup
    "MegaEmbed"            // 10 - Último recurso (muito complexo)
)
```

## Vantagens do PlayerEmbedAPI

1. ✅ **Vídeos no Google Cloud Storage** - Alta disponibilidade
2. ✅ **Qualidade boa** - Geralmente 1080p
3. ✅ **Velocidade** - Google CDN é rápido
4. ✅ **Confiável** - Menos bloqueios que outros players
5. ✅ **Simples de implementar** - WebView faz todo o trabalho

## Desvantagens

1. ❌ **Requer WebView** - Mais pesado que HTTP puro
2. ❌ **Mais lento** - ~5 segundos para carregar
3. ❌ **Ads** - PlayerEmbedAPI tem popups (mas não afeta extração)

## Testes Realizados

### ✅ Teste 1: Captura de URL
- **URL**: `https://playerembedapi.link/?v=kBJLtxCD3`
- **Resultado**: `https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4`
- **Status**: ✅ Sucesso

### ✅ Teste 2: Reprodução
- **URL do vídeo**: Testada no navegador
- **Status**: ✅ Reproduz normalmente
- **Qualidade**: 1080p

### ✅ Teste 3: Headers
- **Referer**: Necessário
- **Origin**: Opcional mas recomendado
- **User-Agent**: Necessário

## Próximos Passos

1. ✅ Análise completa - CONCLUÍDO
2. ✅ Captura de URL - CONCLUÍDO
3. ⏳ Implementar no MaxSeries Provider
4. ⏳ Testar com múltiplos episódios
5. ⏳ Adicionar tratamento de erros
6. ⏳ Deploy e teste no CloudStream

## Arquivos Criados

1. `capture-playerembedapi-video.py` - Script Playwright funcional
2. `PLAYEREMBEDAPI_ANALYSIS.md` - Análise inicial
3. `PLAYEREMBEDAPI_SOLUTION.md` - Tentativa de descriptografia
4. `PLAYEREMBEDAPI_FINAL_SUMMARY.md` - Resumo completo
5. `PLAYWRIGHT_VS_BURPSUITE.md` - Comparação de ferramentas
6. `PLAYEREMBEDAPI_IMPLEMENTATION_GUIDE.md` - Este arquivo

## Conclusão

PlayerEmbedAPI é uma **excelente opção** para o MaxSeries porque:
- Vídeos hospedados no Google Cloud Storage (confiável)
- Implementação simples com WebView
- Não requer reverse engineering complexo
- Future-proof (funciona mesmo se mudarem a encriptação)

**Recomendação**: Implementar como extrator prioritário #2 (depois do Doodstream).
