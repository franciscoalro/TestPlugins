package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

// MaxSeries Provider - Versão 23.0 - SIMPLIFICADO
// Apenas loadExtractor sem newExtractorLink problemático
// Baseado em descobertas HAR com código limpo

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
            
            Log.d("MaxSeries", "📺 Analisando série (v23.0): $title")
            
            val mainIframe = doc.selectFirst("iframe")?.attr("src")
            
            if (!mainIframe.isNullOrEmpty()) {
                try {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "🖼️ Carregando iframe: $iframeSrc")
                    
                    val iframeDoc = app.get(iframeSrc).document
                    
                    val seasons = mutableMapOf<String, Int>()
                    iframeDoc.select("ul.header-navigation li[data-season-id]").forEach { seasonLi ->
                        val seasonId = seasonLi.attr("data-season-id")
                        val seasonNumber = seasonLi.attr("data-season-number").toIntOrNull() ?: 1
                        if (seasonId.isNotEmpty()) {
                            seasons[seasonId] = seasonNumber
                        }
                    }
                    
                    if (seasons.isEmpty()) {
                        seasons["default"] = 1
                    }
                    
                    val episodeElements = iframeDoc.select("li[data-season-id][data-episode-id] a")
                    if (episodeElements.isNotEmpty()) {
                        episodeElements.forEachIndexed { index, epLink ->
                            val seasonId = epLink.parent()?.attr("data-season-id") ?: "default"
                            val episodeId = epLink.parent()?.attr("data-episode-id") ?: ""
                            val epHref = epLink.attr("href")
                            
                            if (epHref.isNotEmpty()) {
                                val epNum = index + 1
                                val seasonNum = seasons[seasonId] ?: 1
                                val epTitle = "Episódio $epNum"
                                
                                val episodeUrl = if (epHref.startsWith("#")) "$iframeSrc$epHref" else epHref
                                
                                episodes.add(newEpisode(episodeUrl) {
                                    this.name = epTitle
                                    this.episode = epNum
                                    this.season = seasonNum
                                })
                            }
                        }
                    }
                    
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                }
            }
            
            if (episodes.isEmpty()) {
                episodes.add(newEpisode(url) {
                    this.name = "Episódio 1"
                    this.episode = 1
                    this.season = 1
                })
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
        Log.d("MaxSeries", "📺 Processando links (v23.0): $data")
        
        var linksFound = 0
        
        try {
            if (data.contains("#") && data.contains("playerthree.online")) {
                val fragmentMatch = Regex("#\\d+_(\\d+)").find(data)
                if (fragmentMatch != null) {
                    val episodeId = fragmentMatch.groupValues[1]
                    
                    // Headers baseados na análise HAR
                    val harHeaders = mapOf(
                        "Referer" to data,
                        "X-Requested-With" to "XMLHttpRequest",
                        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
                    )
                    
                    val baseUrl = "https://playerthree.online"
                    val ajaxUrl = "$baseUrl/episodio/$episodeId"
                    
                    Log.d("MaxSeries", "📡 AJAX HAR: $ajaxUrl")
                    
                    val ajaxResponse = app.get(ajaxUrl, headers = harHeaders)
                    
                    if (ajaxResponse.isSuccessful) {
                        val ajaxDoc = ajaxResponse.document
                        
                        val playerButtons = ajaxDoc.select("button[data-source], .btn[data-source]")
                        
                        playerButtons.forEach { button ->
                            val playerName = button.text().trim().ifEmpty { "Player" }
                            val dataSource = button.attr("data-source")
                            
                            if (dataSource.isNotEmpty() && dataSource.startsWith("http")) {
                                if (!dataSource.contains("youtube", ignoreCase = true) && 
                                    !dataSource.contains("trailer", ignoreCase = true)) {
                                    
                                    Log.d("MaxSeries", "🎯 Player: $playerName -> $dataSource")
                                    
                                    try {
                                        // Usar extractor padrão do CloudStream
                                        if (loadExtractor(dataSource, data, subtitleCallback, callback)) {
                                            linksFound++
                                            Log.d("MaxSeries", "✅ Extractor: $playerName")
                                        }
                                    } catch (e: Exception) {
                                        Log.e("MaxSeries", "❌ Erro player $playerName: ${e.message}")
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                // Processamento padrão para URLs que não são de iframe
                val doc = app.get(data).document
                
                val mainIframe = doc.selectFirst("iframe")?.attr("src")
                if (!mainIframe.isNullOrEmpty()) {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    
                    try {
                        if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {
                            linksFound++
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro iframe: ${e.message}")
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