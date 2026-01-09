package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log
import java.util.Base64

// MaxSeries Provider - Versão 16.0 - EXTRACTORS CORRIGIDOS
// Problema identificado: Players usam JavaScript complexo que os extractors padrão não conseguem processar
// Solução: Implementar extractors customizados para PlayerEmbedAPI e MegaEmbed
// Análise completa realizada em 08/01/2026
// - 5 episódios detectados por série
// - Players: playerembedapi.link, megaembed.link
// - Estrutura: playerthree.online iframes com navegação por fragmentos

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
            
            Log.d("MaxSeries", "📺 Analisando série (v16.0): $title")
            
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
        Log.d("MaxSeries", "📺 Processando links (v16.0 - Extractors Corrigidos): $data")
        
        var linksFound = 0
        
        try {
            if (data.contains("#") && data.contains("playerthree.online")) {
                val fragmentMatch = Regex("#\\d+_(\\d+)").find(data)
                if (fragmentMatch != null) {
                    val episodeId = fragmentMatch.groupValues[1]
                    
                    val baseUrl = "https://playerthree.online"
                    val ajaxUrl = "$baseUrl/episodio/$episodeId"
                    
                    val ajaxHeaders = mapOf(
                        "Referer" to data,
                        "X-Requested-With" to "XMLHttpRequest"
                    )
                    
                    val ajaxResponse = app.get(ajaxUrl, headers = ajaxHeaders)
                    
                    if (ajaxResponse.isSuccessful) {
                        val ajaxDoc = ajaxResponse.document
                        
                        val playerButtons = ajaxDoc.select("button[data-source], .btn[data-source]")
                        
                        playerButtons.forEach { button ->
                            val playerName = button.text().trim().ifEmpty { "Player" }
                            val dataSource = button.attr("data-source")
                            
                            if (dataSource.isNotEmpty() && dataSource.startsWith("http")) {
                                if (!dataSource.contains("youtube", ignoreCase = true) && 
                                    !dataSource.contains("trailer", ignoreCase = true)) {
                                    
                                    Log.d("MaxSeries", "🎯 Processando player: $playerName -> $dataSource")
                                    
                                    // Usar extractors customizados em vez dos padrão
                                    try {
                                        when {
                                            dataSource.contains("playerembedapi.link") -> {
                                                if (extractPlayerEmbedAPI(dataSource, data, callback)) {
                                                    linksFound++
                                                    Log.d("MaxSeries", "✅ Sucesso PlayerEmbedAPI customizado: $playerName")
                                                }
                                            }
                                            dataSource.contains("megaembed.link") -> {
                                                if (extractMegaEmbed(dataSource, data, callback)) {
                                                    linksFound++
                                                    Log.d("MaxSeries", "✅ Sucesso MegaEmbed customizado: $playerName")
                                                }
                                            }
                                            else -> {
                                                // Fallback para outros extractors
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

    // EXTRACTOR CUSTOMIZADO - PlayerEmbedAPI
    private suspend fun extractPlayerEmbedAPI(
        url: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🔧 Extractor customizado PlayerEmbedAPI: $url")
        
        try {
            val response = app.get(url, referer = referer)
            val content = response.text
            
            // Procurar dados base64 no JavaScript (padrão do PlayerEmbedAPI)
            val base64Regex = Regex("""atob\(["']([^"']+)["']\)""")
            val base64Match = base64Regex.find(content)
            
            if (base64Match != null) {
                try {
                    val base64Data = base64Match.groupValues[1]
                    val decodedData = String(Base64.getDecoder().decode(base64Data))
                    
                    Log.d("MaxSeries", "🔍 Dados decodificados PlayerEmbedAPI encontrados")
                    
                    // Procurar URLs de vídeo nos dados decodificados
                    val videoUrlRegex = Regex(""""(?:file|source|url)"\s*:\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"''')
                    val videoMatches = videoUrlRegex.findAll(decodedData)
                    
                    videoMatches.forEach { match ->
                        val videoUrl = match.groupValues[1]
                        if (videoUrl.startsWith("http")) {
                            Log.d("MaxSeries", "✅ Vídeo PlayerEmbedAPI encontrado: $videoUrl")
                            
                            callback.invoke(
                                newExtractorLink(
                                    "PlayerEmbedAPI",
                                    "PlayerEmbedAPI",
                                    videoUrl,
                                    referer,
                                    if (videoUrl.contains(".m3u8")) Qualities.Unknown.value else Qualities.P720.value,
                                    videoUrl.contains(".m3u8")
                                )
                            )
                            return true
                        }
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao decodificar base64: ${e.message}")
                }
            }
            
            // Fallback: procurar URLs diretas no JavaScript
            val directUrlRegex = Regex(""""(?:file|source)"\s*:\s*"(https?://[^"]+\.(?:m3u8|mp4)[^"]*)"''')
            val directMatches = directUrlRegex.findAll(content)
            
            directMatches.forEach { match ->
                val videoUrl = match.groupValues[1]
                Log.d("MaxSeries", "✅ Vídeo direto PlayerEmbedAPI: $videoUrl")
                
                callback.invoke(
                    newExtractorLink(
                        "PlayerEmbedAPI",
                        "PlayerEmbedAPI Direct",
                        videoUrl,
                        referer,
                        Qualities.P720.value,
                        videoUrl.contains(".m3u8")
                    )
                )
                return true
            }
            
            // Último fallback: procurar qualquer URL de vídeo
            val anyVideoRegex = Regex("""(https?://[^"'\s]+\.(?:m3u8|mp4)[^"'\s]*)""")
            val anyMatches = anyVideoRegex.findAll(content)
            
            anyMatches.forEach { match ->
                val videoUrl = match.groupValues[1]
                Log.d("MaxSeries", "✅ Vídeo genérico PlayerEmbedAPI: $videoUrl")
                
                callback.invoke(
                    newExtractorLink(
                        "PlayerEmbedAPI",
                        "PlayerEmbedAPI Generic",
                        videoUrl,
                        referer,
                        Qualities.P720.value,
                        videoUrl.contains(".m3u8")
                    )
                )
                return true
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro no extractor PlayerEmbedAPI: ${e.message}")
        }
        
        return false
    }

    // EXTRACTOR CUSTOMIZADO - MegaEmbed
    private suspend fun extractMegaEmbed(
        url: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "🔧 Extractor customizado MegaEmbed: $url")
        
        try {
            val response = app.get(url, referer = referer)
            val content = response.text
            val doc = response.document
            
            // MegaEmbed usa JavaScript moderno com módulos
            // Procurar por assets JavaScript
            val assetRegex = Regex("""/assets/[^"']+\.js""")
            val assetMatches = assetRegex.findAll(content)
            
            for (assetMatch in assetMatches) {
                val assetUrl = "https://megaembed.link" + assetMatch.value
                
                try {
                    val assetResponse = app.get(assetUrl, referer = url)
                    val assetContent = assetResponse.text
                    
                    // Procurar configurações de vídeo no asset
                    val videoConfigRegex = Regex(""""(?:file|source|url)"\s*:\s*"([^"]+)"''')
                    val configMatches = videoConfigRegex.findAll(assetContent)
                    
                    configMatches.forEach { match ->
                        val videoUrl = match.groupValues[1]
                        if (videoUrl.startsWith("http") && (videoUrl.contains(".m3u8") || videoUrl.contains(".mp4"))) {
                            Log.d("MaxSeries", "✅ Vídeo MegaEmbed asset encontrado: $videoUrl")
                            
                            callback.invoke(
                                newExtractorLink(
                                    "MegaEmbed",
                                    "MegaEmbed",
                                    videoUrl,
                                    referer,
                                    Qualities.P720.value,
                                    videoUrl.contains(".m3u8")
                                )
                            )
                            return true
                        }
                    }
                } catch (e: Exception) {
                    Log.d("MaxSeries", "⚠️ Erro ao carregar asset MegaEmbed: ${e.message}")
                }
            }
            
            // Fallback: procurar iframes aninhados
            val iframes = doc.select("iframe[src]")
            
            for (iframe in iframes) {
                val iframeSrc = iframe.attr("src")
                if (iframeSrc.isNotEmpty()) {
                    val fullIframeUrl = if (iframeSrc.startsWith("//")) "https:$iframeSrc" 
                                       else if (iframeSrc.startsWith("/")) "https://megaembed.link$iframeSrc"
                                       else iframeSrc
                    
                    try {
                        val iframeResponse = app.get(fullIframeUrl, referer = url)
                        val iframeContent = iframeResponse.text
                        
                        val videoRegex = Regex(""""(?:file|source)"\s*:\s*"(https?://[^"]+\.(?:m3u8|mp4)[^"]*)"''')
                        val videoMatches = videoRegex.findAll(iframeContent)
                        
                        videoMatches.forEach { match ->
                            val videoUrl = match.groupValues[1]
                            Log.d("MaxSeries", "✅ Vídeo MegaEmbed iframe: $videoUrl")
                            
                            callback.invoke(
                                newExtractorLink(
                                    "MegaEmbed",
                                    "MegaEmbed Iframe",
                                    videoUrl,
                                    referer,
                                    Qualities.P720.value,
                                    videoUrl.contains(".m3u8")
                                )
                            )
                            return true
                        }
                    } catch (e: Exception) {
                        Log.d("MaxSeries", "⚠️ Erro ao processar iframe MegaEmbed: ${e.message}")
                    }
                }
            }
            
            // Último fallback: procurar qualquer URL de vídeo no conteúdo
            val anyVideoRegex = Regex("""(https?://[^"'\s]+\.(?:m3u8|mp4)[^"'\s]*)""")
            val anyMatches = anyVideoRegex.findAll(content)
            
            anyMatches.forEach { match ->
                val videoUrl = match.groupValues[1]
                Log.d("MaxSeries", "✅ Vídeo genérico MegaEmbed: $videoUrl")
                
                callback.invoke(
                    newExtractorLink(
                        "MegaEmbed",
                        "MegaEmbed Generic",
                        videoUrl,
                        referer,
                        Qualities.P720.value,
                        videoUrl.contains(".m3u8")
                    )
                )
                return true
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro no extractor MegaEmbed: ${e.message}")
        }
        
        return false
    }
}