package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log
import org.json.JSONObject

// MaxSeries Provider - Versão 17.0 - BASEADO EM ANÁLISE HAR
// Descobertas do HAR:
// 1. MegaEmbed usa API específica: /api/v1/info?id=X e /api/v1/video?id=X
// 2. Headers específicos necessários (referer, user-agent)
// 3. Tokens de autenticação em URLs longas
// 4. Requisição AJAX para /episodio/{id} funciona

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
            
            Log.d("MaxSeries", "📺 Analisando série (v17.0 HAR-based): $title")
            
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
        Log.d("MaxSeries", "📺 Processando links (v17.0 HAR-based): $data")
        
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
                    
                    Log.d("MaxSeries", "📡 AJAX HAR-based: $ajaxUrl")
                    
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
                                    
                                    Log.d("MaxSeries", "🎯 Processando player HAR: $playerName -> $dataSource")
                                    
                                    try {
                                        // Usar extractors específicos baseados no HAR
                                        when {
                                            dataSource.contains("megaembed.link") -> {
                                                if (extractMegaEmbedHAR(dataSource, data, callback)) {
                                                    linksFound++
                                                    Log.d("MaxSeries", "✅ Sucesso MegaEmbed HAR: $playerName")
                                                }
                                            }
                                            dataSource.contains("playerembedapi.link") -> {
                                                // Usar extractor padrão para PlayerEmbedAPI
                                                if (loadExtractor(dataSource, data, subtitleCallback, callback)) {
                                                    linksFound++
                                                    Log.d("MaxSeries", "✅ Sucesso PlayerEmbedAPI: $playerName")
                                                }
                                            }
                                            else -> {
                                                // Fallback padrão
                                                if (loadExtractor(dataSource, data, subtitleCallback, callback)) {
                                                    linksFound++
                                                    Log.d("MaxSeries", "✅ Sucesso extractor padrão: $playerName")
                                                }
                                            }
                                        }
                                    } catch (e: Exception) {
                                        Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${e.message}")
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
                        Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro geral no loadLinks: ${e.message}")
        }
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }

    // EXTRACTOR MEGAEMBED BASEADO EM ANÁLISE HAR
    private suspend fun extractMegaEmbedHAR(
        url: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🔧 Extractor MegaEmbed HAR-based: $url")
        
        try {
            // Extrair ID do MegaEmbed da URL
            val idMatch = Regex("#([^&]+)").find(url)
            if (idMatch == null) {
                Log.d("MaxSeries", "❌ ID não encontrado na URL MegaEmbed")
                return false
            }
            
            val megaId = idMatch.groupValues[1]
            Log.d("MaxSeries", "🔍 MegaEmbed ID: $megaId")
            
            // Headers baseados na análise HAR
            val harHeaders = mapOf(
                "Referer" to "https://megaembed.link/",
                "Origin" to "https://megaembed.link",
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
            )
            
            // 1. Primeira requisição: /api/v1/info?id=X (descoberta no HAR)
            val infoUrl = "https://megaembed.link/api/v1/info?id=$megaId"
            Log.d("MaxSeries", "📡 HAR Info API: $infoUrl")
            
            val infoResponse = app.get(infoUrl, headers = harHeaders)
            
            if (infoResponse.isSuccessful) {
                Log.d("MaxSeries", "✅ Info API sucesso: ${infoResponse.code}")
                
                // 2. Segunda requisição: /api/v1/video?id=X&w=2144&h=1206&r=playerthree.online (descoberta no HAR)
                val videoUrl = "https://megaembed.link/api/v1/video?id=$megaId&w=2144&h=1206&r=playerthree.online"
                Log.d("MaxSeries", "📡 HAR Video API: $videoUrl")
                
                val videoResponse = app.get(videoUrl, headers = harHeaders)
                
                if (videoResponse.isSuccessful) {
                    Log.d("MaxSeries", "✅ Video API sucesso: ${videoResponse.code}")
                    
                    try {
                        val videoJson = JSONObject(videoResponse.text)
                        
                        // Procurar URL do vídeo na resposta JSON
                        val videoSrc = when {
                            videoJson.has("url") -> videoJson.getString("url")
                            videoJson.has("source") -> videoJson.getString("source")
                            videoJson.has("file") -> videoJson.getString("file")
                            videoJson.has("stream") -> videoJson.getString("stream")
                            else -> null
                        }
                        
                        if (!videoSrc.isNullOrEmpty() && videoSrc.startsWith("http")) {
                            Log.d("MaxSeries", "✅ Vídeo MegaEmbed HAR encontrado: $videoSrc")
                            
                            callback.invoke(
                                newExtractorLink(
                                    source = "MegaEmbed HAR",
                                    name = "MegaEmbed HAR",
                                    url = videoSrc,
                                    referer = referer,
                                    quality = Qualities.P720.value,
                                    isM3u8 = videoSrc.contains(".m3u8")
                                )
                            )
                            return true
                        } else {
                            Log.d("MaxSeries", "⚠️ URL de vídeo não encontrada na resposta JSON")
                            Log.d("MaxSeries", "📄 Resposta: ${videoResponse.text}")
                        }
                        
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro ao processar JSON: ${e.message}")
                        Log.d("MaxSeries", "📄 Resposta raw: ${videoResponse.text}")
                    }
                } else {
                    Log.d("MaxSeries", "❌ Video API falhou: ${videoResponse.code}")
                }
            } else {
                Log.d("MaxSeries", "❌ Info API falhou: ${infoResponse.code}")
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro no extractor MegaEmbed HAR: ${e.message}")
        }
        
        return false
    }
}