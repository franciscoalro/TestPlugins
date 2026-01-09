package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.Qualities
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

    // Extractor para DoodStream clones (myvidplay, bysebuho, g9r6)
    private suspend fun extractDoodStream(url: String, referer: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "🔍 DoodStream: $url")
            
            val embedUrl = url.replace("/d/", "/e/")
            val response = app.get(embedUrl, referer = referer)
            val html = response.text
            val host = getBaseUrl(response.url)
            
            // Extrair pass_md5 path
            val passMd5Path = Regex("""/pass_md5/[^']*""").find(html)?.value ?: return false
            val md5Url = host + passMd5Path
            
            Log.d("MaxSeries", "📡 pass_md5: $md5Url")
            
            // Obter URL base do vídeo
            val videoBase = app.get(md5Url, referer = embedUrl).text
            
            // Construir URL final
            val token = passMd5Path.substringAfterLast("/")
            val videoUrl = videoBase + createHashTable() + "?token=$token"
            
            Log.d("MaxSeries", "🎬 Video URL: $videoUrl")
            
            // Extrair qualidade do título
            val quality = Regex("""\d{3,4}p""")
                .find(html.substringAfter("<title>").substringBefore("</title>"))
                ?.value
            
            val sourceName = when {
                url.contains("myvidplay") -> "MyVidPlay"
                url.contains("bysebuho") -> "Bysebuho"
                url.contains("g9r6") -> "G9R6"
                else -> "DoodStream"
            }
            
            callback(
                ExtractorLink(
                    source = sourceName,
                    name = sourceName,
                    url = videoUrl,
                    referer = "$host/",
                    quality = getQualityFromName(quality),
                    isM3u8 = false
                )
            )
            
            return true
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ DoodStream erro: ${e.message}")
            return false
        }
    }
    
    // WebView Extractor para hosts difíceis (megaembed, playerembedapi)
    private suspend fun extractWithWebView(url: String, referer: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "🌐 WebView: $url")
            
            // Usar WebViewResolver para interceptar URLs de vídeo
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|index\.m3u8"""),
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4"""),
                    Regex("""cloudatacdn"""),
                    Regex("""/video/"""),
                    Regex("""/stream/""")
                ),
                useOkhttp = false,
                timeout = 20_000L
            )
            
            val response = app.get(url, referer = referer, interceptor = resolver)
            val interceptedUrl = response.url
            
            if (interceptedUrl.isNotEmpty() && (interceptedUrl.contains(".m3u8") || interceptedUrl.contains(".mp4"))) {
                Log.d("MaxSeries", "🎬 WebView interceptou: $interceptedUrl")
                
                val isM3u8 = interceptedUrl.contains(".m3u8")
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    else -> "WebView"
                }
                
                if (isM3u8) {
                    M3u8Helper.generateM3u8(
                        sourceName,
                        interceptedUrl,
                        url
                    ).forEach(callback)
                } else {
                    callback(
                        ExtractorLink(
                            source = sourceName,
                            name = sourceName,
                            url = interceptedUrl,
                            referer = url,
                            quality = Qualities.Unknown.value,
                            isM3u8 = false
                        )
                    )
                }
                
                return true
            }
            
            return false
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ WebView erro: ${e.message}")
            return false
        }
    }
    
    // Extractor genérico
    private suspend fun extractVideo(
        url: String, 
        referer: String, 
        subtitleCallback: (SubtitleFile) -> Unit, 
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🎯 Extraindo: $url")
        
        // 1. DoodStream clones (prioridade - funcionam melhor)
        if (isDoodStreamClone(url)) {
            if (extractDoodStream(url, referer, callback)) return true
        }
        
        // 2. Extractor padrão do CloudStream
        try {
            if (loadExtractor(url, referer, subtitleCallback, callback)) return true
        } catch (e: Exception) {
            Log.d("MaxSeries", "⚠️ Extractor padrão falhou: ${e.message}")
        }
        
        // 3. WebView para hosts difíceis
        if (isHardHost(url)) {
            if (extractWithWebView(url, referer, callback)) return true
        }
        
        return false
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
    
    private val hardHosts = listOf(
        "megaembed.link", "playerembedapi.link", "embedsito.com"
    )
    
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
            Log.d("MaxSeries", "🎬 loadLinks: $data")
            
            val playerUrls = mutableListOf<String>()
            
            if (data.contains("#") && data.contains("playerthree")) {
                val epId = Regex("#\\d+_(\\d+)").find(data)?.groupValues?.get(1) ?: return false
                Log.d("MaxSeries", "📺 Episódio: $epId")
                
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
            
            Log.d("MaxSeries", "🔗 Players: ${playerUrls.size}")
            
            // Ordenar: DoodStream primeiro
            val sortedUrls = playerUrls.sortedByDescending { isDoodStreamClone(it) }
            
            for (playerUrl in sortedUrls) {
                if (extractVideo(playerUrl, data, subtitleCallback, callback)) found++
            }
            
            Log.d("MaxSeries", "✅ Links: $found")
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro: ${e.message}")
        }
        
        return found > 0
    }
}
