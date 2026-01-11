package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor v4 - Dynamic CDN Capture
 * 
 * Baseado na descoberta que o CDN é gerado automaticamente:
 * - sipt.marvellaholdings.sbs (descoberto em produção)
 * - stzm/srcf/sbi6/s6p9.marvellaholdings.sbs (mapeados anteriormente)
 * 
 * Estratégia v4:
 * 1. WebView com interceptação inteligente (captura CDN real)
 * 2. Construção baseada no padrão (fallback com CDNs conhecidos)
 * 3. WebView com JavaScript execution (fallback)
 * 4. API tradicional (último recurso)
 */
class MegaEmbedExtractorV4 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractorV4"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        // CDNs conhecidos (atualizados com descobertas)
        private val KNOWN_CDN_DOMAINS = listOf(
            "sipt.marvellaholdings.sbs",  // Descoberto em produção
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
        Log.d(TAG, "=== MegaEmbed Extractor v4 - Dynamic CDN Capture ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // Método 1: WebView com interceptação inteligente (PRINCIPAL)
            Log.d(TAG, "🔄 Tentando método WebView com interceptação inteligente...")
            if (extractWithIntelligentInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptação inteligente funcionou!")
                return
            }
            
            // Método 2: Construção baseada no padrão (fallback com CDNs conhecidos)
            Log.d(TAG, "🔄 Tentando método construção por padrão...")
            if (extractWithPatternConstruction(url, referer, callback)) {
                Log.d(TAG, "✅ Construção por padrão funcionou!")
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
     * Método 1: WebView com interceptação inteligente (NOVO)
     * Captura o CDN real gerado automaticamente pelo MegaEmbed
     */
    private suspend fun extractWithIntelligentInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🧠 Iniciando interceptação inteligente...")
            
            val videoId = extractVideoId(url)
            if (videoId == null) {
                Log.e(TAG, "❌ Não foi possível extrair videoId")
                return false
            }
            
            Log.d(TAG, "🆔 VideoId extraído: $videoId")
            
            var capturedCdnUrl: String? = null
            var capturedPlaylistUrl: String? = null
            
            // Interceptar padrões específicos do MegaEmbed com foco no CDN dinâmico
            val resolver = WebViewResolver(
                // Interceptar qualquer domínio marvellaholdings.sbs
                interceptUrl = Regex("""marvellaholdings\.sbs.*cf-master\.\d+\.txt"""),
                additionalUrls = listOf(
                    // Padrão específico para capturar CDN dinâmico
                    Regex("""https?://[^/]+\.marvellaholdings\.sbs/v4/[^/]+/$videoId/cf-master\.\d+\.txt"""),
                    // Padrões gerais
                    Regex("""https?://[^/]+\.marvellaholdings\.sbs/v4/[^/]+/[^/]+/cf-master\.\d+\.txt"""),
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4""")
                ),
                useOkhttp = false,
                timeout = 35_000L,
                // Script para aguardar o carregamento completo
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 100; // 10 segundos
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                // Procurar por requisições de rede no console/logs
                                var result = '';
                                
                                // Aguardar carregamento completo
                                if (document.readyState === 'complete') {
                                    // Procurar padrões no HTML
                                    var html = document.documentElement.innerHTML;
                                    var patterns = [
                                        /https?:\/\/[^"'\s]+\.marvellaholdings\.sbs\/v4\/[^"'\s]+\/$videoId\/cf-master\.\d+\.txt/g,
                                        /https?:\/\/[^"'\s]+\.marvellaholdings\.sbs\/v4\/[^"'\s]+\/[^"'\s]+\/cf-master\.\d+\.txt/g
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
                """.trimIndent(),
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedPlaylistUrl = result.trim('"')
                        Log.d(TAG, "📜 JavaScript capturou playlist: $capturedPlaylistUrl")
                    }
                }
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
            
            capturedCdnUrl = response.url
            Log.d(TAG, "🔍 URL interceptada: $capturedCdnUrl")
            
            // Priorizar URL capturada pelo JavaScript (mais precisa)
            val finalUrl = capturedPlaylistUrl ?: capturedCdnUrl
            
            if (isValidVideoUrl(finalUrl)) {
                Log.d(TAG, "✅ URL válida capturada: $finalUrl")
                
                // Extrair CDN da URL capturada para cache futuro
                extractAndCacheCdn(finalUrl, videoId)
                
                emitExtractorLink(finalUrl, url, callback)
                return true
            }
            
            Log.d(TAG, "⚠️ URL interceptada não é vídeo válido")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na interceptação inteligente: ${e.message}")
            false
        }
    }

    /**
     * Extrai e faz cache do CDN descoberto para uso futuro
     */
    private fun extractAndCacheCdn(url: String, videoId: String) {
        try {
            val cdnPattern = Regex("""https?://([^/]+\.marvellaholdings\.sbs)""")
            val match = cdnPattern.find(url)
            
            if (match != null) {
                val discoveredCdn = match.groupValues[1]
                Log.d(TAG, "🎯 CDN descoberto: $discoveredCdn para videoId: $videoId")
                
                // TODO: Implementar cache simples (SharedPreferences ou similar)
                // Por enquanto, apenas log para debug
                Log.d(TAG, "💾 CDN $discoveredCdn pode ser usado para futuras extrações")
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair CDN: ${e.message}")
        }
    }

    /**
     * Método 2: Construção baseada no padrão (fallback)
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
                Log.e(TAG, "❌ Não foi possível extrair videoId")
                return false
            }
            
            Log.d(TAG, "🆔 VideoId extraído: $videoId")
            
            // Shards mais comuns (baseado nas descobertas)
            val possibleShards = listOf("x6b", "x7c", "x8d", "x9e")
            
            // Usar timestamp atual
            val timestamp = System.currentTimeMillis() / 1000
            
            for (cdn in KNOWN_CDN_DOMAINS) {
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
                            Log.d(TAG, "⚠️ URL construída retornou: ${response.code}")
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
     * Método 3: WebView com JavaScript execution (fallback)
     */
    private suspend fun extractWithWebViewJavaScript(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "📜 Iniciando WebView com JavaScript execution...")
            
            val videoId = extractVideoId(url)
            if (videoId == null) return false
            
            // Script JavaScript otimizado para capturar CDN dinâmico
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 80; // 8 segundos
                        
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';
                            
                            // 1. Procurar padrões específicos com videoId
                            var html = document.documentElement.innerHTML;
                            var patterns = [
                                new RegExp('https?://[^"\'\\s]+\\.marvellaholdings\\.sbs/v4/[^"\'\\s]+/$videoId/cf-master\\.\\d+\\.txt', 'g'),
                                /https?:\/\/[^"'\s]+\.marvellaholdings\.sbs\/v4\/[^"'\s]+\/[^"'\s]+\/cf-master\.\d+\.txt/g,
                                /https?:\/\/[^"'\s]+\.m3u8[^"'\s]*/g
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
                                    if (video.src && video.src.includes('marvellaholdings.sbs')) {
                                        result = video.src;
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
                interceptUrl = Regex("""marvellaholdings\.sbs.*cf-master"""),
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
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

    // Métodos auxiliares (extractVideoId, isValidVideoUrl, emitExtractorLink)
    // ... (mesmos da v3)
    
    private fun extractVideoId(url: String): String? {
        return try {
            val patterns = listOf(
                Regex("""#([a-zA-Z0-9]+)$"""),
                Regex("""/embed/([a-zA-Z0-9]+)"""),
                Regex("""/([a-zA-Z0-9]+)/?$"""),
                Regex("""id=([a-zA-Z0-9]+)"""),
                Regex("""v=([a-zA-Z0-9]+)""")
            )
            
            for (pattern in patterns) {
                val match = pattern.find(url)
                if (match != null) {
                    return match.groupValues[1]
                }
            }
            null
        } catch (e: Exception) {
            null
        }
    }

    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        if (!url.startsWith("http")) return false
        
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("cf-master") ||
               url.contains("marvellaholdings.sbs")
    }

    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        try {
            val cleanUrl = videoUrl.substringBefore("#")
            val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl
            
            if (videoUrl.contains(".m3u8") || videoUrl.contains("cf-master")) {
                Log.d(TAG, "📺 Processando como HLS: $cleanUrl")
                val m3u8Links = M3u8Helper.generateM3u8(name, cleanUrl, effectiveReferer)
                for (link in m3u8Links) {
                    callback(link)
                }
            } else {
                Log.d(TAG, "📺 Processando como MP4: $cleanUrl")
                callback.invoke(
                    newExtractorLink(name, "$name - HD", cleanUrl) {
                        this.referer = effectiveReferer
                        this.quality = Qualities.Unknown.value
                    }
                )
            }
            
            Log.d(TAG, "✅ ExtractorLink emitido com sucesso!")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao emitir ExtractorLink: ${e.message}")
        }
    }
}