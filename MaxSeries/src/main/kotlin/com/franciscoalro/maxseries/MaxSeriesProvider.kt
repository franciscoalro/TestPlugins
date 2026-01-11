package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.LoadResponse.Companion.addActors
import com.lagradost.cloudstream3.LoadResponse.Companion.addTrailer
import org.jsoup.nodes.Element
import com.franciscoalro.maxseries.extractors.*

class MaxSeriesProvider : MainAPI() { // all providers must be an instance of MainAPI
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(
        TvType.Movie,
        TvType.TvSeries,
        TvType.Anime
    )

    override val mainPage = mainPageOf(
        "$mainUrl/movies/page/" to "Filmes",
        "$mainUrl/series/page/" to "Séries",
        "$mainUrl/animes/page/" to "Animes"
    )

    override suspend fun getMainPage(
        page: Int,
        request: MainPageRequest
    ): HomePageResponse {
        val document = app.get(request.data + page).document
        val home = document.select("article.item").mapNotNull {
            it.toSearchResult()
        }
        return newHomePageResponse(request.name, home)
    }

    private fun Element.toSearchResult(): SearchResponse? {
        val title = this.selectFirst("h3.title")?.text()?.trim() ?: return null
        val href = this.selectFirst("a")?.attr("href") ?: return null
        val posterUrl = this.selectFirst("img")?.attr("src")
        val quality = this.selectFirst(".quality")?.text()

        // Garantir URL absoluta
        val absoluteHref = if (href.startsWith("http")) href else "$mainUrl$href"
        
        // Detectar tipo baseado na URL ou classe
        val tvType = when {
            href.contains("/series/") -> TvType.TvSeries
            href.contains("/filme/") || href.contains("/movie/") -> TvType.Movie
            href.contains("/anime/") -> TvType.Anime
            this.selectFirst(".item_type")?.text()?.contains("SÉRIE", true) == true -> TvType.TvSeries
            else -> TvType.TvSeries // Default para séries
        }

        return newMovieSearchResponse(title, absoluteHref, tvType) {
            this.posterUrl = posterUrl
            this.quality = getQualityFromString(quality)
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        val document = app.get("$mainUrl/?s=$query").document

        return document.select("article.item").mapNotNull {
            it.toSearchResult()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        val document = app.get(url).document

        val title = document.selectFirst("h1.entry-title")?.text()?.trim()
            ?: return null
        val poster = document.selectFirst(".poster img")?.attr("src")
        val tags = document.select(".genres a").map { it.text() }
        val year = document.selectFirst(".year")?.text()?.toIntOrNull()
        val tvType = if (document.select(".seasons-lst").isNotEmpty()) TvType.TvSeries else TvType.Movie
        val description = document.selectFirst(".description p")?.text()?.trim()
        val trailer = document.selectFirst("iframe[src*=youtube]")?.attr("src")
        val ratingText = document.selectFirst(".rating .value")?.text()
        val actors = document.select(".cast .person").map {
            Actor(it.selectFirst(".name")?.text() ?: "", it.selectFirst("img")?.attr("src"))
        }

        val recommendations = document.select(".related-posts .item").mapNotNull {
            it.toSearchResult()
        }

        return if (tvType == TvType.TvSeries) {
            val episodes = document.select(".seasons-lst .season").flatMap { season ->
                val seasonNumber = season.selectFirst(".season-title")?.text()?.filter { it.isDigit() }?.toIntOrNull() ?: 1
                season.select(".episode-item").mapNotNull { ep ->
                    val epNum = ep.selectFirst(".episode-number")?.text()?.toIntOrNull()
                    val epTitle = ep.selectFirst(".episode-title")?.text()
                    val epUrl = ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null
                    
                    newEpisode(epUrl) {
                        this.name = epTitle
                        this.season = seasonNumber
                        this.episode = epNum
                    }
                }
            }
            newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster
                this.year = year
                this.plot = description
                this.tags = tags
                addActors(actors)
                this.recommendations = recommendations
                addTrailer(trailer)
            }
        } else {
            newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster
                this.year = year
                this.plot = description
                this.tags = tags
                addActors(actors)
                this.recommendations = recommendations
                addTrailer(trailer)
            }
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val document = app.get(data).document
        
        // Log para debug
        println("🔍 MaxSeries v50 - Carregando links para: $data")
        
        // Buscar todos os botões de player (incluindo data-show-player)
        val playerButtons = document.select("button[data-source], button[data-show-player]")
        println("🎯 Encontrados ${playerButtons.size} botões de player")
        
        var sourcesFound = 0
        
        playerButtons.forEach { button ->
            try {
                val sourceName = button.text().trim()
                val sourceUrl = button.attr("data-source").ifEmpty { 
                    button.attr("data-show-player") 
                }
                
                if (sourceUrl.isNotEmpty() && !isYouTubeUrl(sourceUrl)) {
                    println("🎬 Processando fonte: $sourceName -> $sourceUrl")
                    
                    when {
                        // DoodStream e clones (Fase 1 - Expandido)
                        sourceUrl.contains("dood", true) ||
                        sourceUrl.contains("bysebuho", true) ||
                        sourceUrl.contains("g9r6", true) ||
                        sourceUrl.contains("vidplay", true) ||
                        sourceUrl.contains("myvidplay", true) -> {
                            println("🟢 Detectado DoodStream/VidPlay: $sourceName")
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        // MegaEmbed (Fase 2 - WebView V4 com captura dinâmica de CDN)
                        sourceUrl.contains("megaembed", true) -> {
                            println("🔥 Detectado MegaEmbed: $sourceName")
                            val megaExtractor = MegaEmbedExtractorV4()
                            megaExtractor.getUrl(sourceUrl, data, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        // PlayerEmbedAPI (Fase 3 - Enhanced Chain)
                        sourceUrl.contains("playerembedapi", true) ||
                        sourceUrl.contains("embed", true) -> {
                            println("🎯 Detectado PlayerEmbedAPI: $sourceName")
                            val playerExtractor = PlayerEmbedAPIExtractor()
                            playerExtractor.getUrl(sourceUrl, data, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        else -> {
                            println("🔄 Tentando extrator padrão CloudStream para: $sourceName")
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            sourcesFound++
                        }
                    }
                } else if (isYouTubeUrl(sourceUrl)) {
                    println("🚫 Ignorando link do YouTube: $sourceName -> $sourceUrl")
                } else {
                    println("⚠️ Botão sem URL: $sourceName")
                }
            } catch (e: Exception) {
                println("❌ Erro ao processar fonte ${button.text()}: ${e.message}")
            }
        }
        
        // Fallback: buscar iframes se não encontrou botões
        if (playerButtons.isEmpty()) {
            println("🔍 Nenhum botão encontrado, buscando iframes...")
            
            val iframes = document.select("iframe[src]")
            println("📺 Encontrados ${iframes.size} iframes")
            
            iframes.forEach { iframe ->
                val iframeUrl = iframe.attr("src")
                if (iframeUrl.isNotEmpty() && !isYouTubeUrl(iframeUrl)) {
                    println("📺 Processando iframe: $iframeUrl")
                    
                    // Extrair episode ID do iframe se necessário
                    val episodeId = extractEpisodeIdFromIframe(iframe, data)
                    if (episodeId != null) {
                        println("🆔 Episode ID extraído: $episodeId")
                        
                        when {
                            iframeUrl.contains("megaembed", true) -> {
                                println("🔥 Iframe MegaEmbed detectado")
                                val megaExtractor = MegaEmbedExtractorV4()
                                megaExtractor.getUrl(iframeUrl, data, subtitleCallback, callback)
                                sourcesFound++
                            }
                            else -> {
                                loadExtractor(iframeUrl, subtitleCallback, callback)
                                sourcesFound++
                            }
                        }
                    } else {
                        loadExtractor(iframeUrl, subtitleCallback, callback)
                        sourcesFound++
                    }
                } else if (isYouTubeUrl(iframeUrl)) {
                    println("🚫 Ignorando iframe do YouTube: $iframeUrl")
                }
            }
        }
        
        println("✅ MaxSeries processou $sourcesFound fontes")
        return sourcesFound > 0
    }
    
    private suspend fun extractEpisodeIdFromIframe(iframe: Element, pageUrl: String): String? {
        // Tentar extrair do src do iframe
        val iframeSrc = iframe.attr("src")
        
        // Padrão 1: #123_456 no final da URL
        val hashPattern = "\\#(\\d+)_(\\d+)".toRegex()
        hashPattern.find(pageUrl)?.let { match ->
            return "${match.groupValues[1]}_${match.groupValues[2]}"
        }
        
        // Padrão 2: episode/123/456 na URL
        val episodePattern = "episode/(\\d+)/(\\d+)".toRegex()
        episodePattern.find(pageUrl)?.let { match ->
            return "${match.groupValues[1]}_${match.groupValues[2]}"
        }
        
        // Padrão 3: Buscar no HTML do iframe
        try {
            val iframeDoc = app.get(iframeSrc).document
            val scriptContent = iframeDoc.select("script").joinToString(" ") { it.html() }
            
            // Buscar padrões comuns de episode ID
            val patterns = listOf(
                "episode['\"]?:\\s*['\"]?(\\d+)['\"]?",
                "season['\"]?:\\s*['\"]?(\\d+)['\"]?",
                "ep['\"]?:\\s*['\"]?(\\d+)['\"]?"
            )
            
            patterns.forEach { pattern ->
                pattern.toRegex().find(scriptContent)?.let { match ->
                    return match.groupValues[1]
                }
            }
        } catch (e: Exception) {
            println("⚠️ Erro ao extrair episode ID do iframe: ${e.message}")
        }
        
        return null
    }
    
    private fun isYouTubeUrl(url: String): Boolean {
        return url.contains("youtube.com", true) || 
               url.contains("youtu.be", true) ||
               url.contains("youtube-nocookie.com", true)
    }
}
