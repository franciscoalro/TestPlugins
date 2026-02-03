/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * MAXSERIES PROVIDER - Versão Final Otimizada
 * Integração PlayerEmbedAPI com Extração Ultra-Rápida (~250ms)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Técnicas de Extração (ordem de prioridade):
 * 1. HTTP Direto Otimizado (~200-300ms) - Regex direto, sem parsing complexo
 * 2. Construção de URL CDN (~100ms) - A partir dos dados extraídos
 * 3. WebView Fallback (~10-15s) - Quando HTTP falha
 * 
 * Otimizações:
 * - Keep-Alive connections
 * - Regex pré-compiladas
 * - Timeout agressivo (5s para HTTP, 30s para WebView)
 * - Sem parsing complexo (BeautifulSoup)
 * - Headers otimizados
 */

package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.regex.Pattern

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    // Timeout otimizado - rápido para não bloquear UI
    private val HTTP_TIMEOUT = 5000L  // 5 segundos para HTTP
    private val WEBVIEW_TIMEOUT = 30000L  // 30 segundos para WebView

    // Regex pré-compiladas para máxima velocidade
    private val RE_DATAS = Pattern.compile("""const\s+datas\s*=\s*"([^"]+)""")
    private val RE_SLUG = Pattern.compile(""""slug":"([^"]+)""")
    private val RE_MD5 = Pattern.compile(""""md5_id":(\d+)""")
    private val RE_USER = Pattern.compile(""""user_id":(\d+)""")

    override val mainPage = mainPageOf(
        "$mainUrl/" to "Home",
        "$mainUrl/series/" to "Series",
        "$mainUrl/filmes/" to "Filmes"
    )

    // ═══════════════════════════════════════════════════════════════════════════
    // MAIN PAGE & SEARCH
    // ═══════════════════════════════════════════════════════════════════════════

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        val url = if (page > 1) {
            if (request.data.endsWith("/")) "${request.data}page/$page/" else "${request.data}/page/$page/"
        } else { request.data }
        
        val doc = app.get(url).document
        val home = doc.select("article.item").mapNotNull {
            val title = it.selectFirst(".data h3 a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".data h3 a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".poster img")?.attr("src")
            if (href.contains("/series/")) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) { this.posterUrl = image }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) { this.posterUrl = image }
            }
        }
        return newHomePageResponse(request.name, home)
    }

    override suspend fun search(query: String): List<SearchResponse> {
        val doc = app.get("$mainUrl/?s=$query").document
        return doc.select(".result-item").mapNotNull {
            val title = it.selectFirst(".details .title a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".details .title a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".image img")?.attr("src")
            if (href.contains("/series/")) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) { this.posterUrl = image }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) { this.posterUrl = image }
            }
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        val doc = app.get(url).document
        val title = doc.selectFirst(".data h1")?.text() ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        val bg = doc.selectFirst(".backdrop img")?.attr("src")
        
        if (url.contains("/series/")) {
            val episodes = mutableListOf<Episode>()
            val iframe = doc.selectFirst("iframe")?.attr("src")
            if (!iframe.isNullOrEmpty()) {
                val iframeSrc = if (iframe.startsWith("//")) "https:$iframe" else iframe
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    iframeDoc.select("li[data-episode-id] a").forEachIndexed { i, ep ->
                        val href = ep.attr("href")
                        if (href.isNotEmpty()) {
                            val epUrl = if (href.startsWith("#")) "$iframeSrc$href" else href
                            episodes.add(newEpisode(epUrl) { name = "Ep ${i+1}"; episode = i+1; season = 1 })
                        }
                    }
                } catch (_: Exception) {}
            }
            if (episodes.isEmpty()) episodes.add(newEpisode(url) { name = "Ep 1"; episode = 1; season = 1 })
            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster; this.plot = desc; this.backgroundPosterUrl = bg
            }
        } else {
            return newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster; this.plot = desc; this.backgroundPosterUrl = bg
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // LOAD LINKS - EXTRAÇÃO PRINCIPAL
    // ═══════════════════════════════════════════════════════════════════════════

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var found = 0
        
        try {
            val playerUrls = mutableListOf<String>()
            
            // Obter URLs dos players
            if (data.contains("#") && data.contains("playerthree")) {
                val epId = Regex("#\\d+_(\\d+)").find(data)?.groupValues?.get(1) ?: return false
                
                val ajax = app.get(
                    "https://playerthree.online/episodio/$epId",
                    headers = mapOf("Referer" to data, "X-Requested-With" to "XMLHttpRequest")
                )
                
                if (ajax.isSuccessful) {
                    ajax.document.select("button[data-source]").forEach { btn ->
                        val src = btn.attr("data-source")
                        if (src.startsWith("http") && !src.contains("youtube", true)) {
                            playerUrls.add(src)
                        }
                    }
                }
            } else {
                val doc = app.get(data).document
                val iframe = doc.selectFirst("iframe")?.attr("src")
                if (!iframe.isNullOrEmpty()) {
                    playerUrls.add(if (iframe.startsWith("//")) "https:$iframe" else iframe)
                }
            }
            
            Log.d("MaxSeries", "Players encontrados: ${playerUrls.size}")
            
            // Processar cada player
            for (playerUrl in playerUrls) {
                Log.d("MaxSeries", "Processando: $playerUrl")
                
                when {
                    // PlayerEmbedAPI - Prioridade máxima
                    playerUrl.contains("playerembedapi") -> {
                        if (extractPlayerEmbedAPI(playerUrl, callback)) {
                            found++
                            continue
                        }
                    }
                    
                    // DoodStream clones - HTTP puro
                    isDoodStreamClone(playerUrl) -> {
                        if (extractDoodStream(playerUrl, callback)) {
                            found++
                            continue
                        }
                    }
                    
                    // Extractor padrão do CloudStream
                    else -> {
                        try {
                            if (loadExtractor(playerUrl, data, subtitleCallback, callback)) {
                                found++
                                continue
                            }
                        } catch (_: Exception) {}
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "Erro: ${e.message}")
        }
        
        return found > 0
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // PLAYEREMBEDAPI EXTRACTOR - ULTRA FAST
    // ═══════════════════════════════════════════════════════════════════════════

    private suspend fun extractPlayerEmbedAPI(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean = withContext(Dispatchers.IO) {
        val startTime = System.currentTimeMillis()
        
        try {
            Log.d("MaxSeries", "[PlayerEmbedAPI] Iniciando extração: $url")
            
            // ═══════════════════════════════════════════════════════════════════
            // TÉCNICA 1: HTTP Direto Otimizado (~200-300ms)
            // ═══════════════════════════════════════════════════════════════════
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
                    "Accept-Encoding" to "gzip, deflate",
                    "DNT" to "1",
                    "Connection" to "keep-alive",
                ),
                timeout = HTTP_TIMEOUT.toInt()
            )
            
            val html = response.text
            val downloadTime = System.currentTimeMillis() - startTime
            Log.d("MaxSeries", "[PlayerEmbedAPI] Download: ${downloadTime}ms")
            
            // Extrair campo datas com regex pré-compilada
            val datasMatcher = RE_DATAS.matcher(html)
            if (!datasMatcher.find()) {
                Log.e("MaxSeries", "[PlayerEmbedAPI] Campo datas não encontrado")
                return@withContext false
            }
            
            val datasB64 = datasMatcher.group(1)
            
            // Decodificar base64
            val decoded = try {
                val padded = if (datasB64.length % 4 != 0) {
                    datasB64 + "=".repeat(4 - datasB64.length % 4)
                } else datasB64
                android.util.Base64.decode(padded, android.util.Base64.DEFAULT)
            } catch (e: Exception) {
                Log.e("MaxSeries", "[PlayerEmbedAPI] Erro decode base64: ${e.message}")
                return@withContext false
            }
            
            val decodedStr = String(decoded, Charsets.UTF_8)
            
            // Extrair campos com regex pré-compiladas
            val slugMatcher = RE_SLUG.matcher(decodedStr)
            val md5Matcher = RE_MD5.matcher(decodedStr)
            
            if (!slugMatcher.find() || !md5Matcher.find()) {
                Log.e("MaxSeries", "[PlayerEmbedAPI] Slug ou MD5 não encontrado")
                return@withContext false
            }
            
            val slug = slugMatcher.group(1)
            val md5Id = md5Matcher.group(1)
            
            Log.d("MaxSeries", "[PlayerEmbedAPI] Dados: slug=$slug, md5_id=$md5Id")
            
            // Construir URLs CDN
            val cdnUrls = listOf(
                "https://${slug}.sssrr.org/sora/${md5Id}/",
                "https://cdn.sssrr.org/sora/${md5Id}/"
            )
            
            val processingTime = System.currentTimeMillis() - startTime
            Log.d("MaxSeries", "[PlayerEmbedAPI] Processamento: ${processingTime}ms")
            
            // ═══════════════════════════════════════════════════════════════════
            // TÉCNICA 2: Tentar CDN direto
            // ═══════════════════════════════════════════════════════════════════
            
            for (cdnUrl in cdnUrls) {
                try {
                    Log.d("MaxSeries", "[PlayerEmbedAPI] Testando CDN: $cdnUrl")
                    
                    val cdnResponse = app.head(
                        cdnUrl,
                        headers = mapOf(
                            "Referer" to url,
                            "Origin" to "https://playerembedapi.link"
                        ),
                        timeout = 10
                    )
                    
                    if (cdnResponse.isSuccessful) {
                        Log.d("MaxSeries", "[PlayerEmbedAPI] CDN válido: $cdnUrl")
                        
                        callback(
                            newExtractorLink(
                                "PlayerEmbedAPI",
                                "PlayerEmbedAPI - HD",
                                cdnUrl
                            ) {
                                this.referer = url
                                this.quality = Qualities.Unknown.value
                            }
                        )
                        
                        Log.d("MaxSeries", "[PlayerEmbedAPI] ✅ Extração completa em ${System.currentTimeMillis() - startTime}ms")
                        return@withContext true
                    }
                } catch (e: Exception) {
                    Log.w("MaxSeries", "[PlayerEmbedAPI] CDN falhou: ${e.message}")
                }
            }
            
            // ═══════════════════════════════════════════════════════════════════
            // TÉCNICA 3: WebView Fallback (~10-15s)
            // ═══════════════════════════════════════════════════════════════════
            
            Log.d("MaxSeries", "[PlayerEmbedAPI] Usando WebView fallback...")
            
            val webViewResult = extractWithWebView(url, callback)
            if (webViewResult) {
                Log.d("MaxSeries", "[PlayerEmbedAPI] ✅ WebView sucesso")
                return@withContext true
            }
            
            Log.e("MaxSeries", "[PlayerEmbedAPI] ❌ Todas as técnicas falharam")
            false
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "[PlayerEmbedAPI] Erro: ${e.message}")
            false
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // WEBVIEW FALLBACK
    // ═══════════════════════════════════════════════════════════════════════════

    private suspend fun extractWithWebView(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val script = """
                (function() {
                    return new Promise(function(resolve) {
                        setTimeout(function() {
                            var result = '';
                            
                            // JWPlayer
                            if (window.jwplayer) {
                                try {
                                    var jw = jwplayer();
                                    if (jw && jw.getPlaylist) {
                                        var playlist = jw.getPlaylist();
                                        if (playlist && playlist[0] && playlist[0].file) {
                                            result = playlist[0].file;
                                        }
                                    }
                                } catch(e) {}
                            }
                            
                            // Video element
                            if (!result) {
                                var video = document.querySelector('video');
                                if (video && video.src) result = video.src;
                            }
                            
                            resolve(result);
                        }, 3000);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = Regex("""(?i)(sssrr\.org|\.m3u8|\.mp4|/video/)"""),
                useOkhttp = false,
                script = script,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result.startsWith("http")) {
                        capturedUrl = result
                    }
                },
                timeout = WEBVIEW_TIMEOUT
            )
            
            val response = app.get(url, interceptor = resolver)
            
            val videoUrl = when {
                response.url.contains(".m3u8") || response.url.contains(".mp4") -> response.url
                !capturedUrl.isNullOrEmpty() -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8("PlayerEmbedAPI", videoUrl, url).forEach(callback)
                } else {
                    callback(
                        newExtractorLink("PlayerEmbedAPI", "PlayerEmbedAPI", videoUrl) {
                            this.referer = url
                            this.quality = Qualities.Unknown.value
                        }
                    )
                }
                true
            } else {
                false
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "[WebView] Erro: ${e.message}")
            false
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // DOODSTREAM EXTRACTOR
    // ═══════════════════════════════════════════════════════════════════════════

    private suspend fun extractDoodStream(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        return try {
            Log.d("MaxSeries", "[DoodStream] Extraindo: $url")
            
            val embedUrl = url.replace("/d/", "/e/")
            val req = app.get(embedUrl)
            val host = getBaseUrl(req.url)
            val html = req.text
            
            val md5Path = Regex("""/pass_md5/[^'"\s]+""").find(html)?.value ?: return false
            val md5Url = host + md5Path
            
            val baseUrl = app.get(md5Url, referer = req.url).text.trim()
            if (baseUrl.isEmpty() || !baseUrl.startsWith("http")) return false
            
            val token = md5Path.substringAfterLast("/")
            val expiry = System.currentTimeMillis()
            val trueUrl = "$baseUrl${createHashTable()}?token=$token&expiry=$expiry"
            
            val quality = Regex("""\d{3,4}p""").find(html)?.value
            
            callback(
                newExtractorLink(
                    getDoodName(url),
                    "${getDoodName(url)} - ${quality ?: "HD"}",
                    trueUrl
                ) {
                    this.referer = "$host/"
                    this.quality = getQualityFromName(quality)
                }
            )
            
            true
        } catch (e: Exception) {
            Log.e("MaxSeries", "[DoodStream] Erro: ${e.message}")
            false
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // HELPERS
    // ═══════════════════════════════════════════════════════════════════════════

    private fun isDoodStreamClone(url: String): Boolean {
        val domains = listOf(
            "myvidplay.com", "bysebuho.com", "g9r6.com", "doodstream.com",
            "dood.to", "dood.watch", "dood.pm", "dood.wf", "dood.re",
            "dood.so", "dood.cx", "dood.la", "dood.ws", "dood.sh",
            "doodstream.co", "d0000d.com", "d000d.com", "dooood.com", "ds2play.com"
        )
        return domains.any { url.contains(it, true) }
    }

    private fun getDoodName(url: String): String {
        return when {
            url.contains("myvidplay") -> "MyVidPlay"
            url.contains("bysebuho") -> "Bysebuho"
            url.contains("g9r6") -> "G9R6"
            else -> "DoodStream"
        }
    }

    private fun getBaseUrl(url: String): String {
        return Regex("""^(https?://[^/]+)""").find(url)?.value ?: url
    }

    private fun createHashTable(): String {
        val alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return buildString { repeat(10) { append(alphabet.random()) } }
    }

    private fun getQualityFromName(name: String?): Int {
        return when {
            name.isNullOrEmpty() -> Qualities.Unknown.value
            name.contains("1080", true) -> Qualities.P1080.value
            name.contains("720", true) -> Qualities.P720.value
            name.contains("480", true) -> Qualities.P480.value
            name.contains("360", true) -> Qualities.P360.value
            else -> Qualities.Unknown.value
        }
    }
}
