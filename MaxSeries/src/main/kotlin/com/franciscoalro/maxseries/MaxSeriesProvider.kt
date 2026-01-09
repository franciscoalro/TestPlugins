package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override val mainPage = mainPageOf(
        "$mainUrl/" to "Home",
        "$mainUrl/series/" to "Series",
        "$mainUrl/filmes/" to "Filmes"
    )

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

    // ==================== EXTRACTORS ====================

    // DoodStream Extractor (igual ao oficial do CloudStream)
    private suspend fun extractDoodStream(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            val embedUrl = url.replace("/d/", "/e/")
            val req = app.get(embedUrl)
            val host = getBaseUrl(req.url)
            val html = req.text
            
            val md5Path = Regex("/pass_md5/[^']*").find(html)?.value ?: return false
            val md5Url = host + md5Path
            
            val trueUrl = app.get(md5Url, referer = req.url).text + 
                          createHashTable() + 
                          "?token=" + md5Path.substringAfterLast("/")
            
            val quality = Regex("\\d{3,4}p")
                .find(html.substringAfter("<title>").substringBefore("</title>"))
                ?.value
            
            val sourceName = when {
                url.contains("myvidplay") -> "MyVidPlay"
                url.contains("bysebuho") -> "Bysebuho"
                url.contains("g9r6") -> "G9R6"
                else -> "DoodStream"
            }
            
            callback(
                newExtractorLink(
                    sourceName,
                    sourceName,
                    trueUrl,
                ) {
                    this.referer = "$host/"
                    this.quality = getQualityFromName(quality)
                }
            )
            
            return true
        } catch (e: Exception) {
            Log.e("MaxSeries", "DoodStream erro: ${e.message}")
            return false
        }
    }
    
    // StreamWish-like Extractor (usa JsUnpacker)
    private suspend fun extractWithUnpack(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            val response = app.get(url)
            val html = response.text
            
            // Tentar desempacotar JavaScript P.A.C.K.E.R.
            val packed = getPacked(html)
            val unpacked = if (!packed.isNullOrEmpty()) {
                JsUnpacker(packed).unpack()
            } else {
                html
            }
            
            if (unpacked == null) return false
            
            // Procurar URL do vídeo
            val videoUrl = Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']""").find(unpacked)?.groupValues?.get(1)
                ?: Regex("""sources:\s*\[\s*\{\s*file:\s*["']([^"']+)["']""").find(unpacked)?.groupValues?.get(1)
                ?: Regex("""source:\s*["']([^"']+\.m3u8[^"']*)["']""").find(unpacked)?.groupValues?.get(1)
            
            if (videoUrl != null) {
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    else -> "Unpacked"
                }
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(
                        sourceName,
                        videoUrl,
                        url
                    ).forEach(callback)
                } else {
                    callback(
                        newExtractorLink(sourceName, sourceName, videoUrl) {
                            this.referer = url
                            this.quality = Qualities.Unknown.value
                        }
                    )
                }
                return true
            }
            
            return false
        } catch (e: Exception) {
            Log.e("MaxSeries", "Unpack erro: ${e.message}")
            return false
        }
    }
    
    // WebView Extractor (fallback final) - com script que simula clique e captura vídeo
    private suspend fun extractWithWebView(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "WebView: $url")
            
            // Script JS avançado que:
            // 1. Tenta clicar automaticamente no botão de play
            // 2. Espera o vídeo carregar
            // 3. Captura a URL do elemento video
            val captureScript = """
                (function() {
                    // Função para capturar URL do vídeo
                    function getVideoUrl() {
                        var video = document.querySelector('video');
                        if (video) {
                            if (video.src && video.src.length > 10) return video.src;
                            if (video.currentSrc && video.currentSrc.length > 10) return video.currentSrc;
                        }
                        var source = document.querySelector('video source');
                        if (source && source.src) return source.src;
                        
                        // Tentar jwplayer
                        if (typeof jwplayer !== 'undefined' && jwplayer().getPlaylistItem) {
                            var item = jwplayer().getPlaylistItem();
                            if (item && item.file) return item.file;
                        }
                        
                        // Tentar Plyr
                        if (typeof Plyr !== 'undefined') {
                            var plyr = document.querySelector('.plyr');
                            if (plyr && plyr.plyr && plyr.plyr.source) return plyr.plyr.source;
                        }
                        
                        return '';
                    }
                    
                    // Tentar clicar em botões de play
                    var playButtons = document.querySelectorAll('[class*="play"], .play-btn, .btn-play, button[aria-label*="play"], .vjs-big-play-button');
                    playButtons.forEach(function(btn) {
                        try { btn.click(); } catch(e) {}
                    });
                    
                    // Tentar clicar no centro do player
                    var player = document.querySelector('.player, .video-container, .embed-responsive, #player');
                    if (player) {
                        try {
                            var event = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                            player.dispatchEvent(event);
                        } catch(e) {}
                    }
                    
                    // Retornar URL se já disponível
                    return getVideoUrl();
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                // Interceptar URLs de vídeo incluindo Google Storage
                interceptUrl = Regex("""\\.m3u8|\\.mp4|storage\\.googleapis\\.com|master\\.txt|/hls/|/video/|googlevideo|akamaized"""),
                additionalUrls = listOf(Regex("""\\.m3u8|\\.mp4|\\.ts|storage\\.googleapis""")),
                useOkhttp = false,  // IMPORTANTE: false para bypass Cloudflare
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result.length > 10) {
                        capturedUrl = result.trim('"')
                        Log.d("MaxSeries", "Script capturou: $capturedUrl")
                    }
                },
                timeout = 30_000L  // Aumentar timeout para dar tempo ao JS
            )
            
            val response = app.get(url, interceptor = resolver)
            val interceptedUrl = response.url
            
            Log.d("MaxSeries", "URL interceptada: $interceptedUrl")
            
            // Usar URL interceptada ou capturada pelo script
            val videoUrl = when {
                interceptedUrl.contains(".m3u8") || interceptedUrl.contains(".mp4") || interceptedUrl.contains("storage.googleapis.com") -> interceptedUrl
                !capturedUrl.isNullOrEmpty() && (capturedUrl!!.contains(".m3u8") || capturedUrl!!.contains(".mp4") || capturedUrl!!.contains("storage.googleapis.com")) -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d("MaxSeries", "Vídeo encontrado: $videoUrl")
                
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    videoUrl.contains("googleapis") -> "GoogleStorage"
                    else -> "WebView"
                }
                
                // Extrair qualidade da URL se disponível
                val quality = Regex("(\\d{3,4})p").find(videoUrl)?.groupValues?.get(1)?.toIntOrNull()
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(sourceName, videoUrl, url).forEach(callback)
                } else {
                    callback(
                        newExtractorLink(sourceName, sourceName, videoUrl) {
                            this.referer = url
                            this.quality = quality ?: Qualities.Unknown.value
                        }
                    )
                }
                return true
            }
            
            return false
        } catch (e: Exception) {
            Log.e("MaxSeries", "WebView erro: ${e.message}")
            return false
        }
    }
    
    // Helpers
    private fun createHashTable(): String {
        val alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return buildString { repeat(10) { append(alphabet.random()) } }
    }
    
    private fun getBaseUrl(url: String): String {
        return Regex("""^(https?://[^/]+)""").find(url)?.value ?: url
    }
    

    
    private val doodStreamDomains = listOf(
        "myvidplay.com", "bysebuho.com", "g9r6.com",
        "doodstream.com", "dood.to", "dood.watch", "dood.pm",
        "dood.wf", "dood.re", "dood.so", "dood.cx",
        "dood.la", "dood.ws", "dood.sh", "doodstream.co",
        "d0000d.com", "d000d.com", "dooood.com", "ds2play.com"
    )
    
    private val hardHosts = listOf("megaembed.link", "playerembedapi.link")
    
    private fun isDoodStreamClone(url: String) = doodStreamDomains.any { url.contains(it, true) }
    private fun isHardHost(url: String) = hardHosts.any { url.contains(it, true) }

    // ==================== LOAD LINKS ====================

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var found = 0
        
        try {
            val playerUrls = mutableListOf<String>()
            
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
            
            // Ordenar: DoodStream primeiro (mais confiável)
            val sortedUrls = playerUrls.sortedByDescending { isDoodStreamClone(it) }
            
            for (playerUrl in sortedUrls) {
                Log.d("MaxSeries", "Processando: $playerUrl")
                
                // 1. DoodStream clones
                if (isDoodStreamClone(playerUrl)) {
                    if (extractDoodStream(playerUrl, callback)) { found++; continue }
                }
                
                // 2. Extractor padrão do CloudStream
                try {
                    if (loadExtractor(playerUrl, data, subtitleCallback, callback)) { found++; continue }
                } catch (_: Exception) {}
                
                // 3. Tentar desempacotar JavaScript
                if (extractWithUnpack(playerUrl, callback)) { found++; continue }
                
                // 4. WebView como fallback
                if (isHardHost(playerUrl)) {
                    if (extractWithWebView(playerUrl, callback)) { found++; continue }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "Erro: ${e.message}")
        }
        
        return found > 0
    }
}
