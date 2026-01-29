package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.app
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v226 - Captura Imediata
 * 
 * Estratégia: Capturar URL do Google Storage assim que aparecer e ENCERRAR
 * Não esperar redirecionamento para abyss.to
 */
class PlayerEmbedAPIWebViewExtractor {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 10000L // 10s apenas - rápido!
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "🚀 v226 EXTRACT: ${sourceUrl.take(50)}...")
        
        return withContext(Dispatchers.Main) {
            var capturedUrl: String? = null
            var webView: WebView? = null
            
            try {
                val context = Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
                
                webView = createWebView(context, referer) { url ->
                    // Callback quando encontrar URL
                    if (capturedUrl == null && url.contains("googleapis.com")) {
                        capturedUrl = url
                        android.util.Log.wtf(TAG, "🎬 URL CAPTURADA: ${url.take(60)}...")
                    }
                }
                
                // Carregar URL
                android.util.Log.d(TAG, "🌐 Loading...")
                webView.loadUrl(sourceUrl)
                
                // Aguardar com timeout, mas verificar a cada 500ms
                var elapsed = 0L
                while (elapsed < TIMEOUT_MS && capturedUrl == null) {
                    delay(500)
                    elapsed += 500
                    
                    // Log de progresso
                    if (elapsed % 2000 == 0L) {
                        android.util.Log.d(TAG, "⏳ Aguardando... ${elapsed/1000}s")
                    }
                }
                
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Erro: ${e.message}")
            } finally {
                // SEMPRE fechar WebView
                webView?.stopLoading()
                webView?.destroy()
                android.util.Log.d(TAG, "🧹 WebView destruído")
            }
            
            // Processar resultado
            if (capturedUrl != null) {
                android.util.Log.wtf(TAG, "✅ SUCESSO: URL obtida em tempo recorde!")
                createLink(capturedUrl!!, referer)
            } else {
                android.util.Log.e(TAG, "❌ Timeout - nenhuma URL capturada")
                emptyList()
            }
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(context: android.content.Context, referer: String, onUrlCaptured: (String) -> Unit): WebView {
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
                    
                    // CAPTURAR IMEDIATAMENTE Google Storage
                    if (url.contains("googleapis.com") && url.contains(".mp4")) {
                        android.util.Log.wtf(TAG, "📹 GOOGLEAPIS: ${url.take(60)}...")
                        onUrlCaptured(url)
                    }
                    
                    // Também capturar sssrr como backup
                    if (url.contains("sssrr.org") && url.contains("timestamp")) {
                        android.util.Log.wtf(TAG, "🎯 SSSRR: ${url.take(60)}...")
                        // Tentar seguir redirect em background
                        followRedirectAsync(url, referer, onUrlCaptured)
                    }
                    
                    // Bloquear ads
                    if (url.contains("googleads") || url.contains("doubleclick")) {
                        return WebResourceResponse("text/plain", "utf-8", null)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    android.util.Log.d(TAG, "📄 Page: ${url.take(50)}")
                    
                    if (url.contains("abyss.to")) {
                        android.util.Log.w(TAG, "⚠️ ABYSS.TO - mas URL já deve ter sido capturada")
                    }
                    
                    // Clicks automáticos rápidos
                    injectQuickClicks(view)
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    handler?.proceed()
                }
            }
        }
    }
    
    private fun followRedirectAsync(url: String, referer: String, callback: (String) -> Unit) {
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val response = app.get(
                    url = url,
                    allowRedirects = true,
                    headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Referer" to referer
                    ),
                    timeout = 10
                )
                
                val finalUrl = response.url
                if (finalUrl.contains("googleapis.com")) {
                    android.util.Log.wtf(TAG, "✅ Redirect OK: ${finalUrl.take(60)}")
                    withContext(Dispatchers.Main) {
                        callback(finalUrl)
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Redirect falhou: ${e.message}")
            }
        }
    }
    
    private fun injectQuickClicks(webView: WebView) {
        val script = """
            (function() {
                ['#overlay', '.overlay', '.play-button', 'video'].forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) el.click();
                });
            })();
        """
        webView.evaluateJavascript(script, null)
    }
    
    private suspend fun createLink(url: String, referer: String): List<ExtractorLink> {
        return listOf(
            newExtractorLink(
                source = "PlayerEmbedAPI",
                name = "PlayerEmbedAPI HD",
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
