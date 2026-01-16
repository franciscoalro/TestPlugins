package com.franciscoalro.maxseries.extractors.v5

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log
import com.franciscoalro.maxseries.extractors.MegaEmbedLinkFetcher

/**
 * MegaEmbed Extractor v5 - LIVE CAPTURE (WebView Only)
 * 
 * ESTRATÉGIA V5 (v90+):
 * - Bruteforce removido completamente (causava timeouts)
 * - WebView Interception é o ÚNICO método principal
 * - Classe renomeada para forçar limpeza de cache no Cloudstream
 */
class MegaEmbedExtractorV5 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        // TAG ÚNICA para confirmar que a V5 (Live Capture) está rodando
        private const val TAG = "MegaEmbedExtractorV5_LIVE"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        // CDNs conhecidos (backup apenas)
        private val KNOWN_CDN_DOMAINS = listOf(
            "valenium.shop", // NOVO (v94)
            "sqtd.luminairemotion.online",
            "stzm.luminairemotion.online",
            "srcf.luminairemotion.online",
            "sipt.marvellaholdings.sbs",
            "stzm.marvellaholdings.sbs",
            "srcf.marvellaholdings.sbs", 
            "sbi6.marvellaholdings.sbs",
            "s6p9.marvellaholdings.sbs",
            "sr81.virelodesignagency.cyou"
        )
        
        // Shards conhecidos
        private val KNOWN_SHARDS = listOf("is3", "x6b", "x7c", "x8d", "x9e", "5w3")
        
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
        Log.d(TAG, "=== MEGAEMBED V5 LIVE CAPTURE (v91) ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // Método 1: WebView com interceptação (LIVE CAPTURE)
            // ÚNICO método principal para evitar delays
            Log.d(TAG, "🚀 Iniciando WebView Interception (Modo Exclusivo)...")
            if (extractWithIntelligentInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptou com sucesso!")
                return
            }
            
            // Método 2: WebView com JavaScript (Fallback secundário)
            Log.d(TAG, "⚠️ Interceptação direta falhou, tentando injeção JS...")
            if (extractWithWebViewJavaScript(url, referer, callback)) {
                Log.d(TAG, "✅ JS funcionou!")
                return
            }
            
            // Método 3: API Tradicional (Último recurso)
            Log.d(TAG, "⚠️ JS falhou, tentando API legacy...")
            if (extractWithApiTraditional(url, referer, callback)) {
                Log.d(TAG, "✅ API Legacy salvou!")
                return
            }
            
            Log.e(TAG, "❌ FALHA TOTAL: Nenhum método conseguiu capturar o vídeo.")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico V5: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * Método Principal: Interceptação Inteligente
     */
    private suspend fun extractWithIntelligentInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val videoId = extractVideoId(url)
            if (videoId == null) return false
            
            Log.d(TAG, "🆔 VideoId alvo: $videoId")
            
            var capturedCdnUrl: String? = null
            var capturedPlaylistUrl: String? = null
            
            val resolver = WebViewResolver(
                // Regex genérico para qualquer domínio marvellaholdings/luminairemotion
                interceptUrl = Regex(""".*cf-master.*\.txt"""),
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4""")
                ),
                useOkhttp = false,
                timeout = 15_000L, // 15s para garantir carregamento completo
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 100; // 10s
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                // Estratégia 1: Regex no HTML
                                var html = document.documentElement.innerHTML;
                                var match = html.match(/https?:\/\/[^"'\s]+\/cf-master\.\d+\.txt/);
                                if (match) {
                                    clearInterval(interval);
                                    resolve(match[0]);
                                    return;
                                }
                                
                                // Estratégia 2: Player Source
                                var videos = document.querySelectorAll('video');
                                for (var i = 0; i < videos.length; i++) {
                                    if (videos[i].src && videos[i].src.includes('http')) {
                                        clearInterval(interval);
                                        resolve(videos[i].src);
                                        return;
                                    }
                                }

                                if (attempts >= maxAttempts) {
                                    clearInterval(interval);
                                    resolve('');
                                }
                            }, 100);
                        });
                    })()
                """.trimIndent(),
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedPlaylistUrl = result.trim('"')
                        Log.d(TAG, "📜 JS Callback capturou: $capturedPlaylistUrl")
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
            Log.d(TAG, "🔍 URL final do WebView: $capturedCdnUrl")
            
            val finalUrl = capturedPlaylistUrl ?: capturedCdnUrl
            
            if (isValidVideoUrl(finalUrl)) {
                Log.d(TAG, "🎯 URL VÁLIDA ENCONTRADA: $finalUrl")
                emitExtractorLink(finalUrl, url, callback)
                return true
            }
            
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro interceptação: ${e.message}")
            false
        }
    }

    private suspend fun extractWithWebViewJavaScript(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // Implementação simplificada para backup
        return false // Por enquanto foca na interceptação
    }

    private suspend fun extractWithApiTraditional(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val videoId = extractVideoId(url) ?: return false
            val playlistUrl = MegaEmbedLinkFetcher.fetchPlaylistUrl(videoId)
            if (playlistUrl != null && isValidVideoUrl(playlistUrl)) {
                emitExtractorLink(playlistUrl, url, callback)
                return true
            }
            false
        } catch (e: Exception) {
            false
        }
    }

    private fun extractVideoId(url: String): String? {
        return try {
            val patterns = listOf(
                Regex("""#([a-zA-Z0-9]+)$"""),
                Regex("""/embed/([a-zA-Z0-9]+)"""),
                Regex("""v=([a-zA-Z0-9]+)""")
            )
            for (pattern in patterns) {
                pattern.find(url)?.let { return it.groupValues[1] }
            }
            null
        } catch (e: Exception) { null }
    }

    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty() || !url.startsWith("http")) return false
        
        // Anti-Analytics
        if (url.contains("google-analytics") || url.contains("googletagmanager")) return false
        
        // Validação positiva (v94: Mais permissiva)
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("cf-master") ||
               url.contains("valenium.shop") || // NOVO
               url.contains("marvellaholdings.sbs") ||
               url.contains("luminairemotion.online") ||
               url.contains("virelodesignagency.cyou")
    }

    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        val cleanUrl = videoUrl.substringBefore("#")
        val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl
        
        if (videoUrl.contains(".m3u8") || videoUrl.contains("cf-master")) {
            val m3u8Links = M3u8Helper.generateM3u8(
                name, 
                cleanUrl, 
                effectiveReferer,
                headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
                    "Referer" to effectiveReferer,
                    "Origin" to effectiveReferer.substringBefore("/", "https://megaembed.link")
                )
            )
            m3u8Links.forEach { callback(it) }
        } else {
            callback.invoke(
                newExtractorLink(name, "$name - HD", cleanUrl) {
                    this.referer = effectiveReferer
                }
            )
        }
    }
}