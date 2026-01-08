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
        
        // Step 1: Extract the main iframe (playerthree.online or viewplayer.online)
        val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
            ?: doc.selectFirst("iframe[src*=playerthree], iframe[src*=viewplayer]")?.attr("src")
        
        if (mainIframe.isNullOrEmpty()) {
            Log.e("MaxSeries", "❌ Nenhum iframe principal encontrado em $pageUrl")
            return false
        }
        
        val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
        Log.d("MaxSeries", "📺 Iframe principal encontrado: $iframeSrc")
        
        // Step 2: Navigate to the iframe and extract player buttons
        try {
            // If we have an episode ID, we need to construct the URL with the episode
            val iframeUrl = if (episodeId != null) {
                "$iframeSrc?ep=$episodeId"
            } else {
                iframeSrc
            }
            
            Log.d("MaxSeries", "🎬 Acessando: $iframeUrl")
            val iframeDoc = app.get(iframeUrl).document
            
            // Look for player buttons with data-source attribute
            iframeDoc.select("button.btn[data-source]").forEach { btn ->
                val playerName = btn.text().trim()
                val videoLink = btn.attr("data-source")
                
                if (videoLink.isNotEmpty()) {
                    var fixedLink = if (videoLink.startsWith("//")) "https:$videoLink" else videoLink
                    
                    // Filter out YouTube trailers
                    if (fixedLink.contains("youtube.com", ignoreCase = true) || 
                        fixedLink.contains("youtu.be", ignoreCase = true)) {
                        Log.w("MaxSeries", "⚠️ Ignorando trailer do YouTube: $fixedLink")
                        return@forEach
                    }
                    
                    // Handle redirects for known embed domains (maxseries uses these to hide real hosts)
                    if (fixedLink.contains("playerembedapi.link") || 
                        fixedLink.contains("megaembed.link") || 
                        fixedLink.contains("bysebuho.com") ||
                        fixedLink.contains("embed") || 
                        fixedLink.contains("storage")) {
                        try {
                            Log.d("MaxSeries", "🔄 Resolvendo cadeia de redirects para: $fixedLink")
                            var currentLink = fixedLink
                            var redirects = 0
                            val headers = mapOf(
                                "Referer" to iframeUrl,
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                            )
                            
                            // Follow redirects manually to find the final host
                            while (redirects < 5) {
                                val response = app.get(currentLink, headers = headers, allowRedirects = false)
                                if (response.code in 301..308) {
                                    val location = response.headers["location"] ?: response.headers["Location"]
                                    if (!location.isNullOrEmpty()) {
                                        currentLink = if (location.startsWith("//")) "https:$location" else if (location.startsWith("/")) {
                                            val uri = java.net.URI(currentLink)
                                            "${uri.scheme}://${uri.host}$location"
                                        } else location
                                        redirects++
                                        Log.d("MaxSeries", "  ↳ Pulou para ($redirects): $currentLink")
                                        continue
                                    }
                                }
                                break
                            }
                            fixedLink = currentLink
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao resolver cadeia de redirects: ${e.message}")
                        }
                    }
                    
                    Log.d("MaxSeries", "✅ Link final encontrado: $fixedLink")
                    
                    try {
                        // 1. Try standard extractor
                        val loaded = loadExtractor(fixedLink, iframeUrl, subtitleCallback, callback)
                        
                        // 2. Fallback: Manual extraction for hosts like Abyss.to or BySebuho (embedwish)
                        if (!loaded) {
                            Log.d("MaxSeries", "🛠️ Tentando extração manual para: $fixedLink")
                            val pageHeaders = mapOf("Referer" to iframeUrl)
                            val pageContent = app.get(fixedLink, headers = pageHeaders).text
                            
                            // Look for .m3u8 or .mp4 links in the page source
                            val videoRegex = Regex("""["'](http[^"']+\.(?:m3u8|mp4|mkv)[^"']*)["']""")
                            val matches = videoRegex.findAll(pageContent)
                            
                            var manualFound = false
                            matches.forEach { match ->
                                val streamUrl = match.groupValues[1].replace("\\/", "/")
                                Log.d("MaxSeries", "🎯 Link manual encontrado: $streamUrl")
                                
                                if (streamUrl.contains(".m3u8")) {
                                    // For m3u8 streams, use M3u8Helper
                                    com.lagradost.cloudstream3.utils.M3u8Helper.generateM3u8(
                                        playerName,
                                        streamUrl,
                                        fixedLink,
                                        headers = mapOf("Referer" to iframeUrl)
                                    ).forEach(callback)
                                } else {
                                    // For direct mp4/mkv links
                                    callback.invoke(
                                        newExtractorLink(
                                            source = playerName,
                                            name = playerName,
                                            url = streamUrl,
                                            referer = fixedLink,
                                            quality = getQualityFromName(""),
                                        )
                                    )
                                }
                                manualFound = true
                                linksFound++
                            }
                            
                            if (manualFound) {
                                linksFound++
                            } else if (fixedLink.contains("abyss.to")) {
                                // Specific fallback for Abyss.to if regex fails
                                Log.d("MaxSeries", "🔎 Tentando extração específica para Abyss.to")
                                // Abyss sometimes hides the link in a data attribute or base64
                                // For now, we rely on the generic regex above, but could add more here
                            }
                        } else {
                            linksFound++
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro ao processar link $fixedLink: ${e.message}")
                    }
                }
            }
            
            // Fallback: Look for any iframes inside the player iframe
            if (linksFound == 0) {
                iframeDoc.select("iframe").forEach { iframe ->
                    val src = iframe.attr("src").ifEmpty { iframe.attr("data-src") }
                    if (src.isNotEmpty() && !src.contains("facebook.com") && 
                        !src.contains("twitter.com") && !src.contains("google.com") &&
                        !src.contains("youtube.com", ignoreCase = true)) {
                        val fixedSrc = if (src.startsWith("//")) "https:$src" else src
                        if (fixedSrc.startsWith("http")) {
                            try {
                                Log.d("MaxSeries", "🔄 Tentando iframe aninhado: $fixedSrc")
                                loadExtractor(fixedSrc, iframeUrl, subtitleCallback, callback)
                                linksFound++
                            } catch (e: Exception) {
                                Log.e("MaxSeries", "❌ Erro ao carregar iframe aninhado: ${e.message}")
                            }
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
}
