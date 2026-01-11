package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.LoadResponse.Companion.addActors
import com.lagradost.cloudstream3.LoadResponse.Companion.addTrailer
import org.jsoup.nodes.Element
import com.franciscoalro.maxseries.extractors.*
import android.util.Log

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(
        TvType.Movie,
        TvType.TvSeries
    )

    // URLs corretas baseadas na estrutura real do site
    override val mainPage = mainPageOf(
        "$mainUrl/filmes" to "Filmes",
        "$mainUrl/series" to "Séries"
    )

    override suspend fun getMainPage(
        page: Int,
        request: MainPageRequest
    ): HomePageResponse {
        return try {
            // Para páginas com paginação, adicionar /page/X
            val url = if (page > 1) "${request.data}/page/$page" else request.data
            val document = app.get(url).document
            
            // Estrutura real: cada item está em um div sem classe específica, mas com estrutura consistente
            val home = document.select("div").filter { div ->
                // Filtrar divs que contêm título, data e sinopse (estrutura dos items)
                div.selectFirst("h3") != null && 
                div.text().matches(".*\\d{4}.*".toRegex()) // Contém ano
            }.mapNotNull { it.toSearchResult() }
            
            Log.d("MaxSeries", "✅ ${request.name}: ${home.size} items encontrados (página $page)")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao carregar ${request.name} página $page: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private fun Element.toSearchResult(): SearchResponse? {
        return try {
            // Estrutura real: título está em h3 dentro do div
            val titleElement = this.selectFirst("h3")
            val title = titleElement?.text()?.trim() ?: return null
            
            // Link está no h3 > a
            val linkElement = titleElement.selectFirst("a") ?: this.selectFirst("a")
            val href = fixUrl(linkElement?.attr("href") ?: return null)
            
            // Imagem está antes do h3
            val img = this.selectFirst("img")
            val posterUrl = fixUrlNull(
                img?.attr("src")
                    ?: img?.attr("data-src")
                    ?: img?.attr("data-lazy-src")
            )
            
            // Detectar tipo baseado na URL real
            val tvType = when {
                href.contains("/series/") -> TvType.TvSeries
                href.contains("/filmes/") -> TvType.Movie
                else -> {
                    // Fallback: analisar o texto para detectar se é série
                    val text = this.text().lowercase()
                    if (text.contains("temporada") || text.contains("episódio") || text.contains("season")) {
                        TvType.TvSeries
                    } else {
                        TvType.Movie
                    }
                }
            }
            
            // Extrair ano se disponível
            val yearText = this.text()
            val year = "\\b(19|20)\\d{2}\\b".toRegex().find(yearText)?.value?.toIntOrNull()
            
            // Extrair rating IMDb se disponível
            val ratingText = this.text()
            val imdbRating = "IMDb: ([0-9.]+)".toRegex().find(ratingText)?.groupValues?.get(1)?.toFloatOrNull()

            newMovieSearchResponse(title, href, tvType) {
                this.posterUrl = posterUrl
                this.year = year
                if (imdbRating != null) {
                    this.rating = (imdbRating * 1000).toInt() // CloudStream usa rating * 1000
                }
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao processar item: ${e.message}")
            null
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) return emptyList()
        
        return try {
            Log.d("MaxSeries", "🔍 Pesquisando: $query")
            val document = app.get("$mainUrl/?s=${query.replace(" ", "+")}").document
            
            // Usar a mesma lógica de parsing da página principal
            val results = document.select("div").filter { div ->
                div.selectFirst("h3") != null && 
                div.text().matches(".*\\d{4}.*".toRegex())
            }.mapNotNull { it.toSearchResult() }
            
            Log.d("MaxSeries", "✅ Pesquisa '$query': ${results.size} resultados")
            results
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro na pesquisa '$query': ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            Log.d("MaxSeries", "📖 Carregando: $url")
            val document = app.get(url).document

            // Título principal (h1 ou similar)
            val title = document.selectFirst("h1, .title")?.text()?.trim()
                ?: document.title().substringBefore(" - ").trim()
            
            if (title.isBlank()) {
                Log.e("MaxSeries", "❌ Título não encontrado: $url")
                return null
            }

            // Título original
            val originalTitle = document.select("*:contains(Título original)").firstOrNull()
                ?.text()?.substringAfter(":")?.trim()

            // Poster/imagem
            val poster = fixUrlNull(
                document.selectFirst("img[src*=tmdb], img[src*=imdb], .poster img, img")?.attr("src")
                    ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            )

            // Gêneros
            val genres = document.select("*:contains(GÊNEROS)").firstOrNull()
                ?.text()?.substringAfter(":")?.trim()?.split(" ")?.filter { it.isNotBlank() } ?: emptyList()

            // Ano
            val yearText = document.select("*:contains(DATA DE LANÇAMENTO), *:contains(LANÇAMENTO)").firstOrNull()
                ?.text() ?: document.text()
            val year = "\\b(19|20)\\d{2}\\b".toRegex().find(yearText)?.value?.toIntOrNull()

            // Rating
            val ratingText = document.text()
            val rating = "IMDb: ([0-9.]+)".toRegex().find(ratingText)?.groupValues?.get(1)?.toFloatOrNull()

            // Sinopse
            val plot = document.select("*:contains(SINOPSE)").firstOrNull()
                ?.parent()?.text()?.substringAfter("SINOPSE")?.trim()
                ?: document.selectFirst(".description, .synopsis, .plot")?.text()?.trim()

            // Detectar se é série ou filme
            val isSeriesPage = url.contains("/series/") || 
                              document.text().contains("TEMPORADAS:", true) ||
                              document.text().contains("episódio", true)

            Log.d("MaxSeries", "✅ Carregado '$title' - Tipo: ${if (isSeriesPage) "Série" else "Filme"}")

            return if (isSeriesPage) {
                // Para séries, criar lista de episódios (pode ser expandido futuramente)
                val episodes = listOf(
                    newEpisode(url) {
                        this.name = title
                        this.episode = 1
                        this.season = 1
                    }
                )

                newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                    this.rating = rating?.let { (it * 1000).toInt() }
                }
            } else {
                newMovieLoadResponse(title, url, TvType.Movie, url) {
                    this.posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                    this.rating = rating?.let { (it * 1000).toInt() }
                }
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao carregar $url: ${e.message}")
            null
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d("MaxSeries", "🔗 Carregando links: $data")
            val document = app.get(data).document
            
            var linksFound = 0
            
            // Procurar por botões de player ou iframes
            val playerElements = document.select("button[data-source], iframe[src], a[href*=player]")
            
            playerElements.forEach { element ->
                val sourceUrl = element.attr("data-source").ifEmpty { 
                    element.attr("src").ifEmpty { 
                        element.attr("href") 
                    }
                }
                
                if (sourceUrl.isNotEmpty() && !sourceUrl.contains("youtube", true)) {
                    Log.d("MaxSeries", "🎬 Processando: $sourceUrl")
                    
                    when {
                        sourceUrl.contains("dood", true) ||
                        sourceUrl.contains("vidplay", true) -> {
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        sourceUrl.contains("megaembed", true) -> {
                            // Usar extrator específico se disponível
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            linksFound++
                        }
                        else -> {
                            loadExtractor(sourceUrl, subtitleCallback, callback)
                            linksFound++
                        }
                    }
                }
            }
            
            Log.d("MaxSeries", "✅ Links processados: $linksFound")
            linksFound > 0
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro ao carregar links: ${e.message}")
            false
        }
    }
}