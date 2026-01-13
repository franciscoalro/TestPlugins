package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element
import org.jsoup.nodes.Document
import android.util.Log

/**
 * MaxSeries Provider v4 - Multi-Player Support (Jan 2026)
 * 
 * Fluxo de extração:
 * 1. maxseries.one/series/... → iframe playerthree.online
 * 2. playerthree.online/episodio/{id} → botões data-source
 * 3. Sources disponíveis:
 *    - playerembedapi.link (MP4 direto - PRIORIDADE 1)
 *    - myvidplay.com / dood (MP4/HLS - PRIORIDADE 2)
 *    - megaembed.link (HLS ofuscado - PRIORIDADE 3)
 * 
 * Priorização: PlayerEmbedAPI > Dood/myvidplay > MegaEmbed
 * (evita erro 3003 se tiver player compatível)
 */
class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)

    companion object {
        private const val TAG = "MaxSeriesProvider"
        // User-Agent do Firefox (HAR real)
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override val mainPage = mainPageOf(
        "$mainUrl/filmes" to "Filmes",
        "$mainUrl/series" to "Séries"
    )
    
    private fun upgradeImageQuality(url: String?): String? {
        if (url.isNullOrBlank()) return null
        return url.replace("/w185/", "/w780/")
                  .replace("/w300/", "/w780/")
                  .replace("/w500/", "/w780/")
                  .replace("/w342/", "/w780/")
    }

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val url = if (page > 1) "${request.data}/page/$page" else request.data
            val document = app.get(url).document
            val home = document.select("article.item").mapNotNull { it.toSearchResult() }
            Log.d(TAG, "✅ ${request.name}: ${home.size} items (página $page)")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private fun Element.toSearchResult(): SearchResponse? {
        return try {
            val titleElement = this.selectFirst("h3.title, .title, h3")
            val title = titleElement?.text()?.trim() ?: return null
            
            if (title.contains("Login", true) || 
                title.contains("Register", true) ||
                title.contains("Account", true) ||
                title.length < 2) return null
            
            val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
            if (!href.contains("/filmes/") && !href.contains("/series/")) return null
            
            val img = this.selectFirst(".image img, img")
            val rawPoster = img?.attr("src") ?: img?.attr("data-src")
            val posterUrl = upgradeImageQuality(fixUrlNull(rawPoster))
            
            val yearText = this.selectFirst(".data span, span")?.text() ?: ""
            val year = "\\b(19|20)\\d{2}\\b".toRegex().find(yearText)?.value?.toIntOrNull()
            
            val tvType = if (href.contains("/series/")) TvType.TvSeries else TvType.Movie

            newMovieSearchResponse(title, href, tvType) {
                this.posterUrl = posterUrl
                this.year = year
            }
        } catch (e: Exception) {
            null
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) return emptyList()
        return try {
            val document = app.get("$mainUrl/?s=${query.replace(" ", "+")}").document
            document.select("article.item").mapNotNull { it.toSearchResult() }
        } catch (e: Exception) {
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            val document = app.get(url).document
            val title = document.selectFirst("h1")?.text()?.trim()
                ?: document.title().substringBefore(" - ").trim()
            
            if (title.isBlank() || title.contains("Login", true)) return null

            val rawPoster = document.selectFirst(".poster img")?.attr("src")
                ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            val poster = upgradeImageQuality(fixUrlNull(rawPoster))
            val genres = document.select(".sgeneros a").map { it.text().trim() }

            val pageText = document.text()
            val year = "DATA DE LANÇAMENTO[:\\s]*([A-Za-z.]+\\s*\\d{1,2},?\\s*)?(\\d{4})".toRegex()
                .find(pageText)?.groupValues?.lastOrNull()?.toIntOrNull()
                ?: "\\b(19|20)\\d{2}\\b".toRegex().find(pageText)?.value?.toIntOrNull()

            val plot = "SINOPSE\\s*(.+?)(?:COMPARTILHE|ELENCO|TRAILER|$)".toRegex(RegexOption.DOT_MATCHES_ALL)
                .find(pageText)?.groupValues?.get(1)?.trim()?.take(500)

            val isSeriesPage = url.contains("/series/") || pageText.contains("TEMPORADAS:", true)

            // Extrair iframe do playerthree
            val playerthreeUrl = extractPlayerthreeUrl(document)
            Log.d(TAG, "🎬 Playerthree URL: $playerthreeUrl")

            return if (isSeriesPage) {
                val episodes = if (playerthreeUrl != null) {
                    parseEpisodesFromPlayerthree(playerthreeUrl, url)
                } else {
                    parseEpisodesFromPage(document, url)
                }
                
                newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                }
            } else {
                // Para filmes, usar a URL do playerthree ou a página original
                val dataUrl = playerthreeUrl ?: url
                newMovieLoadResponse(title, url, TvType.Movie, dataUrl) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro load: ${e.message}")
            null
        }
    }

    /**
     * Extrai URL do iframe playerthree da página
     */
    private fun extractPlayerthreeUrl(document: Document): String? {
        // Procurar iframe do playerthree
        val iframes = document.select("iframe[src*=playerthree], iframe[src*=player]")
        for (iframe in iframes) {
            val src = iframe.attr("src")
            if (src.contains("playerthree.online")) {
                return src
            }
        }
        
        // Procurar no HTML bruto (às vezes está em texto)
        val html = document.html()
        val pattern = Regex("""https?://playerthree\.online/embed/[^"'\s]+""")
        val match = pattern.find(html)
        return match?.value
    }

    /**
     * Busca episódios do playerthree.online
     */
    private suspend fun parseEpisodesFromPlayerthree(playerthreeUrl: String, baseUrl: String): List<Episode> {
        val episodes = mutableListOf<Episode>()
        
        try {
            Log.d(TAG, "🔄 Buscando episódios de: $playerthreeUrl")
            
            val response = app.get(
                playerthreeUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to baseUrl
                )
            )
            
            val document = response.document
            
            // Extrair temporadas
            val seasonElements = document.select(".header-navigation li[data-season-id]")
            val seasons = seasonElements.map { 
                it.attr("data-season-id") to (it.attr("data-season-number").toIntOrNull() ?: 1)
            }.ifEmpty { listOf("1" to 1) }
            
            Log.d(TAG, "📺 Temporadas encontradas: ${seasons.size}")
            
            // Extrair episódios de cada card
            val cards = document.select(".card")
            
            for (card in cards) {
                val cardTitle = card.selectFirst(".card-title")?.text() ?: ""
                val isDubbed = cardTitle.contains("Dublado", true)
                val isSubbed = cardTitle.contains("Legendado", true)
                
                val episodeItems = card.select("li[data-episode-id]")
                
                for (item in episodeItems) {
                    val episodeId = item.attr("data-episode-id")
                    val seasonId = item.attr("data-season-id")
                    
                    if (episodeId.isEmpty()) continue
                    
                    val linkElement = item.selectFirst("a")
                    val episodeTitle = linkElement?.text()?.trim() ?: "Episódio"
                    
                    // Extrair número do episódio do título
                    val epNumMatch = Regex("""^(\d+)\s*[-–]""").find(episodeTitle)
                    val epNum = epNumMatch?.groupValues?.get(1)?.toIntOrNull() ?: 1
                    
                    // Encontrar número da temporada
                    val seasonNum = seasons.find { it.first == seasonId }?.second ?: 1
                    
                    // Criar data URL com informações necessárias
                    val dataUrl = "$playerthreeUrl|episodio|$episodeId"
                    
                    val suffix = when {
                        isDubbed -> " (Dublado)"
                        isSubbed -> " (Legendado)"
                        else -> ""
                    }
                    
                    episodes.add(newEpisode(dataUrl) {
                        this.name = "$episodeTitle$suffix"
                        this.season = seasonNum
                        this.episode = epNum
                    })
                }
            }
            
            Log.d(TAG, "✅ Total de episódios: ${episodes.size}")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao buscar episódios do playerthree: ${e.message}")
        }
        
        if (episodes.isEmpty()) {
            episodes.add(newEpisode(playerthreeUrl) {
                this.name = "Assistir"
                this.season = 1
                this.episode = 1
            })
        }
        
        return episodes
    }

    /**
     * Fallback: parse episódios da página do MaxSeries
     */
    private fun parseEpisodesFromPage(document: Document, baseUrl: String): List<Episode> {
        val episodes = mutableListOf<Episode>()
        
        val seasonElements = document.select(".se-c, .seasons .se-a, #seasons .se-c")
        
        if (seasonElements.isNotEmpty()) {
            seasonElements.forEachIndexed { seasonIndex, seasonEl ->
                val seasonNum = seasonIndex + 1
                val episodeElements = seasonEl.select(".episodios li, .se-a ul li, ul.episodios li")
                
                episodeElements.forEachIndexed { epIndex, epEl ->
                    val epLink = epEl.selectFirst("a")?.attr("href") ?: baseUrl
                    val epTitle = epEl.selectFirst(".episodiotitle a, .epst")?.text()?.trim() 
                        ?: "Episódio ${epIndex + 1}"
                    val epNum = epIndex + 1
                    
                    episodes.add(newEpisode(fixUrl(epLink)) {
                        this.name = epTitle
                        this.season = seasonNum
                        this.episode = epNum
                    })
                }
            }
        }
        
        if (episodes.isEmpty()) {
            episodes.add(newEpisode(baseUrl) {
                this.name = "Assistir"
                this.season = 1
                this.episode = 1
            })
        }
        
        return episodes
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "🔗 loadLinks: $data")
        
        return try {
            var linksFound = 0
            
            // Verificar se é URL do playerthree com episodeId
            if (data.contains("|episodio|")) {
                val parts = data.split("|episodio|")
                val playerthreeUrl = parts[0]
                val episodeId = parts[1]
                
                linksFound = extractFromPlayerthreeEpisode(playerthreeUrl, episodeId, subtitleCallback, callback)
            } 
            // URL direta do playerthree
            else if (data.contains("playerthree.online")) {
                linksFound = extractFromPlayerthreeDirect(data, subtitleCallback, callback)
            }
            // URL do MaxSeries (fallback)
            else {
                linksFound = extractFromMaxSeriesPage(data, subtitleCallback, callback)
            }
            
            Log.d(TAG, "✅ Links encontrados: $linksFound")
            linksFound > 0
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro loadLinks: ${e.message}")
            false
        }
    }

    /**
     * Extrai links de um episódio específico do playerthree
     */
    private suspend fun extractFromPlayerthreeEpisode(
        playerthreeUrl: String,
        episodeId: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        try {
            // Extrair base URL do playerthree
            val baseUrl = playerthreeUrl.substringBefore("/embed/").let {
                if (it.isEmpty()) "https://playerthree.online" else it
            }
            
            val episodeUrl = "$baseUrl/episodio/$episodeId"
            Log.d(TAG, "🎬 Buscando episódio: $episodeUrl")
            
            val response = app.get(
                episodeUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to playerthreeUrl,
                    "X-Requested-With" to "XMLHttpRequest",
                    "Accept" to "*/*",
                    "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
                )
            )
            
            val html = response.text
            Log.d(TAG, "📄 Resposta do episódio: ${html.take(500)}")
            
            // Extrair botões de player com data-source
            val sources = extractPlayerSources(html)
            Log.d(TAG, "🎯 Sources encontradas: ${sources.size}")
            
            // PRIORIZAÇÃO ATUALIZADA:
            // 1. PlayerEmbedAPI (MP4 direto - mais compatível)
            // 2. Dood/myvidplay (MP4/HLS normal - compatível)
            // 3. MegaEmbed (HLS ofuscado - pode dar erro 3003)
            val sortedSources = sources.sortedWith(
                compareByDescending<String> { it.contains("playerembedapi") }
                    .thenByDescending { it.contains("myvidplay") || it.contains("dood") }
                    .thenByDescending { !it.contains("megaembed") }
            )
            
            Log.d(TAG, "📋 Sources ordenadas: $sortedSources")
            
            for (source in sortedSources) {
                Log.d(TAG, "🔄 Processando source: $source")
                try {
                    when {
                        // PRIORIDADE 1: PlayerEmbedAPI (MP4 do Google Cloud Storage)
                        source.contains("playerembedapi") -> {
                            Log.d(TAG, "🎬 [PRIORIDADE 1] PlayerEmbedAPIExtractor")
                            val playerExtractor = com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractor()
                            playerExtractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 2: Dood/myvidplay (MP4/HLS normal - compatível)
                        source.contains("myvidplay") || source.contains("dood") -> {
                            Log.d(TAG, "🎬 [PRIORIDADE 2] Dood/myvidplay via loadExtractor")
                            loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 3: MegaEmbed (HLS ofuscado - pode dar erro 3003)
                        source.contains("megaembed") -> {
                            Log.d(TAG, "🎬 [PRIORIDADE 3] MegaEmbedSimpleExtractor")
                            val megaExtractor = com.franciscoalro.maxseries.extractors.MegaEmbedSimpleExtractor()
                            megaExtractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // Fallback: outros players via loadExtractor genérico
                        else -> {
                            Log.d(TAG, "🎬 [FALLBACK] loadExtractor genérico")
                            loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "⚠️ Erro no extractor para $source: ${e.message}")
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair episódio: ${e.message}")
        }
        
        return linksFound
    }

    /**
     * Extrai links diretamente da página do playerthree
     */
    private suspend fun extractFromPlayerthreeDirect(
        playerthreeUrl: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        try {
            val response = app.get(
                playerthreeUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to mainUrl
                )
            )
            
            val document = response.document
            
            // Procurar primeiro episódio disponível
            val firstEpisode = document.selectFirst("li[data-episode-id]")
            if (firstEpisode != null) {
                val episodeId = firstEpisode.attr("data-episode-id")
                if (episodeId.isNotEmpty()) {
                    linksFound = extractFromPlayerthreeEpisode(playerthreeUrl, episodeId, subtitleCallback, callback)
                }
            }
            
            // Se não encontrou episódios, procurar sources diretas
            if (linksFound == 0) {
                val sources = extractPlayerSources(document.html())
                for (source in sources) {
                    try {
                        loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
                        linksFound++
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro no extractor: ${e.message}")
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair do playerthree: ${e.message}")
        }
        
        return linksFound
    }

    /**
     * Fallback: extrai links da página do MaxSeries
     */
    private suspend fun extractFromMaxSeriesPage(
        url: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        try {
            val document = app.get(url).document
            
            // Primeiro, tentar extrair do playerthree se existir
            val playerthreeUrl = extractPlayerthreeUrl(document)
            if (playerthreeUrl != null) {
                linksFound = extractFromPlayerthreeDirect(playerthreeUrl, subtitleCallback, callback)
                if (linksFound > 0) return linksFound
            }
            
            // Fallback: procurar iframes e links diretos
            val sources = mutableListOf<String>()
            
            document.select("iframe[src]").forEach { iframe ->
                val src = iframe.attr("src")
                if (src.isNotEmpty() && !src.contains("youtube", true)) {
                    sources.add(fixUrl(src))
                }
            }
            
            document.select("[data-source], [data-src]").forEach { btn ->
                val src = btn.attr("data-source").ifEmpty { btn.attr("data-src") }
                if (src.isNotEmpty()) sources.add(fixUrl(src))
            }
            
            for (source in sources.distinct()) {
                try {
                    loadExtractor(source, url, subtitleCallback, callback)
                    linksFound++
                } catch (e: Exception) {
                    Log.e(TAG, "⚠️ Erro no extractor: ${e.message}")
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair da página: ${e.message}")
        }
        
        return linksFound
    }

    /**
     * Extrai URLs de player do HTML (data-source dos botões)
     * Regex melhorada para pegar todos os players conhecidos
     */
    private fun extractPlayerSources(html: String): List<String> {
        val sources = mutableListOf<String>()
        
        // Padrão 1: data-source="url"
        val dataSourcePattern = Regex("""data-source=["']([^"']+)["']""")
        dataSourcePattern.findAll(html).forEach { match ->
            val url = match.groupValues[1]
            if (url.isNotEmpty() && url.startsWith("http")) {
                sources.add(url)
            }
        }
        
        // Padrão 2: data-src="url"
        val dataSrcPattern = Regex("""data-src=["']([^"']+)["']""")
        dataSrcPattern.findAll(html).forEach { match ->
            val url = match.groupValues[1]
            if (url.isNotEmpty() && url.startsWith("http") && !sources.contains(url)) {
                sources.add(url)
            }
        }
        
        // Padrão 3: URLs conhecidas no HTML (regex melhorada)
        val knownPatterns = listOf(
            Regex("""https?://megaembed\.link[^"'\s<>]+"""),
            Regex("""https?://playerembedapi\.link[^"'\s<>]+"""),
            Regex("""https?://myvidplay\.com[^"'\s<>]+"""),
            Regex("""https?://[^"'\s<>]*dood[^"'\s<>]+"""),
            Regex("""https?://[^"'\s<>]*doodstream[^"'\s<>]+"""),
            Regex("""https?://[^"'\s<>]*embed[^"'\s<>]*\?[^"'\s<>]+""")
        )
        
        for (pattern in knownPatterns) {
            pattern.findAll(html).forEach { match ->
                val url = match.value.trim()
                if (url.isNotEmpty() && !sources.contains(url)) {
                    sources.add(url)
                }
            }
        }
        
        Log.d(TAG, "📋 Sources extraídas: $sources")
        return sources.distinct()
    }
}
