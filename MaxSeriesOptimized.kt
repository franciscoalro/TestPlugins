package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
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
        
        val isSeries = url.contains("/series/") || url.contains("/tv/") || 
                      doc.selectFirst(".seasons, .se-c, .episodios")?.let { true } ?: false

        if (isSeries) {
            val episodes = mutableListOf<Episode>()
            
            Log.d("MaxSeries", "📺 Analisando série: $title")
            
            // Método 1: DooPlay padrão com temporadas
            doc.select("div.se-c").forEachIndexed { seasonIndex, seasonDiv ->
                val seasonNum = seasonDiv.attr("id").replace("season-", "").toIntOrNull() 
                    ?: (seasonIndex + 1)
                
                Log.d("MaxSeries", "🎬 Processando temporada $seasonNum")
                
                seasonDiv.select("ul.episodios li").forEachIndexed { epIndex, epLi ->
                    val epA = epLi.selectFirst("a")
                    if (epA != null) {
                        val epTitle = epA.text().trim()
                        val epHref = epA.attr("href")
                        
                        if (epHref.isNotEmpty()) {
                            // Extrair número do episódio de múltiplas fontes
                            val epNum = epLi.selectFirst(".numerando")?.text()?.let { numerando ->
                                // Formato: "1 - 1" ou "S1E1" ou "1x1"
                                numerando.split("-").lastOrNull()?.trim()?.toIntOrNull()
                                    ?: numerando.replace(Regex("[^0-9]"), "").toIntOrNull()
                            } ?: epTitle.replace(Regex(".*?[Ee]pisódio\\s*(\\d+).*"), "$1").toIntOrNull()
                                ?: epTitle.replace(Regex(".*?(\\d+).*"), "$1").toIntOrNull()
                                ?: (epIndex + 1)
                            
                            episodes.add(newEpisode(epHref) {
                                this.name = if (epTitle.isNotEmpty()) epTitle else "Episódio $epNum"
                                this.episode = epNum
                                this.season = seasonNum
                            })
                            
                            Log.d("MaxSeries", "✅ Episódio: T${seasonNum}E${epNum} - $epTitle")
                        }
                    }
                }
            }
            
            // Método 2: Estruturas alternativas
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "🔄 Tentando estruturas alternativas")
                
                val episodeSelectors = listOf(
                    "ul.episodios li a",
                    ".episodios a",
                    ".episode-list a",
                    ".episodes a",
                    "li[data-episode] a",
                    ".wp-content a[href*=episodio]",
                    ".wp-content a[href*=episode]"
                )
                
                episodeSelectors.forEach { selector ->
                    if (episodes.isEmpty()) {
                        doc.select(selector).forEachIndexed { index, epA ->
                            val epTitle = epA.text().trim()
                            val epHref = epA.attr("href")
                            
                            if (epHref.isNotEmpty() && epTitle.isNotEmpty() && 
                                (epHref.contains("episodio") || epHref.contains("episode") || 
                                 epTitle.contains("episódio", ignoreCase = true) || 
                                 epTitle.contains("episode", ignoreCase = true))) {
                                
                                val epNum = epTitle.replace(Regex(".*?[Ee]pisódio\\s*(\\d+).*"), "$1").toIntOrNull()
                                    ?: epTitle.replace(Regex(".*?(\\d+).*"), "$1").toIntOrNull()
                                    ?: (index + 1)
                                
                                episodes.add(newEpisode(epHref) {
                                    this.name = epTitle
                                    this.episode = epNum
                                    this.season = 1
                                })
                                
                                Log.d("MaxSeries", "✅ Episódio alternativo: E${epNum} - $epTitle")
                            }
                        }
                    }
                }
            }
            
            // Método 3: Fallback inteligente
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "🔄 Aplicando fallback inteligente")
                
                val pageText = doc.text()
                val hasMultipleEpisodes = pageText.contains("temporada", ignoreCase = true) ||
                    pageText.contains("season", ignoreCase = true) ||
                    pageText.contains("episódios", ignoreCase = true) ||
                    pageText.contains("episodes", ignoreCase = true)
                
                if (hasMultipleEpisodes) {
                    // Detectar episódios no texto
                    val episodePatterns = listOf(
                        Regex("(?i)episódio\\s+(\\d+)"),
                        Regex("(?i)episode\\s+(\\d+)"),
                        Regex("(?i)ep\\s+(\\d+)")
                    )
                    
                    val foundEpisodes = mutableSetOf<Int>()
                    episodePatterns.forEach { pattern ->
                        pattern.findAll(pageText).forEach { match ->
                            val epNum = match.groupValues[1].toIntOrNull()
                            if (epNum != null && epNum <= 50 && !foundEpisodes.contains(epNum)) {
                                foundEpisodes.add(epNum)
                            }
                        }
                    }
                    
                    if (foundEpisodes.isNotEmpty()) {
                        foundEpisodes.sorted().forEach { epNum ->
                            episodes.add(newEpisode(url) {
                                this.name = "Episódio $epNum"
                                this.episode = epNum
                                this.season = 1
                            })
                        }
                        Log.d("MaxSeries", "✅ Criados ${foundEpisodes.size} episódios do texto")
                    } else {
                        // Criar estrutura padrão
                        for (i in 1..10) {
                            episodes.add(newEpisode(url) {
                                this.name = "Episódio $i"
                                this.episode = i
                                this.season = 1
                            })
                        }
                        Log.d("MaxSeries", "✅ Criados 10 episódios padrão")
                    }
                } else {
                    // Episódio único
                    episodes.add(newEpisode(url) {
                        this.name = "Episódio 1"
                        this.episode = 1
                        this.season = 1
                    })
                    Log.d("MaxSeries", "✅ Criado episódio único")
                }
            }
            
            Log.d("MaxSeries", "✅ Total: ${episodes.size} episódios")

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
        Log.d("MaxSeries", "📺 Processando links: $data")
        
        var linksFound = 0
        
        try {
            val doc = app.get(data).document
            
            // Método 1: ViewPlayer com botões data-source (baseado no HTML real)
            val mainIframe = doc.selectFirst("iframe.metaframe")?.attr("src")
                ?: doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
                ?: doc.selectFirst("iframe[src*=embed]")?.attr("src")
                ?: doc.selectFirst("#player iframe")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                Log.d("MaxSeries", "📺 Carregando iframe: $iframeSrc")
                
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Procurar botões com data-source (estrutura real do ViewPlayer)
                    iframeDoc.select("button[data-source], .btn[data-source]").forEach { button ->
                        val source = button.attr("data-source")
                        val playerName = button.text().trim()
                        
                        if (source.isNotEmpty() && source.startsWith("http")) {
                            Log.d("MaxSeries", "🎯 Player: $playerName -> $source")
                            
                            try {
                                if (loadExtractor(source, data, subtitleCallback, callback)) {
                                    linksFound++
                                }
                            } catch (e: Exception) {
                                Log.e("MaxSeries", "❌ Erro no player $playerName: ${e.message}")
                            }
                        }
                    }
                    
                    // Procurar configurações JavaScript (gleam.config)
                    iframeDoc.select("script").forEach { script ->
                        val scriptContent = script.html()
                        
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
                                        
                                        Log.d("MaxSeries", "🎯 URL do script: $videoUrl")
                                        
                                        try {
                                            if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {
                                                linksFound++
                                            }
                                        } catch (e: Exception) {
                                            Log.e("MaxSeries", "❌ Erro na URL do script: ${e.message}")
                                        }
                                    }
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro no iframe: ${e.message}")
                }
            }
            
            // Método 2: DooPlay AJAX (fallback)
            if (linksFound == 0) {
                Log.d("MaxSeries", "🔄 Tentando DooPlay AJAX")
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
                            Log.e("MaxSeries", "❌ Erro AJAX: ${e.message}")
                        }
                    }
                }
            }
            
            // Método 3: Iframes diretos (fallback)
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
                                    Log.e("MaxSeries", "❌ Erro iframe direto: ${e.message}")
                                }
                            }
                        }
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro geral: ${e.message}")
        }
        
        Log.d("MaxSeries", "✅ Links encontrados: $linksFound")
        return linksFound > 0
    }
}