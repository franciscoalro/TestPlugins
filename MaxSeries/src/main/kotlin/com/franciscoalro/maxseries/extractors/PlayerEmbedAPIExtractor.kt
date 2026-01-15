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
        
        // 1. Script MELHORADO para captura de vídeo (v81)
        val captureScript = """
            (function() {
                return new Promise(function(resolve) {
                    var attempts = 0;
                    var maxAttempts = 150; // 15 segundos (aumentado)
                    
                    function tryPlayVideo() {
                        // Tentar reproduzir vídeos existentes
                        var vids = document.getElementsByTagName('video');
                        for(var i=0; i<vids.length; i++){
                            var v = vids[i];
                            if(v.paused) {
                                v.muted = true;
                                v.play().catch(function(e){});
                            }
                        }
                        
                        // Clicar em botões de play
                        var overlays = document.querySelectorAll('.play-button, .vjs-big-play-button, [class*="play"]');
                        for(var j=0; j<overlays.length; j++) { 
                            try { overlays[j].click(); } catch(e) {} 
                        }
                        
                        // Tentar iniciar JWPlayer se existir
                        if (window.jwplayer && typeof window.jwplayer === 'function') {
                            try {
                                var players = document.querySelectorAll('[id*="player"]');
                                for(var k=0; k<players.length; k++) {
                                    var playerId = players[k].id;
                                    if(playerId) {
                                        var player = window.jwplayer(playerId);
                                        if(player && player.play) {
                                            player.setMute(true);
                                            player.play();
                                        }
                                    }
                                }
                            } catch(e) {}
                        }
                    }

                    var interval = setInterval(function() {
                        attempts++;
                        tryPlayVideo();
                        
                        var result = '';
                        
                        // 1. Busca em tags video
                        var videos = document.querySelectorAll('video');
                        for (var i = 0; i < videos.length; i++) {
                            var video = videos[i];
                            if (video.src && video.src.startsWith('http')) {
                                result = video.src;
                                break;
                            }
                            // Verificar currentSrc também
                            if (video.currentSrc && video.currentSrc.startsWith('http')) {
                                result = video.currentSrc;
                                break;
                            }
                        }
                        
                        // 2. Busca em sources
                        if (!result) {
                            var sources = document.querySelectorAll('source[src]');
                            for (var j = 0; j < sources.length; j++) {
                                var src = sources[j].src;
                                if (src && (src.includes('.m3u8') || src.includes('.mp4') || src.includes('googleapis'))) {
                                    result = src;
                                    break;
                                }
                            }
                        }
                        
                        // 3. Busca em JWPlayer
                        if (!result && window.jwplayer) {
                            try {
                                var players = document.querySelectorAll('[id*="player"]');
                                for(var k=0; k<players.length; k++) {
                                    var playerId = players[k].id;
                                    if(playerId) {
                                        var player = window.jwplayer(playerId);
                                        if(player && player.getPlaylistItem) {
                                            var item = player.getPlaylistItem();
                                            if(item && item.file) {
                                                result = item.file;
                                                break;
                                            }
                                        }
                                    }
                                }
                            } catch(e) {}
                        }
                        
                        // 4. Busca variáveis globais
                        if (!result) {
                            if(window.sources && window.sources.length > 0) {
                                result = window.sources[0].file || window.sources[0].src;
                            } else if(window.playerConfig && window.playerConfig.file) {
                                result = window.playerConfig.file;
                            } else if(window.videoUrl) {
                                result = window.videoUrl;
                            }
                        }

                        if (result && result.length > 0 && result.startsWith('http')) {
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

        // 2. Configurar Resolver com timeout aumentado
        val resolver = WebViewResolver(
            // Intercepta MP4, M3U8, e Google Cloud Storage
            interceptUrl = Regex("""\.mp4|\.m3u8|storage\.googleapis\.com|googlevideo\.com|cloudatacdn\.com"""),
            script = captureScript,
            scriptCallback = { result ->
                if (result.isNotEmpty() && result.startsWith("http")) {
                    Log.d(TAG, "✅ JS Capture: $result")
                }
            },
            timeout = 45_000L // 45 segundos (aumentado de 30s)
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
                        source = this.name,
                        name = this.name,
                        url = captured,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = url
                        this.quality = Qualities.Unknown.value
                    }
                )
            } else {
                Log.w(TAG, "⚠️ Falha ao interceptar URL de vídeo. URL final: $captured")
            }

        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro WebView: ${e.message}")
        }
    }
}
