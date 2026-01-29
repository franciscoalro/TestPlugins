package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v230 - Rapido e Confiavel
 * 
 * Correcoes:
 * - Timeout reduzido para 8s (evita Job cancelled)
 * - Sem GlobalScope (usa CoroutineScope adequado)
 * - Callback mais rapido
 */
class PlayerEmbedAPIWebViewExtractor {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 8000L // 8 segundos apenas
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀 v230: ${sourceUrl.take(40)}...")
        
        return withContext(Dispatchers.Main) {
            var videoUrl: String? = null
            var webView: WebView? = null
            
            try {
                val context = Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
                
                webView = createWebView(context) { url ->
                    if (videoUrl == null) {
                        videoUrl = url
                        android.util.Log.wtf(TAG, "🎬 CAPTURADO!")
                    }
                }
                
                android.util.Log.d(TAG, "⏳ Carregando...")
                webView.loadUrl(sourceUrl)
                
                // Aguardar com timeout curto
                var elapsed = 0L
                while (elapsed < TIMEOUT_MS && videoUrl == null) {
                    delay(200) // Verifica a cada 200ms
                    elapsed += 200
                }
                
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro: ${e.message}")
            } finally {
                try {
                    webView?.stopLoading()
                    webView?.destroy()
                } catch (e: Exception) {}
            }
            
            if (videoUrl != null) {
                createLink(videoUrl!!, referer)
            } else {
                android.util.Log.w(TAG, "⚠️ Timeout sem video")
                emptyList()
            }
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(context: android.content.Context, onVideoFound: (String) -> Unit): WebView {
        return WebView(context).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? {
                    val url = request.url.toString()
                    
                    // IGNORAR arquivos estaticos PRIMEIRO
                    if (url.endsWith(".js") || url.endsWith(".css") || 
                        url.endsWith(".png") || url.endsWith(".jpg") ||
                        url.contains("/player/") || url.contains("jwplayer") ||
                        url.contains("statics.sssrr")) {
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // CAPTURAR VIDEO
                    if (url.contains("googleapis.com") && url.contains(".mp4")) {
                        android.util.Log.wtf(TAG, "📹 GOOGLE: ${url.take(50)}")
                        onVideoFound(url)
                    }
                    else if (url.contains("sssrr.org") && url.contains("timestamp=")) {
                        android.util.Log.wtf(TAG, "🎯 SSSRR: ${url.take(50)}")
                        // Nao seguir redirect - usa URL direta mesmo
                        onVideoFound(url)
                    }
                    else if (url.endsWith(".mp4") || url.endsWith(".m3u8")) {
                        android.util.Log.wtf(TAG, "🎬 VIDEO: ${url.take(50)}")
                        onVideoFound(url)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    android.util.Log.d(TAG, "📄: ${url.take(30)}")
                    
                    // Clicks rapidos
                    view.evaluateJavascript("""
                        (function() {
                            ['#overlay','.overlay','.jwplayer','video'].forEach(s => {
                                const e = document.querySelector(s);
                                if (e) { e.click(); e.click(); }
                            });
                        })();
                    """, null)
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    handler?.proceed()
                }
            }
        }
    }
    
    private suspend fun createLink(url: String, referer: String): List<ExtractorLink> {
        val quality = when {
            url.contains("1080") -> "1080p"
            url.contains("720") -> "720p"
            url.contains("480") -> "480p"
            url.contains("360") -> "360p"
            else -> "HD"
        }
        
        return listOf(
            newExtractorLink(
                source = "PlayerEmbedAPI",
                name = "🎬 PlayerEmbedAPI [$quality]",
                url = url,
                type = ExtractorLinkType.VIDEO
            ) {
                this.referer = referer
                this.headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            }
        )
    }
}
