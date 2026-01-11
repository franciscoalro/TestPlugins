package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.LoadResponse.Companion.addActors
import com.lagradost.cloudstream3.LoadResponse.Companion.addTrailer
import org.jsoup.nodes.Element
import com.franciscoalro.maxseries.extractors.*
import android.util.Log

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
        return try {
            val document = app.get(request.data + page).document
            val home = document.select("div.items article.item").mapNotNull {
                it.toSearchResult()
            }
            if (home.isEmpty()) {
                android.util.Log.d("MaxSeries", "⚠️ Nenhum resultado encontrado na página ${request.name} (página $page)")
            }
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            android.util.Log.e("MaxSeries", "❌ Erro ao carregar página principal ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private fun Element.toSearchResult(): SearchResponse? {
        return try {
            val title = this.selectFirst("h3.title, h3")?.text()?.trim() ?: return null
            val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
            
            // Melhor busca de imagem (similar ao AnimesOnlineCC)
            val img = this.selectFirst("img")
            val posterUrl = fixUrlNull(
                img?.attr("src")
                    ?: img?.attr("data-src")
                    ?: img?.attr("data-lazy-src")
                    ?: img?.attr("data-original")
            )
            
            val quality = this.selectFirst(".quality")?.text()
            
            // Detectar tipo baseado na URL ou classe
            val tvType = when {
                href.contains("/series/") -> TvType.TvSeries
                href.contains("/filme/") || href.contains("/movie/") -> TvType.Movie
                href.contains("/anime/") -> TvType.Anime
                this.selectFirst(".item_type")?.text()?.contains("SÉRIE", true) == true -> TvType.TvSeries
                else -> TvType.TvSeries // Default para séries
            }

            newMovieSearchResponse(title, href, tvType) {
                this.posterUrl = posterUrl
                this.quality = getQualityFromString(quality)
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao processar item: ${e.message}")
            null
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) {
            android.util.Log.d("MaxSeries", "⚠️ Pesquisa vazia, retornando lista vazia")
            return emptyList()
        }
        
        return try {
            android.util.Log.d("MaxSeries", "🔍 Pesquisando por: $query")
            val document = app.get("$mainUrl/?s=$query").document
            
            val results = document.select("div.items article.item").mapNotNull {
                it.toSearchResult()
            }
            
            android.util.Log.d("MaxSeries", "✅ Encontrados ${results.size} resultados para '$query'")
            results
        } catch (e: Exception) {
            android.util.Log.e("MaxSeries", "❌ Erro na pesquisa '$query': ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            Log.d("MaxSeries", "📖 Carregando detalhes: $url")
            val document = app.get(url).document

            val title = document.selectFirst("h1.entry-title, h1")?.text()?.trim()
            if (title.isNullOrBlank()) {
                Log.e("MaxSeries", "❌ Título não encontrado em: $url")
                return null
            }
            
            // Melhor busca de poster (similar ao AnimesOnlineCC)
            val img = document.selectFirst(".poster img, div.poster img, .sheader .poster img")
            val poster = fixUrlNull(
                img?.attr("src")
                    ?: img?.attr("data-src")
                    ?: img?.attr("data-lazy-src")
                    ?: img?.attr("data-original")
                    ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            )
            
            val tags = document.select(".genres a, .sgeneros a").map { it.text() }
            val year = document.selectFirst(".year, span.date, span.year, .extra span")?.text()
                ?.replace("\\D".toRegex(), "")?.take(4)?.toIntOrNull()
            val tvType = if (document.select(".seasons-lst, ul.episodios").isNotEmpty()) TvType.TvSeries else TvType.Movie
            val description = document.selectFirst(".description p, div.description, div.wp-content")?.text()?.trim()
            val trailer = document.selectFirst("iframe[src*=youtube]")?.attr("src")
            val ratingText = document.selectFirst(".rating .value")?.text()
            val actors = document.select(".cast .person").map {
                Actor(it.selectFirst(".name")?.text() ?: "", it.selectFirst("img")?.attr("src"))
            }

            val recommendations = document.select(".related-posts .item, .items article.item").mapNotNull {
                it.toSearchResult()
            }

            Log.d("MaxSeries", "✅ Carregado '$title' como $tvType")

            return if (tvType == TvType.TvSeries) {
                val episodes = document.select(".seasons-lst .season, ul.episodios li").flatMap { season ->
                    if (season.tagName() == "li") {
                        // Formato AnimesOnlineCC
                        val epTitle = season.selectFirst(".episodiotitle a, a")?.text() ?: return@flatMap emptyList()
                        val epHref = fixUrl(season.selectFirst("a")?.attr("href") ?: return@flatMap emptyList())
                        val epNum = epTitle.replace("\\D".toRegex(), "").toIntOrNull()
                        
                        listOf(newEpisode(epHref) {
                            this.name = epTitle
                            this.episode = epNum
                        })
                    } else {
                        // Formato MaxSeries original
                        val seasonNumber = season.selectFirst(".season-title")?.text()?.filter { it.isDigit() }?.toIntOrNull() ?: 1
                        season.select(".episode-item").mapNotNull { ep ->
                            val epNum = ep.selectFirst(".episode-number")?.text()?.toIntOrNull()
                            val epTitle = ep.selectFirst(".episode-title")?.text()
                            val epUrl = ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null
                            
                            newEpisode(fixUrl(epUrl)) {
                                this.name = epTitle
                                this.season = seasonNumber
                                this.episode = epNum
                            }
                        }
                    }
                }
                
                Log.d("MaxSeries", "✅ Série '$title' com ${episodes.size} episódios")
                
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
                Log.d("MaxSeries", "✅ Filme '$title'")
                
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
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao carregar detalhes de $url: ${e.message}")
            null
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
        Log.d("MaxSeries", "🔍 MaxSeries v54 - Carregando links para: $data")
        
        // Buscar todos os botões de player (incluindo data-show-player)
        val playerButtons = document.select("button[data-source], button[data-show-player]")
        Log.d("MaxSeries", "🎯 Encontrados ${playerButtons.size} botões de player")
        
        var sourcesFound = 0
        
        playerButtons.forEach { button ->
            try {
                val sourceName = button.text().trim()
                val sourceUrl = button.attr("data-source").ifEmpty { 
                    button.attr("data-show-player") 
                }
                
                if (sourceUrl.isNotEmpty() && !isYouTubeUrl(sourceUrl)) {
                    Log.d("MaxSeries", "🎬 Processando fonte: $sourceName -> $sourceUrl")
                    
                    when {
                        // DoodStream e clones (Fase 1 - Expandido)
                        sourceUrl.contains("dood", true) ||
                        sourceUrl.contains("bysebuho", true) ||
                        sourceUrl.contains("g9r6", true) ||
                        sourceUrl.contains("vidplay", true) ||
                        sourceUrl.contains("myvidplay", true) -> {
                            Log.d("MaxSeries", "🟢 Detectado DoodStream/VidPlay: $sourceName")
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        // MegaEmbed (Fase 2 - WebView V4 com captura dinâmica de CDN)
                        sourceUrl.contains("megaembed", true) -> {
                            Log.d("MaxSeries", "🔥 Detectado MegaEmbed: $sourceName")
                            val megaExtractor = MegaEmbedExtractorV4()
                            megaExtractor.getUrl(sourceUrl, data, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        // PlayerEmbedAPI (Fase 3 - Enhanced Chain)
                        sourceUrl.contains("playerembedapi", true) ||
                        sourceUrl.contains("embed", true) -> {
                            Log.d("MaxSeries", "🎯 Detectado PlayerEmbedAPI: $sourceName")
                            val playerExtractor = PlayerEmbedAPIExtractor()
                            playerExtractor.getUrl(sourceUrl, data, subtitleCallback, callback)
                            sourcesFound++
                        }
                        
                        else -> {
                            Log.d("MaxSeries", "🔄 Tentando extrator padrão CloudStream para: $sourceName")
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            sourcesFound++
                        }
                    }
                } else if (isYouTubeUrl(sourceUrl)) {
                    Log.d("MaxSeries", "🚫 Ignorando link do YouTube: $sourceName -> $sourceUrl")
                } else {
                    Log.d("MaxSeries", "⚠️ Botão sem URL: $sourceName")
                }
            } catch (e: Exception) {
                Log.e("MaxSeries", "❌ Erro ao processar fonte ${button.text()}: ${e.message}")
            }
        }
        
        // Fallback: buscar iframes se não encontrou botões
        if (playerButtons.isEmpty()) {
            Log.d("MaxSeries", "🔍 Nenhum botão encontrado, buscando iframes...")
            
            val iframes = document.select("iframe[src]")
            Log.d("MaxSeries", "📺 Encontrados ${iframes.size} iframes")
            
            iframes.forEach { iframe ->
                val iframeUrl = iframe.attr("src")
                if (iframeUrl.isNotEmpty() && !isYouTubeUrl(iframeUrl)) {
                    Log.d("MaxSeries", "📺 Processando iframe: $iframeUrl")
                    
                    // Extrair episode ID do iframe se necessário
                    val episodeId = extractEpisodeIdFromIframe(iframe, data)
                    if (episodeId != null) {
                        Log.d("MaxSeries", "🆔 Episode ID extraído: $episodeId")
                        
                        when {
                            iframeUrl.contains("megaembed", true) -> {
                                Log.d("MaxSeries", "🔥 Iframe MegaEmbed detectado")
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
                    Log.d("MaxSeries", "🚫 Ignorando iframe do YouTube: $iframeUrl")
                }
            }
        }
        
        Log.d("MaxSeries", "✅ MaxSeries processou $sourcesFound fontes")
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
            Log.e("MaxSeries", "⚠️ Erro ao extrair episode ID do iframe: ${e.message}")
        }
        
        return null
    }
    
    private fun isYouTubeUrl(url: String): Boolean {
        return url.contains("youtube.com", true) || 
               url.contains("youtu.be", true) ||
               url.contains("youtube-nocookie.com", true)
    }
}
