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
        private const val TAG = "MegaEmbedExtractorV5_v116"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        // CDNs conhecidos (backup apenas) - v107 updated from network logs
        private val KNOWN_CDN_DOMAINS = listOf(
            "valenium.shop",
            "spo3.marvellaholdings.sbs", // NOVO (v107) - de logs de rede
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
        Log.d(TAG, "=== MEGAEMBED V5 WEBVIEW-ONLY (v116) ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // v116: API Tradicional DESABILITADA - Só WebView funciona
            // Motivo: MegaEmbedLinkFetcher testa 30 hosts e todos falham (9s perdidos)
            
            // Método 1: WebView com interceptação (ÚNICO MÉTODO)
            Log.d(TAG, "🚀 Iniciando WebView Interception (Modo Exclusivo)...")
            if (extractWithIntelligentInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptou com sucesso!")
                return
            }
            
            // Método 2: WebView com JavaScript (Fallback)
            Log.d(TAG, "⚠️ Interceptação direta falhou, tentando injeção JS...")
            if (extractWithWebViewJavaScript(url, referer, callback)) {
                Log.d(TAG, "✅ JS funcionou!")
                return
            }
            
            // Método 3: API Tradicional DESABILITADO (v116)
            // Motivo: Hosts dinâmicos mudam constantemente, bruteforce não funciona
            // Log.d(TAG, "⚠️ JS falhou, tentando API legacy...")
            // if (extractWithApiTraditional(url, referer, callback)) {
            //     Log.d(TAG, "✅ API Legacy salvou!")
            //     return
            // }
            
            Log.e(TAG, "❌ FALHA TOTAL: WebView não conseguiu capturar o vídeo.")
            
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
                // v115: REGEX MELHORADO - Captura .txt (m3u8 camuflado)
                // Pattern: /v4/{shard}/{video_id}/cf-master.*.txt
                // Exemplo: https://spo3.marvellaholdings.sbs/v4/x6b/ilbwoq/cf-master.1768694011.txt
                // Hosts dinâmicos: marvellaholdings.sbs, vivonaengineering.*, travianastudios.*, etc
                interceptUrl = Regex("""(?:https?://)?[^/]+/v4/[a-z0-9]+/[a-z0-9]+/(?:cf-master|index-).*?\.txt"""),
                additionalUrls = listOf(
                    Regex("""/v4/.*?\.txt$"""), // Qualquer .txt no path /v4/
                    Regex("""/v4/.*?\.woff2?$"""), // Segmentos disfarçados
                    Regex("""\.m3u8(?:\?.*)?$"""), // M3U8 com query params
                    Regex("""\.mp4(?:\?.*)?$"""), // MP4 com query params
                    Regex("""marvellaholdings\.sbs.*?\.txt"""), // Host específico
                    Regex("""vivonaengineering\.[a-z]+.*?\.txt"""), // Variações de host
                    Regex("""travianastudios\.[a-z]+.*?\.txt"""),
                    Regex("""luminairemotion\.[a-z]+.*?\.txt""")
                ),
                useOkhttp = false,
                timeout = 30_000L, // v115: 30s (aumentado)
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 250; // 25s
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                // Estratégia 1: Regex AGRESSIVO no HTML para .txt
                                var html = document.documentElement.innerHTML;
                                
                                // Procurar cf-master.*.txt (PRIORIDADE MÁXIMA)
                                var txtMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[a-z0-9]+\/[a-z0-9]+\/cf-master\.\d+\.txt/i);
                                if (txtMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado cf-master.txt:', txtMatch[0]);
                                    resolve(txtMatch[0]);
                                    return;
                                }
                                
                                // Procurar index-*.txt (alternativa)
                                var indexMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[a-z0-9]+\/[a-z0-9]+\/index-[^"'\s]+\.txt/i);
                                if (indexMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado index.txt:', indexMatch[0]);
                                    resolve(indexMatch[0]);
                                    return;
                                }
                                
                                // Procurar qualquer .txt no path /v4/
                                var anyTxtMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.txt/i);
                                if (anyTxtMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado .txt genérico:', anyTxtMatch[0]);
                                    resolve(anyTxtMatch[0]);
                                    return;
                                }
                                
                                // Estratégia 2: Player Source (fallback)
                                var videos = document.querySelectorAll('video');
                                for (var i = 0; i < videos.length; i++) {
                                    if (videos[i].src && videos[i].src.includes('http')) {
                                        clearInterval(interval);
                                        console.log('🎯 Capturado video.src:', videos[i].src);
                                        resolve(videos[i].src);
                                        return;
                                    }
                                }
                                
                                // Estratégia 3: Procurar em variáveis globais
                                if (window.playlistUrl) {
                                    clearInterval(interval);
                                    resolve(window.playlistUrl);
                                    return;
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
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
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
               url.contains(".txt") || // Permitir playlists ofuscadas em .txt
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
        
        if (videoUrl.contains(".m3u8") || videoUrl.contains(".txt") || videoUrl.contains("cf-master")) {
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name - Auto",
                    url = cleanUrl,
                    type = ExtractorLinkType.M3U8
                ) {
                    this.referer = "https://megaembed.link/"
                    this.quality = Qualities.Unknown.value
                    this.headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
                        "Referer" to "https://megaembed.link/",
                        "Origin" to "https://megaembed.link",
                        "Accept" to "*/*",
                        "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept-Encoding" to "gzip, deflate, br",
                        "Connection" to "keep-alive",
                        "Sec-Fetch-Dest" to "empty",
                        "Sec-Fetch-Mode" to "cors",
                        "Sec-Fetch-Site" to "cross-site",
                        "Te" to "trailers"
                    )
                }
            )

            // M3u8Helper removido temporariamente para garantir build (v113)
        } else {
            callback.invoke(
                newExtractorLink(name, "$name - HD", cleanUrl) {
                    this.referer = effectiveReferer
                }
            )
        }
    }
}