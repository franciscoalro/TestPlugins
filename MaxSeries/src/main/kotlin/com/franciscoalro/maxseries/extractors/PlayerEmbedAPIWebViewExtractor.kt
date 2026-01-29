package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v228 - Filtro Rigido
 * 
 * Garante que NENHUM arquivo .js/.css seja capturado como video.
 * Verifica extensao PRIMEIRO, antes de qualquer outra coisa.
 */
class PlayerEmbedAPIWebViewExtractor {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 12000L
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀 v228 EXTRACT: ${sourceUrl.take(40)}...")
        
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
                        android.util.Log.wtf(TAG, "📹 VIDEO OK: ${url.take(50)}...")
                    }
                }
                
                android.util.Log.d(TAG, "🌐 Loading...")
                webView.loadUrl(sourceUrl)
                
                var elapsed = 0L
                while (elapsed < TIMEOUT_MS && videoUrl == null) {
                    delay(300)
                    elapsed += 300
                }
                
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro: ${e.message}")
            } finally {
                webView?.stopLoading()
                webView?.destroy()
            }
            
            if (videoUrl != null) {
                createLink(videoUrl!!, referer)
            } else {
                android.util.Log.e(TAG, "❌ Timeout - sem video")
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
                    val url = request.url.toString().lowercase()
                    
                    // ========== PRIMEIRO: IGNORAR ARQUIVOS JS/CSS/ETC ==========
                    // Se for arquivo estatico do player, IGNORAR IMEDIATAMENTE
                    if (url.endsWith(".js") || 
                        url.endsWith(".css") || 
                        url.endsWith(".json") ||
                        url.endsWith(".png") ||
                        url.endsWith(".jpg") ||
                        url.endsWith(".svg") ||
                        url.endsWith(".woff") ||
                        url.endsWith(".woff2") ||
                        url.endsWith(".ttf") ||
                        url.contains("/player/") && url.contains(".js") ||
                        url.contains("jwplayer") ||
                        url.contains("statics.sssrr")) {
                        // Silencioso - nao loga nada para nao poluir
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // ========== DEPOIS: VERIFICAR SE E VIDEO ==========
                    
                    // 1. Google Storage com video
                    if (url.contains("googleapis.com") && 
                        (url.contains(".mp4") || url.contains(".m3u8") || url.contains("video"))) {
                        android.util.Log.wtf(TAG, "📹 GOOGLE: ${url.take(60)}")
                        onVideoFound(request.url.toString())
                    }
                    
                    // 2. URL intermediaria SSSRR (deve ter timestamp E id, mas NAO ser arquivo)
                    else if (url.contains("sssrr.org") && 
                             url.contains("timestamp=") && 
                             url.contains("id=") &&
                             !url.contains(".js") &&
                             !url.contains(".css")) {
                        android.util.Log.wtf(TAG, "🎯 SSSRR: ${url.take(60)}")
                        followRedirect(request.url.toString(), onVideoFound)
                    }
                    
                    // 3. Outros videos diretos
                    else if ((url.endsWith(".mp4") || url.endsWith(".m3u8")) &&
                             !url.contains(".js") && 
                             !url.contains(".css")) {
                        android.util.Log.wtf(TAG, "🎬 VIDEO: ${url.take(60)}")
                        onVideoFound(request.url.toString())
                    }
                    
                    // Bloquear ads
                    if (url.contains("googleads") || url.contains("doubleclick") || 
                        url.contains("googlesyndication") || url.contains("facebook")) {
                        return WebResourceResponse("text/plain", "utf-8", null)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    android.util.Log.d(TAG, "📄 Page: ${url.take(40)}")
                    
                    if (url.contains("abyss.to")) {
                        android.util.Log.w(TAG, "⚠️ ABYSS.TO")
                    }
                    
                    injectClicks(view)
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    handler?.proceed()
                }
            }
        }
    }
    
    private fun followRedirect(url: String, callback: (String) -> Unit) {
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = com.lagradost.cloudstream3.app.get(
                    url = url,
                    allowRedirects = true,
                    headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept" to "*/*"
                    ),
                    timeout = 10
                )
                
                val finalUrl = response.url
                if (finalUrl.contains("googleapis.com") || finalUrl.contains(".mp4")) {
                    android.util.Log.wtf(TAG, "✅ REDIRECT: ${finalUrl.take(60)}")
                    withContext(Dispatchers.Main) {
                        callback(finalUrl)
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Redirect erro: ${e.message}")
            }
        }
    }
    
    private fun injectClicks(webView: WebView) {
        val script = """
            (function() {
                ['#overlay','.overlay','.jwplayer','video','[class*="play"]'].forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) { el.click(); el.click(); }
                });
            })();
        """
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun createLink(url: String, referer: String): List<ExtractorLink> {
        // Detectar qualidade da URL
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
                    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Origin" to "https://playerembedapi.link"
                )
            }
        )
    }
}
