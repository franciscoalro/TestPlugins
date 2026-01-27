package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.webkit.*
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache
import com.franciscoalro.maxseries.utils.WebViewPool

/**
 * PlayerEmbedAPI Extractor v4.0 - MANUAL WEBVIEW (Jan 2026)
 * 
 * MUDANÇA v4.0:
 * - 🔧 WebView MANUAL com botão de click (igual MegaEmbed)
 * - ⚡ Usuário clica manualmente no overlay
 * - 🎯 Captura URL via hooks de rede
 * - ✅ Mais confiável que automação
 * 
 * LÓGICA:
 * 1. Cria WebView real (invisível)
 * 2. Injeta script de Hook de Rede
 * 3. USUÁRIO clica no overlay manualmente
 * 4. Script captura URL e envia via console.log
 * 5. WebChromeClient intercepta e retorna link
 */
class PlayerEmbedAPIExtractorManual : ExtractorApi() {
    override val name = "PlayerEmbedAPI"
    override val mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val TIMEOUT_SECONDS = 30L  // Reduced from 60L (50% reduction)
        private const val QUICK_TIMEOUT_SECONDS = 15L  // For retry attempts
        private const val MAX_RETRIES = 2  // Maximum retry attempts
    }

    private val headers = mapOf(
        "Referer" to "https://playerembedapi.link/",
        "Origin" to "https://playerembedapi.link",
        "Accept-Language" to "en-US,en;q=0.9",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🚀 [MANUAL] Iniciando PlayerEmbedAPI Manual para: $url")
        
        var attempt = 0
        var success = false
        
        while (attempt < MAX_RETRIES && !success) {
            attempt++
            
            // Adaptive timeout: 30s for first attempt, 15s for retry
            val timeout = if (attempt == 1) TIMEOUT_SECONDS else QUICK_TIMEOUT_SECONDS
            Log.d(TAG, "🔄 Tentativa $attempt/$MAX_RETRIES (timeout: ${timeout}s)")
            
            var finalUrl: String? = null
            val latch = CountDownLatch(1)
            var webViewRef: WebView? = null  // Referência para cleanup

            val handler = Handler(Looper.getMainLooper())
        
        handler.post {
            try {
                // Obter Contexto Global via Reflection
                val context = try {
                    val activityThread = Class.forName("android.app.ActivityThread")
                    val currentAppMethod = activityThread.getMethod("currentApplication")
                    currentAppMethod.invoke(null) as android.content.Context
                } catch (e: Exception) {
                    Log.e(TAG, "❌ Erro: Não foi possível obter Contexto: ${e.message}")
                    null
                }

                if (context == null) {
                    Log.e(TAG, "❌ Contexto nulo! Impossível criar WebView.")
                    latch.countDown()
                    return@post
                }
                
                Log.d(TAG, "⚡ Adquirindo WebView do pool...")
                val webView = WebViewPool.acquire(context)
                webViewRef = webView  // Armazenar referência para cleanup
                
                // Atualizar apenas User-Agent (outras settings já otimizadas pelo pool)
                webView.settings.userAgentString = headers["User-Agent"]

                // Script injetado para capturar URL
                val injectedScript = """
                    (function() {
                        console.log('[PlayerEmbedAPI] INJETADO: Iniciando Hooks de Rede...');
                        
                        // Captura de erros JS
                        window.onerror = function(message, source, lineno, colno, error) {
                            console.log('[PlayerEmbedAPI] JS ERROR: ' + message + ' at ' + source + ':' + lineno);
                        };

                        function reportSuccess(url) {
                            if (window.hasReported) return;
                            window.hasReported = true;
                            console.log('PLAYEREMBED_RESULT:' + url);
                        }

                        // HOOK: XMLHttpRequest
                        const origOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function(method, url) {
                            if (typeof url === 'string') {
                                // Capturar URLs do sssrr.org (PlayerEmbedAPI usa esse CDN)
                                if (url.includes('sssrr.org') && (url.includes('/sora/') || url.includes('.m3u8') || url.includes('.mp4'))) {
                                    console.log('[PlayerEmbedAPI] XHR capturou: ' + url);
                                    reportSuccess(url);
                                }
                            }
                            this.addEventListener('load', function() {
                                if (this.responseURL && this.responseURL.includes('sssrr.org')) {
                                    console.log('[PlayerEmbedAPI] XHR responseURL: ' + this.responseURL);
                                    reportSuccess(this.responseURL);
                                }
                            });
                            return origOpen.apply(this, arguments);
                        };
                        
                        // HOOK: Fetch
                        const origFetch = window.fetch;
                        window.fetch = function(input, init) {
                            const url = (typeof input === 'string') ? input : (input && input.url);
                            if (url && url.includes('sssrr.org')) {
                                console.log('[PlayerEmbedAPI] Fetch capturou: ' + url);
                                reportSuccess(url);
                            }
                            
                            return origFetch.apply(this, arguments).then(response => {
                                if (response.url && response.url.includes('sssrr.org')) {
                                    console.log('[PlayerEmbedAPI] Fetch responseURL: ' + response.url);
                                    reportSuccess(response.url);
                                }
                                return response;
                            });
                        };

                        // REMOVER OVERLAY DO DOM (para facilitar click manual)
                        function removeOverlay() {
                            const overlay = document.getElementById('overlay');
                            if (overlay) {
                                console.log('[PlayerEmbedAPI] Removendo overlay do DOM...');
                                overlay.remove();
                                return true;
                            }
                            return false;
                        }

                        // Tentar remover overlay após carregamento
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', function() {
                                setTimeout(removeOverlay, 500);
                            });
                        } else {
                            setTimeout(removeOverlay, 500);
                        }

                        // Também tentar remover periodicamente
                        setInterval(removeOverlay, 1000);

                        console.log('[PlayerEmbedAPI] Hooks instalados! Aguardando click manual do usuário...');
                    })();
                """.trimIndent()

                webView.webChromeClient = object : WebChromeClient() {
                    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                        val message = consoleMessage?.message() ?: return false
                        
                        if (message.startsWith("PLAYEREMBED_RESULT:")) {
                            val capturedUrl = message.removePrefix("PLAYEREMBED_RESULT:")
                            Log.d(TAG, "✅ [MANUAL] URL CAPTURADA: $capturedUrl")
                            finalUrl = capturedUrl
                            latch.countDown()
                            return true
                        }
                        
                        // Log outros console.log para debug
                        if (message.contains("[PlayerEmbedAPI]")) {
                            Log.d(TAG, "Console: $message")
                        }
                        
                        return super.onConsoleMessage(consoleMessage)
                    }
                }

                webView.webViewClient = object : WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        Log.d(TAG, "📄 Página carregada: $url")
                        
                        // Injetar script após página carregar
                        handler.postDelayed({
                            try {
                                webView.evaluateJavascript(injectedScript, null)
                                Log.d(TAG, "💉 Script injetado com sucesso!")
                            } catch (e: Exception) {
                                Log.e(TAG, "Erro ao injetar script: ${e.message}")
                            }
                        }, 1000)
                    }

                    override fun onReceivedError(
                        view: WebView?,
                        request: WebResourceRequest?,
                        error: WebResourceError?
                    ) {
                        Log.e(TAG, "❌ WebView Error: ${error?.description}")
                        super.onReceivedError(view, request, error)
                    }
                }

                Log.d(TAG, "🌐 Carregando URL no WebView: $url")
                webView.loadUrl(url, headers)

            } catch (e: Exception) {
                Log.e(TAG, "❌ Erro fatal no WebView: ${e.message}", e)
                latch.countDown()
            }
        }

        // Aguardar captura com timeout adaptativo
        val captured = latch.await(timeout, TimeUnit.SECONDS)
        
        if (captured && finalUrl != null) {
            Log.d(TAG, "✅ [MANUAL] Sucesso na tentativa $attempt! URL: $finalUrl")
            success = true
            
            val quality = QualityDetector.detectFromUrl(finalUrl!!)
            VideoUrlCache.put(url, finalUrl!!, quality, name)
            
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(quality)} (Manual)",
                    url = finalUrl!!,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "https://playerembedapi.link/"
                    this.quality = quality
                }
            )
        } else {
            Log.w(TAG, "⏱️ Timeout após ${timeout}s (tentativa $attempt)")
            
            if (attempt < MAX_RETRIES) {
                Log.d(TAG, "🔄 Tentando novamente com timeout reduzido...")
            } else {
                Log.e(TAG, "❌ [MANUAL] Falha após $MAX_RETRIES tentativas. Fallback para próximo extractor.")
                Log.e(TAG, "💡 Sugestão: Verifique se o usuário clicou no overlay ou se a rede está lenta.")
            }
        }
        
        // Sempre liberar WebView de volta ao pool
        webViewRef?.let { webView ->
            handler.post {
                try {
                    Log.d(TAG, "🔓 Liberando WebView de volta ao pool (tentativa $attempt)...")
                    WebViewPool.release(webView)
                } catch (e: Exception) {
                    Log.e(TAG, "Erro ao liberar WebView: ${e.message}")
                }
            }
        }
        
        } // End of retry loop
    }
}
