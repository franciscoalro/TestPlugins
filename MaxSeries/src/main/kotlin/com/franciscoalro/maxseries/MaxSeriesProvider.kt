package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// MaxSeries Provider - Versão Final baseada em análise GeckoDriver
// Análise completa realizada em 08/01/2026
// - 5 episódios detectados por série
// - Players: playerembedapi.link, megaembed.link
// - Estrutura: playerthree.online iframes com navegação por fragmentos
// - gleam.config detectado com configurações de player

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
            
            Log.d("MaxSeries", "📺 Analisando série (GeckoFinal): $title")
            
            // Método baseado na análise GeckoDriver: playerthree.online iframes
            val mainIframe = doc.selectFirst("iframe")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                try {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "🖼️ Carregando iframe: $iframeSrc")
                    
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Extrair temporadas da navegação (baseado na análise)
                    val seasons = mutableMapOf<String, Int>()
                    iframeDoc.select("ul.header-navigation li[data-season-id]").forEach { seasonLi ->
                        val seasonId = seasonLi.attr("data-season-id")
                        val seasonNumber = seasonLi.attr("data-season-number").toIntOrNull() ?: 1
                        if (seasonId.isNotEmpty()) {
                            seasons[seasonId] = seasonNumber
                            Log.d("MaxSeries", "🎬 Temporada detectada: $seasonNumber (ID: $seasonId)")
                        }
                    }
                    
                    // Se não encontrar temporadas na navegação, usar fallback
                    if (seasons.isEmpty()) {
                        seasons["default"] = 1
                        Log.d("MaxSeries", "🎬 Usando temporada padrão: 1")
                    }
                    
                    // Extrair episódios (baseado na análise: li[data-season-id][data-episode-id] a)
                    val episodeElements = iframeDoc.select("li[data-season-id][data-episode-id] a")
                    if (episodeElements.isNotEmpty()) {
                        Log.d("MaxSeries", "📺 Encontrados ${episodeElements.size} episódios via data attributes")
                        
                        episodeElements.forEachIndexed { index, epLink ->
                            val seasonId = epLink.parent()?.attr("data-season-id") ?: "default"
                            val episodeId = epLink.parent()?.attr("data-episode-id") ?: ""
                            val epHref = epLink.attr("href")
                            
                            if (epHref.isNotEmpty()) {
                                val epNum = index + 1
                                val seasonNum = seasons[seasonId] ?: 1
                                val epTitle = "Episódio $epNum"
                                
                                // URL do episódio inclui o iframe base + fragmento
                                val episodeUrl = if (epHref.startsWith("#")) "$iframeSrc$epHref" else epHref
                                
                                episodes.add(newEpisode(episodeUrl) {
                                    this.name = epTitle
                                    this.episode = epNum
                                    this.season = seasonNum
                                })
                                
                                Log.d("MaxSeries", "✅ Episódio: T${seasonNum}E${epNum} - $epTitle -> $episodeUrl")
                            }
                        }
                    } else {
                        // Fallback: procurar por links com fragmentos (#)
                        Log.d("MaxSeries", "🔄 Fallback: procurando links com fragmentos")
                        
                        val fragmentLinks = iframeDoc.select("a[href*='#']")
                        fragmentLinks.forEachIndexed { index, link ->
                            val href = link.attr("href")
                            if (href.contains("#") && href.contains("_")) {
                                val epNum = index + 1
                                val episodeUrl = if (href.startsWith("#")) "$iframeSrc$href" else href
                                
                                episodes.add(newEpisode(episodeUrl) {
                                    this.name = "Episódio $epNum"
                                    this.episode = epNum
                                    this.season = 1
                                })
                                
                                Log.d("MaxSeries", "✅ Episódio (fallback): E${epNum} -> $episodeUrl")
                            }
                        }
                    }
                    
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                }
            }
            
            // Fallback final se nenhum episódio for encontrado
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "⚠️ Fallback final: criando episódio único")
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
        Log.d("MaxSeries", "📺 Processando links (GeckoFinal): $data")
        
        var linksFound = 0
        
        try {
            // Verificar se é uma URL de episódio do iframe (contém #)
            if (data.contains("#") && data.contains("playerthree.online")) {
                Log.d("MaxSeries", "🎯 Processando episódio do iframe playerthree")
                
                // Carregar a página do iframe com o fragmento do episódio
                val doc = app.get(data).document
                
                // Método 1: Procurar botões de player (baseado na análise)
                val playerButtons = doc.select("button[data-source], .btn[data-source], button[data-show-player]")
                
                if (playerButtons.isNotEmpty()) {
                    Log.d("MaxSeries", "🎮 Encontrados ${playerButtons.size} players")
                    
                    playerButtons.forEach { button ->
                        val playerName = button.text().trim().ifEmpty { "Player" }
                        Log.d("MaxSeries", "🔄 Testando player: $playerName")
                        
                        try {
                            // Procurar URLs nos atributos (baseado na análise)
                            val dataSource = button.attr("data-source")
                            val dataUrl = button.attr("data-url")
                            val dataPlayer = button.attr("data-player")
                            
                            val videoUrl = dataSource.ifEmpty { dataUrl.ifEmpty { dataPlayer } }
                            
                            if (videoUrl.isNotEmpty() && videoUrl.startsWith("http")) {
                                Log.d("MaxSeries", "🎯 URL encontrada: $videoUrl")
                                
                                if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {
                                    linksFound++
                                    Log.d("MaxSeries", "✅ Sucesso: $playerName -> $videoUrl")
                                }
                            }
                            
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${e.message}")
                        }
                    }
                }
                
                // Método 2: Procurar gleam.config nos scripts (baseado na análise)
                if (linksFound == 0) {
                    Log.d("MaxSeries", "🔄 Procurando gleam.config")
                    
                    doc.select("script").forEach { script ->
                        val scriptContent = script.html()
                        
                        if (scriptContent.contains("gleam.config", ignoreCase = true)) {
                            Log.d("MaxSeries", "🎬 Script gleam.config encontrado")
                            
                            // Extrair URL do gleam.config
                            val gleamUrlRegex = Regex(""""url"\s*:\s*"([^"]+)"""")
                            val gleamMatch = gleamUrlRegex.find(scriptContent)
                            
                            if (gleamMatch != null) {
                                val gleamUrl = gleamMatch.groupValues[1].replace("\\/", "/")
                                Log.d("MaxSeries", "🎯 Gleam URL: $gleamUrl")
                                
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
                            
                            // Procurar outras URLs de vídeo no script
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
                }
                
            } else {
                // Processamento padrão para URLs que não são de iframe
                Log.d("MaxSeries", "🔄 Processamento padrão")
                val doc = app.get(data).document
                
                // Procurar iframe principal
                val mainIframe = doc.selectFirst("iframe")?.attr("src")
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
                
                // Fallback: DooPlay AJAX players
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
                                Log.e("MaxSeries", "❌ Erro no player AJAX: ${e.message}")
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