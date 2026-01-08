package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import com.lagradost.cloudstream3.utils.newExtractorLink
import android.util.Log

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
            
            // Method 1: Standard DooPlay structure
            doc.select("div.se-c").forEach { seasonDiv ->
                val seasonNum = seasonDiv.attr("id").replace("season-", "").toIntOrNull() ?: 1
                
                seasonDiv.select("ul.episodios li").forEach { epLi ->
                    val epA = epLi.selectFirst("a") ?: return@forEach
                    val epTitle = epA.text().trim()
                    val epHref = epA.attr("href")
                    
                    if (epHref.isNotEmpty()) {
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
            
            // Method 2: Alternative episode structures
            if (episodes.isEmpty()) {
                doc.select("ul.episodios li a, .episodios a").forEach { epA ->
                    val epTitle = epA.text().trim()
                    val epHref = epA.attr("href")
                    
                    if (epHref.isNotEmpty() && epTitle.isNotEmpty()) {
                        episodes.add(newEpisode(epHref) {
                            this.name = epTitle
                            this.episode = episodes.size + 1
                            this.season = 1
                        })
                    }
                }
            }
            
            // Method 3: If no episodes found, create a single episode pointing to the series page
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "⚠️ Nenhum episódio encontrado, criando episódio único")
                episodes.add(newEpisode(url) {
                    this.name = "Episódio 1"
                    this.episode = 1
                    this.season = 1
                })
            }
            
            Log.d("MaxSeries", "✅ Encontrados ${episodes.size} episódios para $title")

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
        Log.d("MaxSeries", "📺 Processando links para: $data")
        
        var linksFound = 0
        
        try {
            val doc = app.get(data).document
            
            // Method 1: Look for ViewPlayer iframe structure (like the HTML you showed)
            val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                ?: doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
                ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
                ?: doc.selectFirst("#player iframe")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                Log.d("MaxSeries", "📺 Carregando player iframe: $iframeSrc")
                
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Look for player buttons with data-source (like in your HTML)
                    iframeDoc.select("button[data-source], .btn[data-source]").forEach { button ->
                        val source = button.attr("data-source")
                        val playerName = button.text().trim()
                        
                        if (source.isNotEmpty() && source.startsWith("http")) {
                            Log.d("MaxSeries", "🎯 Player encontrado: $playerName -> $source")
                            
                            try {
                                if (loadExtractor(source, data, subtitleCallback, callback)) {
                                    linksFound++
                                }
                            } catch (e: Exception) {
                                Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${e.message}")
                            }
                        }
                    }
                    
                    // Look for direct video sources in JavaScript
                    iframeDoc.select("script").forEach { script ->
                        val scriptContent = script.html()
                        
                        // Look for gleam.config or similar configurations
                        if (scriptContent.contains("gleam.config", ignoreCase = true) ||
                            scriptContent.contains("jwplayer", ignoreCase = true)) {
                            
                            Log.d("MaxSeries", "🎬 Script de configuração encontrado")
                            
                            val videoPatterns = listOf(
                                Regex(""""url"\s*:\s*"([^"]+)""""),
                                Regex(""""file"\s*:\s*"([^"]+)""""),
                                Regex(""""source"\s*:\s*"([^"]+)""""),
                                Regex("""data-source=["']([^"']+)["']"""),
                                Regex("""https://[^"'\s]+\.(?:m3u8|mp4|mkv|avi)""")
                            )
                            
                            videoPatterns.forEach { pattern ->
                                pattern.findAll(scriptContent).forEach { match ->
                                    val videoUrl = match.groupValues.getOrNull(1) ?: match.value
                                    
                                    if (videoUrl.startsWith("http") && 
                                        !videoUrl.contains("youtube.com", ignoreCase = true) &&
                                        !videoUrl.contains("facebook.com", ignoreCase = true) &&
                                        !videoUrl.contains("ads", ignoreCase = true)) {
                                        
                                        Log.d("MaxSeries", "🎯 URL encontrada no script: $videoUrl")
                                        
                                        try {
                                            if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {
                                                linksFound++
                                            }
                                        } catch (e: Exception) {
                                            Log.e("MaxSeries", "❌ Erro ao processar URL do script: ${e.message}")
                                        }
                                    }
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                }
            }
            
            // Method 2: Look for DooPlay AJAX players (fallback)
            if (linksFound == 0) {
                Log.d("MaxSeries", "🔄 Tentando método DooPlay AJAX")
                doc.select("#playeroptionsul li, .playeroptionsul li").forEach { option ->
                    val playerId = option.attr("data-post")
                    val playerNum = option.attr("data-nume")
                    val playerType = option.attr("data-type").ifEmpty { "movie" }
                    
                    if (playerId.isNotEmpty() && playerNum.isNotEmpty()) {
                        try {
                            val ajaxUrl = "$mainUrl/wp-admin/admin-ajax.php"
                            val ajaxData = mapOf(
                                "action" to "doo_player_ajax",
                                "post" to playerId,
                                "nume" to playerNum,
                                "type" to playerType
                            )
                            
                            val ajaxResponse = app.post(ajaxUrl, data = ajaxData).text
                            val iframeRegex = Regex("""src=["']([^"']+)["']""")
                            val iframeMatch = iframeRegex.find(ajaxResponse)
                            
                            if (iframeMatch != null) {
                                val iframeUrl = iframeMatch.groupValues[1]
                                val cleanUrl = if (iframeUrl.startsWith("//")) "https:$iframeUrl" else iframeUrl
                                
                                if (loadExtractor(cleanUrl, data, subtitleCallback, callback)) {
                                    linksFound++
                                }
                            }
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro no player AJAX: ${e.message}")
                        }
                    }
                }
            }
            
            // Method 3: Look for direct iframes (fallback)
            if (linksFound == 0) {
                Log.d("MaxSeries", "🔄 Tentando iframes diretos")
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
                            
                            if (!cleanUrl.contains("youtube.com", ignoreCase = true) && 
                                !cleanUrl.contains("facebook.com", ignoreCase = true)) {
                                
                                try {
                                    if (loadExtractor(cleanUrl, data, subtitleCallback, callback)) {
                                        linksFound++
                                    }
                                } catch (e: Exception) {
                                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                                }
                            }
                        }
                    }
                }
            }
            
            // Method 4: Look for direct video links in page source (last resort)
            if (linksFound == 0) {
                Log.d("MaxSeries", "🔄 Procurando links diretos na página")
                val pageContent = doc.html()
                val videoPatterns = listOf(
                    Regex("""["']([^"']*\.m3u8[^"']*)["']"""),
                    Regex("""["']([^"']*\.mp4[^"']*)["']"""),
                    Regex("""file\s*:\s*["']([^"']+)["']"""),
                    Regex("""source\s*:\s*["']([^"']+)["']""")
                )
                
                videoPatterns.forEach { pattern ->
                    pattern.findAll(pageContent).forEach { match ->
                        val videoUrl = match.groupValues[1]
                        
                        if (videoUrl.startsWith("http") && 
                            !videoUrl.contains("youtube.com", ignoreCase = true) &&
                            !videoUrl.contains("facebook.com", ignoreCase = true) &&
                            !videoUrl.contains("ads", ignoreCase = true)) {
                            
                            try {
                                callback.invoke(
                                    newExtractorLink(
                                        "MaxSeries",
                                        "MaxSeries Video",
                                        videoUrl
                                    ) {
                                        this.referer = data
                                        this.quality = Qualities.Unknown.value
                                    }
                                )
                                linksFound++
                            } catch (e: Exception) {
                                Log.e("MaxSeries", "❌ Erro ao processar vídeo direto: ${e.message}")
                            }
                        }
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro geral no loadLinks: ${e.message}")
        }
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }
}