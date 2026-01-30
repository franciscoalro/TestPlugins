package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.webkit.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI WebView Extractor v231 - DEBUG COMPLETO
 * 
 * Logs detalhados para identificar onde está falhando
 */
class PlayerEmbedAPIWebViewExtractor {
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_MS = 15000L // 15s para debug
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun extractFromUrl(sourceUrl: String, referer: String): List<ExtractorLink> {
        android.util.Log.wtf(TAG, "========================================")
        android.util.Log.wtf(TAG, "🚀 v231 INICIANDO EXTRACAO")
        android.util.Log.wtf(TAG, "📍 URL: $sourceUrl")
        android.util.Log.wtf(TAG, "📄 Referer: $referer")
        android.util.Log.wtf(TAG, "========================================")
        
        return withContext(Dispatchers.Main) {
            val capturedUrls = mutableListOf<String>()
            var webView: WebView? = null
            var isCompleted = false
            
            try {
                val context = Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication")
                    .invoke(null) as android.content.Context
                
                android.util.Log.d(TAG, "✅ Contexto obtido")
                
                webView = createWebView(context) { url, type ->
                    android.util.Log.wtf(TAG, "📡 CALLBACK recebido: $type")
                    android.util.Log.wtf(TAG, "🔗 URL: ${url.take(60)}")
                    capturedUrls.add(url)
                    isCompleted = true
                }
                
                android.util.Log.d(TAG, "🌐 WebView criado, carregando URL...")
                webView.loadUrl(sourceUrl)
                
                // Aguardar com verificacao frequente
                var elapsed = 0L
                while (elapsed < TIMEOUT_MS && !isCompleted) {
                    delay(100) // Verifica a cada 100ms
                    elapsed += 100
                    
                    if (elapsed % 1000 == 0L) {
                        android.util.Log.d(TAG, "⏳ Aguardando... ${elapsed/1000}s | Capturadas: ${capturedUrls.size}")
                    }
                }
                
                if (isCompleted) {
                    android.util.Log.wtf(TAG, "✅ URL capturada em ${elapsed}ms")
                } else {
                    android.util.Log.w(TAG, "⚠️ Timeout apos ${TIMEOUT_MS}ms")
                    android.util.Log.d(TAG, "📊 URLs capturadas no total: ${capturedUrls.size}")
                }
                
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ ERRO CRITICO: ${e.message}")
                e.printStackTrace()
            } finally {
                android.util.Log.d(TAG, "🧹 Limpando WebView...")
                try {
                    webView?.stopLoading()
                    webView?.destroy()
                } catch (e: Exception) {
                    android.util.Log.e(TAG, "❌ Erro ao limpar WebView: ${e.message}")
                }
            }
            
            android.util.Log.wtf(TAG, "========================================")
            android.util.Log.wtf(TAG, "📊 RESULTADO FINAL:")
            android.util.Log.wtf(TAG, "   URLs capturadas: ${capturedUrls.size}")
            
            if (capturedUrls.isNotEmpty()) {
                val url = capturedUrls.first()
                android.util.Log.wtf(TAG, "   Usando: ${url.take(50)}...")
                android.util.Log.wtf(TAG, "========================================")
                createLink(url, referer)
            } else {
                android.util.Log.e(TAG, "   ❌ NENHUMA URL CAPTURADA")
                android.util.Log.wtf(TAG, "========================================")
                emptyList()
            }
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(context: android.content.Context, onUrlFound: (String, String) -> Unit): WebView {
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
                    
                    // LOG TODAS AS REQUISICOES (para debug)
                    if (url.contains("sssrr") || url.contains("googleapis") || url.contains("player")) {
                        android.util.Log.v(TAG, "📡 REQ: ${url.take(80)}")
                    }
                    
                    // IGNORAR arquivos estaticos
                    if (url.endsWith(".js") || url.endsWith(".css") || 
                        url.endsWith(".png") || url.endsWith(".jpg") ||
                        url.contains("/player/") || url.contains("jwplayer") ||
                        url.contains("statics.sssrr")) {
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // CAPTURAR GOOGLE STORAGE
                    if (url.contains("googleapis.com") && url.contains(".mp4")) {
                        android.util.Log.wtf(TAG, "🎬 VIDEO GOOGLEapis: ${url.take(60)}")
                        onUrlFound(url, "GOOGLE")
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // CAPTURAR URL INTERMEDIARIA SSSRR
                    if (url.contains("sssrr.org") && url.contains("timestamp=") && url.contains("id=")) {
                        android.util.Log.wtf(TAG, "🎯 INTERMEDIARIA SSSRR: ${url.take(60)}")
                        // Seguir redirect
                        followRedirect(url, onUrlFound)
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    // CAPTURAR QUALQUER MP4/M3U8
                    if (url.endsWith(".mp4") || url.endsWith(".m3u8")) {
                        android.util.Log.wtf(TAG, "🎬 VIDEO DIRETO: ${url.take(60)}")
                        onUrlFound(url, "DIRETO")
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    return super.shouldInterceptRequest(view, request)
                }
                
                override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                    android.util.Log.d(TAG, "🚀 Page START: ${url?.take(40)}")
                }
                
                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    android.util.Log.d(TAG, "📄 Page FINISHED: ${url.take(40)}")
                    
                    if (url.contains("abyss.to")) {
                        android.util.Log.e(TAG, "❌ ABYSS.TO DETECTADO! Site bloqueou automacao.")
                    }
                    
                    // Clicks rapidos no player
                    view.evaluateJavascript("""
                        (function() {
                            console.log('🚀 Script de automacao injetado');
                            
                            // Clicar em elementos do player
                            var selectors = ['#overlay', '.overlay', '.jwplayer', '.play-button', 'video', '[class*="play"]', '[id*="play"]'];
                            selectors.forEach(function(sel) {
                                var el = document.querySelector(sel);
                                if (el) {
                                    console.log('✅ Clicando em: ' + sel);
                                    el.click();
                                    setTimeout(function() { el.click(); }, 100);
                                    setTimeout(function() { el.click(); }, 300);
                                }
                            });
                            
                            // Verificar se video ja esta disponivel
                            var video = document.querySelector('video');
                            if (video && video.src) {
                                console.log('📹 Video encontrado: ' + video.src);
                            }
                        })();
                    """, null)
                }
                
                override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                    android.util.Log.e(TAG, "❌ WebView Error: ${error?.description}")
                }
                
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                    android.util.Log.w(TAG, "⚠️ SSL Error (ignorado)")
                    handler?.proceed()
                }
            }
            
            // Adicionar console.log do JavaScript
            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    android.util.Log.d("WebViewJS", "${message.message()}")
                    return true
                }
            }
        }
    }
    
    private fun followRedirect(url: String, callback: (String, String) -> Unit) {
        android.util.Log.d(TAG, "🔄 Seguindo redirect...")
        
        kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
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
                android.util.Log.wtf(TAG, "✅ REDIRECT RESULTADO: ${finalUrl.take(60)}")
                
                if (finalUrl.contains("googleapis.com") || finalUrl.contains(".mp4")) {
                    kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                        callback(finalUrl, "REDIRECT")
                    }
                } else {
                    android.util.Log.w(TAG, "⚠️ Redirect nao retornou video: ${finalUrl.take(40)}")
                }
            } catch (e: Exception) {
                android.util.Log.e(TAG, "❌ Redirect falhou: ${e.message}")
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
        
        android.util.Log.wtf(TAG, "✅ CRIANDO LINK: $quality")
        
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
                    "Accept" to "*/*",
                    "Referer" to referer
                )
            }
        )
    }
}
