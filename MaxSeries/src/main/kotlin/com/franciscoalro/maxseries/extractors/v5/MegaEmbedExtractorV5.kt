package com.franciscoalro.maxseries.extractors.v5

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor v5 - WEBVIEW-ONLY (v118)
 * 
 * ESTRATÉGIA V118:
 * - API retorna dados criptografados (não funciona)
 * - WebView Headless com interceptação de REDE real
 * - Intercepta: cf-master*.txt, index-*.txt, index-f*.txt
 * - Headers corretos, cookies do WebView, bypass do erro 30002
 */
class MegaEmbedExtractorV5 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        // TAG ÚNICA para confirmar que a V5 (Live Capture) está rodando
        private const val TAG = "MegaEmbedExtractorV5_v118"
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
        Log.d(TAG, "=== MEGAEMBED V5 WEBVIEW-ONLY (v118) ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // v118: WEBVIEW-ONLY com interceptação de rede REAL
            // API retorna dados criptografados, então só WebView funciona
            // Intercepta: cf-master*.txt, index-*.txt, index-f*.txt
            
            Log.d(TAG, "🚀 Iniciando WebView com interceptação de rede...")
            if (extractWithIntelligentInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView interceptou com sucesso!")
                return
            }
            
            Log.e(TAG, "❌ FALHA: WebView não conseguiu capturar o vídeo.")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico V5: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * Método Principal v118: Interceptação de Rede REAL (WebView Headless)
     * Intercepta cf-master*.txt, index-*.txt, index-f*.txt
     * Com headers corretos, cookies do WebView, e bypass do erro 30002
     */
    private suspend fun extractWithIntelligentInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val videoId = extractVideoId(url)
            if (videoId == null) {
                Log.d(TAG, "❌ VideoId não encontrado")
                return false
            }
            
            Log.d(TAG, "🆔 VideoId: $videoId")
            
            var capturedCdnUrl: String? = null
            var capturedPlaylistUrl: String? = null
            
            val resolver = WebViewResolver(
                // v118: REGEX MELHORADO - Intercepta cf-master*.txt, index-*.txt, index-f*.txt
                // Padrão observado nos logs:
                // - https://{host}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt
                // - https://{host}/v4/{shard}/{video_id}/index-f{quality}.txt
                // - https://{host}/{hash}/{shard}/{video_id}/{quality}/cf-master.*.txt
                interceptUrl = Regex("""(?:https?://)?[^/]+/(?:v4/[a-z0-9]+/[a-z0-9]+|[^/]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+)/(?:cf-master|index-f|index-).*?\.txt"""),
                additionalUrls = listOf(
                    Regex("""/cf-master\.[0-9]+\.txt"""), // cf-master.1768694011.txt
                    Regex("""/index-f[0-9]+\.txt"""), // index-f1.txt, index-f2.txt
                    Regex("""/index-[^/]+\.txt"""), // index-*.txt genérico
                    Regex("""\.txt(?:\?.*)?$"""), // Qualquer .txt com query params
                    Regex("""\.m3u8(?:\?.*)?$"""), // M3U8 com query params
                    Regex("""marvellaholdings\.sbs.*?\.txt"""), // Host específico
                    Regex("""vivonaengineering\.[a-z]+.*?\.txt"""),
                    Regex("""travianastudios\.[a-z]+.*?\.txt"""),
                    Regex("""luminairemotion\.[a-z]+.*?\.txt"""),
                    Regex("""valenium\.shop.*?\.txt""")
                ),
                useOkhttp = false,
                timeout = 45_000L, // v118: 45s (aumentado para dar tempo ao WebView)
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 400; // 40s
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                // Estratégia 1: Procurar cf-master*.txt no HTML (PRIORIDADE MÁXIMA)
                                var html = document.documentElement.innerHTML;
                                
                                // cf-master.{timestamp}.txt
                                var cfMasterMatch = html.match(/https?:\/\/[^"'\s]+\/cf-master\.[0-9]+\.txt/i);
                                if (cfMasterMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado cf-master.txt:', cfMasterMatch[0]);
                                    resolve(cfMasterMatch[0]);
                                    return;
                                }
                                
                                // index-f{quality}.txt
                                var indexFMatch = html.match(/https?:\/\/[^"'\s]+\/index-f[0-9]+\.txt/i);
                                if (indexFMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado index-f.txt:', indexFMatch[0]);
                                    resolve(indexFMatch[0]);
                                    return;
                                }
                                
                                // index-*.txt genérico
                                var indexMatch = html.match(/https?:\/\/[^"'\s]+\/index-[^"'\s]+\.txt/i);
                                if (indexMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado index.txt:', indexMatch[0]);
                                    resolve(indexMatch[0]);
                                    return;
                                }
                                
                                // Qualquer .txt no path /v4/ ou com hash
                                var anyTxtMatch = html.match(/https?:\/\/[^"'\s]+\/(?:v4|[a-z0-9_-]{20,})\/[^"'\s]+\.txt/i);
                                if (anyTxtMatch) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado .txt genérico:', anyTxtMatch[0]);
                                    resolve(anyTxtMatch[0]);
                                    return;
                                }
                                
                                // Estratégia 2: Procurar em variáveis globais do player
                                if (window.__PLAYER_CONFIG__ && window.__PLAYER_CONFIG__.url) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado de __PLAYER_CONFIG__:', window.__PLAYER_CONFIG__.url);
                                    resolve(window.__PLAYER_CONFIG__.url);
                                    return;
                                }
                                
                                if (window.playlistUrl) {
                                    clearInterval(interval);
                                    console.log('🎯 Capturado de playlistUrl:', window.playlistUrl);
                                    resolve(window.playlistUrl);
                                    return;
                                }
                                
                                // Estratégia 3: Procurar em elementos <video>
                                var videos = document.querySelectorAll('video');
                                for (var i = 0; i < videos.length; i++) {
                                    if (videos[i].src && videos[i].src.includes('http')) {
                                        clearInterval(interval);
                                        console.log('🎯 Capturado video.src:', videos[i].src);
                                        resolve(videos[i].src);
                                        return;
                                    }
                                }

                                if (attempts >= maxAttempts) {
                                    clearInterval(interval);
                                    console.log('⏱️ Timeout atingido após', attempts, 'tentativas');
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
                    "Referer" to "https://megaembed.link/", // v118: Referer correto
                    "Origin" to "https://megaembed.link",
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding" to "gzip, deflate, br",
                    "Connection" to "keep-alive",
                    "Upgrade-Insecure-Requests" to "1"
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
            
            Log.d(TAG, "⚠️ URL não é válida: $finalUrl")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro interceptação: ${e.message}")
            e.printStackTrace()
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
        
        // Validação positiva (v118: Mais permissiva)
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("cf-master") ||
               url.contains("index-f") ||
               url.contains("index-") ||
               url.contains(".txt") || // Permitir playlists ofuscadas em .txt
               url.contains("marvellaholdings.sbs") ||
               url.contains("luminairemotion.online") ||
               url.contains("valenium.shop") ||
               url.contains("vivonaengineering") ||
               url.contains("travianastudios") ||
               url.contains("virelodesignagency.cyou")
    }

    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        val cleanUrl = videoUrl.substringBefore("#")
        val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl
        
        if (videoUrl.contains(".m3u8") || videoUrl.contains(".txt") || videoUrl.contains("cf-master") || videoUrl.contains("index-")) {
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
        } else {
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name - HD",
                    url = cleanUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = effectiveReferer
                    this.quality = Qualities.Unknown.value
                }
            )
        }
    }
}
