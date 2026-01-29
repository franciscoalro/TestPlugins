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
import com.franciscoalro.maxseries.utils.VideoUrlCache

// Extractor único: MegaEmbed V8 (v156 com fetch/XHR hooks)
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV8
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV9
import com.franciscoalro.maxseries.extractors.MyVidPlayExtractor
import com.franciscoalro.maxseries.extractors.DoodStreamExtractor
import com.franciscoalro.maxseries.extractors.StreamtapeExtractor
import com.franciscoalro.maxseries.extractors.MixdropExtractor
import com.franciscoalro.maxseries.extractors.FilemoonExtractor
import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIWebViewExtractor

/**
 * MaxSeries Provider v223 - PlayerEmbedAPI Redirect Fix FINAL (Jan 2026)
 * 
 * v223 Changes (28 Jan 2026):
 * - 🔄 FIX FINAL: Segue redirect de sssrr.org → googleapis.com automaticamente
 * - 🎯 Headers completos para Google Storage (Sec-Fetch-*)
 * - ✅ Verificação de redirect bem-sucedido
 * - 🐛 Corrige ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
 * 
 * v222 Changes (28 Jan 2026):
 * - 🔄 FIX: Segue redirect de sssrr.org → googleapis.com automaticamente
 * - 🎯 Adiciona headers corretos (User-Agent, Origin, Referer)
 * - ✅ URLs finais do Google Storage funcionam no player
 * - 🐛 Corrige ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
 * 
 * v221 Changes (28 Jan 2026):
 * - ⚡ DETECÇÃO INSTANTÂNEA: MutationObserver detecta elementos assim que aparecem
 * - ⚡ POLLING RÁPIDO: 100ms nos primeiros 10s, depois 1s
 * - ⚡ TIMEOUT REDUZIDO: 20s (antes 30s) - detecção mais rápida
 * - 🎯 Cliques automáticos assim que botões ficam disponíveis
 * - 📊 Melhor performance e tempo de resposta
 * 
 * v219 Changes (27 Jan 2026):
 * - ✅ PlayerEmbedAPI RE-ADICIONADO via WebView
 * - 🌐 Carrega através do ViewPlayer (https://viewplayer.online/filme/{imdbId})
 * - 🤖 Automação com JavaScript injection
 * - 📡 Interceptação de requisições via shouldInterceptRequest
 * - ⚡ ~20-30s de extração, 90-95% taxa de sucesso
 * - 🎯 Captura URLs: sssrr.org + googleapis.com
 * 
 * v218 Changes (27 Jan 2026):
 * - ❌ PlayerEmbedAPI REMOVIDO (detecta automação e redireciona para abyss.to)
 * - ✅ Mantidos: MegaEmbed, MyVidPlay, DoodStream, StreamTape, Mixdrop, Filemoon
 * - 🎯 Foco em extractors que funcionam sem detecção
 * 
 * v217 Changes (27 Jan 2026):
 * - 💾 Cache persistente com SharedPreferences (30min TTL)
 * - 🚀 LRU eviction (max 100 URLs)
 * - 📊 Hit rate tracking (target: >60%)
 * - ⚡ Cache sobrevive restart do app
 * 
 * v216 Changes (26 Jan 2026):
 * - 🔧 PlayerEmbedAPI agora usa WebView MANUAL (igual MegaEmbed)
 * - 👆 Usuário clica manualmente no overlay
 * - ⚡ Mais confiável que automação
 * - ✅ Hooks de rede capturam URL após click
 * 
 * v211 Changes (26 Jan 2026):
 * - ❌ Removidas categorias "Filmes" e "Séries"
 * - 📊 Total de 23 categorias
 */
class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.pics"
    override var name = "MaxSeries v226"
    override val hasMainPage = true
    override val hasQuickSearch = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)

    companion object {
        private const val TAG = "MaxSeriesProvider"
        // User-Agent do Firefox (HAR real)
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }
    
    init {
        Log.wtf(TAG, "🚀🚀🚀 MAXSERIES PROVIDER v226 CARREGADO! 🚀🚀🚀")
        Log.wtf(TAG, "Name: $name, MainUrl: $mainUrl")
        Log.wtf(TAG, "Extractors: PlayerEmbedAPI (WebView + Redirect FIX v223), MegaEmbed, MyVidPlay, DoodStream, StreamTape, Mixdrop, Filemoon")
        Log.wtf(TAG, "Categories: 23 (Inicio, Em Alta, Adicionados Recentemente, 20 generos)")
        Log.wtf(TAG, "⚡ NEW: Detecção instantânea + Redirect automático sssrr.org → googleapis.com")
        
        // v217: Inicializar cache persistente
        try {
            val context = Class.forName("android.app.ActivityThread")
                .getMethod("currentApplication")
                .invoke(null) as android.content.Context
            VideoUrlCache.init(context)
            Log.d(TAG, "✅ Cache persistente inicializado (30min TTL, 100 URLs max)")
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao inicializar cache persistente: ${e.message}")
            Log.e(TAG, "⚠️ Usando apenas cache em memória (5min TTL)")
        }
        
        // Note: WebViewPool.destroy() não é chamado aqui pois o pool é singleton
        // e deve persistir durante toda a vida do app. Android gerencia o cleanup
        // quando o app é destruído.
    }

    override val mainPage = mainPageOf(
        "$mainUrl/" to "Início",
        "$mainUrl/trending" to "Em Alta",
        "$mainUrl/" to "Adicionados Recentemente",
        "$mainUrl/generos/acao" to "Ação",
        "$mainUrl/generos/aventura" to "Aventura",
        "$mainUrl/generos/animacao" to "Animação",
        "$mainUrl/generos/comedia" to "Comédia",
        "$mainUrl/generos/crime" to "Crime",
        "$mainUrl/generos/documentario" to "Documentário",
        "$mainUrl/generos/drama" to "Drama",
        "$mainUrl/generos/familia" to "Família",
        "$mainUrl/generos/fantasia" to "Fantasia",
        "$mainUrl/generos/faroeste" to "Faroeste",
        "$mainUrl/generos/ficcao-cientifica" to "Ficção Científica",
        "$mainUrl/generos/guerra" to "Guerra",
        "$mainUrl/generos/historia" to "História",
        "$mainUrl/generos/kids" to "Infantil",
        "$mainUrl/generos/misterio" to "Mistério",
        "$mainUrl/generos/musica" to "Música",
        "$mainUrl/generos/romance" to "Romance",
        "$mainUrl/generos/terror" to "Terror",
        "$mainUrl/generos/thriller" to "Thriller"
    )
    
    private fun upgradeImageQuality(url: String?): String? {
        if (url.isNullOrBlank()) return null
        return url.replace("/w185/", "/original/")
                  .replace("/w300/", "/original/")
                  .replace("/w342/", "/original/")
                  .replace("/w500/", "/original/")
                  .replace("/w780/", "/original/")
                  .replace("/w1280/", "/original/")
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

            // FIXME: 'toRatingInt' is deprecated. Implement new Score API.
            // val rating = document.selectFirst(".dt_rating_vgs")?.text()?.trim()?.toRatingInt()

            // Extrair recomendações
            val recommendations = document.select(".srelacionados article").mapNotNull {
                val recTitle = it.selectFirst("img")?.attr("alt") ?: return@mapNotNull null
                val recHref = it.selectFirst("a")?.attr("href") ?: return@mapNotNull null
                val recPoster = it.selectFirst("img")?.attr("src")
                newMovieSearchResponse(recTitle, fixUrl(recHref), TvType.Movie) {
                    this.posterUrl = upgradeImageQuality(fixUrlNull(recPoster))
                }
            }

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
                    // this.rating = rating
                    this.recommendations = recommendations
                }
            } else {
                // Para filmes, usar a URL do playerthree ou a página original
                val dataUrl = playerthreeUrl ?: url
                newMovieLoadResponse(title, url, TvType.Movie, dataUrl) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                    // this.rating = rating
                    this.recommendations = recommendations
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro load: ${e.message}")
            null
        }
    }

    /**
     * Extrai URL do iframe playerthree/viewplayer da página
     */
    private fun extractPlayerthreeUrl(document: Document): String? {
        // Procurar iframe do playerthree ou viewplayer
        val iframes = document.select("iframe[src*=playerthree], iframe[src*=viewplayer], iframe[src*=player]")
        for (iframe in iframes) {
            val src = iframe.attr("src")
            if (src.contains("playerthree.online") || src.contains("viewplayer.online")) {
                return src
            }
        }
        
        // Fallback: procurar no HTML usando regex
        val html = document.html()
        val pattern = Regex("""https?://(playerthree|viewplayer)\.online/(embed|filme)/[^"'\s]+""")
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
                
                val episodeItems = card.select("li")
                
                for (item in episodeItems) {
                    val linkElement = item.selectFirst("a") ?: continue
                    val href = linkElement.attr("href")
                    
                    // Formato esperado: #seasonId_episodeId (Ex: #12962_255703)
                    if (!href.startsWith("#")) continue
                    
                    val ids = href.removePrefix("#").split("_")
                    if (ids.size < 2) continue
                    
                    val seasonId = ids[0]
                    val episodeId = ids[1]
                    
                    val episodeTitle = linkElement.text().trim()
                    
                    // Extrair número do episódio do título
                    val epNumMatch = Regex("""^(\d+)\s*[-–]""").find(episodeTitle)
                    val epNum = epNumMatch?.groupValues?.get(1)?.toIntOrNull() ?: 1
                    
                    // Encontrar número da temporada
                    // Tentar achar pelo seasonId, ou usar contador
                    val seasonNum = seasons.find { it.first == seasonId }?.second ?: 1
                    
                    // Data URL v161
                    val dataUrl = "$playerthreeUrl|episodio|$episodeId|$seasonId"
                    
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
        Log.wtf(TAG, "🔗🔗🔗 LOADLINKS CHAMADO! DATA: $data")
        Log.d(TAG, "🔗 loadLinks: $data")
        
        return try {
            var linksFound = 0
            
            // Verificar se é URL do playerthree com episodeId
            if (data.contains("|episodio|")) {
                val parts = data.split("|episodio|")
                val playerthreeUrl = parts[0]
                // v161: Suporte a partes[2] (seasonId)
                val params = parts[1].split("|")
                val episodeId = params[0]
                val seasonId = params.getOrNull(1)
                
                linksFound = extractFromPlayerthreeEpisode(playerthreeUrl, episodeId, seasonId, subtitleCallback, callback)
            } 
            // URL direta do playerthree ou viewplayer (v219: adicionado viewplayer)
            else if (data.contains("playerthree.online") || data.contains("viewplayer.online")) {
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
        seasonId: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Int {
        var linksFound = 0
        
        try {
            // CORREÇÃO v167: playerthree.online mudou!
            // O site NÃO carrega botões via hash (#seasonId_episodeId).
            // É necessário fazer request direto para /episodio/{episodeId}
            val episodeUrl = "https://playerthree.online/episodio/$episodeId"
            
            Log.d(TAG, "🎬 Buscando episódio: $episodeUrl")
            
            // Headers customizados usando HeadersBuilder
            val headers = HeadersBuilder.standard(playerthreeUrl)
            
            val response = app.get(episodeUrl, headers = headers)
            
            val html = response.text
            
            // Extrair botões de player com data-source
            val sources = extractPlayerSources(html)
            Log.d(TAG, "🎯 Sources encontradas: ${sources.size} - $sources")
            
            if (sources.isEmpty()) {
                Log.e(TAG, "❌ Nenhuma source encontrada no playerthree!")
                Log.d(TAG, "📄 HTML snippet: ${html.take(500)}")
                return 0
            }
            
            // PRIORIZAÇÃO AUTOMÁTICA usando ServerPriority
            val sortedSources = ServerPriority.sortByPriority(sources) { source ->
                ServerPriority.detectServer(source)
            }
            
            for (source in sortedSources) {
                try {
                    Log.d(TAG, "🔍 Processando source: $source")
                    when {
                        // v209: MyVidPlay PRIMEIRO (funciona sem iframe!)
                        source.contains("myvidplay", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando MyVidPlayExtractor...")
                            MyVidPlayExtractor().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // v226: PlayerEmbedAPI Captura Imediata
                        source.contains("playerembedapi", ignoreCase = true) -> {
                            Log.wtf(TAG, "🌐🌐🌐 PLAYEREMBEDAPI v226! 🌐🌐🌐")
                            try {
                                val extractor = PlayerEmbedAPIWebViewExtractor()
                                val links = extractor.extractFromUrl(source, episodeUrl)
                                links.forEach { callback(it) }
                                linksFound += links.size
                                Log.wtf(TAG, "✅✅✅ PlayerEmbedAPI v226: ${links.size} links")
                            } catch (e: Exception) {
                                Log.e(TAG, "❌ PlayerEmbedAPI v226 falhou: ${e.message}")
                            }
                        }
                        // MegaEmbed V9 (principal - ~95% sucesso)
                        source.contains("megaembed", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando MegaEmbedExtractorV9...")
                            MegaEmbedExtractorV9().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // DoodStream (muito popular - v209)
                        source.contains("doodstream", ignoreCase = true) || source.contains("dood.", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando DoodStreamExtractor...")
                            DoodStreamExtractor().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // StreamTape (alternativa confiável - v209)
                        source.contains("streamtape", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando StreamtapeExtractor...")
                            StreamtapeExtractor().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // Mixdrop (backup - v209)
                        source.contains("mixdrop", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando MixdropExtractor...")
                            MixdropExtractor().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        // Filemoon (novo - v209)
                        source.contains("filemoon", ignoreCase = true) -> {
                            Log.d(TAG, "⚡ Tentando FilemoonExtractor...")
                            FilemoonExtractor().getUrl(source, episodeUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        else -> {
                             Log.d(TAG, "⚠️ Source desconhecida, tentando loader genérico: $source")
                             loadExtractor(source, episodeUrl, subtitleCallback, callback)
                             linksFound++
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "❌ Erro ao processar source: $source", e)
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
            
            val firstEpisode = document.selectFirst("li[data-episode-id]")
            if (firstEpisode != null) {
                val episodeId = firstEpisode.attr("data-episode-id")
                if (episodeId.isNotEmpty()) {
                    linksFound = extractFromPlayerthreeEpisode(playerthreeUrl, episodeId, null, subtitleCallback, callback)
                }
            }
            
            // Se não encontrou episódios, procurar sources diretas
            if (linksFound == 0) {
                val sources = extractPlayerSources(document.html())
                Log.d(TAG, "🎯 Sources encontradas (direct): ${sources.size} - $sources")
                
                // Processar cada source com o extractor apropriado
                for (source in sources) {
                    try {
                        Log.d(TAG, "🔍 Processando source (direct): $source")
                        when {
                            // v219: PlayerEmbedAPI via WebView
                            source.contains("playerembedapi", ignoreCase = true) -> {
                                Log.wtf(TAG, "🌐🌐🌐 PLAYEREMBEDAPI DETECTADO (DIRECT)! 🌐🌐🌐")
                                Log.d(TAG, "⚡ Tentando PlayerEmbedAPIWebViewExtractor...")
                                try {
                                    val imdbId = extractImdbIdFromUrl(playerthreeUrl)
                                    Log.d(TAG, "🎬 IMDB ID extraído: $imdbId")
                                    
                                    try {
                                        val extractor = PlayerEmbedAPIWebViewExtractor()
                                        val links = extractor.extractFromUrl(source, playerthreeUrl)
                                        links.forEach { callback(it) }
                                        linksFound += links.size
                                        Log.wtf(TAG, "✅✅✅ PlayerEmbedAPI v226: ${links.size} links")
                                    } catch (e: Exception) {
                                        Log.e(TAG, "❌ PlayerEmbedAPI v226 falhou: ${e.message}")
                                    }
                                } catch (e: Exception) {
                                    Log.e(TAG, "❌ PlayerEmbedAPI WebView falhou: ${e.message}")
                                }
                            }
                            // MegaEmbed
                            source.contains("megaembed", ignoreCase = true) -> {
                                Log.d(TAG, "⚡ Tentando MegaEmbedExtractorV9...")
                                MegaEmbedExtractorV9().getUrl(source, playerthreeUrl, subtitleCallback, callback)
                                linksFound++
                            }
                            // MyVidPlay
                            source.contains("myvidplay", ignoreCase = true) -> {
                                Log.d(TAG, "⚡ Tentando MyVidPlayExtractor...")
                                MyVidPlayExtractor().getUrl(source, playerthreeUrl, subtitleCallback, callback)
                                linksFound++
                            }
                            // DoodStream
                            source.contains("doodstream", ignoreCase = true) || source.contains("dood.", ignoreCase = true) -> {
                                Log.d(TAG, "⚡ Tentando DoodStreamExtractor...")
                                DoodStreamExtractor().getUrl(source, playerthreeUrl, subtitleCallback, callback)
                                linksFound++
                            }
                            // Outros
                            else -> {
                                Log.d(TAG, "⚠️ Source desconhecida, tentando loader genérico: $source")
                                loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
                                linksFound++
                            }
                        }
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
     * Extrai IMDB ID da URL do playerthree/viewplayer
     * Exemplos:
     * - https://playerthree.online/filme/tt13893970
     * - https://viewplayer.online/filme/tt13893970
     */
    private fun extractImdbIdFromUrl(url: String): String? {
        val imdbPattern = Regex("""/(filme|series?)/?(tt\d+)""", RegexOption.IGNORE_CASE)
        val match = imdbPattern.find(url)
        return match?.groupValues?.get(2)
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
        
        Log.d(TAG, "📋 Total sources extraídas (v184): ${sources.size} - $sources")
        return sources.distinct()
    }
}
