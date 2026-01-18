package com.franciscoalro.maxseries.extractors.v5

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log
import com.franciscoalro.maxseries.utils.JsUnpackerUtil

/**
 * MegaEmbed Extractor v5 - ALL STRATEGIES (v119)
 * 
 * ESTRATÉGIA V119 - CASCATA COMPLETA:
 * 1. HTML Regex (rápido, sem overhead)
 * 2. JsUnpacker (descompactar JS ofuscado)
 * 3. WebView JavaScript-Only (executar JS e capturar)
 * 4. WebView com Interceptação (fallback final)
 * 
 * Testa TODAS as estratégias até encontrar o vídeo
 */
class MegaEmbedExtractorV5 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractorV5_v126"
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
        Log.d(TAG, "=== MEGAEMBED V5 ALL STRATEGIES (v126) ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            val videoId = extractVideoId(url)
            if (videoId == null) {
                Log.e(TAG, "❌ VideoId não encontrado")
                return
            }
            
            Log.d(TAG, "🆔 VideoId: $videoId")
            
            // ESTRATÉGIA 0: DIRECT API (v125 - NOVO - MAIS RÁPIDO)
            Log.d(TAG, "🔍 [0/5] Tentando Direct API...")
            if (extractWithDirectAPI(videoId, referer, callback)) {
                Log.d(TAG, "✅ Direct API funcionou!")
                return
            }
            
            // ESTRATÉGIA 1: HTML REGEX (mais rápido)
            Log.d(TAG, "🔍 [1/5] Tentando HTML Regex...")
            if (extractWithHtmlRegex(url, referer, callback)) {
                Log.d(TAG, "✅ HTML Regex funcionou!")
                return
            }
            
            // ESTRATÉGIA 2: JS UNPACKER
            Log.d(TAG, "🔍 [2/5] Tentando JsUnpacker...")
            if (extractWithJsUnpacker(url, referer, callback)) {
                Log.d(TAG, "✅ JsUnpacker funcionou!")
                return
            }
            
            // ESTRATÉGIA 3: WEBVIEW JAVASCRIPT-ONLY
            Log.d(TAG, "🔍 [3/5] Tentando WebView JavaScript-Only...")
            if (extractWithWebViewJavaScript(url, referer, callback)) {
                Log.d(TAG, "✅ WebView JavaScript funcionou!")
                return
            }
            
            // ESTRATÉGIA 4: WEBVIEW COM INTERCEPTAÇÃO
            Log.d(TAG, "🔍 [4/5] Tentando WebView com Interceptação...")
            if (extractWithWebViewInterception(url, referer, callback)) {
                Log.d(TAG, "✅ WebView Interceptação funcionou!")
                return
            }
            
            Log.e(TAG, "❌ FALHA: Todas as 5 estratégias falharam")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico V5: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * ESTRATÉGIA 0: Direct API (v125 - NOVO)
     * Faz requisição direta para API sem WebView
     * Baseado nos logs ADB que mostram: /api/v1/info?id=3wnuij
     */
    private suspend fun extractWithDirectAPI(
        videoId: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val apiUrl = "https://megaembed.link/api/v1/info?id=$videoId"
            Log.d(TAG, "📡 Direct API: $apiUrl")
            
            val response = app.get(
                apiUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/",
                    "Origin" to "https://megaembed.link",
                    "Accept" to "application/json, text/plain, */*"
                )
            )
            
            val json = response.text
            Log.d(TAG, "📄 API Response: ${json.take(200)}...")
            
            // Tentar parsear JSON
            val urlRegex = Regex("""https?://[^"'\s]+\.(?:txt|m3u8|mp4)""")
            val urlMatch = urlRegex.find(json)
            
            if (urlMatch != null) {
                val videoUrl = urlMatch.value
                Log.d(TAG, "🎯 Direct API capturou: $videoUrl")
                emitExtractorLink(videoUrl, "https://megaembed.link/", callback)
                return true
            }
            
            // Tentar padrões específicos no JSON
            val patterns = listOf(
                Regex(""""url"\s*:\s*"([^"]+)""""),
                Regex(""""file"\s*:\s*"([^"]+)""""),
                Regex(""""source"\s*:\s*"([^"]+)""""),
                Regex(""""playlist"\s*:\s*"([^"]+)"""")
            )
            
            for (pattern in patterns) {
                val match = pattern.find(json)
                if (match != null) {
                    val videoUrl = match.groupValues[1].replace("\\/", "/")
                    if (isValidVideoUrl(videoUrl)) {
                        Log.d(TAG, "🎯 Direct API capturou (pattern): $videoUrl")
                        emitExtractorLink(videoUrl, "https://megaembed.link/", callback)
                        return true
                    }
                }
            }
            
            Log.d(TAG, "⚠️ Direct API: Nenhuma URL encontrada no JSON")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ Direct API falhou: ${e.message}")
            false
        }
    }

    /**
     * ESTRATÉGIA 1: HTML Regex
     * Busca URLs .txt diretamente no HTML (mais rápido)
     */
    private suspend fun extractWithHtmlRegex(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/",
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                )
            )
            
            val html = response.text
            Log.d(TAG, "📄 HTML baixado: ${html.length} chars")
            
            // Padrões para URLs .txt
            val patterns = listOf(
                Regex("""https?://[^"'\s]+/cf-master\.[0-9]+\.txt"""),
                Regex("""https?://[^"'\s]+/index-f[0-9]+\.txt"""),
                Regex("""https?://[^"'\s]+/index-[^"'\s]+\.txt"""),
                Regex("""https?://[^"'\s]+/v4/[a-z0-9]+/[a-z0-9]+/[^"'\s]+\.txt"""),
                Regex("""https?://marvellaholdings\.sbs[^"'\s]+\.txt"""),
                Regex("""https?://vivonaengineering\.[a-z]+[^"'\s]+\.txt"""),
                Regex("""https?://travianastudios\.[a-z]+[^"'\s]+\.txt"""),
                Regex("""https?://luminairemotion\.[a-z]+[^"'\s]+\.txt"""),
                Regex("""https?://valenium\.shop[^"'\s]+\.txt""")
            )
            
            for (pattern in patterns) {
                val match = pattern.find(html)
                if (match != null) {
                    val videoUrl = match.value
                    Log.d(TAG, "🎯 HTML Regex capturou: $videoUrl")
                    emitExtractorLink(videoUrl, url, callback)
                    return true
                }
            }
            
            Log.d(TAG, "⚠️ HTML Regex: Nenhuma URL .txt encontrada")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ HTML Regex falhou: ${e.message}")
            false
        }
    }

    /**
     * ESTRATÉGIA 2: JsUnpacker
     * Descompacta JavaScript ofuscado
     */
    private suspend fun extractWithJsUnpacker(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/"
                )
            )
            
            val html = response.text
            
            // Procurar por código packed
            val packedRegex = Regex("""eval\s*\(\s*function\s*\(p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[rd]\s*\).+?\}\s*\(\s*(.+?)\s*\)\s*\)\s*;?""", RegexOption.DOT_MATCHES_ALL)
            val packedMatch = packedRegex.find(html)
            
            if (packedMatch != null) {
                Log.d(TAG, "📦 Código packed encontrado")
                val unpacked = JsUnpackerUtil.unpack(packedMatch.value)
                
                if (!unpacked.isNullOrEmpty()) {
                    Log.d(TAG, "🔓 Descompactado: ${unpacked.length} chars")
                    
                    // Buscar URLs no código descompactado
                    val urlRegex = Regex("""https?://[^"'\s]+\.txt""")
                    val urlMatch = urlRegex.find(unpacked)
                    
                    if (urlMatch != null) {
                        val videoUrl = urlMatch.value
                        Log.d(TAG, "🎯 JsUnpacker capturou: $videoUrl")
                        emitExtractorLink(videoUrl, url, callback)
                        return true
                    }
                }
            }
            
            Log.d(TAG, "⚠️ JsUnpacker: Nenhum código packed ou URL encontrada")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ JsUnpacker falhou: ${e.message}")
            false
        }
    }

    /**
     * ESTRATÉGIA 3: WebView JavaScript-Only (v126 - MELHORADO)
     * Executa JavaScript e captura URL via callback
     * Aguarda descriptografia e extração do vídeo
     */
    private suspend fun extractWithWebViewJavaScript(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.txt$"""),
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 1200; // 120s - v126: Aumentado para aguardar descriptografia
                            
                            // Tentar forçar play do vídeo
                            function tryPlay() {
                                try {
                                    var videos = document.querySelectorAll('video');
                                    for(var i=0; i<videos.length; i++) {
                                        if(videos[i].paused) {
                                            videos[i].muted = true;
                                            videos[i].play().catch(function(){});
                                        }
                                    }
                                } catch(e) {}
                            }
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                // Tentar play a cada 10 tentativas
                                if (attempts % 10 === 0) {
                                    tryPlay();
                                }
                                
                                var html = document.documentElement.innerHTML;
                                
                                // Padrão 1: cf-master.{timestamp}.txt
                                var cfMaster = html.match(/https?:\/\/[^"'\s]+\/cf-master\.[0-9]+\.txt/i);
                                if (cfMaster) {
                                    clearInterval(interval);
                                    console.log('Capturado cf-master:', cfMaster[0]);
                                    resolve(cfMaster[0]);
                                    return;
                                }
                                
                                // Padrão 2: index-f{quality}.txt
                                var indexF = html.match(/https?:\/\/[^"'\s]+\/index-f[0-9]+\.txt/i);
                                if (indexF) {
                                    clearInterval(interval);
                                    console.log('Capturado index-f:', indexF[0]);
                                    resolve(indexF[0]);
                                    return;
                                }
                                
                                // Padrão 3: .txt em /v4/
                                var v4Txt = html.match(/https?:\/\/[^"'\s]+\/v4\/[a-z0-9]+\/[a-z0-9]+\/[^"'\s]+\.txt/i);
                                if (v4Txt) {
                                    clearInterval(interval);
                                    console.log('Capturado v4:', v4Txt[0]);
                                    resolve(v4Txt[0]);
                                    return;
                                }
                                
                                // Padrão 4: Hosts conhecidos
                                var knownHost = html.match(/https?:\/\/(marvellaholdings\.sbs|vivonaengineering\.[a-z]+|travianastudios\.[a-z]+|luminairemotion\.[a-z]+|valenium\.shop)[^"'\s]+\.txt/i);
                                if (knownHost) {
                                    clearInterval(interval);
                                    console.log('Capturado host:', knownHost[0]);
                                    resolve(knownHost[0]);
                                    return;
                                }
                                
                                // Padrão 5: Variáveis globais
                                if (window.__PLAYER_CONFIG__ && window.__PLAYER_CONFIG__.url) {
                                    clearInterval(interval);
                                    resolve(window.__PLAYER_CONFIG__.url);
                                    return;
                                }
                                
                                if (window.playlistUrl) {
                                    clearInterval(interval);
                                    resolve(window.playlistUrl);
                                    return;
                                }
                                
                                // Padrão 6: Buscar em objetos do player (v126 NOVO)
                                try {
                                    var players = document.querySelectorAll('[class*="player"]');
                                    for(var i=0; i<players.length; i++) {
                                        var playerData = players[i].getAttribute('data-src') || 
                                                       players[i].getAttribute('data-url') ||
                                                       players[i].getAttribute('src');
                                        if(playerData && playerData.includes('.txt')) {
                                            clearInterval(interval);
                                            resolve(playerData);
                                            return;
                                        }
                                    }
                                } catch(e) {}
                                
                                // Timeout
                                if (attempts >= maxAttempts) {
                                    clearInterval(interval);
                                    console.log('Timeout apos', attempts, 'tentativas');
                                    resolve('');
                                }
                            }, 100);
                        });
                    })()
                """.trimIndent(),
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "📜 JS Callback capturou: $capturedUrl")
                    }
                },
                timeout = 120_000L // 120s - v126: Aumentado de 60s
            )
            
            app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/",
                    "Origin" to "https://megaembed.link",
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                interceptor = resolver
            )
            
            if (capturedUrl != null && isValidVideoUrl(capturedUrl)) {
                Log.d(TAG, "🎯 WebView JS capturou: $capturedUrl")
                emitExtractorLink(capturedUrl!!, url, callback)
                return true
            }
            
            Log.d(TAG, "⚠️ WebView JS: Nenhuma URL capturada")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ WebView JS falhou: ${e.message}")
            e.printStackTrace()
            false
        }
    }

    /**
     * ESTRATÉGIA 4: WebView com Interceptação
     * Intercepta requisições de rede (fallback final)
     */
    private suspend fun extractWithWebViewInterception(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            var capturedCdnUrl: String? = null
            var capturedPlaylistUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = Regex("""(?:https?://)?[^/]+/(?:v4/[a-z0-9]+/[a-z0-9]+|[^/]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+)/(?:cf-master|index-f|index-).*?\.txt"""),
                additionalUrls = listOf(
                    Regex("""/cf-master\.[0-9]+\.txt"""),
                    Regex("""/index-f[0-9]+\.txt"""),
                    Regex("""/index-[^/]+\.txt"""),
                    Regex("""\.txt(?:\?.*)?$"""),
                    Regex("""\.m3u8(?:\?.*)?$"""),
                    Regex("""marvellaholdings\.sbs.*?\.txt"""),
                    Regex("""vivonaengineering\.[a-z]+.*?\.txt"""),
                    Regex("""travianastudios\.[a-z]+.*?\.txt"""),
                    Regex("""luminairemotion\.[a-z]+.*?\.txt"""),
                    Regex("""valenium\.shop.*?\.txt""")
                ),
                script = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 600;
                            
                            var interval = setInterval(function() {
                                attempts++;
                                
                                var html = document.documentElement.innerHTML;
                                var txtMatch = html.match(/https?:\/\/[^"'\s]+\.txt/i);
                                
                                if (txtMatch) {
                                    clearInterval(interval);
                                    resolve(txtMatch[0]);
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
                        Log.d(TAG, "📜 Interceptação JS capturou: $capturedPlaylistUrl")
                    }
                },
                timeout = 60_000L
            )
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/",
                    "Origin" to "https://megaembed.link",
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                interceptor = resolver
            )
            
            capturedCdnUrl = response.url
            Log.d(TAG, "🔍 URL final do WebView: $capturedCdnUrl")
            
            val finalUrl = capturedPlaylistUrl ?: capturedCdnUrl
            
            if (isValidVideoUrl(finalUrl)) {
                Log.d(TAG, "🎯 WebView Interceptação capturou: $finalUrl")
                emitExtractorLink(finalUrl, url, callback)
                return true
            }
            
            Log.d(TAG, "⚠️ WebView Interceptação: URL não é válida")
            false
        } catch (e: Exception) {
            Log.e(TAG, "❌ WebView Interceptação falhou: ${e.message}")
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
        
        // Validação positiva
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("cf-master") ||
               url.contains("index-f") ||
               url.contains("index-") ||
               url.contains(".txt") ||
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
                        "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
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
                    this.referer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl
                    this.quality = Qualities.Unknown.value
                }
            )
        }
    }
}
