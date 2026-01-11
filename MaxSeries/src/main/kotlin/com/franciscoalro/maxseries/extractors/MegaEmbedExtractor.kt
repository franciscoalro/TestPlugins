package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor v2 - WebView Real Implementation
 * 
 * O MegaEmbed usa criptografia AES-CBC no JavaScript para proteger as URLs.
 * Esta implementação usa WebView real para executar o JavaScript e interceptar
 * as requisições de rede para capturar a URL final do vídeo.
 * 
 * Fluxo de funcionamento:
 * 1. Carregar página MegaEmbed no WebView
 * 2. Executar JavaScript que descriptografa a URL
 * 3. Interceptar requisições de rede para .m3u8/.mp4
 * 4. Capturar URL final do vídeo
 * 
 * Fallbacks implementados:
 * - WebView com interceptação de rede (principal)
 * - JavaScript execution com captura de variáveis
 * - HTTP direto via MegaEmbedLinkFetcher (backup)
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
        Log.d(TAG, "=== MegaEmbed Extractor v2 - WebView Implementation ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // Método 1: WebView com interceptação de rede (principal)
            Log.d(TAG, "🔄 Tentando método WebView com interceptação...")
            if (extractWithWebViewInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptação funcionou!")
                return
            }
            
            // Método 2: WebView com JavaScript execution (fallback)
            Log.d(TAG, "🔄 Tentando método WebView com JavaScript...")
            if (extractWithWebViewJavaScript(url, referer, callback)) {
                Log.d(TAG, "✅ WebView JavaScript funcionou!")
                return
            }
            
            // Método 3: HTTP direto (último recurso)
            Log.d(TAG, "🔄 Tentando método HTTP direto...")
            if (extractWithHttpDirect(url, referer, callback)) {
                Log.d(TAG, "✅ HTTP direto funcionou!")
                return
            }
            
            Log.e(TAG, "❌ Todos os métodos falharam para: $url")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico na extração: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * Método 1: WebView com interceptação de rede
     * Intercepta requisições HTTP para capturar URLs de vídeo
     */
    private suspend fun extractWithWebViewInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🌐 Iniciando WebView com interceptação de rede...")
            
            var capturedUrl: String? = null
            
            // Interceptar múltiplos padrões de URL de vídeo
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|/hls/|/video/|/v4/.*\.txt|cloudatacdn|sssrr\.org"""),
                additionalUrls = listOf(
                    Regex("""https?://[^/]+/v4/[^/]+/[^/]+/cf-master\.\d+\.txt"""), // MegaEmbed pattern
                    Regex("""https?://[^/]+\.m3u8"""),
                    Regex("""https?://[^/]+\.mp4"""),
                    Regex("""cloudatacdn\.com[^"'\s]*"""),
                    Regex("""sssrr\.org[^"'\s]*\.m3u8""")
                ),
                useOkhttp = false, // Importante para bypass Cloudflare
                timeout = 45_000L
            )
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl),
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
                ),
                interceptor = resolver
            )
            
            capturedUrl = response.url
            
            Log.d(TAG, "🔍 URL interceptada: $capturedUrl")
            
            // Validar se a URL interceptada é um vídeo válido
            if (isValidVideoUrl(capturedUrl)) {
                Log.d(TAG, "✅ URL de vídeo válida interceptada")
                emitExtractorLink(capturedUrl, url, callback)
                return true
            }
            
            Log.d(TAG, "⚠️ URL interceptada não é vídeo válido")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na interceptação WebView: ${e.message}")
            false
        }
    }

    /**
     * Método 2: WebView com execução de JavaScript
     * Executa JavaScript na página para capturar variáveis de vídeo
     */
    private suspend fun extractWithWebViewJavaScript(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "📜 Iniciando WebView com JavaScript execution...")
            
            // Script JavaScript avançado para capturar URLs de vídeo
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 100; // 10 segundos
                        
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';
                            
                            // 1. Procurar em elementos video
                            var videos = document.querySelectorAll('video');
                            for (var i = 0; i < videos.length; i++) {
                                var video = videos[i];
                                if (video.src && video.src.startsWith('http')) {
                                    result = video.src;
                                    break;
                                }
                                if (video.currentSrc && video.currentSrc.startsWith('http')) {
                                    result = video.currentSrc;
                                    break;
                                }
                            }
                            
                            // 2. Procurar em elementos source
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
                            
                            // 3. Variáveis globais comuns do MegaEmbed
                            if (!result) {
                                var globals = ['videoUrl', 'playlistUrl', 'source', 'file', 'src', 'url'];
                                for (var k = 0; k < globals.length; k++) {
                                    var varName = globals[k];
                                    if (window[varName] && typeof window[varName] === 'string' && window[varName].startsWith('http')) {
                                        result = window[varName];
                                        break;
                                    }
                                }
                            }
                            
                            // 4. Procurar em objetos de configuração
                            if (!result) {
                                if (window.jwplayer) {
                                    try {
                                        var jw = window.jwplayer();
                                        if (jw && jw.getPlaylistItem) {
                                            var item = jw.getPlaylistItem();
                                            if (item && item.file) result = item.file;
                                        }
                                    } catch(e) {}
                                }
                            }
                            
                            // 5. Procurar padrões específicos do MegaEmbed no HTML
                            if (!result) {
                                var html = document.documentElement.innerHTML;
                                var patterns = [
                                    /https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.txt/g,
                                    /https?:\/\/[^"'\s]+\.m3u8[^"'\s]*/g,
                                    /https?:\/\/[^"'\s]+\.mp4[^"'\s]*/g
                                ];
                                
                                for (var p = 0; p < patterns.length; p++) {
                                    var matches = html.match(patterns[p]);
                                    if (matches && matches.length > 0) {
                                        result = matches[0];
                                        break;
                                    }
                                }
                            }
                            
                            if (result && result.length > 0) {
                                clearInterval(interval);
                                resolve(result);
                            } else if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                resolve(''); // Timeout
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|/hls/|/video/|/v4/.*\.txt|cloudatacdn|sssrr\.org"""),
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result.startsWith("http")) {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "📜 JavaScript capturou: $capturedUrl")
                    }
                },
                timeout = 30_000L
            )
            
            app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl)
                ),
                interceptor = resolver
            )
            
            if (!capturedUrl.isNullOrEmpty() && isValidVideoUrl(capturedUrl!!)) {
                Log.d(TAG, "✅ JavaScript capturou URL válida")
                emitExtractorLink(capturedUrl!!, url, callback)
                return true
            }
            
            Log.d(TAG, "⚠️ JavaScript não capturou URL válida")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na execução JavaScript: ${e.message}")
            false
        }
    }

    /**
     * Método 3: HTTP direto (fallback)
     * Usa o MegaEmbedLinkFetcher como último recurso
     */
    private suspend fun extractWithHttpDirect(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🌐 Tentando HTTP direto via MegaEmbedLinkFetcher...")
            
            val videoId = MegaEmbedLinkFetcher.extractVideoId(url)
            if (videoId != null) {
                Log.d(TAG, "🆔 Video ID extraído: $videoId")
                
                val playlistUrl = MegaEmbedLinkFetcher.fetchPlaylistUrl(videoId)
                if (playlistUrl != null && isValidVideoUrl(playlistUrl)) {
                    Log.d(TAG, "✅ HTTP direto obteve URL válida")
                    emitExtractorLink(playlistUrl, url, callback)
                    return true
                }
            }
            
            Log.d(TAG, "⚠️ HTTP direto falhou")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no HTTP direto: ${e.message}")
            false
        }
    }

    /**
     * Valida se uma URL é um vídeo válido
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        if (!url.startsWith("http")) return false
        
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("/hls/") || 
               url.contains("/video/") ||
               url.contains("/v4/") ||
               url.contains("master.txt") ||
               url.contains("cloudatacdn") ||
               url.contains("sssrr.org")
    }

    /**
     * Emite ExtractorLink para o CloudStream
     */
    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        try {
            val cleanUrl = videoUrl.substringBefore("#")
            
            // Determinar qualidade baseada na URL ou conteúdo
            val quality = when {
                videoUrl.contains("1080p") -> Qualities.P1080.value
                videoUrl.contains("720p") -> Qualities.P720.value
                videoUrl.contains("480p") -> Qualities.P480.value
                videoUrl.contains("360p") -> Qualities.P360.value
                else -> Qualities.Unknown.value
            }
            
            val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl
            
            if (videoUrl.contains(".m3u8") || videoUrl.contains("master.txt")) {
                // HLS - usar M3u8Helper para múltiplas qualidades
                Log.d(TAG, "📺 Processando como HLS: $cleanUrl")
                M3u8Helper.generateM3u8(name, cleanUrl, effectiveReferer).forEach(callback)
            } else {
                // MP4 direto
                Log.d(TAG, "📺 Processando como MP4: $cleanUrl")
                callback.invoke(
                    newExtractorLink(
                        name,
                        "$name - ${if (quality != Qualities.Unknown.value) "${quality}p" else "HD"}",
                        cleanUrl
                    ) {
                        this.referer = effectiveReferer
                        this.quality = quality
                    }
                )
            }
            
            Log.d(TAG, "✅ ExtractorLink emitido com sucesso!")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao emitir ExtractorLink: ${e.message}")
        }
    }
}