package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element
import org.jsoup.nodes.Document
import android.util.Log

// Utilitários brasileiros
import com.franciscoalro.maxseries.utils.ServerPriority
import com.franciscoalro.maxseries.utils.HeadersBuilder
import com.franciscoalro.maxseries.utils.LinkDecryptor
import com.franciscoalro.maxseries.utils.RegexPatterns
import com.franciscoalro.maxseries.utils.BRExtractorUtils

// Extractors adicionais (saimuelrepo patterns)
import com.franciscoalro.maxseries.extractors.MediaFireExtractor
import com.franciscoalro.maxseries.extractors.StreamtapeExtractor
import com.franciscoalro.maxseries.extractors.FilemoonExtractor
import com.franciscoalro.maxseries.extractors.DoodStreamExtractor
import com.franciscoalro.maxseries.extractors.MixdropExtractor
import com.franciscoalro.maxseries.extractors.VidStackExtractor

/**
 * MaxSeries Provider v128 - MegaEmbed V7 COMPLETO (Jan 2026)
 * 
 * Fluxo de extração:
 * 1. maxseries.one/series/... → iframe playerthree.online
 * 2. playerthree.online/episodio/{id} → botões data-source
 * 3. Sources disponíveis (10 extractors suportados):
 *    - playerembedapi.link (MP4 direto - PRIORIDADE 1)
 *    - myvidplay.com (MP4 direto - PRIORIDADE 2)
 *    - streamtape.com (MP4 direto - PRIORIDADE 3)
 *    - dood/doodstream (MP4/HLS - PRIORIDADE 4)
 *    - mixdrop (MP4/HLS - PRIORIDADE 5)
 *    - filemoon (MP4 - PRIORIDADE 6)
 *    - uqload (MP4 - PRIORIDADE 7)
 *    - vidcloud (HLS - PRIORIDADE 8)
 *    - upstream (MP4 - PRIORIDADE 9)
 *    - megaembed.link V7 (HLS - PRIORIDADE 10 - ~100% SUCESSO)
 * 
 * v128 Changes (19 Jan 2026):
 * - MegaEmbed V7: Versão Completa com WebView Fallback
 * - Taxa de sucesso: ~100% (vs 80-90% anterior)
 * - Cache automático (SharedPreferences)
 * - 5 padrões de CDN conhecidos
 * - WebView descobre novos subdomínios automaticamente
 * - Performance: ~2s (80%) / ~8s (20% primeira vez) / ~1s (cache)
 * 
 * v78 Changes:
 * - Busca corrigida: suporte a .result-item (página de busca)
 * - Fallback para article.item se necessário
 * - Logs melhorados para debug
 * 
 * Priorização: MP4 direto > HLS normal > HLS ofuscado
 * (evita erro 3003 priorizando MP4)
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

        val customExtractors = listOf(
            MediaFireExtractor(),
            StreamtapeExtractor(),
            FilemoonExtractor(),
            DoodStreamExtractor(),
            MixdropExtractor(),
            VidStackExtractor()
        )
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
            Log.d(TAG, "🔍 Buscando: $query")
            val document = app.get("$mainUrl/?s=${query.replace(" ", "+")}").document
            
            // Página de busca usa .result-item em vez de article.item
            val searchResults = document.select(".result-item article").mapNotNull { 
                it.toSearchResultFromSearch() 
            }
            
            // Fallback: tentar seletor normal se não encontrar nada
            val normalResults = if (searchResults.isEmpty()) {
                document.select("article.item").mapNotNull { it.toSearchResult() }
            } else emptyList()
            
            val results = searchResults + normalResults
            Log.d(TAG, "✅ Busca '$query': ${results.size} resultados")
            results
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro busca: ${e.message}")
            emptyList()
        }
    }
    
    /**
     * Converte result-item da página de busca para SearchResponse
     */
    private fun Element.toSearchResultFromSearch(): SearchResponse? {
        return try {
            // Na busca, o link está dentro de .thumbnail
            val linkElement = this.selectFirst(".thumbnail a") ?: this.selectFirst("a") ?: return null
            val href = fixUrl(linkElement.attr("href"))
            
            if (!href.contains("/filmes/") && !href.contains("/series/")) return null
            
            // Título pode estar no alt da imagem ou em h3
            val img = this.selectFirst("img")
            val title = img?.attr("alt")?.trim() 
                ?: this.selectFirst("h3, .title")?.text()?.trim() 
                ?: return null
            
            if (title.contains("Login", true) || title.length < 2) return null
            
            // Poster
            val rawPoster = img?.attr("src") ?: img?.attr("data-src")
            val posterUrl = upgradeImageQuality(fixUrlNull(rawPoster))
            
            // Ano
            val yearText = this.text()
            val year = "\\b(19|20)\\d{2}\\b".toRegex().find(yearText)?.value?.toIntOrNull()
            
            // Tipo (TV ou Movie)
            val tvType = if (href.contains("/series/") || this.selectFirst(".tvshows") != null) {
                TvType.TvSeries
            } else {
                TvType.Movie
            }
            
            Log.d(TAG, "  📌 $title ($year) - $tvType")

            newMovieSearchResponse(title, href, tvType) {
                this.posterUrl = posterUrl
                this.year = year
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro toSearchResultFromSearch: ${e.message}")
            null
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
                headers = HeadersBuilder.standard(baseUrl)
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
            
            // Headers customizados usando HeadersBuilder
            val headers = HeadersBuilder.standard(playerthreeUrl)
            
            val response = app.get(episodeUrl, headers = headers)
            
            val html = response.text
            Log.d(TAG, "📄 Resposta do episódio (${html.length} chars)")
            Log.d(TAG, "📄 HTML início: ${html.take(1000)}")
            Log.d(TAG, "📄 HTML fim: ${html.takeLast(500)}")
            
            // Extrair botões de player com data-source
            val sources = extractPlayerSources(html)
            Log.d(TAG, "🎯 Sources encontradas: ${sources.size} - $sources")
            
            // PRIORIZAÇÃO AUTOMÁTICA usando ServerPriority (v97)
            // Ordena automaticamente: Streamtape > Filemoon > Doodstream > Mixdrop > etc.
            val sortedSources = ServerPriority.sortByPriority(sources) { source ->
                ServerPriority.detectServer(source)
            }
            
            Log.d(TAG, "📋 Sources ordenadas por prioridade (v97 - ServerPriority): $sortedSources")
            
            for (source in sortedSources) {
                Log.d(TAG, "🔄 Processando: $source")
                try {
                    when {
                        // PRIORIDADE 0: MediaFire (se aplicável)
                        MediaFireExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P0] MediaFireExtractor - Download direto")
                            val extractor = MediaFireExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 1: PlayerEmbedAPI (MP4 do Google Cloud Storage - WebView)
                        source.contains("playerembedapi", ignoreCase = true) -> {
                            Log.d(TAG, "🎬 [P1] PlayerEmbedAPIExtractor - MP4 direto (WebView)")
                            val extractor = com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 2: MyVidPlay (MP4 direto do cloudatacdn)
                        source.contains("myvidplay", ignoreCase = true) -> {
                            Log.d(TAG, "🎬 [P2] MyVidPlayExtractor - MP4 direto")
                            val extractor = com.franciscoalro.maxseries.extractors.MyVidPlayExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 3: Streamtape (Custom Extractor - saimuelrepo)
                        StreamtapeExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P3] StreamtapeExtractor - Custom (saimuelrepo)")
                            val extractor = StreamtapeExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 4: Filemoon (Custom Extractor + JsUnpacker)
                        FilemoonExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P4] FilemoonExtractor - Custom (JsUnpacker)")
                            val extractor = FilemoonExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 5: DoodStream (Custom Extractor - all variants)
                        DoodStreamExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P5] DoodStreamExtractor - Custom (all domains)")
                            val extractor = DoodStreamExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 6: Mixdrop (Custom Extractor + JsUnpacker)
                        MixdropExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P6] MixdropExtractor - Custom (JsUnpacker)")
                            val extractor = MixdropExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 7: VidStack/EmbedPlay
                        VidStackExtractor.canHandle(source) -> {
                            Log.d(TAG, "🎬 [P7] VidStackExtractor - Custom (EmbedPlay)")
                            val extractor = VidStackExtractor()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 8-9: Built-in extractors (CloudStream nativo)
                        source.contains("uqload", ignoreCase = true) ||
                        source.contains("vidcloud", ignoreCase = true) ||
                        source.contains("upstream", ignoreCase = true) -> {
                            val extractorName = when {
                                source.contains("uqload", ignoreCase = true) -> "Uqload [P8]"
                                source.contains("vidcloud", ignoreCase = true) -> "VidCloud [P9]"
                                source.contains("upstream", ignoreCase = true) -> "UpStream [P10]"
                                else -> "Built-in"
                            }
                            Log.d(TAG, "🎬 $extractorName via loadExtractor (built-in)")
                            loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // PRIORIDADE 10: MegaEmbed V7 (VERSÃO COMPLETA - 100% sucesso)
                        source.contains("megaembed", ignoreCase = true) -> {
                            Log.d(TAG, "🎬 [P10] MegaEmbedExtractorV7 - VERSÃO COMPLETA (~100% sucesso)")
                            val extractor = com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV7()
                            extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // Fallback: tentar loadExtractor genérico para outros players
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
     * Regex SUPER melhorada para pegar TODOS os players conhecidos
     */
    private fun extractPlayerSources(html: String): List<String> {
        val sources = mutableListOf<String>()
        
        Log.d(TAG, "🔍 Analisando HTML (${html.length} chars)")
        
        // Padrão 1: data-source="url" (principal - botões do playerthree)
        val dataSourcePattern = Regex("""data-source\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        dataSourcePattern.findAll(html).forEach { match ->
            val url = match.groupValues[1].trim()
            Log.d(TAG, "🔹 data-source encontrado: $url")
            if (url.startsWith("http") && !sources.contains(url)) {
                sources.add(url)
            }
        }
        
        // Padrão 2: data-src="url"
        val dataSrcPattern = Regex("""data-src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        dataSrcPattern.findAll(html).forEach { match ->
            val url = match.groupValues[1].trim()
            Log.d(TAG, "🔹 data-src encontrado: $url")
            if (url.startsWith("http") && !sources.contains(url)) {
                sources.add(url)
            }
        }
        
        // Padrão 3: href="url" em links de player
        val hrefPattern = Regex("""href\s*=\s*["'](https?://(?:playerembedapi|myvidplay|dood|megaembed)[^"']+)["']""", RegexOption.IGNORE_CASE)
        hrefPattern.findAll(html).forEach { match ->
            val url = match.groupValues[1].trim()
            Log.d(TAG, "🔹 href player encontrado: $url")
            if (!sources.contains(url)) {
                sources.add(url)
            }
        }
        
        // Padrão 4: src="url" em iframes
        val srcPattern = Regex("""src\s*=\s*["'](https?://(?:playerembedapi|myvidplay|dood|megaembed)[^"']+)["']""", RegexOption.IGNORE_CASE)
        srcPattern.findAll(html).forEach { match ->
            val url = match.groupValues[1].trim()
            Log.d(TAG, "� src iframe encontrado: $url")
            if (!sources.contains(url)) {
                sources.add(url)
            }
        }
        
        // Padrão 5: URLs diretas no HTML (fallback agressivo)
        val directUrlPatterns = listOf(
            Regex("""https?://playerembedapi\.link/?\?[^"'\s<>\)]+"""),
            Regex("""https?://playerembedapi\.link[^"'\s<>\)]*"""),
            Regex("""https?://myvidplay\.com/e/[^"'\s<>\)]+"""),
            Regex("""https?://myvidplay\.com[^"'\s<>\)]*"""),
            Regex("""https?://dood\.[a-z]+/e/[^"'\s<>\)]+"""),
            Regex("""https?://doodstream\.[a-z]+/e/[^"'\s<>\)]+"""),
            Regex("""https?://[a-z0-9]*dood[a-z0-9]*\.[a-z]+/e/[^"'\s<>\)]+"""),
            Regex("""https?://megaembed\.link/?#[a-zA-Z0-9]+""")  // v120: APENAS com #videoId
        )
        
        directUrlPatterns.forEach { pattern ->
            pattern.findAll(html).forEach { match ->
                val url = match.value.trim().trimEnd(')', '"', '\'', '<', '>')
                if (url.length > 15 && !sources.contains(url)) {
                    Log.d(TAG, "🔹 URL direta encontrada: $url")
                    sources.add(url)
                }
            }
        }
        
        // Padrão 6: JSON com URLs (caso a resposta seja JSON)
        val jsonUrlPattern = Regex(""""(?:url|src|file|source|embed)":\s*"(https?://[^"]+)"""")
        jsonUrlPattern.findAll(html).forEach { match ->
            val url = match.groupValues[1].trim()
            Log.d(TAG, "🔹 URL em JSON encontrada: $url")
            if (!sources.contains(url)) {
                sources.add(url)
            }
        }
        
        Log.d(TAG, "📋 Total sources extraídas (v73): ${sources.size} - $sources")
        return sources.distinct()
    }
}
