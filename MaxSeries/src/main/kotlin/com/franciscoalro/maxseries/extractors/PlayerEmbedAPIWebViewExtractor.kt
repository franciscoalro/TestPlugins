package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.app
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v223 - Redirect Fix
 * 
 * Problema: URL intermediária (sssrr.org) não redireciona automaticamente no player
 * Solução: Seguir redirect 302 manualmente antes de retornar a URL final
 */
class PlayerEmbedAPIWebViewExtractor {
    
    private val capturedUrls = mutableSetOf<String>()
    private var extractionJob: CompletableDeferred<List<ExtractorLink>>? = null
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 20000L // 20 segundos
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extract(imdbId: String, referer: String = "https://viewplayer.online/"): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀🚀🚀 EXTRACT CHAMADO! IMDB: $imdbId 🚀🚀🚀")
        
        return withContext(Dispatchers.Main) {
            android.util.Log.d(TAG, "📱 Iniciando extração na Main thread")
            extractionJob = CompletableDeferred()
            capturedUrls.clear()
            
            // Obter Context do app
            val context = try {
                Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro ao obter Context: ${e.message}")
                return@withContext emptyList()
            }
            
            android.util.Log.d(TAG, "✅ Context obtido: ${context.javaClass.simpleName}")
            
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
                                android.util.Log.wtf(TAG, "🎯🎯🎯 URL SSSRR CAPTURADA: $url")
                                capturedUrls.add(url)
                            }
                            url.contains("googleapis.com") && url.contains(".mp4") -> {
                                android.util.Log.wtf(TAG, "📹📹📹 URL GOOGLEAPIS CAPTURADA: $url")
                                capturedUrls.add(url)
                            }
                            url.contains("trycloudflare.com") && url.contains("/sora/") -> {
                                android.util.Log.d(TAG, "☁️ Captured: $url")
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
            android.util.Log.wtf(TAG, "🌐 Loading: $viewPlayerUrl")
            webView.loadUrl(viewPlayerUrl)
            
            // Timeout de 20 segundos
            android.util.Log.d(TAG, "⏱️ Aguardando extração (${TIMEOUT_MS}ms timeout)...")
            val result = withTimeoutOrNull(TIMEOUT_MS) {
                extractionJob?.await()
            }
            
            // Limpar WebView
            webView.stopLoading()
            webView.destroy()
            
            if (result == null) {
                android.util.Log.e(TAG, "⏱️ Timeout - capturadas ${capturedUrls.size} URLs")
            }
            
            // Processar URLs capturadas (mesmo se timeout)
            val links = processCapturedUrls()
            android.util.Log.wtf(TAG, "✅✅✅ EXTRAÇÃO FINALIZADA: ${links.size} links ✅✅✅")
            links
        }
    }
    
    private fun injectAutomationScript(webView: WebView) {
        val script = """
            (function() {
                console.log('🚀 Automation script injected - v223 Redirect Fix');
                
                // Bloquear window.open
                window.open = function() { 
                    console.log('🚫 Blocked popup');
                    return null; 
                };
                
                // Contador de tentativas
                let attempts = 0;
                const MAX_ATTEMPTS = 60;
                
                // Função para clicar no botão PlayerEmbedAPI
                function clickPlayerEmbedAPIButton() {
                    const btn = document.querySelector('button[data-source*="playerembedapi"]');
                    if (btn && !btn.dataset.clicked) {
                        btn.dataset.clicked = 'true';
                        console.log('✅ PlayerEmbedAPI button found - clicking!');
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
                            if (overlay && overlay.offsetParent !== null && !overlay.dataset.clicked) {
                                overlay.dataset.clicked = 'true';
                                console.log('✅ Overlay found - clicking!');
                                overlay.click();
                                
                                // Múltiplos cliques para remover ads
                                setTimeout(() => overlay.click(), 1000);
                                setTimeout(() => overlay.click(), 2000);
                                
                                return true;
                            }
                        } catch (e) {
                            // Cross-origin
                        }
                    }
                    return false;
                }
                
                // MutationObserver para detectar mudanças no DOM
                const observer = new MutationObserver((mutations) => {
                    clickPlayerEmbedAPIButton();
                    clickOverlay();
                });
                
                // Observar mudanças no body
                if (document.body) {
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        attributes: true
                    });
                }
                
                // Polling rápido inicial (100ms)
                let fastCheckCount = 0;
                const fastCheck = setInterval(() => {
                    fastCheckCount++;
                    
                    clickPlayerEmbedAPIButton();
                    clickOverlay();
                    
                    // Verificar vídeo
                    const videos = document.querySelectorAll('video');
                    for (let v of videos) {
                        if (v.src) {
                            console.log('📹 Video found: ' + v.src);
                            Android.onVideoFound(v.src);
                            clearInterval(fastCheck);
                            clearInterval(slowCheck);
                            observer.disconnect();
                            return;
                        }
                    }
                    
                    // Parar fast check após 10s
                    if (fastCheckCount >= 100) {
                        clearInterval(fastCheck);
                        console.log('⏱️ Switching to slow check...');
                    }
                }, 100);
                
                // Polling lento (1s) após fast check
                const slowCheck = setInterval(() => {
                    attempts++;
                    
                    // Timeout após MAX_ATTEMPTS
                    if (attempts >= MAX_ATTEMPTS) {
                        clearInterval(fastCheck);
                        clearInterval(slowCheck);
                        observer.disconnect();
                        console.log('⏱️ Timeout after ' + attempts + ' seconds');
                        Android.onTimeout();
                    }
                }, 1000);
                
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
    
    /**
     * Processa URLs capturadas e segue redirects se necessário
     * v223: FIX - Segue redirect sssrr.org → googleapis.com
     */
    private suspend fun processCapturedUrls(): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🔄 PROCESSANDO ${capturedUrls.size} URLs CAPTURADAS")
        
        if (capturedUrls.isEmpty()) {
            android.util.Log.e(TAG, "❌ NENHUMA URL CAPTURADA!")
            return emptyList()
        }
        
        return capturedUrls.mapNotNull { url ->
            try {
                android.util.Log.d(TAG, "🔗 Processando URL: $url")
                
                // v223 FIX: Se é URL do sssrr.org, seguir redirect para pegar URL final
                val finalUrl = if (url.contains("sssrr.org")) {
                    android.util.Log.wtf(TAG, "🔄 URL INTERMEDIÁRIA DETECTADA (sssrr.org)")
                    android.util.Log.d(TAG, "📡 Fazendo request para seguir redirect...")
                    
                    try {
                        // Fazer request com allowRedirects = true
                        val response = app.get(
                            url = url,
                            allowRedirects = true,
                            headers = mapOf(
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                "Accept" to "*/*",
                                "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
                                "Referer" to "https://viewplayer.online/",
                                "Origin" to "https://viewplayer.online"
                            ),
                            timeout = 30 // 30 segundos timeout
                        )
                        
                        val redirectedUrl = response.url
                        android.util.Log.wtf(TAG, "✅✅✅ URL FINAL OBTIDA: $redirectedUrl")
                        
                        // Verificar se realmente redirecionou
                        if (redirectedUrl != url && redirectedUrl.contains("googleapis.com")) {
                            android.util.Log.wtf(TAG, "🎉 REDIRECT BEM-SUCEDIDO para Google Storage!")
                            redirectedUrl
                        } else {
                            android.util.Log.w(TAG, "⚠️ Redirect não foi para Google Storage, usando URL original")
                            url
                        }
                        
                    } catch (e: Exception) {
                        android.util.Log.e(TAG, "❌ Erro ao seguir redirect: ${e.message}")
                        android.util.Log.e(TAG, "⚠️ Usando URL intermediária como fallback")
                        e.printStackTrace()
                        url // Usar URL original se falhar
                    }
                } else {
                    android.util.Log.d(TAG, "✅ URL final já capturada: $url")
                    url
                }
                
                // Detectar qualidade da URL
                val quality = detectQuality(finalUrl)
                val qualityLabel = getQualityLabel(quality)
                
                android.util.Log.wtf(TAG, "🎬 CRIANDO EXTRACTOR LINK: $qualityLabel - $finalUrl")
                
                newExtractorLink(
                    source = "PlayerEmbedAPI",
                    name = "PlayerEmbedAPI $qualityLabel",
                    url = finalUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "https://viewplayer.online/"
                    this.headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Origin" to "https://viewplayer.online",
                        "Referer" to "https://viewplayer.online/",
                        "Accept" to "*/*",
                        "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
                        "Accept-Encoding" to "gzip, deflate, br",
                        "Connection" to "keep-alive",
                        "Sec-Fetch-Dest" to "video",
                        "Sec-Fetch-Mode" to "cors",
                        "Sec-Fetch-Site" to "cross-site"
                    )
                }
                
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro ao processar URL: ${e.message}")
                e.printStackTrace()
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
            android.util.Log.wtf(TAG, "📹 JS CALLBACK - Video encontrado: $url")
            capturedUrls.add(url)
            
            // Se capturou URLs, completar extração
            if (capturedUrls.isNotEmpty()) {
                extractionJob?.complete(runBlocking { processCapturedUrls() })
            }
        }
        
        @JavascriptInterface
        fun onTimeout() {
            android.util.Log.d(TAG, "⏱️ JS CALLBACK - Timeout")
            extractionJob?.complete(runBlocking { processCapturedUrls() })
        }
    }
}
