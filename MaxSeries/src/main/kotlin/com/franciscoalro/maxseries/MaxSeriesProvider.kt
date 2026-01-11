package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element
import android.util.Log

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)

    override val mainPage = mainPageOf(
        "$mainUrl/filmes" to "Filmes",
        "$mainUrl/series" to "Séries"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val url = if (page > 1) "${request.data}/page/$page" else request.data
            val document = app.get(url).document
            
            // Seletor correto: article.item (estrutura real do site)
            val home = document.select("article.item").mapNotNull { it.toSearchResult() }
            
            Log.d("MaxSeries", "✅ ${request.name}: ${home.size} items (página $page)")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private fun Element.toSearchResult(): SearchResponse? {
        return try {
            // Estrutura real: article.item > .image > a + img + .data > h3.title + span(ano)
            val titleElement = this.selectFirst("h3.title, .title, h3")
            val title = titleElement?.text()?.trim() ?: return null
            
            // Filtrar items inválidos (login, etc)
            if (title.contains("Login", true) || 
                title.contains("Register", true) ||
                title.contains("Account", true) ||
                title.length < 2) return null
            
            val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
            
            // Filtrar URLs inválidas
            if (!href.contains("/filmes/") && !href.contains("/series/")) return null
            
            // Imagem: .image img
            val img = this.selectFirst(".image img, img")
            val posterUrl = fixUrlNull(img?.attr("src") ?: img?.attr("data-src"))
            
            // Ano: .data span
            val yearText = this.selectFirst(".data span, span")?.text() ?: ""
            val year = "\\b(19|20)\\d{2}\\b".toRegex().find(yearText)?.value?.toIntOrNull()
            
            // Tipo baseado na URL
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

            // Título: h1 ou .sheader h1
            val title = document.selectFirst("h1")?.text()?.trim()
                ?: document.title().substringBefore(" - ").trim()
            
            if (title.isBlank() || title.contains("Login", true)) return null

            // Poster: .poster img
            val poster = fixUrlNull(
                document.selectFirst(".poster img")?.attr("src")
                    ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            )

            // Gêneros: .sgeneros a
            val genres = document.select(".sgeneros a").map { it.text().trim() }

            // Ano: extrair do texto da página
            val pageText = document.text()
            val year = "DATA DE LANÇAMENTO[:\\s]*([A-Za-z.]+\\s*\\d{1,2},?\\s*)?(\\d{4})".toRegex()
                .find(pageText)?.groupValues?.lastOrNull()?.toIntOrNull()
                ?: "\\b(19|20)\\d{2}\\b".toRegex().find(pageText)?.value?.toIntOrNull()

            // Sinopse: texto após SINOPSE até COMPARTILHE ou ELENCO
            val plot = "SINOPSE\\s*(.+?)(?:COMPARTILHE|ELENCO|TRAILER|$)".toRegex(RegexOption.DOT_MATCHES_ALL)
                .find(pageText)?.groupValues?.get(1)?.trim()?.take(500)

            // Detectar tipo
            val isSeriesPage = url.contains("/series/") || 
                              pageText.contains("TEMPORADAS:", true)

            return if (isSeriesPage) {
                // Buscar episódios/temporadas
                val episodes = parseEpisodes(document, url)
                
                newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                }
            } else {
                newMovieLoadResponse(title, url, TvType.Movie, url) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                }
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro load: ${e.message}")
            null
        }
    }
    
    private fun parseEpisodes(document: org.jsoup.nodes.Document, baseUrl: String): List<Episode> {
        val episodes = mutableListOf<Episode>()
        
        // Procurar temporadas e episódios
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
        
        // Se não encontrou episódios, criar um placeholder
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
        return try {
            val document = app.get(data).document
            var linksFound = 0
            
            // Procurar iframes e botões de player
            val sources = mutableListOf<String>()
            
            // Iframes diretos
            document.select("iframe[src]").forEach { iframe ->
                val src = iframe.attr("src")
                if (src.isNotEmpty() && !src.contains("youtube", true)) {
                    sources.add(fixUrl(src))
                }
            }
            
            // Botões com data-source
            document.select("[data-source], [data-src]").forEach { btn ->
                val src = btn.attr("data-source").ifEmpty { btn.attr("data-src") }
                if (src.isNotEmpty()) sources.add(fixUrl(src))
            }
            
            // Links de player
            document.select("a[href*=player], a[href*=embed]").forEach { link ->
                val href = link.attr("href")
                if (href.isNotEmpty() && !href.contains("youtube", true)) {
                    sources.add(fixUrl(href))
                }
            }
            
            // Processar cada source
            sources.distinct().forEach { sourceUrl ->
                try {
                    loadExtractor(sourceUrl, data, subtitleCallback, callback)
                    linksFound++
                } catch (e: Exception) {
                    Log.e("MaxSeries", "Erro extractor: ${e.message}")
                }
            }
            
            linksFound > 0
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro loadLinks: ${e.message}")
            false
        }
    }
}
