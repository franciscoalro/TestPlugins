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
            
            // MaxSeries uses an iframe with specific structure
            val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
                ?: doc.selectFirst("iframe[src*=player]")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                Log.d("MaxSeries", "📺 Carregando episódios do iframe: $iframeSrc")
                
                try {
                    val iframeDoc = app.get(iframeSrc, headers = mapOf(
                        "Referer" to url,
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )).document
                    
                    // Extract episodes from the iframe structure you provided
                    iframeDoc.select("li[data-season-id][data-episode-id]").forEach { epLi ->
                        val seasonId = epLi.attr("data-season-id")
                        val episodeId = epLi.attr("data-episode-id")
                        val epLink = epLi.selectFirst("a")
                        
                        if (epLink != null && seasonId.isNotEmpty() && episodeId.isNotEmpty()) {
                            val epTitle = epLink.text().trim()
                            val epHref = epLink.attr("href").replace("#", "")
                            
                            // Extract season and episode numbers
                            val seasonNum = iframeDoc.selectFirst("li.selected[data-season-number]")
                                ?.attr("data-season-number")?.toIntOrNull() ?: 1
                            
                            val epNum = epTitle.split(" - ").firstOrNull()?.toIntOrNull() ?: episodes.size + 1
                            
                            // Store the iframe URL and episode data for loadLinks
                            val episodeData = "$iframeSrc|$seasonId|$episodeId"
                            
                            episodes.add(newEpisode(episodeData) {
                                this.name = epTitle
                                this.episode = epNum
                                this.season = seasonNum
                            })
                        }
                    }
                    
                    Log.d("MaxSeries", "✅ Encontrados ${episodes.size} episódios para $title")
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar episódios do iframe: ${e.message}")
                }
            }
            
            // Fallback: Standard DooPlay structure
            if (episodes.isEmpty()) {
                Log.w("MaxSeries", "⚠️ Tentando método padrão DooPlay")
                
                doc.select("div.se-c").forEach { seasonDiv ->
                    val seasonNum = seasonDiv.attr("id").replace("season-", "").toIntOrNull() ?: 1
                    
                    seasonDiv.select("ul.episodios li").forEach { epLi ->
                        val epA = epLi.selectFirst("a") ?: return@forEach
                        val epTitle = epA.text().trim()
                        val epHref = epA.attr("href")
                        
                        val epNum = epLi.selectFirst(".numerando")?.text()?.split("-")?.lastOrNull()?.trim()?.toIntOrNull()
                            ?: epTitle.replace(Regex(".*?(\\d+).*"), "$1").toIntOrNull()
                            ?: episodes.size + 1
                        
                        episodes.add(newEpisode(epHref) {
                            this.name = epTitle
                            this.episode = epNum
                            this.season = seasonNum
                        })
                    }
                }
            }
            
            if (episodes.isEmpty()) {
                Log.w("MaxSeries", "⚠️ Nenhum episódio encontrado para $title")
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
        
        var linksFound = 0
        
        // Check if data contains episode info (format: iframeUrl|seasonId|episodeId)
        if (data.contains("|")) {
            val parts = data.split("|")
            if (parts.size >= 3) {
                val iframeUrl = parts[0]
                val seasonId = parts[1]
                val episodeId = parts[2]
                
                Log.d("MaxSeries", "📺 Processando episódio: Season=$seasonId, Episode=$episodeId")
                
                // Load the iframe page
                try {
                    val iframeDoc = app.get(iframeUrl, headers = mapOf(
                        "Referer" to mainUrl,
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )).document
                    
                    // Look for the app.js or similar script that handles episode loading
                    val scripts = iframeDoc.select("script[src*=app.js], script[src*=player], script[src*=jwplayer]")
                    Log.d("MaxSeries", "📜 Scripts encontrados: ${scripts.size}")
                    
                    // Try to make AJAX request to get episode data
                    // Based on the HTML structure, it seems to use JavaScript to load episodes
                    val baseUrl = iframeUrl.substringBefore("?").substringBeforeLast("/")
                    
                    // Try common endpoints for episode data
                    val possibleEndpoints = listOf(
                        "$baseUrl/episode/$seasonId/$episodeId",
                        "$baseUrl/play/$seasonId/$episodeId",
                        "$baseUrl/stream/$seasonId/$episodeId",
                        "$baseUrl/api/episode/$seasonId/$episodeId"
                    )
                    
                    for (endpoint in possibleEndpoints) {
                        try {
                            Log.d("MaxSeries", "🔄 Tentando endpoint: $endpoint")
                            val response = app.get(endpoint, headers = mapOf(
                                "Referer" to iframeUrl,
                                "X-Requested-With" to "XMLHttpRequest",
                                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            ))
                            
                            if (response.code == 200) {
                                val responseText = response.text
                                Log.d("MaxSeries", "✅ Resposta do endpoint: ${responseText.take(200)}...")
                                
                                // Look for video URLs in the response
                                if (extractVideoFromResponse(responseText, endpoint, callback)) {
                                    linksFound++
                                    break
                                }
                            }
                        } catch (e: Exception) {
                            Log.d("MaxSeries", "⚠️ Endpoint $endpoint falhou: ${e.message}")
                        }
                    }
                    
                    // Fallback: Try to simulate the JavaScript behavior
                    if (linksFound == 0) {
                        linksFound += simulateJavaScriptPlayer(iframeDoc, seasonId, episodeId, iframeUrl, callback)
                    }
                    
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao processar iframe: ${e.message}")
                }
            }
        } else {
            // Handle movies or direct URLs
            val doc = app.get(data).document
            
            // Look for DooPlay player options
            doc.select("#playeroptionsul li, .playeroptionsul li, .dooplay_player_option").forEach { option ->
                val playerId = option.attr("data-post") ?: option.attr("data-id")
                val playerNum = option.attr("data-nume") ?: option.attr("data-player")
                val playerType = option.attr("data-type") ?: "movie"
                
                if (playerId.isNotEmpty() && playerNum.isNotEmpty()) {
                    try {
                        Log.d("MaxSeries", "🎬 Tentando player: ID=$playerId, Num=$playerNum, Type=$playerType")
                        
                        val ajaxUrl = "$mainUrl/wp-admin/admin-ajax.php"
                        val ajaxData = mapOf(
                            "action" to "doo_player_ajax",
                            "post" to playerId,
                            "nume" to playerNum,
                            "type" to playerType
                        )
                        
                        val ajaxResponse = app.post(ajaxUrl, data = ajaxData).text
                        Log.d("MaxSeries", "📡 AJAX Response: $ajaxResponse")
                        
                        val iframeRegex = Regex("""src=["']([^"']+)["']""")
                        val iframeMatch = iframeRegex.find(ajaxResponse)
                        
                        if (iframeMatch != null) {
                            val iframeUrl = iframeMatch.groupValues[1]
                            val cleanUrl = if (iframeUrl.startsWith("//")) "https:$iframeUrl" else iframeUrl
                            
                            Log.d("MaxSeries", "🎯 Iframe encontrado: $cleanUrl")
                            
                            if (processPlayerUrl(cleanUrl, data, subtitleCallback, callback)) {
                                linksFound++
                            }
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro no player AJAX: ${e.message}")
                    }
                }
            }
            
            // Fallback: Look for direct iframes
            if (linksFound == 0) {
                val iframeSelectors = listOf(
                    "iframe.metaframe",
                    "iframe[src*=embed]",
                    "iframe[src*=player]",
                    "#player iframe",
                    ".player iframe"
                )
                
                iframeSelectors.forEach { selector ->
                    doc.select(selector).forEach { iframe ->
                        val src = iframe.attr("src")
                        if (src.isNotEmpty()) {
                            val cleanUrl = if (src.startsWith("//")) "https:$src" else src
                            Log.d("MaxSeries", "🎯 Iframe direto encontrado: $cleanUrl")
                            
                            if (processPlayerUrl(cleanUrl, data, subtitleCallback, callback)) {
                                linksFound++
                            }
                        }
                    }
                }
            }
        }
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }
    
    private suspend fun extractVideoFromResponse(
        responseText: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var found = false
        
        // Look for various video URL patterns in the response
        val videoPatterns = listOf(
            Regex("""["']([^"']*\.m3u8[^"']*)["']"""),
            Regex("""["']([^"']*\.mp4[^"']*)["']"""),
            Regex("""["']([^"']*\.mkv[^"']*)["']"""),
            Regex(""""url"\s*:\s*"([^"]+)""""),
            Regex(""""file"\s*:\s*"([^"]+)""""),
            Regex(""""source"\s*:\s*"([^"]+)""""),
            Regex(""""src"\s*:\s*"([^"]+)"""")
        )
        
        videoPatterns.forEach { pattern ->
            pattern.findAll(responseText).forEach { match ->
                val videoUrl = match.groupValues[1].replace("\\/", "/")
                
                if (videoUrl.startsWith("http") && !isBlockedSource(videoUrl)) {
                    Log.d("MaxSeries", "🎯 URL encontrada na resposta: $videoUrl")
                    
                    try {
                        if (videoUrl.contains(".m3u8")) {
                            com.lagradost.cloudstream3.utils.M3u8Helper.generateM3u8(
                                "MaxSeries",
                                videoUrl,
                                referer,
                                headers = mapOf("Referer" to referer)
                            ).forEach(callback)
                        } else {
                            callback.invoke(
                                newExtractorLink(
                                    "MaxSeries",
                                    "MaxSeries Video",
                                    videoUrl
                                ) {
                                    this.referer = referer
                                    this.quality = Qualities.Unknown.value
                                }
                            )
                        }
                        found = true
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro ao processar URL da resposta: ${e.message}")
                    }
                }
            }
        }
        
        return found
    }
    
    private suspend fun simulateJavaScriptPlayer(
        doc: org.jsoup.nodes.Document,
        seasonId: String,
        episodeId: String,
        iframeUrl: String,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        // Look for jwplayer or other player configurations in scripts
        doc.select("script").forEach { script ->
            val scriptContent = script.html()
            
            // Look for jwplayer setup or similar
            if (scriptContent.contains("jwplayer") || scriptContent.contains("player") || scriptContent.contains("setup")) {
                Log.d("MaxSeries", "🎬 Script de player encontrado")
                
                // Extract potential video sources
                val sourcePatterns = listOf(
                    Regex("""file\s*:\s*["']([^"']+)["']"""),
                    Regex("""source\s*:\s*["']([^"']+)["']"""),
                    Regex("""src\s*:\s*["']([^"']+)["']"""),
                    Regex("""["']([^"']*\.m3u8[^"']*)["']"""),
                    Regex("""["']([^"']*\.mp4[^"']*)["']""")
                )
                
                sourcePatterns.forEach { pattern ->
                    pattern.findAll(scriptContent).forEach { match ->
                        val videoUrl = match.groupValues[1]
                        
                        if (videoUrl.startsWith("http") && !isBlockedSource(videoUrl)) {
                            Log.d("MaxSeries", "🎯 URL encontrada em script: $videoUrl")
                            
                            try {
                                callback.invoke(
                                    newExtractorLink(
                                        "MaxSeries",
                                        "MaxSeries Player",
                                        videoUrl
                                    ) {
                                        this.referer = iframeUrl
                                        this.quality = Qualities.Unknown.value
                                    }
                                )
                                linksFound++
                            } catch (e: Exception) {
                                Log.e("MaxSeries", "❌ Erro ao processar URL do script: ${e.message}")
                            }
                        }
                    }
                }
            }
        }
        
        return linksFound
    }
    
    private suspend fun processPlayerUrl(
        url: String,
        referer: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        if (isBlockedSource(url)) {
            Log.w("MaxSeries", "⚠️ URL bloqueada: $url")
            return false
        }
        
        return try {
            // Try standard extractor first
            if (loadExtractor(url, referer, subtitleCallback, callback)) {
                Log.d("MaxSeries", "✅ Extrator padrão funcionou para: $url")
                true
            } else {
                // Manual extraction
                Log.d("MaxSeries", "🛠️ Tentando extração manual para: $url")
                extractManualLinks(url, referer, subtitleCallback, callback)
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao processar URL $url: ${e.message}")
            false
        }
    }
    
    private suspend fun extractManualLinks(
        url: String,
        referer: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val headers = mapOf(
                "Referer" to referer,
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            val pageContent = app.get(url, headers = headers).text
            var linksFound = false
            
            // Enhanced regex patterns
            val videoPatterns = listOf(
                Regex("""["']([^"']*\.m3u8[^"']*)["']"""),
                Regex("""["']([^"']*\.mp4[^"']*)["']"""),
                Regex("""["']([^"']*\.mkv[^"']*)["']"""),
                Regex("""file\s*[:=]\s*["']([^"']+)["']"""),
                Regex("""source\s*[:=]\s*["']([^"']+)["']"""),
                Regex("""src\s*[:=]\s*["']([^"']+)["']"""),
                Regex("""url\s*[:=]\s*["']([^"']+)["']""")
            )
            
            videoPatterns.forEach { pattern ->
                pattern.findAll(pageContent).forEach { match ->
                    val videoUrl = match.groupValues[1].replace("\\/", "/")
                    
                    if (videoUrl.startsWith("http") && !isBlockedSource(videoUrl)) {
                        Log.d("MaxSeries", "🎯 Link manual encontrado: $videoUrl")
                        
                        try {
                            if (videoUrl.contains(".m3u8")) {
                                com.lagradost.cloudstream3.utils.M3u8Helper.generateM3u8(
                                    "Manual",
                                    videoUrl,
                                    url,
                                    headers = headers
                                ).forEach(callback)
                            } else {
                                callback.invoke(
                                    newExtractorLink(
                                        "Manual",
                                        "Manual Video",
                                        videoUrl
                                    ) {
                                        this.referer = url
                                        this.quality = Qualities.Unknown.value
                                    }
                                )
                            }
                            linksFound = true
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar link manual: ${e.message}")
                        }
                    }
                }
            }
            
            linksFound
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro na extração manual: ${e.message}")
            false
        }
    }
    
    private fun isBlockedSource(url: String): Boolean {
        val blockedDomains = listOf(
            "youtube.com", "youtu.be", "facebook.com", "twitter.com",
            "ads.", "ad.", "doubleclick", "googleads", "googlesyndication",
            "popads", "popcash", "propellerads", "adnxs", "adsystem",
            "google.com", "gstatic.com"
        )
        return blockedDomains.any { url.contains(it, ignoreCase = true) }
    }
}
