package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.app
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v224 - Anti-Detecção + Redirect Fix
 * 
 * Melhorias v224:
 * - 🛡️ Anti-detecção: Headers realistas para evitar redirecionamento para abyss.to
 * - 🎭 User-Agent do Chrome desktop
 * - 🍪 Cookie manager habilitado
 * - 🔒 SSL errors ignorados (alguns sites usam certificados inválidos)
 * 
 * v223: Segue redirect sssrr.org → googleapis.com
 */
class PlayerEmbedAPIWebViewExtractor {
    
    private val capturedUrls = mutableSetOf<String>()
    private var extractionJob: CompletableDeferred<List<ExtractorLink>>? = null
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 25000L // 25 segundos
    }
    
    /**
     * Extrai vídeo a partir da URL direta do PlayerEmbedAPI
     * @param sourceUrl URL do playerembedapi.link/?v=...
     * @param referer URL de referência (playerthree)
     */
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀🚀🚀 EXTRACT FROM URL: $sourceUrl 🚀🚀🚀")
        
        return withContext(Dispatchers.Main) {
            extractionJob = CompletableDeferred()
            capturedUrls.clear()
            
            // Obter Context
            val context = try {
                Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro ao obter Context: ${e.message}")
                return@withContext emptyList()
            }
            
            val webView = createWebView(context, referer)
            
            // Carregar URL direta do PlayerEmbedAPI
            android.util.Log.wtf(TAG, "🌐 Loading: $sourceUrl")
            webView.loadUrl(sourceUrl)
            
            // Aguardar extração
            android.util.Log.d(TAG, "⏱️ Aguardando extração (${TIMEOUT_MS}ms)...")
            val result = withTimeoutOrNull(TIMEOUT_MS) {
                extractionJob?.await()
            }
            
            // Limpar
            webView.stopLoading()
            webView.destroy()
            
            if (result == null) {
                android.util.Log.e(TAG, "⏱️ Timeout - ${capturedUrls.size} URLs")
            }
            
            processCapturedUrls(referer)
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(context: android.content.Context, referer: String): WebView {
        return WebView(context).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                useWideViewPort = true
                loadWithOverviewMode = true
                javaScriptCanOpenWindowsAutomatically = false
                setSupportMultipleWindows(false)
                
                // Anti-detecção: User-Agent realista (Chrome Windows)
                userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            // Cookie manager
            CookieManager.getInstance().setAcceptCookie(true)
            CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)
            
            addJavascriptInterface(JavaScriptInterface(), "Android")
            
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? {
                    val url = request.url.toString()
                    
                    // Capturar URLs de vídeo
                    when {
                        url.contains("sssrr.org") && url.contains("?timestamp=") -> {
                            android.util.Log.wtf(TAG, "🎯🎯🎯 URL SSSRR: $url")
                            capturedUrls.add(url)
                        }
                        url.contains("googleapis.com") && url.contains(".mp4") -> {
                            android.util.Log.wtf(TAG, "📹📹📹 GOOGLEAPIS: $url")
                            capturedUrls.add(url)
                        }
                        url.contains("trycloudflare.com") && url.contains("/sora/") -> {
                            android.util.Log.d(TAG, "☁️ Cloudflare: $url")
                            capturedUrls.add(url)
                        }
                    }
                    
                    // Bloquear ads conhecidas
                    if (shouldBlockUrl(url)) {
                        return WebResourceResponse("text/plain", "utf-8", null)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    android.util.Log.d(TAG, "📄 Página carregada: $url")
                    
                    // Injetar script de automação
                    injectAutomationScript(view)
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    // Ignorar erros SSL (alguns players usam certificados inválidos)
                    handler?.proceed()
                }
                
                override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                    android.util.Log.e(TAG, "❌ WebView error: ${error?.description}")
                }
            }
            
            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    android.util.Log.d("WebView", "${message.message()}")
                    return true
                }
            }
        }
    }
    
    private fun shouldBlockUrl(url: String): Boolean {
        val blockedDomains = listOf(
            "usheebainaut.com",
            "attirecideryeah.com",
            "googlesyndication.com",
            "googleadservices.com",
            "doubleclick.net",
            "facebook.com/tr",
            "analytics",
            "tracker"
        )
        return blockedDomains.any { url.contains(it) }
    }
    
    private fun injectAutomationScript(webView: WebView) {
        val script = """
            (function() {
                console.log('🚀 PlayerEmbedAPI Automation v224');
                
                // Anti-popup
                window.open = function() { 
                    console.log('🚫 Popup blocked');
                    return null; 
                };
                
                let attempts = 0;
                const MAX_ATTEMPTS = 50;
                
                // Função para clicar no overlay
                function clickOverlay() {
                    const selectors = [
                        '#overlay',
                        '.overlay',
                        '[class*="overlay"]',
                        '[id*="overlay"]',
                        '.play-button',
                        '[class*="play"]',
                        'video'
                    ];
                    
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el && el.offsetParent !== null) {
                            console.log('✅ Clicking: ' + selector);
                            el.click();
                            
                            // Múltiplos cliques
                            setTimeout(() => el.click(), 500);
                            setTimeout(() => el.click(), 1000);
                            return true;
                        }
                    }
                    return false;
                }
                
                // Observer para detectar elementos
                const observer = new MutationObserver(() => {
                    clickOverlay();
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                // Polling rápido
                const interval = setInterval(() => {
                    attempts++;
                    clickOverlay();
                    
                    // Verificar vídeo
                    const video = document.querySelector('video');
                    if (video && video.src) {
                        console.log('📹 Video found: ' + video.src);
                        Android.onVideoFound(video.src);
                        clearInterval(interval);
                        observer.disconnect();
                    }
                    
                    if (attempts >= MAX_ATTEMPTS) {
                        clearInterval(interval);
                        observer.disconnect();
                        Android.onTimeout();
                    }
                }, 500);
                
            })();
        """.trimIndent()
        
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun processCapturedUrls(referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🔄 Processando ${capturedUrls.size} URLs")
        
        if (capturedUrls.isEmpty()) {
            android.util.Log.e(TAG, "❌ NENHUMA URL CAPTURADA!")
            return emptyList()
        }
        
        return capturedUrls.mapNotNull { url ->
            try {
                val finalUrl = if (url.contains("sssrr.org")) {
                    android.util.Log.wtf(TAG, "🔄 Seguindo redirect...")
                    try {
                        val response = app.get(
                            url = url,
                            allowRedirects = true,
                            headers = mapOf(
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Accept" to "*/*",
                                "Referer" to referer
                            ),
                            timeout = 30
                        )
                        val final = response.url
                        android.util.Log.wtf(TAG, "✅ URL FINAL: $final")
                        final
                    } catch (e: Exception) {
                        android.util.Log.e(TAG, "❌ Erro redirect: ${e.message}")
                        url
                    }
                } else {
                    url
                }
                
                newExtractorLink(
                    source = "PlayerEmbedAPI",
                    name = "PlayerEmbedAPI ${detectQualityLabel(finalUrl)}",
                    url = finalUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = referer
                    this.headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Origin" to "https://playerembedapi.link",
                        "Referer" to referer,
                        "Accept" to "*/*"
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro: ${e.message}")
                null
            }
        }
    }
    
    private fun detectQualityLabel(url: String): String {
        return when {
            url.contains("1080") || url.contains("1080p") -> "1080p"
            url.contains("720") || url.contains("720p") -> "720p"
            url.contains("480") || url.contains("480p") -> "480p"
            url.contains("360") || url.contains("360p") -> "360p"
            else -> "HD"
        }
    }
    
    inner class JavaScriptInterface {
        @JavascriptInterface
        fun onVideoFound(url: String) {
            android.util.Log.wtf(TAG, "📹 Video: $url")
            capturedUrls.add(url)
            if (capturedUrls.isNotEmpty()) {
                extractionJob?.complete(runBlocking { processCapturedUrls("") })
            }
        }
        
        @JavascriptInterface
        fun onTimeout() {
            android.util.Log.d(TAG, "⏱️ Timeout")
            extractionJob?.complete(runBlocking { processCapturedUrls("") })
        }
    }
}
