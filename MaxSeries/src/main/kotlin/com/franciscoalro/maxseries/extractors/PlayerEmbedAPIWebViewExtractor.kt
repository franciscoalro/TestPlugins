package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.app
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v225 - Otimizado + Rápido
 * 
 * Melhorias v225:
 * - ⚡ Timeout reduzido para 15s (mais rápido)
 * - 🎯 Detecção precoce de URLs (não espera timeout)
 * - 🔍 Monitoramento de todas as requisições
 * - 📊 Logs detalhados para debug
 */
class PlayerEmbedAPIWebViewExtractor {
    
    private val capturedUrls = mutableSetOf<String>()
    private var extractionJob: CompletableDeferred<List<ExtractorLink>>? = null
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 15000L // 15 segundos apenas
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀 EXTRACT v225: $sourceUrl")
        
        return withContext(Dispatchers.Main) {
            extractionJob = CompletableDeferred()
            capturedUrls.clear()
            
            val context = try {
                Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro Context: ${e.message}")
                return@withContext emptyList()
            }
            
            val webView = createWebView(context, referer)
            
            android.util.Log.wtf(TAG, "🌐 Loading: $sourceUrl")
            webView.loadUrl(sourceUrl)
            
            // Aguardar com timeout
            val result = withTimeoutOrNull(TIMEOUT_MS) {
                extractionJob?.await()
            }
            
            webView.stopLoading()
            webView.destroy()
            
            if (result == null) {
                android.util.Log.w(TAG, "⏱️ Timeout com ${capturedUrls.size} URLs")
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
                useWideViewPort = true
                loadWithOverviewMode = true
                javaScriptCanOpenWindowsAutomatically = false
                setSupportMultipleWindows(false)
                userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            CookieManager.getInstance().setAcceptCookie(true)
            CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)
            
            addJavascriptInterface(JavaScriptInterface(), "Android")
            
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? {
                    val url = request.url.toString()
                    
                    // LOG TODAS AS REQUISIÇÕES (para debug)
                    if (url.contains("sssrr") || url.contains("googleapis") || url.contains("player") || url.contains("embed")) {
                        android.util.Log.d(TAG, "📡 REQ: ${url.take(80)}")
                    }
                    
                    // Capturar URLs de vídeo
                    when {
                        url.contains("sssrr.org") -> {
                            android.util.Log.wtf(TAG, "🎯🎯🎯 SSSRR: $url")
                            capturedUrls.add(url)
                            // Completar imediatamente quando encontrar
                            if (extractionJob?.isCompleted == false) {
                                extractionJob?.complete(emptyList())
                            }
                        }
                        url.contains("googleapis.com") && url.contains(".mp4") -> {
                            android.util.Log.wtf(TAG, "📹📹📹 GOOGLE: $url")
                            capturedUrls.add(url)
                            if (extractionJob?.isCompleted == false) {
                                extractionJob?.complete(emptyList())
                            }
                        }
                        url.contains(".mp4") || url.contains(".m3u8") || url.contains("video") -> {
                            android.util.Log.d(TAG, "🎬 VIDEO: ${url.take(60)}")
                            capturedUrls.add(url)
                        }
                    }
                    
                    // Bloquear ads
                    if (shouldBlockUrl(url)) {
                        return WebResourceResponse("text/plain", "utf-8", null)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                    android.util.Log.d(TAG, "📄 START: $url")
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    android.util.Log.wtf(TAG, "📄 FINISHED: $url")
                    
                    // Se redirecionou para abyss.to, logar erro
                    if (url.contains("abyss.to")) {
                        android.util.Log.e(TAG, "❌ ABYSS.DETECTADO! Site bloqueou automação")
                    }
                    
                    injectAutomationScript(view)
                    
                    // Se já capturou URLs, completar
                    if (capturedUrls.isNotEmpty() && extractionJob?.isCompleted == false) {
                        extractionJob?.complete(emptyList())
                    }
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    handler?.proceed()
                }
            }
            
            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    android.util.Log.d("WebView", message.message())
                    return true
                }
            }
        }
    }
    
    private fun shouldBlockUrl(url: String): Boolean {
        val blocked = listOf("googleads", "doubleclick", "googlesyndication", "facebook.com/tr", "analytics")
        return blocked.any { url.contains(it) }
    }
    
    private fun injectAutomationScript(webView: WebView) {
        val script = """
            (function() {
                console.log('🚀 v225 Automation');
                
                window.open = function() { return null; };
                
                let clicks = 0;
                const maxClicks = 5;
                
                function tryClick() {
                    if (clicks >= maxClicks) return;
                    clicks++;
                    
                    const selectors = ['#overlay', '.overlay', '.play-button', 'video', '[class*="play"]', '[id*="play"]'];
                    
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) {
                            console.log('✅ Click: ' + sel);
                            el.click();
                        }
                    }
                    
                    // Verificar vídeo
                    const video = document.querySelector('video');
                    if (video && video.src) {
                        console.log('📹 Video: ' + video.src);
                        Android.onVideoFound(video.src);
                    }
                }
                
                // Clicks imediatos
                setTimeout(tryClick, 100);
                setTimeout(tryClick, 500);
                setTimeout(tryClick, 1000);
                setTimeout(tryClick, 2000);
                setTimeout(tryClick, 3000);
                
                // Observer
                const observer = new MutationObserver(tryClick);
                if (document.body) {
                    observer.observe(document.body, { childList: true, subtree: true });
                }
            })();
        """.trimIndent()
        
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun processCapturedUrls(referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🔄 URLs: ${capturedUrls.size}")
        
        if (capturedUrls.isEmpty()) {
            android.util.Log.e(TAG, "❌ NENHUMA URL!")
            return emptyList()
        }
        
        return capturedUrls.mapNotNull { url ->
            try {
                val finalUrl = if (url.contains("sssrr.org")) {
                    android.util.Log.d(TAG, "🔄 Redirect...")
                    try {
                        val response = app.get(
                            url = url,
                            allowRedirects = true,
                            headers = mapOf(
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Referer" to referer
                            ),
                            timeout = 15
                        )
                        response.url
                    } catch (e: Exception) {
                        android.util.Log.e(TAG, "❌ Redirect erro: ${e.message}")
                        url
                    }
                } else {
                    url
                }
                
                newExtractorLink(
                    source = "PlayerEmbedAPI",
                    name = "PlayerEmbedAPI",
                    url = finalUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = referer
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro: ${e.message}")
                null
            }
        }
    }
    
    inner class JavaScriptInterface {
        @JavascriptInterface
        fun onVideoFound(url: String) {
            android.util.Log.wtf(TAG, "📹 JS Video: ${url.take(60)}")
            capturedUrls.add(url)
            if (extractionJob?.isCompleted == false) {
                extractionJob?.complete(emptyList())
            }
        }
    }
}
