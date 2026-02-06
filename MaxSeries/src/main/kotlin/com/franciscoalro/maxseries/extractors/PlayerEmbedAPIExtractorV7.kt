package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.ExtractorLinkType
import android.webkit.*
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache

/**
 * PlayerEmbedAPI Extractor v7 - WebView Network Interception (Jan 2026)
 * 
 * PROBLEMA: O playerembedapi.link carrega o vídeo via JavaScript (JWPlayer).
 * O HTML não contém a URL diretamente.
 * 
 * SOLUÇÃO: Usar WebView para interceptar requisições de rede quando o player carregar.
 * 
 * LÓGICA:
 * 1. Instancia um WebView real (invisível) usando reflection para obter contexto.
 * 2. Intercepta requisições de rede via shouldInterceptRequest e onLoadResource.
 * 3. Injeta script JS para capturar XMLHttpRequest e fetch API.
 * 4. Captura URLs que contenham: .m3u8, .mp4, cloudatacdn.com, storage.googleapis.com, sssrr.org
 * 5. Timeout de 15 segundos para evitar bloqueios.
 */
class PlayerEmbedAPIExtractorV7 : ExtractorApi() {
    override val name = "PlayerEmbedAPI"
    override val mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "PlayerEmbedAPI-v7"
        private const val TIMEOUT_SECONDS = 25L  // Aumentado de 15s para 25s
        private val cleanedUp = AtomicBoolean(false)  // NOVO: Flag atômica
        
        // Padrões de URL de vídeo para capturar
        private val VIDEO_PATTERNS = listOf(
            ".m3u8",
            ".mp4",
            ".mkv",
            ".webm",
            "cloudatacdn.com",
            "storage.googleapis.com",
            "sssrr.org",
            "/video",
            "/stream",
            "/hls",
            "/play"
        )
    }

    private val headers = mapOf(
        "Referer" to "https://playerembedapi.link/",
        "Origin" to "https://playerembedapi.link",
        "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding" to "gzip, deflate, br"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.wtf(TAG, "=== PlayerEmbedAPI v7.0 - WebView Network Interception ===")
        Log.d(TAG, "URL: $url")
        
        // Verificar cache primeiro
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "Cache HIT")
            callback.invoke(
                newExtractorLink(
                    source = "${name}_${System.currentTimeMillis() % 10000}",
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)} (Cached)",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = headers["Referer"]!!
                    this.quality = cached.quality
                    this.headers = headers
                }
            )
            return
        }
        
        val foundUrls = mutableSetOf<String>()
        val latch = CountDownLatch(1)
        val handler = Handler(Looper.getMainLooper())
        var cleanupRef: (() -> Unit)? = null
        
        handler.post {
            try {
                // Obter contexto via reflection
                val context = try {
                    val activityThread = Class.forName("android.app.ActivityThread")
                    val currentAppMethod = activityThread.getMethod("currentApplication")
                    currentAppMethod.invoke(null) as android.content.Context
                } catch (e: Exception) {
                    Log.e(TAG, "❌ Erro ao obter Contexto: ${e.message}")
                    latch.countDown()
                    return@post
                }

                if (context == null) {
                    Log.e(TAG, "❌ Contexto nulo!")
                    latch.countDown()
                    return@post
                }
                
                val webView = WebView(context)
                
                webView.settings.apply {
                    javaScriptEnabled = true
                    domStorageEnabled = true
                    databaseEnabled = true
                    userAgentString = headers["User-Agent"]
                    blockNetworkImage = true // Melhora performance
                    mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                    mediaPlaybackRequiresUserGesture = false
                    cacheMode = WebSettings.LOAD_NO_CACHE // Evita cache
                }

                // WebView invisível (dimensões 1x1)
                webView.layout(0, 0, 1, 1)
                webView.setBackgroundColor(0) // Transparente

                cleanupRef = {
                    if (cleanedUp.compareAndSet(false, true)) {
                        handler.post {
                            try {
                                Log.d(TAG, "🧹 Limpando WebView...")
                                webView.stopLoading()
                                webView.loadUrl("about:blank")
                                // Remover da hierarquia se estiver adicionado
                                webView.removeAllViews()
                                webView.destroy()
                            } catch (e: Exception) {
                                Log.e(TAG, "Erro no cleanup: ${e.message}")
                            }
                        }
                    }
                }

                // Script injetado para interceptar XHR e Fetch
                val injectedScript = """
                    (function() {
                        console.log('[PlayerEmbedAPI-v7] Script injetado');
                        
                        window.onerror = function(msg, url, line) {
                            console.log('[PlayerEmbedAPI-v7] JS Error: ' + msg);
                        };

                        const VIDEO_PATTERNS = ['.m3u8', '.mp4', '.mkv', '.webm', 'cloudatacdn', 'googleapis', 'sssrr', '/video', '/stream', '/hls'];
                        
                        function isVideoUrl(url) {
                            if (!url || typeof url !== 'string') return false;
                            const lowerUrl = url.toLowerCase();
                            return VIDEO_PATTERNS.some(pattern => lowerUrl.includes(pattern));
                        }
                        
                        function reportUrl(url, source) {
                            if (isVideoUrl(url)) {
                                console.log('PLAYEREMBEDAPI_VIDEO_URL:' + url + '|SOURCE:' + source);
                            }
                        }

                        // Hook XMLHttpRequest
                        const origOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function(method, url) {
                            reportUrl(url, 'XHR_OPEN');
                            this.addEventListener('load', function() {
                                reportUrl(this.responseURL, 'XHR_LOAD');
                            });
                            return origOpen.apply(this, arguments);
                        };
                        
                        // Hook Fetch
                        const origFetch = window.fetch;
                        window.fetch = function(input, init) {
                            const url = (typeof input === 'string') ? input : (input && input.url);
                            reportUrl(url, 'FETCH');
                            
                            return origFetch.apply(this, arguments).then(response => {
                                reportUrl(response.url, 'FETCH_RESPONSE');
                                return response;
                            });
                        };
                        
                        // Observar elementos de vídeo
                        function checkVideoElements() {
                            document.querySelectorAll('video, source').forEach(el => {
                                if (el.src) reportUrl(el.src, 'VIDEO_ELEMENT');
                            });
                        }
                        
                        // Verificar a cada 500ms
                        setInterval(checkVideoElements, 500);
                        
                        // Verificar jwplayer se existir
                        if (window.jwplayer) {
                            console.log('[PlayerEmbedAPI-v7] JWPlayer detectado');
                            try {
                                const player = jwplayer();
                                if (player && player.getPlaylist) {
                                    const playlist = player.getPlaylist();
                                    if (playlist && playlist.length > 0) {
                                        playlist.forEach(item => {
                                            if (item.file) reportUrl(item.file, 'JWPLAYER');
                                            if (item.sources) {
                                                item.sources.forEach(src => {
                                                    if (src.file) reportUrl(src.file, 'JWPLAYER_SOURCE');
                                                });
                                            }
                                        });
                                    }
                                }
                            } catch(e) {
                                console.log('[PlayerEmbedAPI-v7] JWPlayer error: ' + e.message);
                            }
                        }
                        
                        console.log('[PlayerEmbedAPI-v7] Hooks instalados');
                    })();
                """.trimIndent()

                webView.webChromeClient = object : WebChromeClient() {
                    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                        val msg = consoleMessage?.message() ?: return false
                        
                        // Capturar URL de vídeo
                        if (msg.contains("PLAYEREMBEDAPI_VIDEO_URL:")) {
                            try {
                                val urlPart = msg.substringAfter("PLAYEREMBEDAPI_VIDEO_URL:").substringBefore("|SOURCE:")
                                val sourcePart = msg.substringAfter("|SOURCE:", "UNKNOWN")
                                
                                Log.d(TAG, "🎯 URL CAPTURADA via $sourcePart: ${urlPart.take(80)}...")
                                
                                if (isValidVideoUrl(urlPart)) {
                                    foundUrls.add(urlPart)
                                    // Não dar latch.countDown() imediatamente - continuar procurando mais qualidades
                                    if (foundUrls.size >= 3) {
                                        latch.countDown()
                                        cleanupRef?.invoke()
                                    }
                                }
                            } catch (e: Exception) {
                                Log.e(TAG, "Erro ao processar console: ${e.message}")
                            }
                            return true
                        }
                        
                        if (msg.contains("[PlayerEmbedAPI-v7]")) {
                            Log.d(TAG, "JS: $msg")
                        }
                        return false
                    }
                }

                webView.webViewClient = object : WebViewClient() {
                    override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                        super.onPageStarted(view, url, favicon)
                        Log.d(TAG, "🟢 Page Started: $url")
                    }

                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        Log.d(TAG, "🏁 Page Finished: $url")
                        
                        if (cleanedUp.get()) return  // Não injetar se já limpou
                        
                        // Injetar script para interceptar requisições
                        try {
                            view?.evaluateJavascript(injectedScript, null)
                        } catch (e: IllegalStateException) {
                            Log.e(TAG, "WebView já destruído")
                        }
                        
                        // Tentar extrair do jwplayer diretamente
                        view?.evaluateJavascript("""
                            (function() {
                                if (window.jwplayer) {
                                    try {
                                        var player = jwplayer();
                                        if (player && player.getPlaylist) {
                                            var playlist = player.getPlaylist();
                                            if (playlist && playlist.length > 0) {
                                                playlist.forEach(function(item) {
                                                    if (item.file) console.log('PLAYEREMBEDAPI_VIDEO_URL:' + item.file + '|SOURCE:JWPLAYER_DIRECT');
                                                });
                                            }
                                        }
                                    } catch(e) {}
                                }
                                return 'checked';
                            })();
                        """, null)
                    }
                    
                    override fun onLoadResource(view: WebView?, url: String?) {
                        super.onLoadResource(view, url)
                        url?.let {
                            if (isValidVideoUrl(it)) {
                                Log.d(TAG, "🔍 LoadResource: ${it.take(80)}...")
                                foundUrls.add(it)
                                // Fallback: liberar imediatamente se for mídia direta
                                if (!cleanedUp.get() &&
                                    (it.contains(".m3u8", ignoreCase = true) ||
                                     it.contains(".mp4", ignoreCase = true))) {
                                    latch.countDown()
                                    cleanupRef?.invoke()
                                }
                            }
                        }
                    }

                    override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                        val requestUrl = request?.url?.toString()
                        requestUrl?.let {
                            if (isValidVideoUrl(it)) {
                                Log.d(TAG, "🕵️ Intercepted: ${it.take(80)}...")
                                foundUrls.add(it)
                                
                                // Se encontrou .m3u8 ou .mp4 diretamente, liberar
                                if (!cleanedUp.get() && 
                                    (it.contains(".m3u8", ignoreCase = true) || 
                                     it.contains(".mp4", ignoreCase = true))) {
                                    latch.countDown()
                                    cleanupRef?.invoke()
                                }
                            }
                        }
                        return super.shouldInterceptRequest(view, request)
                    }

                    override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                        Log.e(TAG, "❌ Page Error: ${error?.toString()} for ${request?.url}")
                        super.onReceivedError(view, request, error)
                    }

                    override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                        Log.d(TAG, "⚠️ SSL Error (proceeding): ${error?.toString()}")
                        handler?.proceed()
                    }
                }

                Log.d(TAG, "Carregando URL no WebView: $url")
                webView.loadUrl(url, headers)

            } catch (e: Exception) {
                Log.e(TAG, "❌ Erro ao iniciar WebView: ${e.message}")
                latch.countDown()
            }
        }

        // Aguardar timeout
        try {
            val captured = latch.await(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            if (!captured) {
                Log.w(TAG, "⏱️ Timeout após ${TIMEOUT_SECONDS}s. URLs encontradas: ${foundUrls.size}")
            }
        } catch (e: InterruptedException) {
            Log.e(TAG, "❌ Interrompido")
        } finally {
            cleanupRef?.invoke()
        }

        // Processar URLs encontradas
        if (foundUrls.isNotEmpty()) {
            Log.wtf(TAG, "=== ${foundUrls.size} URLs capturadas ===")
            
            foundUrls.forEachIndexed { index, videoUrl ->
                val quality = QualityDetector.detectFromUrl(videoUrl)
                val type = if (videoUrl.contains(".m3u8", ignoreCase = true)) {
                    ExtractorLinkType.M3U8
                } else {
                    ExtractorLinkType.VIDEO
                }
                
                // Cachear primeira URL
                if (index == 0) {
                    VideoUrlCache.put(url, videoUrl, quality, name)
                }
                
                callback.invoke(
                    newExtractorLink(
                        source = "${name}_${System.currentTimeMillis() % 10000}",
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (WebView v7)",
                        url = videoUrl,
                        type = type
                    ) {
                        this.referer = headers["Referer"]!!
                        this.headers = headers
                        this.quality = quality
                    }
                )
                
                Log.d(TAG, "✓ Link ${index + 1}: ${videoUrl.take(60)}...")
            }
        } else {
            Log.e(TAG, "❌ Nenhuma URL de vídeo capturada")
        }
    }
    
    /**
     * Verifica se a URL é um vídeo válido
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        val lowerUrl = url.lowercase()
        
        return VIDEO_PATTERNS.any { pattern ->
            lowerUrl.contains(pattern.lowercase())
        }
    }
}
