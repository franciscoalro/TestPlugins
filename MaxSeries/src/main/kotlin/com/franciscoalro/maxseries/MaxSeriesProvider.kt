package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import com.lagradost.cloudstream3.utils.getQualityFromName
import com.lagradost.cloudstream3.utils.newExtractorLink
import android.util.Log
import org.jsoup.nodes.Element

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override val mainPage = mainPageOf(
        "$mainUrl/" to "Home",
        "$mainUrl/series/" to "Séries",
        "$mainUrl/filmes/" to "Filmes"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        val url = if (page > 1) {
            if (request.data.endsWith("/")) "${request.data}page/$page/" else "${request.data}/page/$page/"
        } else {
            request.data
        }
        val doc = app.get(url).document
        val home = doc.select("article.item").mapNotNull {
            val title = it.selectFirst(".data h3 a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".data h3 a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".poster img")?.attr("src")
            val isSeries = href.contains("/series/")
            
            if (isSeries) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) {
                    this.posterUrl = image
                }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) {
                    this.posterUrl = image
                }
            }
        }
        return newHomePageResponse(request.name, home)
    }

    override suspend fun search(query: String): List<SearchResponse> {
        val url = "$mainUrl/?s=$query"
        val doc = app.get(url).document
        return doc.select(".result-item").mapNotNull {
            val title = it.selectFirst(".details .title a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".details .title a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".image img")?.attr("src")
            val typeText = it.selectFirst(".image span")?.text() ?: ""
            val type = if (typeText.contains("TV", true) || href.contains("/series/")) TvType.TvSeries else TvType.Movie

            if (type == TvType.TvSeries) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) {
                    this.posterUrl = image
                }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) {
                    this.posterUrl = image
                }
            }
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        val doc = app.get(url).document
        val title = doc.selectFirst(".data h1")?.text() 
            ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text() 
            ?: doc.selectFirst(".entry-content")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        val bg = doc.selectFirst(".backdrop img")?.attr("src")
        
        val isSeries = url.contains("/series/")

        if (isSeries) {
            val episodes = mutableListOf<Episode>()
            
            // MaxSeries loads episodes inside an iframe (playerthree.online)
            val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                ?: doc.selectFirst("iframe[src*=playerthree]")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                Log.d("MaxSeries", "📺 Carregando episódios do iframe: $iframeSrc")
                
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Extract episodes from the iframe
                    iframeDoc.select("a.episodio").forEachIndexed { index, ep ->
                        val epTitle = ep.text().trim()
                        val epId = ep.attr("data-id")
                        
                        // The episode URL is the series URL (we'll handle player selection in loadLinks)
                        // We store the episode ID in the data field for later use
                        val epData = "$url|$epId"
                        
                        // Try to extract season/episode numbers from title
                        val seasonEpMatch = Regex("(\\d+)\\s*-\\s*(\\d+)").find(epTitle)
                        val seasonNum = seasonEpMatch?.groupValues?.get(1)?.toIntOrNull() ?: 1
                        val epNum = seasonEpMatch?.groupValues?.get(2)?.toIntOrNull() ?: (index + 1)
                        
                        episodes.add(newEpisode(epData) {
                            this.name = epTitle
                            this.episode = epNum
                            this.season = seasonNum
                        })
                    }
                    
                    Log.d("MaxSeries", "✅ Encontrados ${episodes.size} episódios para $title")
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar episódios do iframe: ${e.message}")
                }
            }
            
            // Fallback: Try to extract from main page (old method)
            if (episodes.isEmpty()) {
                Log.w("MaxSeries", "⚠️ Tentando método antigo de extração de episódios")
                
                // Standard DooPlay episode extraction
                doc.select("ul.episodios li").forEach { ep ->
                    val epA = ep.selectFirst("a") ?: return@forEach
                    val epTitle = epA.text().ifEmpty { ep.selectFirst(".episodiotiitle")?.text() ?: "Episódio" }
                    val epHref = epA.attr("href")
                    
                    // Try to extract season/episode from structure or title
                    val seasonNum = ep.parents().select(".se-c").attr("id").replace("season-", "").toIntOrNull() 
                        ?: ep.parents().select("div[id^=season-]").attr("id").replace("season-", "").toIntOrNull()
                        ?: 1
                    
                    val epNum = ep.selectFirst(".numerando")?.text()?.split("-")?.lastOrNull()?.trim()?.toIntOrNull()
                        ?: epTitle.replace(Regex(".*?(\\d+).*"), "$1").toIntOrNull()

                    episodes.add(newEpisode(epHref) {
                        this.name = epTitle
                        this.episode = epNum
                        this.season = seasonNum
                    })
                }

                // Fallback for different DooPlay structures
                if (episodes.isEmpty()) {
                    doc.select("div.se-c").forEach { sDiv ->
                        val sNum = sDiv.attr("id").replace("season-", "").toIntOrNull() ?: 1
                        sDiv.select("ul.list-episodes li a, ul.episodios li a").forEach { ep ->
                            val epTitle = ep.text()
                            val epHref = ep.attr("href")
                            val epNum = ep.selectFirst(".numerando")?.text()?.split("-")?.lastOrNull()?.trim()?.toIntOrNull()
                            
                            episodes.add(newEpisode(epHref) {
                                this.name = epTitle
                                this.episode = epNum
                                this.season = sNum
                            })
                        }
                    }
                }
            }
            
            if (episodes.isEmpty()) {
                Log.w("MaxSeries", "⚠️ Nenhum episódio encontrado para $title - pode estar 'Em breve'")
            }

            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster
                this.plot = desc
                this.backgroundPosterUrl = bg
            }
        } else {
            return newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster
                this.plot = desc
                this.backgroundPosterUrl = bg
            }
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🔍 loadLinks chamado para: $data")
        
        // Check if data contains episode ID (format: url|episodeId)
        val (pageUrl, episodeId) = if (data.contains("|")) {
            val parts = data.split("|")
            Pair(parts[0], parts.getOrNull(1))
        } else {
            Pair(data, null)
        }
        
        val doc = app.get(pageUrl).document
        var linksFound = 0
        
        // Step 1: Try multiple iframe selectors for MaxSeries
        val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
            ?: doc.selectFirst("iframe[src*=playerthree]")?.attr("src")
            ?: doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
            ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
            ?: doc.selectFirst("div.player iframe")?.attr("src")
            ?: doc.selectFirst("#player iframe")?.attr("src")
            ?: doc.selectFirst(".video-player iframe")?.attr("src")
        
        if (mainIframe.isNullOrEmpty()) {
            Log.e("MaxSeries", "❌ Nenhum iframe principal encontrado em $pageUrl")
            
            // Fallback: Try to find direct video links in the page
            return tryDirectVideoExtraction(doc, pageUrl, subtitleCallback, callback)
        }
        
        val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
        Log.d("MaxSeries", "📺 Iframe principal encontrado: $iframeSrc")
        
        // Step 2: Navigate to the iframe and extract player buttons
        try {
            val iframeUrl = if (episodeId != null) {
                "$iframeSrc?ep=$episodeId"
            } else {
                iframeSrc
            }
            
            Log.d("MaxSeries", "🎬 Acessando: $iframeUrl")
            val iframeDoc = app.get(iframeUrl, headers = mapOf(
                "Referer" to pageUrl,
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )).document
            
            // Step 3: Look for multiple types of player buttons and links
            val playerSelectors = listOf(
                "button.btn[data-source]",
                "button[data-url]",
                "a.player-option[data-src]",
                ".server-item[data-video]",
                "li[data-video]",
                "button[onclick*='http']",
                "a[href*='embed']"
            )
            
            playerSelectors.forEach { selector ->
                iframeDoc.select(selector).forEach { element ->
                    val playerName = element.text().trim().ifEmpty { "Player" }
                    val videoLink = element.attr("data-source")
                        .ifEmpty { element.attr("data-url") }
                        .ifEmpty { element.attr("data-src") }
                        .ifEmpty { element.attr("data-video") }
                        .ifEmpty { element.attr("href") }
                        .ifEmpty { 
                            // Extract from onclick attribute
                            val onclick = element.attr("onclick")
                            Regex("""['"]([^'"]*(?:embed|player|stream)[^'"]*)['"]""").find(onclick)?.groupValues?.get(1) ?: ""
                        }
                    
                    if (videoLink.isNotEmpty()) {
                        linksFound += processVideoLink(videoLink, playerName, iframeUrl, pageUrl, subtitleCallback, callback)
                    }
                }
            }
            
            // Step 4: Look for embedded video sources in script tags
            if (linksFound == 0) {
                linksFound += extractFromScripts(iframeDoc, iframeUrl, pageUrl, subtitleCallback, callback)
            }
            
            // Step 5: Fallback - look for nested iframes
            if (linksFound == 0) {
                iframeDoc.select("iframe").forEach { iframe ->
                    val src = iframe.attr("src").ifEmpty { iframe.attr("data-src") }
                    if (src.isNotEmpty() && isValidVideoSource(src)) {
                        val fixedSrc = if (src.startsWith("//")) "https:$src" else src
                        try {
                            Log.d("MaxSeries", "🔄 Tentando iframe aninhado: $fixedSrc")
                            if (loadExtractor(fixedSrc, iframeUrl, subtitleCallback, callback)) {
                                linksFound++
                            }
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao carregar iframe aninhado: ${e.message}")
                        }
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao acessar iframe $iframeSrc: ${e.message}")
        }
        
        if (linksFound == 0) {
            Log.w("MaxSeries", "⚠️ Nenhum link de vídeo encontrado para $data")
        } else {
            Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        }
        
        return linksFound > 0
    }
    
    private suspend fun processVideoLink(
        videoLink: String,
        playerName: String,
        iframeUrl: String,
        pageUrl: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var fixedLink = if (videoLink.startsWith("//")) "https:$videoLink" else videoLink
        
        // Block YouTube trailers and ads
        if (isBlockedSource(fixedLink)) {
            Log.w("MaxSeries", "⚠️ Bloqueando fonte indesejada: $fixedLink")
            return 0
        }
        
        // Handle redirects for known embed domains
        if (needsRedirectResolution(fixedLink)) {
            fixedLink = resolveRedirects(fixedLink, iframeUrl)
        }
        
        Log.d("MaxSeries", "✅ Processando link: $fixedLink")
        
        return try {
            // Try standard extractor first
            if (loadExtractor(fixedLink, iframeUrl, subtitleCallback, callback)) {
                1
            } else {
                // Manual extraction fallback
                extractManualLinks(fixedLink, playerName, iframeUrl, subtitleCallback, callback)
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao processar link $fixedLink: ${e.message}")
            0
        }
    }
    
    private fun isBlockedSource(url: String): Boolean {
        val blockedDomains = listOf(
            "youtube.com", "youtu.be", "facebook.com", "twitter.com",
            "ads.", "ad.", "doubleclick", "googleads", "googlesyndication",
            "popads", "popcash", "propellerads", "adnxs", "adsystem"
        )
        return blockedDomains.any { url.contains(it, ignoreCase = true) }
    }
    
    private fun isValidVideoSource(url: String): Boolean {
        val validDomains = listOf(
            "embed", "player", "stream", "video", "watch",
            "abyss.to", "streamwish", "filemoon", "mixdrop"
        )
        return validDomains.any { url.contains(it, ignoreCase = true) } && !isBlockedSource(url)
    }
    
    private fun needsRedirectResolution(url: String): Boolean {
        val redirectDomains = listOf(
            "playerembedapi.link", "megaembed.link", "bysebuho.com",
            "embed", "storage", "short"
        )
        return redirectDomains.any { url.contains(it, ignoreCase = true) }
    }
    
    private suspend fun resolveRedirects(url: String, referer: String): String {
        var currentLink = url
        var redirects = 0
        val headers = mapOf(
            "Referer" to referer,
            "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try {
            while (redirects < 5) {
                val response = app.get(currentLink, headers = headers, allowRedirects = false)
                if (response.code in 301..308) {
                    val location = response.headers["location"] ?: response.headers["Location"]
                    if (!location.isNullOrEmpty()) {
                        currentLink = if (location.startsWith("//")) {
                            "https:$location"
                        } else if (location.startsWith("/")) {
                            val uri = java.net.URI(currentLink)
                            "${uri.scheme}://${uri.host}$location"
                        } else {
                            location
                        }
                        redirects++
                        Log.d("MaxSeries", "  ↳ Redirect ($redirects): $currentLink")
                        continue
                    }
                }
                break
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao resolver redirects: ${e.message}")
        }
        
        return currentLink
    }
    
    private suspend fun extractManualLinks(
        url: String,
        playerName: String,
        referer: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        return try {
            Log.d("MaxSeries", "🛠️ Extração manual para: $url")
            val pageHeaders = mapOf("Referer" to referer)
            val pageContent = app.get(url, headers = pageHeaders).text
            
            var linksFound = 0
            
            // Enhanced regex patterns for video extraction
            val videoPatterns = listOf(
                Regex("""["'](https?://[^"']+\.m3u8[^"']*)["']"""),
                Regex("""["'](https?://[^"']+\.mp4[^"']*)["']"""),
                Regex("""["'](https?://[^"']+\.mkv[^"']*)["']"""),
                Regex("""file["'\s]*:["'\s]*["']([^"']+)["']"""),
                Regex("""source["'\s]*:["'\s]*["']([^"']+)["']"""),
                Regex("""src["'\s]*:["'\s]*["']([^"']+)["']""")
            )
            
            videoPatterns.forEach { pattern ->
                pattern.findAll(pageContent).forEach { match ->
                    val streamUrl = match.groupValues[1].replace("\\/", "/")
                    if (streamUrl.isNotEmpty() && !isBlockedSource(streamUrl)) {
                        Log.d("MaxSeries", "🎯 Link manual encontrado: $streamUrl")
                        
                        if (streamUrl.contains(".m3u8")) {
                            com.lagradost.cloudstream3.utils.M3u8Helper.generateM3u8(
                                playerName,
                                streamUrl,
                                url,
                                headers = mapOf("Referer" to referer)
                            ).forEach(callback)
                        } else {
                            callback.invoke(
                                newExtractorLink(
                                    playerName,
                                    playerName,
                                    streamUrl
                                ) {
                                    this.referer = url
                                    this.quality = Qualities.Unknown.value
                                }
                            )
                        }
                        linksFound++
                    }
                }
            }
            
            linksFound
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro na extração manual: ${e.message}")
            0
        }
    }
    
    private suspend fun extractFromScripts(
        doc: org.jsoup.nodes.Document,
        iframeUrl: String,
        pageUrl: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        doc.select("script").forEach { script ->
            val scriptContent = script.html()
            
            // Look for video sources in JavaScript
            val jsPatterns = listOf(
                Regex("""['"]([^'"]*\.m3u8[^'"]*)['"]"""),
                Regex("""['"]([^'"]*\.mp4[^'"]*)['"]"""),
                Regex("""source['":\s]*['"]([^'"]+)['"]"""),
                Regex("""file['":\s]*['"]([^'"]+)['"]""")
            )
            
            jsPatterns.forEach { pattern ->
                pattern.findAll(scriptContent).forEach { match ->
                    val videoUrl = match.groupValues[1]
                    if (videoUrl.isNotEmpty() && !isBlockedSource(videoUrl) && videoUrl.startsWith("http")) {
                        Log.d("MaxSeries", "🎯 Link encontrado em script: $videoUrl")
                        
                        try {
                            if (loadExtractor(videoUrl, iframeUrl, subtitleCallback, callback)) {
                                linksFound++
                            }
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar link do script: ${e.message}")
                        }
                    }
                }
            }
        }
        
        return linksFound
    }
    
    private suspend fun tryDirectVideoExtraction(
        doc: org.jsoup.nodes.Document,
        pageUrl: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🔄 Tentando extração direta da página")
        
        // Look for direct video elements
        doc.select("video source, video").forEach { video ->
            val src = video.attr("src")
            if (src.isNotEmpty() && !isBlockedSource(src)) {
                try {
                    callback.invoke(
                        newExtractorLink(
                            "Direct",
                            "Direct Video",
                            src
                        ) {
                            this.referer = pageUrl
                            this.quality = Qualities.Unknown.value
                        }
                    )
                    return true
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao processar vídeo direto: ${e.message}")
                }
            }
        }
        
        return false
    }
}
