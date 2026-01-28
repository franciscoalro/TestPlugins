package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.Qualities
import kotlinx.coroutines.*
import java.util.concurrent.TimeUnit

class PlayerEmbedAPIWebViewExtractor {
    
    private val capturedUrls = mutableSetOf<String>()
    private var extractionJob: CompletableDeferred<List<ExtractorLink>>? = null
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extract(imdbId: String, referer: String = "https://viewplayer.online/"): List<ExtractorLink> {
        return withContext(Dispatchers.Main) {
            extractionJob = CompletableDeferred()
            capturedUrls.clear()
            
            val webView = WebView(com.lagradost.cloudstream3.app).apply {
                settings.apply {
                    javaScriptEnabled = true
                    domStorageEnabled = true
                    databaseEnabled = true
                    useWideViewPort = true
                    loadWithOverviewMode = true
                    
                    // Bloquear popups
                    javaScriptCanOpenWindowsAutomatically = false
                    setSupportMultipleWindows(false)
                    
                    // User agent real
                    userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                // Interceptar requisições
                webViewClient = object : WebViewClient() {
                    override fun shouldInterceptRequest(
                        view: WebView,
                        request: WebResourceRequest
                    ): WebResourceResponse? {
                        val url = request.url.toString()
                        
                        // Capturar URLs de vídeo
                        when {
                            url.contains("sssrr.org") && url.contains("?timestamp=") -> {
                                android.util.Log.d("PlayerEmbedAPI", "🎯 Captured: $url")
                                capturedUrls.add(url)
                            }
                            url.contains("googleapis.com") && url.contains(".mp4") -> {
                                android.util.Log.d("PlayerEmbedAPI", "📹 Captured: $url")
                                capturedUrls.add(url)
                            }
                            url.contains("trycloudflare.com") && url.contains("/sora/") -> {
                                android.util.Log.d("PlayerEmbedAPI", "☁️ Captured: $url")
                                capturedUrls.add(url)
                            }
                        }
                        
                        // Bloquear ads
                        if (url.contains("usheebainaut.com") || 
                            url.contains("attirecideryeah.com") ||
                            url.contains("googlesyndication.com")) {
                            return WebResourceResponse("text/plain", "utf-8", null)
                        }
                        
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    override fun onPageFinished(view: WebView, url: String) {
                        super.onPageFinished(view, url)
                        
                        if (url.contains("viewplayer.online")) {
                            // Injetar script para automatizar cliques
                            injectAutomationScript(view)
                        }
                    }
                }
                
                // Chrome client para debug
                webChromeClient = object : WebChromeClient() {
                    override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                        android.util.Log.d("WebView", "${message.message()} -- From line ${message.lineNumber()}")
                        return true
                    }
                }
            }
            
            // Carregar ViewPlayer
            val viewPlayerUrl = "https://viewplayer.online/filme/$imdbId"
            android.util.Log.d("PlayerEmbedAPI", "Loading: $viewPlayerUrl")
            webView.loadUrl(viewPlayerUrl)
            
            // Timeout de 30 segundos
            withTimeoutOrNull(30000) {
                extractionJob?.await()
            } ?: run {
                android.util.Log.e("PlayerEmbedAPI", "Timeout - captured ${capturedUrls.size} URLs")
                convertToExtractorLinks()
            }
        }
    }
    
    private fun injectAutomationScript(webView: WebView) {
        val script = """
            (function() {
                console.log('🚀 Automation script injected');
                
                // Bloquear window.open
                window.open = function() { 
                    console.log('🚫 Blocked popup');
                    return null; 
                };
                
                // Função para clicar no botão PlayerEmbedAPI
                function clickPlayerEmbedAPIButton() {
                    const btn = document.querySelector('button[data-source*="playerembedapi"]');
                    if (btn) {
                        console.log('✅ Clicking PlayerEmbedAPI button');
                        btn.click();
                        return true;
                    }
                    return false;
                }
                
                // Função para clicar no overlay do player
                function clickOverlay() {
                    // Procurar em todos os iframes
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const overlay = iframeDoc.getElementById('overlay');
                            if (overlay) {
                                console.log('✅ Clicking overlay');
                                overlay.click();
                                
                                // Clicar novamente após 3s
                                setTimeout(() => {
                                    console.log('✅ Clicking overlay again');
                                    overlay.click();
                                }, 3000);
                                
                                return true;
                            }
                        } catch (e) {
                            // Cross-origin, não pode acessar
                        }
                    }
                    return false;
                }
                
                // Tentar clicar no botão após 3s
                setTimeout(() => {
                    if (clickPlayerEmbedAPIButton()) {
                        // Tentar clicar no overlay após 10s
                        setTimeout(() => {
                            clickOverlay();
                        }, 10000);
                    }
                }, 3000);
                
                // Monitorar elemento video
                let checkCount = 0;
                const checkVideo = setInterval(() => {
                    checkCount++;
                    
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const video = iframeDoc.querySelector('video');
                            if (video && video.src) {
                                console.log('📹 Video found: ' + video.src);
                                Android.onVideoFound(video.src);
                            }
                        } catch (e) {}
                    }
                    
                    // Parar após 40 tentativas (40s)
                    if (checkCount >= 40) {
                        clearInterval(checkVideo);
                        console.log('⏱️ Timeout');
                        Android.onTimeout();
                    }
                }, 1000);
            })();
        """.trimIndent()
        
        webView.evaluateJavascript(script, null)
    }
    
    private fun convertToExtractorLinks(): List<ExtractorLink> {
        return capturedUrls.mapNotNull { url ->
            try {
                ExtractorLink(
                    source = "PlayerEmbedAPI",
                    name = "PlayerEmbedAPI",
                    url = url,
                    referer = "https://viewplayer.online/",
                    quality = detectQuality(url),
                    isM3u8 = false
                )
            } catch (e: Exception) {
                android.util.Log.e("PlayerEmbedAPI", "Error creating link: ${e.message}")
                null
            }
        }
    }
    
    private fun detectQuality(url: String): Int {
        return when {
            url.contains("1080") || url.contains("1080p") -> Qualities.P1080.value
            url.contains("720") || url.contains("720p") -> Qualities.P720.value
            url.contains("480") || url.contains("480p") -> Qualities.P480.value
            url.contains("360") || url.contains("360p") -> Qualities.P360.value
            else -> Qualities.Unknown.value
        }
    }
    
    // Interface JavaScript para comunicação
    inner class JavaScriptInterface {
        @JavascriptInterface
        fun onVideoFound(url: String) {
            android.util.Log.d("PlayerEmbedAPI", "JS callback - Video: $url")
            capturedUrls.add(url)
            
            // Se capturou URLs, completar extração
            if (capturedUrls.isNotEmpty()) {
                extractionJob?.complete(convertToExtractorLinks())
            }
        }
        
        @JavascriptInterface
        fun onTimeout() {
            android.util.Log.d("PlayerEmbedAPI", "JS callback - Timeout")
            extractionJob?.complete(convertToExtractorLinks())
        }
    }
}
