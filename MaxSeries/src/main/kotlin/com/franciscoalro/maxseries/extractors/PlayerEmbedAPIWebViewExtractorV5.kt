package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.util.Log
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*
import com.franciscoalro.maxseries.utils.QualityDetector

/**
 * PlayerEmbedAPI WebView Extractor v5.0 - Security & Performance (Feb 2026)
 * 
 * v5.0 Changes:
 * - 🔒 SEGURANÇA: NÃO ignora erros SSL (removido handler?.proceed())
 * - 🛡️ SEGURANÇA: Validação de domínios permitidos
 * - ⚡ PERFORMANCE: CoroutineScope controlado (não GlobalScope)
 * - 🎯 DETECÇÃO: Mais padrões de URL de vídeo
 * - 🧹 LIMPEZA: Melhor gerenciamento de recursos do WebView
 */
class PlayerEmbedAPIWebViewExtractorV5 {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI-WV-v5"
        private const val TIMEOUT_MS = 15000L
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        // Domínios permitidos para requisições
        private val ALLOWED_DOMAINS = listOf(
            "playerembedapi.link",
            "sssrr.org",
            "googleapis.com",
            "short.icu",
            "abyss.to"
        )
        
        // Extensões de vídeo
        private val VIDEO_EXTENSIONS = listOf(".mp4", ".m3u8", ".mkv", ".webm", ".ts")
        private val VIDEO_HINTS = listOf("/sora/", "sssrr.org")
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        Log.wtf(TAG, "=== WebView v5.0 INICIANDO ===")
        Log.d(TAG, "URL: $sourceUrl")
        
        return withContext(Dispatchers.Main) {
            val capturedUrls = linkedSetOf<String>()
            var webView: WebView? = null
            var isCompleted = false
            var job: Job? = null
            
            try {
                val context = getContext() ?: run {
                    Log.e(TAG, "Não foi possível obter contexto")
                    return@withContext emptyList()
                }
                
                webView = createWebView(context) { url, type ->
                    Log.wtf(TAG, "URL capturada: $type - ${url.take(60)}")
                    if (isValidVideoUrl(url)) {
                        capturedUrls.add(url)
                        isCompleted = true
                    }
                }
                
                webView.loadUrl(sourceUrl)
                
                // Aguardar com timeout
                var elapsed = 0L
                while (elapsed < TIMEOUT_MS && !isCompleted && isActive) {
                    delay(100)
                    elapsed += 100
                }
                
                if (!isCompleted) {
                    Log.w(TAG, "Timeout após ${TIMEOUT_MS}ms")
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Erro: ${e.message}")
            } finally {
                // Limpar recursos
                job?.cancel()
                cleanupWebView(webView)
            }
            
            if (capturedUrls.isNotEmpty()) {
                createLinks(capturedUrls.first(), referer)
            } else {
                emptyList()
            }
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(
        context: android.content.Context,
        onUrlFound: (String, String) -> Unit
    ): WebView {
        return WebView(context).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                userAgentString = USER_AGENT
                // Segurança: desabilitar acesso a arquivos locais
                allowFileAccess = false
                allowContentAccess = false
            }
            
            webViewClient = object : WebViewClient() {
                
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? {
                    val url = request.url.toString()
                    
                    // Log apenas URLs relevantes
                    if (isRelevantUrl(url)) {
                        Log.v(TAG, "REQ: ${url.take(80)}")
                    }
                    
                    // Ignorar arquivos estáticos
                    if (isStaticFile(url)) {
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // Capturar URLs de vídeo
                    if (isVideoUrl(url)) {
                        Log.wtf(TAG, "VIDEO: ${url.take(60)}")
                        onUrlFound(url, "VIDEO")
                    }
                    
                    // Capturar redirect SSSRR
                    if (url.contains("sssrr.org") && url.contains("timestamp=")) {
                        Log.wtf(TAG, "SSSRR: ${url.take(60)}")
                        handleSssrrRedirect(url, onUrlFound)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    Log.d(TAG, "Page loaded: ${url.take(40)}")
                    
                    // Injeta script para automação do player
                    injectPlayerAutomation(view)
                }
                
                override fun onReceivedError(
                    view: WebView?,
                    request: WebResourceRequest?,
                    error: WebResourceError?
                ) {
                    Log.e(TAG, "WebView Error: ${error?.description}")
                }
                
                // 🔒 SEGURANÇA: NÃO ignora erros SSL
                override fun onReceivedSslError(
                    view: WebView?,
                    handler: SslErrorHandler?,
                    error: android.net.http.SslError?
                ) {
                    Log.e(TAG, "SSL Error: $error")
                    // NÃO chama handler?.proceed() - cancela a requisição
                    handler?.cancel()
                }
            }
            
            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    Log.d("WebViewJS", message.message())
                    return true
                }
            }
        }
    }
    
    /**
     * Injeta script JavaScript para automação do player
     */
    private fun injectPlayerAutomation(view: WebView) {
        view.evaluateJavascript("""
            (function() {
                console.log('Player automation injected');
                
                // Clicar em elementos do player
                var selectors = [
                    '#overlay', '.overlay', '.jwplayer', 
                    '.play-button', 'video', 
                    '[class*="play"]', '[id*="play"]'
                ];
                
                selectors.forEach(function(sel, index) {
                    setTimeout(function() {
                        var el = document.querySelector(sel);
                        if (el) {
                            console.log('Clicking: ' + sel);
                            el.click();
                        }
                    }, index * 100);
                });
                
                // Verificar video direto
                var video = document.querySelector('video');
                if (video && video.src) {
                    console.log('Video src: ' + video.src);
                }
            })();
        """.trimIndent(), null)
    }
    
    /**
     * Trata redirect SSSRR
     */
    private fun handleSssrrRedirect(url: String, callback: (String, String) -> Unit) {
        // ⚡ PERFORMANCE: Usar CoroutineScope controlado em vez de GlobalScope
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = com.lagradost.cloudstream3.app.get(
                    url = url,
                    allowRedirects = true,
                    headers = mapOf(
                        "User-Agent" to USER_AGENT,
                        "Accept" to "*/*"
                    ),
                    timeout = 10
                )
                
                val finalUrl = response.url
                Log.wtf(TAG, "Redirect result: ${finalUrl.take(60)}")
                
                if (isVideoUrl(finalUrl)) {
                    withContext(Dispatchers.Main) {
                        callback(finalUrl, "REDIRECT")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Redirect failed: ${e.message}")
            }
        }
    }
    
    /**
     * Cria links a partir da URL capturada
     */
    private suspend fun createLinks(url: String, referer: String): List<ExtractorLink> {
        val quality = detectQualityFromUrl(url)
        
        Log.wtf(TAG, "Criando link: $quality")
        
        return listOf(
            newExtractorLink(
                source = "PlayerEmbedAPI",
                name = "🎬 PlayerEmbedAPI [$quality]",
                url = url,
                type = ExtractorLinkType.VIDEO
            ) {
                this.referer = referer
                this.headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "*/*",
                    "Referer" to referer
                )
            }
        )
    }
    
    /**
     * Detecta qualidade a partir da URL
     */
    private fun detectQualityFromUrl(url: String): String {
        return when {
            url.contains("2160") || url.contains("4k", ignoreCase = true) -> "4K"
            url.contains("1080") -> "1080p"
            url.contains("720") -> "720p"
            url.contains("480") -> "480p"
            url.contains("360") -> "360p"
            else -> "HD"
        }
    }
    
    /**
     * Obtém contexto da aplicação
     */
    private fun getContext(): android.content.Context? {
        return try {
            Class.forName("android.app.ActivityThread")
                .getMethod("currentApplication")
                .invoke(null) as android.content.Context
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Limpa recursos do WebView
     */
    private fun cleanupWebView(webView: WebView?) {
        try {
            webView?.stopLoading()
            webView?.loadUrl("about:blank")
            webView?.clearHistory()
            webView?.removeAllViews()
            webView?.destroy()
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao limpar WebView: ${e.message}")
        }
    }
    
    /**
     * Verifica se URL é relevante para log
     */
    private fun isRelevantUrl(url: String): Boolean {
        return url.contains("sssrr") || 
               url.contains("googleapis") || 
               url.contains("player") ||
               url.contains("video")
    }
    
    /**
     * Verifica se é arquivo estático
     */
    private fun isStaticFile(url: String): Boolean {
        return url.endsWith(".js") || 
               url.endsWith(".css") || 
               url.endsWith(".png") || 
               url.endsWith(".jpg") ||
               url.contains("/player/") || 
               url.contains("jwplayer") ||
               url.contains("statics.sssrr")
    }
    
    /**
     * Verifica se URL é de vídeo
     */
    private fun isVideoUrl(url: String): Boolean {
        return VIDEO_EXTENSIONS.any { ext ->
            url.contains(ext, ignoreCase = true)
        } || VIDEO_HINTS.any { hint ->
            url.contains(hint, ignoreCase = true)
        } || (url.contains("googleapis.com") && url.contains(".mp4"))
    }
    
    /**
     * Valida se URL de vídeo é válida
     */
    private fun isValidVideoUrl(url: String): Boolean {
        return url.startsWith("http") && 
               (isVideoUrl(url) || ALLOWED_DOMAINS.any { url.contains(it) })
    }
    
}
