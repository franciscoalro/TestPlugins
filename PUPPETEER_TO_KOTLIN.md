# 🔄 Puppeteer → Kotlin: Guia de Migração

## 📋 Fluxo de Trabalho

```
1. Testar com Puppeteer (JavaScript) ✅
   ↓
2. Validar extração funciona
   ↓
3. Implementar em Kotlin (CloudStream)
   ↓
4. Testar no dispositivo Android
```

---

## 🧪 Passo 1: Testar com Puppeteer

### Instalação
```bash
cd c:\Users\KYTHOURS\Desktop\brcloudstream
npm install
```

### Executar Teste
```bash
# Teste básico
node test-puppeteer-extractor.js https://maxseries.one/episodio/258444

# Ou use o script npm
npm run test:episode
```

### O Que o Script Faz
✅ Abre o navegador (visível para debug)  
✅ Intercepta todas as requisições de rede  
✅ Analisa todos os iframes da página  
✅ Extrai URLs de vídeo (M3U8, MP4, TS, WOFF2)  
✅ Categoriza URLs por tipo  
✅ Salva resultados em `puppeteer-results.json`

---

## 📊 Exemplo de Saída

```
🚀 Iniciando Puppeteer...

✅ Puppeteer configurado

🔍 Analisando: https://maxseries.one/episodio/258444

📥 Carregando página...
✅ Página carregada

📊 Encontrados 3 iframes

🎥 Iframe 1:
   URL: https://megaembed.cc/embed/abc123
   Tipo: MegaEmbed
   ✅ Acesso ao frame permitido
   🎯 Encontrados 2 URLs no HTML:
      - https://cdn.megaembed.cc/playlist.m3u8
      - https://cdn.megaembed.cc/segment001.ts

📡 Requisição: https://cdn.megaembed.cc/master.m3u8
📥 Resposta: https://cdn.megaembed.cc/master.m3u8 (Status: 200)
   Content-Type: application/vnd.apple.mpegurl

============================================================
📊 RESUMO DA EXTRAÇÃO
============================================================

🎥 Player 1 - MegaEmbed
   URL: https://megaembed.cc/embed/abc123
   ✅ Vídeos encontrados:
      https://cdn.megaembed.cc/playlist.m3u8
      https://cdn.megaembed.cc/segment001.ts

📡 TODAS AS URLs CAPTURADAS (3):
────────────────────────────────────────────────────────────

🎬 M3U8 Playlists:
   https://cdn.megaembed.cc/master.m3u8
   https://cdn.megaembed.cc/playlist.m3u8

📦 TS Segments:
   https://cdn.megaembed.cc/segment001.ts

============================================================
✅ Análise concluída!

💾 Resultados salvos em: puppeteer-results.json
```

---

## 🔄 Passo 2: Analisar Resultados

### Abrir JSON de Resultados
```bash
# Windows
notepad puppeteer-results.json

# Ou visualize no VS Code
code puppeteer-results.json
```

### Estrutura do JSON
```json
{
  "iframes": [
    {
      "index": 1,
      "url": "https://megaembed.cc/embed/abc123",
      "type": "MegaEmbed",
      "videoUrls": [
        "https://cdn.megaembed.cc/playlist.m3u8"
      ]
    }
  ],
  "capturedUrls": [
    "https://cdn.megaembed.cc/master.m3u8",
    "https://cdn.megaembed.cc/segment001.ts"
  ],
  "summary": {
    "totalIframes": 1,
    "totalUrls": 2
  }
}
```

---

## 🔨 Passo 3: Implementar em Kotlin

### Mapeamento: JavaScript → Kotlin

| Conceito JavaScript | Equivalente Kotlin CloudStream |
|---------------------|--------------------------------|
| `puppeteer.launch()` | `WebView` ou `app.get()` |
| `page.goto(url)` | `app.get(url)` |
| `page.on('request')` | `WebView.shouldInterceptRequest()` |
| `iframe.contentFrame()` | `document.select("iframe")` |
| `html.match(regex)` | `Regex().find(html)` |

### Exemplo: Puppeteer → Kotlin

#### JavaScript (Puppeteer)
```javascript
// Interceptar requisições
page.on('request', request => {
  const url = request.url();
  if (url.includes('.m3u8')) {
    console.log('M3U8 encontrado:', url);
    capturedUrls.add(url);
  }
});
```

#### Kotlin (CloudStream)
```kotlin
// WebView com interceptação
override fun shouldInterceptRequest(
    view: WebView,
    request: WebResourceRequest
): WebResourceResponse? {
    val url = request.url.toString()
    
    if (url.contains(".m3u8")) {
        Log.d("MaxSeries", "M3U8 encontrado: $url")
        capturedUrls.add(url)
    }
    
    return super.shouldInterceptRequest(view, request)
}
```

---

## 📝 Template Kotlin Baseado no Puppeteer

Vou criar um extractor Kotlin baseado nos resultados do Puppeteer:

```kotlin
package com.franciscoalro.maxseries.extractors

import android.util.Log
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.ExtractorApi
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.M3u8Helper
import kotlinx.coroutines.delay
import java.util.concurrent.ConcurrentHashMap

/**
 * Extractor baseado nos testes do Puppeteer
 * 
 * Fluxo:
 * 1. Detectar tipo de player (MegaEmbed, PlayerEmbedAPI, etc)
 * 2. Usar WebView para interceptar requisições
 * 3. Capturar URLs de vídeo (M3U8, MP4, TS)
 * 4. Retornar links para o CloudStream
 */
class PuppeteerBasedExtractor : ExtractorApi() {
    override val name = "PuppeteerBased"
    override val mainUrl = "https://maxseries.one"
    override val requiresReferer = true

    private val capturedUrls = ConcurrentHashMap<String, String>()
    private val TAG = "PuppeteerExtractor"

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🔍 Analisando: $url")

        // Identificar tipo de player
        val playerType = identifyPlayer(url)
        Log.d(TAG, "   Tipo: $playerType")

        when (playerType) {
            PlayerType.MEGAEMBED -> extractMegaEmbed(url, callback)
            PlayerType.PLAYEREMBEDAPI -> extractPlayerEmbedAPI(url, callback)
            PlayerType.DOODSTREAM -> extractDoodStream(url, callback)
            else -> extractGeneric(url, callback)
        }
    }

    private fun identifyPlayer(url: String): PlayerType {
        return when {
            url.contains("megaembed", ignoreCase = true) -> PlayerType.MEGAEMBED
            url.contains("playerembedapi", ignoreCase = true) ||
            url.contains("playerthree", ignoreCase = true) -> PlayerType.PLAYEREMBEDAPI
            url.contains("doodstream", ignoreCase = true) ||
            url.contains("dood", ignoreCase = true) -> PlayerType.DOODSTREAM
            else -> PlayerType.UNKNOWN
        }
    }

    private suspend fun extractMegaEmbed(
        url: String,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Extraindo MegaEmbed...")

        // Tentar extração direta primeiro
        val html = app.get(url).text
        
        // Buscar M3U8 no HTML (como Puppeteer faz)
        val m3u8Regex = Regex("""https?://[^\s"'<>]+\.m3u8[^\s"'<>]*""")
        val m3u8Matches = m3u8Regex.findAll(html)

        m3u8Matches.forEach { match ->
            val m3u8Url = match.value
            Log.d(TAG, "   ✅ M3U8 encontrado: $m3u8Url")

            M3u8Helper.generateM3u8(
                source = name,
                streamUrl = m3u8Url,
                referer = url,
                headers = mapOf("Referer" to url)
            ).forEach(callback)
        }

        // Se não encontrou, usar WebView (como Puppeteer com interceptação)
        if (m3u8Matches.count() == 0) {
            Log.d(TAG, "   ⚠️  M3U8 não encontrado no HTML, usando WebView...")
            extractWithWebView(url, callback)
        }
    }

    private suspend fun extractPlayerEmbedAPI(
        url: String,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Extraindo PlayerEmbedAPI...")
        
        // Similar ao MegaEmbed
        extractWithWebView(url, callback)
    }

    private suspend fun extractDoodStream(
        url: String,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Extraindo DoodStream...")
        
        // Usar extractor existente
        // (DoodStream já tem implementação no projeto)
    }

    private suspend fun extractGeneric(
        url: String,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Extração genérica...")
        extractWithWebView(url, callback)
    }

    private suspend fun extractWithWebView(
        url: String,
        callback: (ExtractorLink) -> Unit
    ) {
        capturedUrls.clear()

        // WebView com interceptação (equivalente ao Puppeteer page.on('request'))
        val webView = WebView(/* context */)
        
        webView.webViewClient = object : android.webkit.WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val requestUrl = request.url.toString()

                // Capturar URLs de vídeo (como Puppeteer faz)
                if (isVideoUrl(requestUrl)) {
                    Log.d(TAG, "📡 Requisição capturada: $requestUrl")
                    capturedUrls[requestUrl] = requestUrl
                }

                return super.shouldInterceptRequest(view, request)
            }
        }

        // Carregar URL
        webView.loadUrl(url)

        // Aguardar (equivalente ao Puppeteer waitForTimeout)
        delay(10000)

        // Processar URLs capturadas
        capturedUrls.values.forEach { videoUrl ->
            when {
                videoUrl.contains(".m3u8") -> {
                    Log.d(TAG, "   ✅ Processando M3U8: $videoUrl")
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = videoUrl,
                        referer = url
                    ).forEach(callback)
                }
                videoUrl.contains(".mp4") -> {
                    Log.d(TAG, "   ✅ Processando MP4: $videoUrl")
                    callback(
                        ExtractorLink(
                            source = name,
                            name = name,
                            url = videoUrl,
                            referer = url,
                            quality = 1080
                        )
                    )
                }
            }
        }
    }

    private fun isVideoUrl(url: String): Boolean {
        val videoExtensions = listOf(".m3u8", ".mp4", ".ts", ".woff2")
        return videoExtensions.any { url.contains(it, ignoreCase = true) }
    }

    enum class PlayerType {
        MEGAEMBED,
        PLAYEREMBEDAPI,
        DOODSTREAM,
        UNKNOWN
    }
}
```

---

## 🧪 Passo 4: Testar Implementação Kotlin

### Build do Plugin
```bash
cd c:\Users\KYTHOURS\Desktop\brcloudstream
.\gradlew MaxSeries:make
```

### Instalar no Dispositivo
```bash
adb install -r MaxSeries\build\MaxSeries.cs3
```

### Capturar Logs
```bash
adb logcat | Select-String "PuppeteerExtractor"
```

---

## 📊 Comparação: Puppeteer vs Kotlin

| Tarefa | Puppeteer (Teste) | Kotlin (Produção) |
|--------|-------------------|-------------------|
| **Interceptar rede** | `page.on('request')` | `shouldInterceptRequest()` |
| **Aguardar** | `await page.waitForTimeout(10000)` | `delay(10000)` |
| **Regex** | `html.match(/\.m3u8/gi)` | `Regex("\.m3u8").findAll(html)` |
| **Log** | `console.log()` | `Log.d()` |
| **Armazenar URLs** | `Set<string>` | `ConcurrentHashMap<String, String>` |

---

## ✅ Checklist de Migração

- [ ] Executar teste Puppeteer
- [ ] Analisar `puppeteer-results.json`
- [ ] Identificar padrões de URL
- [ ] Criar extractor Kotlin baseado nos padrões
- [ ] Implementar interceptação WebView
- [ ] Adicionar logs de debug
- [ ] Build do plugin
- [ ] Testar no dispositivo
- [ ] Validar com ADB logs
- [ ] Ajustar baseado nos resultados

---

**Próximo Passo:** Execute o teste Puppeteer e analise os resultados!

```bash
npm install
node test-puppeteer-extractor.js https://maxseries.one/episodio/258444
```
