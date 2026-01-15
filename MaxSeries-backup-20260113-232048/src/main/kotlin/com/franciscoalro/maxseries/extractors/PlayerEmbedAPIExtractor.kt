package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * PlayerEmbedAPI Extractor - Robust WebView Implementation
 * 
 * Handles AES-CTR encrypted sources ("core.bundle.js") by running the actual Page logic
 * and intercepting the final video request.
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 PlayerEmbedAPI: $url")
        
        // 1. Script para forçar reprodução e extração
        // (Reutilizando a lógica robusta criada para o MegaEmbed)
        val captureScript = """
            (function() {
                return new Promise(function(resolve) {
                    var attempts = 0;
                    var maxAttempts = 100; // 10 segundos
                    
                    function tryPlayVideo() {
                        var vids = document.getElementsByTagName('video');
                        for(var i=0; i<vids.length; i++){
                            var v = vids[i];
                            if(v.paused) {
                                v.muted = true;
                                v.play().catch(function(e){});
                            }
                        }
                        var overlays = document.querySelectorAll('.play-button, .vjs-big-play-button, [class*="play"]');
                        for(var j=0; j<overlays.length; j++) { try { overlays[j].click(); } catch(e) {} }
                    }

                    var interval = setInterval(function() {
                        attempts++;
                        tryPlayVideo();
                        
                        var result = '';
                        
                        // Busca em tags video
                        var videos = document.querySelectorAll('video');
                        for (var i = 0; i < videos.length; i++) {
                            var video = videos[i];
                            if (video.src && video.src.startsWith('http')) {
                                result = video.src;
                                break;
                            }
                        }
                        
                        // Busca em sources
                        if (!result) {
                            var sources = document.querySelectorAll('source[src]');
                            for (var j = 0; j < sources.length; j++) {
                                var src = sources[j].src;
                                if (src && (src.includes('.m3u8') || src.includes('.mp4'))) {
                                    result = src;
                                    break;
                                }
                            }
                        }
                        
                        // Busca variáveis globais típicas
                        if (!result) {
                            if(window.sources && window.sources.length > 0) {
                                result = window.sources[0].file;
                            }
                        }

                        if (result && result.length > 0) {
                            clearInterval(interval);
                            resolve(result);
                        } else if (attempts >= maxAttempts) {
                            clearInterval(interval);
                            resolve('');
                        }
                    }, 100);
                });
            })()
        """.trimIndent()

        // 2. Configurar Resolver
        val resolver = WebViewResolver(
            // Intercepta qualquer coisa que pareça video
            interceptUrl = Regex("""\.mp4|\.m3u8|storage\.googleapis\.com|googlevideo\.com"""),
            script = captureScript,
            scriptCallback = { result ->
                if (result.isNotEmpty() && result.startsWith("http")) {
                    Log.d(TAG, "✅ JS Capture: $result")
                }
            },
            timeout = 30_000L
        )

        // 3. Executar Request
        try {
            val headers = mapOf(
                "User-Agent" to USER_AGENT,
                "Referer" to (referer ?: mainUrl)
            )

            // WebViewResolver vai lidar com a interceptação e chamar o callback
            val response = app.get(
                url, 
                headers = headers, 
                interceptor = resolver
            )
            
            // Se o Resolver pegou algo, ele retorna a URL no response.url
            val captured = response.url
            if (captured.contains(".mp4") || captured.contains(".m3u8") || captured.contains("googleapis")) {
                Log.d(TAG, "✅ URL Interceptada: $captured")
                
                callback.invoke(
                     newExtractorLink(
                        this.name,
                        this.name,
                        captured,
                        referer = url,
                        quality = Qualities.Unknown.value
                    )
                )
            } else {
                Log.w(TAG, "⚠️ Falha ao interceptar URL de vídeo. URL final: $captured")
            }

        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro WebView: ${e.message}")
        }
    }
}
