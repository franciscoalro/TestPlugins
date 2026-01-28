package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*

class PlayerEmbedAPIWebViewExtractor {
    
    private val capturedUrls = mutableSetOf<String>()
    private var extractionJob: CompletableDeferred<List<ExtractorLink>>? = null
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extract(imdbId: String, referer: String = "https://viewplayer.online/"): List<ExtractorLink> {
        android.util.Log.wtf("PlayerEmbedAPI", "🚀🚀🚀 EXTRACT CHAMADO! IMDB: $imdbId 🚀🚀🚀")
        
        return withContext(Dispatchers.Main) {
            android.util.Log.d("PlayerEmbedAPI", "📱 Iniciando extração na Main thread")
            extractionJob = CompletableDeferred()
            capturedUrls.clear()
            
            // Obter Context do app
            val context = try {
                Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
            } catch (e: Exception) {
                android.util.Log.e("PlayerEmbedAPI", "❌ Erro ao obter Context: ${e.message}")
                return@withContext emptyList()
            }
            
            android.util.Log.d("PlayerEmbedAPI", "✅ Context obtido: ${context.javaClass.simpleName}")
            
            val webView = WebView(context).apply {
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
                
                // Adicionar interface JavaScript
                addJavascriptInterface(JavaScriptInterface(), "Android")
                
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
            android.util.Log.wtf("PlayerEmbedAPI", "🌐 Loading: $viewPlayerUrl")
            webView.loadUrl(viewPlayerUrl)
            
            // Timeout de 20 segundos (reduzido de 30s - detecção mais rápida)
            android.util.Log.d("PlayerEmbedAPI", "⏱️ Aguardando extração (20s timeout)...")
            withTimeoutOrNull(20000) {
                extractionJob?.await()
            } ?: run {
                android.util.Log.e("PlayerEmbedAPI", "⏱️ Timeout - captured ${capturedUrls.size} URLs")
                convertToExtractorLinks()
            }
        }
    }
    
    private fun injectAutomationScript(webView: WebView) {
        val script = """
            (function() {
                console.log('🚀 Automation script injected - FAST MODE');
                
                // Bloquear window.open
                window.open = function() { 
                    console.log('🚫 Blocked popup');
                    return null; 
                };
                
                // Contador de tentativas
                let attempts = 0;
                const MAX_ATTEMPTS = 60; // 60 segundos max
                
                // Função para clicar no botão PlayerEmbedAPI
                function clickPlayerEmbedAPIButton() {
                    const btn = document.querySelector('button[data-source*="playerembedapi"]');
                    if (btn) {
                        console.log('✅ PlayerEmbedAPI button found - clicking immediately!');
                        btn.click();
                        return true;
                    }
                    return false;
                }
                
                // Função para clicar no overlay do player
                function clickOverlay() {
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const overlay = iframeDoc.getElementById('overlay');
                            if (overlay && overlay.offsetParent !== null) {
                                console.log('✅ Overlay found - clicking immediately!');
                                overlay.click();
                                
                                // Segundo clique após 2s
                                setTimeout(() => {
                                    if (overlay.offsetParent !== null) {
                                        console.log('✅ Second overlay click');
                                        overlay.click();
                                    }
                                }, 2000);
                                
                                return true;
                            }
                        } catch (e) {
                            // Cross-origin
                        }
                    }
                    return false;
                }
                
                // Função para verificar vídeo
                function checkForVideo() {
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const video = iframeDoc.querySelector('video');
                            if (video && video.src) {
                                console.log('📹 Video found: ' + video.src);
                                return video.src;
                            }
                        } catch (e) {}
                    }
                    return null;
                }
                
                // MutationObserver para detectar mudanças no DOM
                const observer = new MutationObserver((mutations) => {
                    // Verificar botão PlayerEmbedAPI
                    const btn = document.querySelector('button[data-source*="playerembedapi"]');
                    if (btn && !btn.dataset.clicked) {
                        btn.dataset.clicked = 'true';
                        console.log('🎯 Button detected via MutationObserver!');
                        btn.click();
                    }
                    
                    // Verificar overlay em iframes
                    const iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const overlay = iframeDoc.getElementById('overlay');
                            if (overlay && overlay.offsetParent !== null && !overlay.dataset.clicked) {
                                overlay.dataset.clicked = 'true';
                                console.log('🎯 Overlay detected via MutationObserver!');
                                overlay.click();
                                
                                setTimeout(() => {
                                    if (overlay.offsetParent !== null) {
                                        overlay.click();
                                    }
                                }, 2000);
                            }
                        } catch (e) {}
                    }
                });
                
                // Observar mudanças no body
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true
                });
                
                // Polling rápido inicial (100ms) para elementos já presentes
                let fastCheckCount = 0;
                const fastCheck = setInterval(() => {
                    fastCheckCount++;
                    
                    // Tentar clicar no botão
                    if (clickPlayerEmbedAPIButton()) {
                        console.log('⚡ Button clicked in fast check!');
                    }
                    
                    // Tentar clicar no overlay
                    if (clickOverlay()) {
                        console.log('⚡ Overlay clicked in fast check!');
                    }
                    
                    // Verificar vídeo
                    const videoUrl = checkForVideo();
                    if (videoUrl) {
                        console.log('⚡ Video found in fast check!');
                        clearInterval(fastCheck);
                        clearInterval(slowCheck);
                        observer.disconnect();
                        Android.onVideoFound(videoUrl);
                        return;
                    }
                    
                    // Parar fast check após 10s, continuar com slow check
                    if (fastCheckCount >= 100) { // 100 * 100ms = 10s
                        clearInterval(fastCheck);
                        console.log('⏱️ Switching to slow check...');
                    }
                }, 100); // Check a cada 100ms
                
                // Polling lento (1s) após fast check
                const slowCheck = setInterval(() => {
                    attempts++;
                    
                    // Verificar vídeo
                    const videoUrl = checkForVideo();
                    if (videoUrl) {
                        console.log('📹 Video found in slow check!');
                        clearInterval(fastCheck);
                        clearInterval(slowCheck);
                        observer.disconnect();
                        Android.onVideoFound(videoUrl);
                        return;
                    }
                    
                    // Timeout após MAX_ATTEMPTS
                    if (attempts >= MAX_ATTEMPTS) {
                        clearInterval(fastCheck);
                        clearInterval(slowCheck);
                        observer.disconnect();
                        console.log('⏱️ Timeout after ' + attempts + ' seconds');
                        Android.onTimeout();
                    }
                }, 1000); // Check a cada 1s
                
                // Cleanup ao descarregar página
                window.addEventListener('beforeunload', () => {
                    clearInterval(fastCheck);
                    clearInterval(slowCheck);
                    observer.disconnect();
                });
            })();
        """.trimIndent()
        
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun convertToExtractorLinks(): List<ExtractorLink> {
        return capturedUrls.mapNotNull { url ->
            try {
                // Se é URL do sssrr.org, seguir redirect para pegar URL final
                val finalUrl = if (url.contains("sssrr.org")) {
                    android.util.Log.d("PlayerEmbedAPI", "🔄 Seguindo redirect: $url")
                    try {
                        val response = com.lagradost.cloudstream3.app.get(
                            url,
                            allowRedirects = true,
                            headers = mapOf(
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Referer" to "https://viewplayer.online/"
                            )
                        )
                        val redirectedUrl = response.url
                        android.util.Log.d("PlayerEmbedAPI", "✅ URL final: $redirectedUrl")
                        redirectedUrl
                    } catch (e: Exception) {
                        android.util.Log.e("PlayerEmbedAPI", "❌ Erro ao seguir redirect: ${e.message}")
                        url // Usar URL original se falhar
                    }
                } else {
                    url
                }
                
                newExtractorLink(
                    source = "PlayerEmbedAPI",
                    name = "PlayerEmbedAPI ${getQualityLabel(detectQuality(finalUrl))}",
                    url = finalUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "https://viewplayer.online/"
                    this.headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Origin" to "https://viewplayer.online",
                        "Accept" to "*/*"
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e("PlayerEmbedAPI", "Error creating link: ${e.message}")
                null
            }
        }
    }
    
    private fun getQualityLabel(quality: Int): String {
        return when (quality) {
            Qualities.P1080.value -> "1080p"
            Qualities.P720.value -> "720p"
            Qualities.P480.value -> "480p"
            Qualities.P360.value -> "360p"
            else -> "HD"
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
                extractionJob?.complete(runBlocking { convertToExtractorLinks() })
            }
        }
        
        @JavascriptInterface
        fun onTimeout() {
            android.util.Log.d("PlayerEmbedAPI", "JS callback - Timeout")
            extractionJob?.complete(runBlocking { convertToExtractorLinks() })
        }
    }
}
