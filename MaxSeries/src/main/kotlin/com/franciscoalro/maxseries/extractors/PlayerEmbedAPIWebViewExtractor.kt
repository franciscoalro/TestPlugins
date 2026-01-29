package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v227 - Filtro Correto de Vídeo
 * 
 * Correção: Capturar APENAS URLs de vídeo (.mp4, .m3u8, googleapis.com)
 * IGNORAR arquivos JS/CSS do player (jwplayer.min.js, etc.)
 */
class PlayerEmbedAPIWebViewExtractor {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 12000L // 12s
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀 v227 EXTRACT: ${sourceUrl.take(40)}...")
        
        return withContext(Dispatchers.Main) {
            var videoUrl: String? = null
            var webView: WebView? = null
            
            try {
                val context = Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
                
                webView = createWebView(context) { url ->
                    // Callback quando encontrar URL de vídeo
                    if (videoUrl == null) {
                        videoUrl = url
                        android.util.Log.wtf(TAG, "📹 VIDEO CAPTURADO!")
                    }
                }
                
                android.util.Log.d(TAG, "🌐 Loading...")
                webView.loadUrl(sourceUrl)
                
                // Aguardar com verificação frequente
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
                android.util.Log.wtf(TAG, "✅ SUCESSO: ${videoUrl!!.take(50)}...")
                createLink(videoUrl!!, referer)
            } else {
                android.util.Log.e(TAG, "❌ Timeout - sem vídeo")
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
                    
                    // ✅ CAPTURAR APENAS URLs DE VÍDEO
                    // URL direta do Google Storage
                    if (url.contains("googleapis.com") && 
                        (url.contains(".mp4") || url.contains(".m3u8"))) {
                        android.util.Log.wtf(TAG, "📹 GOOGLEAPIS: ${url.take(60)}")
                        onVideoFound(url)
                    }
                    
                    // URL intermediária sssrr (com timestamp e id)
                    else if (url.contains("sssrr.org") && 
                             url.contains("timestamp=") && 
                             url.contains("id=")) {
                        android.util.Log.wtf(TAG, "🎯 SSSRR INTERMEDIÁRIA: ${url.take(60)}")
                        // Tentar seguir redirect
                        followRedirect(url, onVideoFound)
                    }
                    
                    // Outros vídeos diretos
                    else if ((url.contains(".mp4") || url.contains(".m3u8")) &&
                             !url.contains(".js") && !url.contains(".css")) {
                        android.util.Log.d(TAG, "🎬 VÍDEO: ${url.take(60)}")
                        onVideoFound(url)
                    }
                    
                    // ❌ IGNORAR arquivos do player
                    else if (url.contains("sssrr.org") && 
                             (url.contains(".js") || url.contains(".css"))) {
                        // Log silencioso apenas
                        android.util.Log.v(TAG, "🚫 JS ignorado: ${url.take(40)}")
                    }
                    
                    // Bloquear ads
                    if (url.contains("googleads") || url.contains("doubleclick") || 
                        url.contains("googlesyndication")) {
                        return WebResourceResponse("text/plain", "utf-8", null)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    android.util.Log.d(TAG, "📄 Page: ${url.take(40)}")
                    
                    if (url.contains("abyss.to")) {
                        android.util.Log.w(TAG, "⚠️ ABYSS.TO detectado")
                    }
                    
                    // Clicks rápidos
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
                    android.util.Log.wtf(TAG, "✅ REDIRECT OK: ${finalUrl.take(60)}")
                    withContext(Dispatchers.Main) {
                        callback(finalUrl)
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Redirect falhou: ${e.message}")
            }
        }
    }
    
    private fun injectClicks(webView: WebView) {
        val script = """
            (function() {
                ['#overlay', '.overlay', '.jwplayer', 'video'].forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) { el.click(); el.click(); el.click(); }
                });
            })();
        """
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun createLink(url: String, referer: String): List<ExtractorLink> {
        return listOf(
            newExtractorLink(
                source = "PlayerEmbedAPI",
                name = "PlayerEmbedAPI",
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
