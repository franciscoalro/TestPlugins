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

/**
 * MegaEmbed Extractor v9 - MANUAL WEBVIEW IMPLEMENTATION (v190)
 * 
 * LÓGICA DEFINITIVA:
 * 1. Instancia um WebView real (invisível) usando AcraApplication.context.
 * 2. Injeta o script de Hook de Rede + Triplo Clique.
 * 3. O script captura a URL exata do .txt/m3u8 e envia via console.log("MEGA_EMBED_RESULT: ...").
 * 4. O WebChromeClient intercepta essa mensagem e retorna o link.
 * 
 * Isso bypassa qualquer falha de interceptação de rede do CloudStream ou timeouts do Resolver.
 */
class MegaEmbedExtractorV9 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MegaEmbedV9"
    }

    private val cdnHeaders = mapOf(
        "Referer" to "https://playerthree.online/",
        "Origin" to "https://megaembed.link",
        "Accept-Language" to "en-US,en;q=0.9",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val videoId = extractVideoId(url) ?: return
        Log.d(TAG, "🚀 [MANUAL] Iniciando MegaEmbed V9 para ID: $videoId")
        
        val embedUrl = "https://megaembed.link/#$videoId"
        var finalUrl: String? = null
        val latch = CountDownLatch(1)

        val handler = Handler(Looper.getMainLooper())
        
        handler.post {
            try {
                // HACK: Obter Contexto Global via Reflection para bypassar limitações do Plugin
                // Isso evita o erro "Unresolved reference: AcraApplication" no build
                val context = try {
                    val activityThread = Class.forName("android.app.ActivityThread")
                    val currentAppMethod = activityThread.getMethod("currentApplication")
                    currentAppMethod.invoke(null) as android.content.Context
                } catch (e: Exception) {
                    Log.e(TAG, "❌ Erro fatal: Não foi possível obter Contexto do Android: ${e.message}")
                    null
                }

                if (context == null) {
                    Log.e(TAG, "❌ Contexto nulo! Impossível criar WebView.")
                    latch.countDown()
                    return@post
                }
                
                val webView = WebView(context)
                
                webView.settings.apply {
                    javaScriptEnabled = true
                    domStorageEnabled = true
                    databaseEnabled = true
                    userAgentString = cdnHeaders["User-Agent"]
                    blockNetworkImage = false // v196: Reabilitar imagens para garantir carregamento correto do player
                    mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                    mediaPlaybackRequiresUserGesture = false // v196: Permitir autoplay
                }

                // v196: Forçar dimensões virtuais para o WebView (1920x1080)
                // Isso permite que o JS calcule coordenadas e 'veja' o site corretamente
                webView.layout(0, 0, 1920, 1080)

                // Script injetado para capturar e "gritar" a URL
                val injectedScript = """
                    (function() {
                        console.log('[MegaEmbedV9] INJETADO: Iniciando Hooks e Clicker Inteligente...');
                        
                        // v197: Captura de erros JS globais
                        window.onerror = function(message, source, lineno, colno, error) {
                            console.log('[MegaEmbedV9] JS ERROR: ' + message + ' at ' + source + ':' + lineno);
                        };

                        function reportSuccess(url) {
                            if (window.hasReported) return;
                            window.hasReported = true;
                            console.log('MEGA_EMBED_RESULT:' + url);
                        }

                        // HOOK: XMLHttpRequest
                        const origOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function(method, url) {
                            if (typeof url === 'string') {
                                if (url.includes('/v4/') && (url.includes('.txt') || url.includes('.m3u8') || url.includes('cf-master'))) {
                                    reportSuccess(url);
                                }
                            }
                            this.addEventListener('load', function() {
                                if (this.responseURL && this.responseURL.includes('cf-master')) {
                                    reportSuccess(this.responseURL);
                                }
                            });
                            return origOpen.apply(this, arguments);
                        };
                        
                        // HOOK: Fetch
                        const origFetch = window.fetch;
                        window.fetch = function(input, init) {
                            const url = (typeof input === 'string') ? input : (input && input.url);
                            if (url && url.includes('cf-master')) reportSuccess(url);
                            
                            return origFetch.apply(this, arguments).then(response => {
                                if (response.url && response.url.includes('cf-master')) reportSuccess(response.url);
                                return response;
                            });
                        };

                        // AUTOMAÇÃO v198: Alvo Exato (#player-button-container) + 3 Cliques
                        let clickCount = 0;
                        function smartClick() {
                            // PRIORIDADE MÁXIMA: O overlay identificado pelo usuário
                            const targets = [
                                document.querySelector('#player-button-container'),
                                document.querySelector('#player-button'),
                                document.querySelector('#player'),
                                document.querySelector('video'),
                                document.querySelector('.play')
                            ];
                            
                            let clicked = false;
                            targets.forEach(el => {
                                if(el && !clicked) {
                                    try {
                                        // Força visibilidade se necessário (hack para webview oculto)
                                        el.style.display = 'block';
                                        el.style.visibility = 'visible';
                                        el.style.zIndex = '9999';
                                        
                                        // Dispara eventos nativos de mouse
                                        const ev = new MouseEvent('click', { view: window, bubbles: true, cancelable: true });
                                        el.dispatchEvent(ev);
                                        
                                        // Tenta o método .click() padrão também
                                        el.click();
                                        
                                        console.log('[MegaEmbedV9] 🎯 CLIQUE REALIZADO EM: #' + el.id + ' (' + el.tagName + ')');
                                        clicked = true;
                                    } catch(e) {
                                        console.log('[MegaEmbedV9] Erro ao clicar: ' + e.message);
                                    }
                                }
                            });
                            
                            // Fallback: Clique no centro (caso o seletor falhe)
                            if (!clicked) {
                                const x = 960; const y = 540; // Centro de 1920x1080
                                const el = document.elementFromPoint(x, y) || document.body;
                                const ev = new MouseEvent('click', {
                                    view: window, bubbles: true, cancelable: true, clientX: x, clientY: y
                                });
                                el.dispatchEvent(ev);
                                console.log('[MegaEmbedV9] Clicked at (960, 540) - Fallback');
                            }
                        }

                        // Executa 4 vezes para garantir os "3 cliques" com margem de segurança
                        let interval = setInterval(() => {
                            clickCount++;
                            console.log('[MegaEmbedV9] Tentativa de clique #' + clickCount);
                            smartClick();
                            if(clickCount >= 4) clearInterval(interval);
                        }, 1500); // Intervalo de 1.5s entre cliques

                    })();
                """.trimIndent()

                webView.webChromeClient = object : WebChromeClient() {
                    // v197: Monitorar progresso real da página
                    override fun onProgressChanged(view: WebView?, newProgress: Int) {
                        Log.d(TAG, "⏳ [SPY] Progress: $newProgress%")
                        super.onProgressChanged(view, newProgress)
                    }

                    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                        val msg = consoleMessage?.message() ?: return false
                        
                        // Filtra apenas nossa mensagem de sucesso
                        if (msg.contains("MEGA_EMBED_RESULT:")) {
                            val extracted = msg.substringAfter("MEGA_EMBED_RESULT:")
                            Log.d(TAG, "🎯 URL CAPTURADA VIA CONSOLE: $extracted")
                            finalUrl = extracted
                            latch.countDown()
                            return true
                        }
                        
                        if (msg.contains("[MegaEmbedV9]")) {
                            Log.d(TAG, "JS LOG: $msg")
                        }
                        return false
                    }
                }

                webView.webViewClient = object : WebViewClient() {
                    override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                        super.onPageStarted(view, url, favicon)
                        Log.d(TAG, "🟢 [SPY] Page Started: $url")
                    }

                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        Log.d(TAG, "🏁 [SPY] Page Finished: $url")
                        Log.d(TAG, "Pagina carregada, injetando script...")
                        view?.evaluateJavascript(injectedScript, null)
                    }
                    
                    // SPY MODE: Logar TUDO que o WebView carrega
                    override fun onLoadResource(view: WebView?, url: String?) {
                        super.onLoadResource(view, url)
                        if (url != null) {
                            Log.d(TAG, "🔍 [SPY] LoadResource: $url")
                        }
                    }

                    // SPY MODE: Interceptar requisições para análise profunda
                    override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                        val url = request?.url?.toString()
                        if (url != null) {
                            Log.d(TAG, "🕵️ [SPY] Request: $url")
                            // Tenta capturar aqui também, caso o JS falhe
                            if (url.contains("cf-master") || url.contains(".m3u8") || url.contains("v4/xy")) {
                                Log.d(TAG, "🔥 [SPY] ALVO DETECTADO via Request: $url")
                                finalUrl = url
                                latch.countDown()
                            }
                        }
                        return super.shouldInterceptRequest(view, request)
                    }

                    // v197: Capturar erros de carregamento (DNS, Connection Refused, etc)
                    override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                        Log.e(TAG, "❌ [SPY] Page Error: ${error?.toString()} for ${request?.url}")
                        super.onReceivedError(view, request, error)
                    }

                    // Permite bypass de erros SSL se necessário
                    override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: android.net.http.SslError?) {
                        Log.d(TAG, "⚠️ SSL Error: ${error?.toString()}")
                        handler?.proceed()
                    }
                }

                Log.d(TAG, "Carregando URL no WebView: $embedUrl")
                // Headers customizados no loadUrl
                webView.loadUrl(embedUrl, cdnHeaders)

            } catch (e: Exception) {
                Log.e(TAG, "Erro ao iniciar WebView: ${e.message}")
                latch.countDown()
            }
        }

        // Aguarda até 90 segundos pela captura (v194: aumentado para superar lentidão)
        try {
            val captured = latch.await(90, TimeUnit.SECONDS)
            if (!captured) {
                Log.e(TAG, "❌ Timeout: Nenhuma URL capturada em 90s.")
            }
        } catch (e: InterruptedException) {
            Log.e(TAG, "❌ Interrompido.")
        }

        // Se capturou, processa
        finalUrl?.let { link ->
            processUrl(link, url, callback)
        }
    }

    private suspend fun processUrl(link: String, originalUrl: String, callback: (ExtractorLink) -> Unit) {
        val quality = QualityDetector.detectFromUrl(link)
        // Cacheia para o futuro
        VideoUrlCache.put(originalUrl, link, quality, name)
        
        M3u8Helper.generateM3u8(
            source = name,
            streamUrl = link,
            referer = mainUrl,
            headers = cdnHeaders
        ).forEach(callback)
    }

    private fun extractVideoId(url: String): String? {
        return Regex("""#([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
    }
}
