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
            ?: doc.selectFirst("h1")?.text() 
            ?: doc.selectFirst(".entry-title")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text() 
            ?: doc.selectFirst(".entry-content")?.text()
            ?: doc.selectFirst(".wp-content")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
            ?: doc.selectFirst(".wp-post-image")?.attr("src")
        val bg = doc.selectFirst(".backdrop img")?.attr("src")
        
        val isSeries = url.contains("/series/") || url.contains("/tv/")

        if (isSeries) {
            val episodes = mutableListOf<Episode>()
            
            Log.d("MaxSeries", "📺 Analisando série: $title")
            
            // Method 1: Check for iframe with MaxSeries episode structure
            val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                ?: doc.selectFirst("iframe[src*=playerthree]")?.attr("src")
                ?: doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
                ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
                ?: doc.selectFirst("#player iframe")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                try {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "📺 Carregando iframe de episódios: $iframeSrc")
                    
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Extract seasons from navigation
                    val seasons = mutableMapOf<String, Int>()
                    iframeDoc.select("ul.header-navigation li[data-season-id]").forEach { seasonLi ->
                        val seasonId = seasonLi.attr("data-season-id")
                        val seasonNumber = seasonLi.attr("data-season-number").toIntOrNull() ?: 1
                        if (seasonId.isNotEmpty()) {
                            seasons[seasonId] = seasonNumber
                            Log.d("MaxSeries", "🎬 Temporada encontrada: $seasonNumber (ID: $seasonId)")
                        }
                    }
                    
                    // Extract episodes with real season/episode data
                    iframeDoc.select("li[data-season-id][data-episode-id]").forEach { epLi ->
                        val seasonId = epLi.attr("data-season-id")
                        val episodeId = epLi.attr("data-episode-id")
                        val epLink = epLi.selectFirst("a")
                        
                        if (seasonId.isNotEmpty() && episodeId.isNotEmpty() && epLink != null) {
                            val epTitle = epLink.text().trim()
                            val epHref = epLink.attr("href") // Format: #12956_255628
                            
                            // Extract episode number from title (format: "1 - Episode Title")
                            val epNum = epTitle.split(" - ").firstOrNull()?.trim()?.toIntOrNull() ?: 1
                            val seasonNum = seasons[seasonId] ?: 1
                            
                            // Create episode URL that includes the iframe URL and episode reference
                            val episodeUrl = "$iframeSrc$epHref"
                            
                            episodes.add(newEpisode(episodeUrl) {
                                this.name = epTitle
                                this.episode = epNum
                                this.season = seasonNum
                            })
                            
                            Log.d("MaxSeries", "✅ Episódio: T${seasonNum}E${epNum} - $epTitle")
                        }
                    }
                    
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                }
            }
            
            // Method 2: Standard DooPlay structure (fallback)
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "🔄 Tentando estrutura DooPlay padrão")
                doc.select("div.se-c").forEachIndexed { seasonIndex, seasonDiv ->
                    val seasonNum = seasonDiv.attr("id").replace("season-", "").toIntOrNull() 
                        ?: (seasonIndex + 1)
                    
                    seasonDiv.select("ul.episodios li").forEachIndexed { epIndex, epLi ->
                        val epA = epLi.selectFirst("a")
                        if (epA != null) {
                            val epTitle = epA.text().trim()
                            val epHref = epA.attr("href")
                            
                            if (epHref.isNotEmpty()) {
                                val epNum = epLi.selectFirst(".numerando")?.text()?.let { numerando ->
                                    numerando.split("-").lastOrNull()?.trim()?.toIntOrNull()
                                        ?: numerando.replace(Regex("[^0-9]"), "").toIntOrNull()
                                } ?: (epIndex + 1)
                                
                                episodes.add(newEpisode(epHref) {
                                    this.name = if (epTitle.isNotEmpty()) epTitle else "Episódio $epNum"
                                    this.episode = epNum
                                    this.season = seasonNum
                                })
                            }
                        }
                    }
                }
            }
            
            // Method 3: Fallback - single episode
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "⚠️ Nenhum episódio encontrado, criando episódio único")
                episodes.add(newEpisode(url) {
                    this.name = "Episódio 1"
                    this.episode = 1
                    this.season = 1
                })
            }
            
            Log.d("MaxSeries", "✅ Total: ${episodes.size} episódios em ${episodes.map { it.season }.distinct().size} temporadas")

            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster
                this.plot = desc
                this.backgroundPosterUrl = bg
            }
        } else {
            Log.d("MaxSeries", "🎬 Processando filme: $title")
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
            // Check if this is an episode URL from iframe (contains #)
            if (data.contains("#")) {
                Log.d("MaxSeries", "🎯 Processando episódio do iframe")
                
                // Load the iframe page with the episode fragment
                val doc = app.get(data).document
                
                // Look for player selection buttons (like "Player #1", "Player #2")
                val playerButtons = doc.select("button[data-show-player], .btn[data-show-player]")
                
                if (playerButtons.isNotEmpty()) {
                    Log.d("MaxSeries", "🎮 Encontrados ${playerButtons.size} players")
                    
                    playerButtons.forEach { button ->
                        val playerName = button.text().trim()
                        Log.d("MaxSeries", "🔄 Testando player: $playerName")
                        
                        try {
                            // Simulate clicking the player button to get the video player
                            // This might trigger JavaScript that loads the actual video URL
                            
                            // Look for data attributes that might contain video info
                            val dataSource = button.attr("data-source")
                            val dataUrl = button.attr("data-url")
                            val dataPlayer = button.attr("data-player")
                            
                            val videoUrl = dataSource.ifEmpty { dataUrl.ifEmpty { dataPlayer } }
                            
                            if (videoUrl.isNotEmpty() && videoUrl.startsWith("http")) {
                                Log.d("MaxSeries", "🎯 URL encontrada no botão: $videoUrl")
                                
                                if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {
                                    linksFound++
                                }
                            }
                            
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${e.message}")
                        }
                    }
                }
                
                // Look for gleam.config in scripts (as shown in your HTML)
                doc.select("script").forEach { script ->
                    val scriptContent = script.html()
                    
                    if (scriptContent.contains("gleam.config", ignoreCase = true)) {
                        Log.d("MaxSeries", "🎬 Script gleam.config encontrado")
                        
                        // Extract gleam.config URL
                        val gleamUrlRegex = Regex(""""url"\s*:\s*"([^"]+)"""")
                        val gleamMatch = gleamUrlRegex.find(scriptContent)
                        
                        if (gleamMatch != null) {
                            val gleamUrl = gleamMatch.groupValues[1].replace("\\/", "/")
                            Log.d("MaxSeries", "🎯 Gleam URL: $gleamUrl")
                            
                            // This might be the base URL for the video player
                            if (gleamUrl.startsWith("http")) {
                                try {
                                    if (loadExtractor(gleamUrl, data, subtitleCallback, callback)) {
                                        linksFound++
                                    }
                                } catch (e: Exception) {
                                    Log.e("MaxSeries", "❌ Erro ao processar gleam URL: ${e.message}")
                                }
                            }
                        }
                        
                        // Look for other video URLs in the script
                        val videoPatterns = listOf(
                            Regex(""""file"\s*:\s*"([^"]+)""""),
                            Regex(""""source"\s*:\s*"([^"]+)""""),
                            Regex(""""video"\s*:\s*"([^"]+)""""),
                            Regex("""https://[^"'\s]+\.(?:m3u8|mp4|mkv|avi)""")
                        )
                        
                        videoPatterns.forEach { pattern ->
                            pattern.findAll(scriptContent).forEach { match ->
                                val videoUrl = match.groupValues.getOrNull(1) ?: match.value
                                
                                if (videoUrl.startsWith("http") && 
                                    !videoUrl.contains("ads", ignoreCase = true) &&
                                    !videoUrl.contains("analytics", ignoreCase = true)) {
                                    
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
                
            } else {
                // Standard processing for non-iframe URLs
                Log.d("MaxSeries", "🔄 Processamento padrão")
                val doc = app.get(data).document
                
                // Look for iframe that contains the episode player
                val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                    ?: doc.selectFirst("iframe[src*=playerthree]")?.attr("src")
                    ?: doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
                    ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
                    ?: doc.selectFirst("#player iframe")?.attr("src")
                
                if (!mainIframe.isNullOrEmpty()) {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "📺 Carregando iframe principal: $iframeSrc")
                    
                    try {
                        if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {
                            linksFound++
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                    }
                }
                
                // Method 2: Look for DooPlay AJAX players (fallback)
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
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro geral no loadLinks: ${e.message}")
        }
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }
}