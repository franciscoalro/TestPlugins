package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor v3 - Pattern-Based Implementation
 * 
 * Baseado na descoberta dos links reais do MegaEmbed:
 * https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
 * 
 * Estrutura descoberta:
 * - CDN: stzm/srcf/sbi6/s6p9.marvellaholdings.sbs (rotativo)
 * - Path: /v4/{shard}/{videoId}/cf-master.{timestamp}.txt
 * - videoId: 3wnuij (fixo para o episódio)
 * - timestamp: 1767386783 (temporário, muda a cada play)
 * 
 * Fluxo de funcionamento:
 * 1. WebView com interceptação (principal - para JS complexo)
 * 2. Construção baseada no padrão (novo - para casos simples)
 * 3. WebView com JavaScript execution (fallback)
 * 4. API tradicional (último recurso)
 */
class MegaEmbedExtractorV3 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractorV3"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        // CDNs descobertos na análise real
        private val CDN_DOMAINS = listOf(
            "stzm.marvellaholdings.sbs",
            "srcf.marvellaholdings.sbs", 
            "sbi6.marvellaholdings.sbs",
            "s6p9.marvellaholdings.sbs"
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
        Log.d(TAG, "=== MegaEmbed Extractor v3 - Pattern-Based Implementation ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // Método 1: Construção baseada no padrão (NOVO - mais rápido)
            Log.d(TAG, "🔄 Tentando método construção por padrão...")
            if (extractWithPatternConstruction(url, referer, callback)) {
                Log.d(TAG, "✅ Construção por padrão funcionou!")
                return
            }
            
            // Método 2: WebView com interceptação de rede (para JS complexo)
            Log.d(TAG, "🔄 Tentando método WebView com interceptação...")
            if (extractWithWebViewInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptação funcionou!")
                return
            }
            
            // Método 3: WebView com JavaScript execution (fallback)
            Log.d(TAG, "🔄 Tentando método WebView com JavaScript...")
            if (extractWithWebViewJavaScript(url, referer, callback)) {
                Log.d(TAG, "✅ WebView JavaScript funcionou!")
                return
            }
            
            // Método 4: API tradicional (último recurso)
            Log.d(TAG, "🔄 Tentando método API tradicional...")
            if (extractWithApiTraditional(url, referer, callback)) {
                Log.d(TAG, "✅ API tradicional funcionou!")
                return
            }
            
            Log.e(TAG, "❌ Todos os métodos falharam para: $url")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico na extração: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * Método 1: Construção baseada no padrão descoberto (NOVO)
     * Mais rápido que WebView, baseado na análise real dos links
     */
    private suspend fun extractWithPatternConstruction(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🔨 Iniciando construção baseada no padrão...")
            
            val videoId = extractVideoId(url)
            if (videoId == null) {
                Log.e(TAG, "❌ Não foi possível extrair videoId de: $url")
                return false
            }
            
            Log.d(TAG, "🆔 VideoId extraído: $videoId")
            
            // Shards mais comuns (baseado no teste bem-sucedido)
            val possibleShards = listOf("x6b", "x7c", "x8d")
            
            // Usar timestamp atual
            val timestamp = System.currentTimeMillis() / 1000
            
            for (cdn in CDN_DOMAINS) {
                for (shard in possibleShards) {
                    val constructedUrl = "https://$cdn/v4/$shard/$videoId/cf-master.$timestamp.txt"
                    
                    Log.d(TAG, "🧪 Testando URL construída: $constructedUrl")
                    
                    try {
                        val response = app.get(
                            constructedUrl,
                            headers = mapOf(
                                "User-Agent" to USER_AGENT,
                                "Referer" to (referer ?: mainUrl)
                            ),
                            timeout = 8
                        )
                        
                        if (response.isSuccessful && response.text.contains("#EXTM3U")) {
                            Log.d(TAG, "✅ URL construída funcionou: $constructedUrl")
                            Log.d(TAG, "📄 Playlist preview: ${response.text.take(200)}...")
                            
                            emitExtractorLink(constructedUrl, url, callback)
                            return true
                        } else {
                            Log.d(TAG, "⚠️ URL construída retornou: ${response.code} - ${response.text.take(50)}")
                        }
                    } catch (e: Exception) {
                        Log.d(TAG, "⚠️ URL construída falhou: ${e.message}")
                        continue
                    }
                }
            }
            
            Log.d(TAG, "❌ Nenhuma URL construída funcionou")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na construção por padrão: ${e.message}")
            false
        }
    }

    /**
     * Método 2: WebView com interceptação de rede
     * Para casos onde JS é necessário para gerar o link
     */
    private suspend fun extractWithWebViewInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🌐 Iniciando WebView com interceptação de rede...")
            
            // Interceptar padrões específicos do MegaEmbed
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|/hls/|/video/|/v4/.*\.txt|marvellaholdings\.sbs"""),
                additionalUrls = listOf(
                    Regex("""https?://[^/]+\.marvellaholdings\.sbs/v4/[^/]+/[^/]+/cf-master\.\d+\.txt"""), // Padrão específico
                    Regex("""https?://[^/]+/v4/[^/]+/[^/]+/[^"'\s]*\.txt"""),
                    Regex("""https?://[^/]+\.m3u8"""),
                    Regex("""https?://[^/]+\.mp4""")
                ),
                useOkhttp = false, // Importante para bypass Cloudflare
                timeout = 30_000L
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
            
            val capturedUrl = response.url
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
     * Método 3: WebView com execução de JavaScript
     * Para casos onde variáveis JS precisam ser capturadas
     */
    private suspend fun extractWithWebViewJavaScript(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "📜 Iniciando WebView com JavaScript execution...")
            
            // Script JavaScript otimizado para MegaEmbed
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 80; // 8 segundos
                        
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';
                            
                            // 1. Procurar padrões específicos do MegaEmbed no HTML
                            var html = document.documentElement.innerHTML;
                            var patterns = [
                                /https?:\/\/[^"'\s]+\.marvellaholdings\.sbs\/v4\/[^"'\s]+\.txt/g,
                                /https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\/[^"'\s]+\/cf-master\.\d+\.txt/g,
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
                            
                            // 2. Procurar em elementos video/source
                            if (!result) {
                                var videos = document.querySelectorAll('video');
                                for (var i = 0; i < videos.length; i++) {
                                    var video = videos[i];
                                    if (video.src && video.src.startsWith('http')) {
                                        result = video.src;
                                        break;
                                    }
                                }
                            }
                            
                            // 3. Variáveis globais
                            if (!result) {
                                var globals = ['videoUrl', 'playlistUrl', 'source', 'file'];
                                for (var k = 0; k < globals.length; k++) {
                                    var varName = globals[k];
                                    if (window[varName] && typeof window[varName] === 'string' && window[varName].startsWith('http')) {
                                        result = window[varName];
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
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|marvellaholdings\.sbs"""),
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result.startsWith("http")) {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "📜 JavaScript capturou: $capturedUrl")
                    }
                },
                timeout = 25_000L
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
     * Método 4: API tradicional (último recurso)
     * Usa MegaEmbedLinkFetcher como fallback
     */
    private suspend fun extractWithApiTraditional(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🌐 Tentando API tradicional...")
            
            val videoId = extractVideoId(url)
            if (videoId != null) {
                Log.d(TAG, "🆔 Video ID extraído: $videoId")
                
                val playlistUrl = MegaEmbedLinkFetcher.fetchPlaylistUrl(videoId)
                if (playlistUrl != null && isValidVideoUrl(playlistUrl)) {
                    Log.d(TAG, "✅ API tradicional funcionou: $playlistUrl")
                    emitExtractorLink(playlistUrl, url, callback)
                    return true
                }
            }
            
            Log.d(TAG, "⚠️ API tradicional falhou")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na API tradicional: ${e.message}")
            false
        }
    }

    /**
     * Extrai o videoId da URL do MegaEmbed
     */
    private fun extractVideoId(url: String): String? {
        return try {
            Log.d(TAG, "🔍 Extraindo videoId de: $url")
            
            val patterns = listOf(
                Regex("""#([a-zA-Z0-9]+)$"""),           // #3wnuij
                Regex("""/embed/([a-zA-Z0-9]+)"""),      // /embed/3wnuij
                Regex("""/([a-zA-Z0-9]+)/?$"""),         // /3wnuij
                Regex("""id=([a-zA-Z0-9]+)"""),          // ?id=3wnuij
                Regex("""v=([a-zA-Z0-9]+)""")            // ?v=3wnuij
            )
            
            for (pattern in patterns) {
                val match = pattern.find(url)
                if (match != null) {
                    val videoId = match.groupValues[1]
                    Log.d(TAG, "✅ VideoId encontrado: $videoId")
                    return videoId
                }
            }
            
            Log.e(TAG, "❌ VideoId não encontrado na URL")
            null
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair videoId: ${e.message}")
            null
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
               url.contains("marvellaholdings.sbs") ||
               url.contains("cf-master")
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
            
            if (videoUrl.contains(".m3u8") || videoUrl.contains("master.txt") || videoUrl.contains("cf-master")) {
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