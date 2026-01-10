package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.JsUnpacker
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor para CloudStream
 * 
 * O MegaEmbed usa criptografia AES-CBC no JavaScript para proteger as URLs.
 * A única forma confiável de extrair é via WebView que executa o JavaScript.
 * 
 * Fluxo:
 * 1. Carregar página no WebView
 * 2. Aguardar JavaScript descriptografar
 * 3. Interceptar requisições de rede para .m3u8/.mp4
 * 4. Ou capturar do elemento video/player
 */
class MegaEmbedExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        fun canHandle(url: String): Boolean {
            return DOMAINS.any { url.contains(it, ignoreCase = true) }
        }
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MegaEmbed Extractor ===")
        Log.d(TAG, "URL: $url")
        
        // WebView é o único método confiável para MegaEmbed
        tryWebViewExtraction(url, referer, callback)
    }

    /**
     * WebView Extraction - Método principal
     * 
     * O MegaEmbed descriptografa a URL do vídeo via JavaScript.
     * Precisamos:
     * 1. Carregar a página completa
     * 2. Simular clique no play (se necessário)
     * 3. Interceptar a URL do vídeo quando o player carregar
     */
    private suspend fun tryWebViewExtraction(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            Log.d(TAG, "Iniciando WebView extraction...")
            
            // Script avançado para capturar URL do vídeo
            // Executa após a página carregar e tenta múltiplos métodos
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 100; // 10 segundos
                        var foundUrl = '';
                        
                        // Função para validar URL de vídeo
                        function isVideoUrl(url) {
                            if (!url || typeof url !== 'string') return false;
                            return url.includes('.m3u8') || 
                                   url.includes('.mp4') || 
                                   url.includes('/hls/') ||
                                   url.includes('/video/') ||
                                   url.includes('master.txt') ||
                                   url.includes('/stream/');
                        }
                        
                        // Função para extrair URL
                        function tryCapture() {
                            // 1. Elemento video direto
                            var video = document.querySelector('video');
                            if (video) {
                                if (video.src && isVideoUrl(video.src)) return video.src;
                                if (video.currentSrc && isVideoUrl(video.currentSrc)) return video.currentSrc;
                                
                                // Source dentro do video
                                var source = video.querySelector('source');
                                if (source && source.src && isVideoUrl(source.src)) return source.src;
                            }
                            
                            // 2. Player global (VidStack, JWPlayer, etc)
                            if (window.player) {
                                if (window.player.src && isVideoUrl(window.player.src)) return window.player.src;
                                if (window.player.getPlaylistItem) {
                                    var item = window.player.getPlaylistItem();
                                    if (item && item.file && isVideoUrl(item.file)) return item.file;
                                }
                            }
                            
                            // 3. HLS.js
                            if (window.hls) {
                                if (window.hls.url && isVideoUrl(window.hls.url)) return window.hls.url;
                                if (window.hls.levels && window.hls.levels.length > 0) {
                                    var level = window.hls.levels[0];
                                    if (level.url && isVideoUrl(level.url)) return level.url;
                                }
                            }
                            
                            // 4. Variáveis globais comuns
                            var globals = ['source', 'videoUrl', 'streamUrl', 'hlsUrl', 'file', 'src'];
                            for (var i = 0; i < globals.length; i++) {
                                if (window[globals[i]] && isVideoUrl(window[globals[i]])) {
                                    return window[globals[i]];
                                }
                            }
                            
                            // 5. Media-provider do VidStack
                            var mediaProvider = document.querySelector('media-provider video');
                            if (mediaProvider) {
                                if (mediaProvider.src && isVideoUrl(mediaProvider.src)) return mediaProvider.src;
                                if (mediaProvider.currentSrc && isVideoUrl(mediaProvider.currentSrc)) return mediaProvider.currentSrc;
                            }
                            
                            return '';
                        }
                        
                        // Tentar clicar no play automaticamente
                        function tryClickPlay() {
                            var playSelectors = [
                                '#play',
                                '.play-button',
                                '.vjs-big-play-button',
                                '[class*="play"]',
                                'button[class*="play"]',
                                '#player-button-container'
                            ];
                            
                            for (var i = 0; i < playSelectors.length; i++) {
                                var btn = document.querySelector(playSelectors[i]);
                                if (btn && btn.click) {
                                    try { btn.click(); } catch(e) {}
                                }
                            }
                        }
                        
                        // Clicar no play após 1 segundo
                        setTimeout(tryClickPlay, 1000);
                        setTimeout(tryClickPlay, 2000);
                        
                        // Loop de captura
                        var interval = setInterval(function() {
                            attempts++;
                            
                            var url = tryCapture();
                            if (url && url.length > 0) {
                                foundUrl = url;
                                clearInterval(interval);
                                resolve(foundUrl);
                                return;
                            }
                            
                            if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                resolve(foundUrl);
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            // Interceptar requisições de rede para URLs de vídeo
            // IMPORTANTE: Regex ultra-específico para NUNCA capturar .js
            val resolver = WebViewResolver(
                // Padrões para interceptar - APENAS URLs que terminam com extensões de vídeo
                // Usa lookahead negativo para garantir que não é .js
                interceptUrl = Regex(
                    """(?!.*\.js).*?(\.m3u8|\.mp4|\.ts|master\.txt)(\?.*)?$""",
                    RegexOption.IGNORE_CASE
                ),
                additionalUrls = listOf(
                    Regex("""(?!.*\.js).*?\.m3u8(\?.*)?$""", RegexOption.IGNORE_CASE),
                    Regex("""(?!.*\.js).*?\.mp4(\?.*)?$""", RegexOption.IGNORE_CASE),
                    Regex("""(?!.*\.js).*?master\.txt(\?.*)?$""", RegexOption.IGNORE_CASE),
                    Regex("""(?!.*\.js).*?/cf-master\..*?(\?.*)?$""", RegexOption.IGNORE_CASE),
                    Regex("""(?!.*\.js).*?/tt/master\..*?(\?.*)?$""", RegexOption.IGNORE_CASE)
                ),
                useOkhttp = false,
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result != "undefined") {
                        val cleanResult = result.trim('"', '\'', ' ')
                        Log.d(TAG, "Script retornou: $cleanResult")
                        
                        // VALIDAÇÃO RIGOROSA: Rejeitar qualquer arquivo não-vídeo
                        if (cleanResult.contains(".js", ignoreCase = true) ||
                            cleanResult.contains(".css", ignoreCase = true) ||
                            cleanResult.contains(".woff", ignoreCase = true) ||
                            cleanResult.contains(".ttf", ignoreCase = true) ||
                            cleanResult.contains(".svg", ignoreCase = true) ||
                            cleanResult.contains(".png", ignoreCase = true) ||
                            cleanResult.contains(".jpg", ignoreCase = true)) {
                            Log.w(TAG, "❌ Rejeitado (não é vídeo): $cleanResult")
                            return@scriptCallback
                        }
                        
                        if (isValidVideoUrl(cleanResult)) {
                            capturedUrl = cleanResult
                            Log.d(TAG, "✅ Script capturou URL válida: $capturedUrl")
                        } else {
                            Log.w(TAG, "❌ URL inválida: $cleanResult")
                        }
                    }
                },
                timeout = 45_000L // 45 segundos para dar tempo de descriptografar
            )
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl),
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                interceptor = resolver
            )
            
            val interceptedUrl = response.url
            Log.d(TAG, "URL interceptada da rede: $interceptedUrl")
            
            // Validar se a URL interceptada não é um arquivo .js ou outro não-vídeo
            val isInterceptedValid = isValidVideoUrl(interceptedUrl) && 
                                     !interceptedUrl.contains(".js", ignoreCase = true) &&
                                     !interceptedUrl.contains(".css", ignoreCase = true)
            
            if (!isInterceptedValid && interceptedUrl.isNotEmpty()) {
                Log.w(TAG, "❌ URL interceptada rejeitada (não é vídeo): $interceptedUrl")
            }
            
            // Priorizar URL interceptada da rede (mais confiável)
            // Mas ignorar se for .js ou outro arquivo não-vídeo
            val videoUrl = when {
                isInterceptedValid -> {
                    Log.d(TAG, "✅ Usando URL interceptada da rede: $interceptedUrl")
                    interceptedUrl
                }
                !capturedUrl.isNullOrEmpty() && isValidVideoUrl(capturedUrl) -> {
                    Log.d(TAG, "✅ Usando URL do script: $capturedUrl")
                    capturedUrl!!
                }
                else -> {
                    Log.w(TAG, "❌ Nenhuma URL válida encontrada")
                    null
                }
            }
            
            if (videoUrl != null) {
                Log.d(TAG, "✅ URL final: $videoUrl")
                emitExtractorLink(videoUrl, url, callback)
                return true
            }
            
            Log.w(TAG, "❌ Nenhuma URL de vídeo encontrada")
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no WebView: ${e.message}")
            e.printStackTrace()
        }
        
        return false
    }

    /**
     * Emite ExtractorLink para o CloudStream
     */
    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        // Determinar referer correto
        val effectiveReferer = when {
            videoUrl.contains("cf-master") || videoUrl.contains("/cf/") -> "https://megaembed.link/"
            videoUrl.contains("tt/master") || videoUrl.contains("/tt/") -> "https://megaembed.link/"
            else -> referer
        }
        
        Log.d(TAG, "Emitindo link: $videoUrl (referer: $effectiveReferer)")
        
        if (videoUrl.contains(".m3u8") || videoUrl.contains("master.txt")) {
            try {
                // HLS - usar M3u8Helper para múltiplas qualidades
                M3u8Helper.generateM3u8(name, videoUrl, effectiveReferer).forEach { link ->
                    Log.d(TAG, "M3u8Helper gerou: ${link.name} - ${link.quality}")
                    callback(link)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Erro no M3u8Helper: ${e.message}")
                // Fallback: emitir link direto
                callback(
                    newExtractorLink(name, "$name HLS", videoUrl) {
                        this.referer = effectiveReferer
                        this.quality = Qualities.Unknown.value
                    }
                )
            }
        } else {
            // MP4 direto
            callback(
                newExtractorLink(name, name, videoUrl) {
                    this.referer = effectiveReferer
                    this.quality = Qualities.Unknown.value
                }
            )
        }
    }

    /**
     * Valida se é uma URL de vídeo válida
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        if (!url.startsWith("http")) return false
        
        // Ignorar arquivos que não são vídeo
        if (url.contains(".js") || url.contains(".css") || url.contains(".png") || 
            url.contains(".jpg") || url.contains(".gif") || url.contains(".svg") ||
            url.contains(".woff") || url.contains(".ttf")) {
            return false
        }
        
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("/hls/") || 
               url.contains("/video/") ||
               url.contains("master.txt") ||
               url.contains("/stream/") ||
               url.contains("/cf-master") ||
               url.contains("/tt/master")
    }
}
