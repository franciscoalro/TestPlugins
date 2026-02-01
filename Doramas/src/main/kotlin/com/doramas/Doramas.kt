package com.doramas

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.LoadResponse.Companion.addActors
import com.lagradost.cloudstream3.LoadResponse.Companion.addTrailer
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Document
import org.jsoup.nodes.Element
import android.util.Log

/**
 * Doramas - Provider de conteúdo asiático
 * 
 * Suporte a:
 * - Doramas coreanos
 * - Doramas chineses
 * - Doramas japoneses
 * - Filmes asiáticos
 */
class Doramas : MainAPI() {
    override var mainUrl = "https://doramasonline.co"
    override var name = "Doramas Online"
    override var lang = "pt-br"
    override val hasMainPage = true
    override val hasDownloadSupport = true
    override val hasQuickSearch = true
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)

    companion object {
        private const val TAG = "Doramas"
    }

    override val mainPage = mainPageOf(
        "$mainUrl/category/lancamentos/" to "🆕 Lançamentos",
        "$mainUrl/category/comedia/" to "😂 Comédia",
        "$mainUrl/category/crime/" to "🚔 Crime",
        "$mainUrl/category/documentario/" to "📺 Documentário",
        "$mainUrl/category/drama/" to "🎭 Drama",
        "$mainUrl/category/familia/" to "👨‍👩‍👧‍👦 Família",
        "$mainUrl/category/misterio/" to "🔍 Mistério",
        "$mainUrl/category/romance/" to "❤️ Romance",
        "$mainUrl/category/terror/" to "👻 Terror",
        "$mainUrl/category/thriller/" to "😰 Thriller"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val url = request.data + if (page > 1) "page/$page/" else ""
            val document = app.get(url).document
            val home = document.select("div.aa-cn div#movies-a ul.post-lst li")
                .mapNotNull { it.toSearchResult() }

            Log.d(TAG, "✅ ${request.name}: ${home.size} items (página $page)")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) return emptyList()
        
        return try {
            Log.d(TAG, "🔍 Buscando: $query")
            val document = app.get("$mainUrl/?s=$query").document
            val results = document.select("div.aa-cn div#movies-a ul.post-lst li")
                .mapNotNull { it.toSearchResult() }
            
            Log.d(TAG, "✅ Busca '$query': ${results.size} resultados")
            results
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro busca: ${e.message}")
            emptyList()
        }
    }

    private fun Element.toSearchResult(): SearchResponse? {
        return try {
            val title = selectFirst("header.entry-header h2.entry-title")?.text()?.trim() ?: return null
            val href = selectFirst("a.lnk-blk")?.attr("href") ?: return null
            val poster = selectPoster("div.post-thumbnail figure img", "/w500/")
            val year = selectFirst("span.year")?.text()?.toIntOrNull()
            val ratingText = selectFirst("div.entry-meta span.vote")?.text()
                ?.replace("TMDB", "")
                ?.trim()

            newMovieSearchResponse(title, href, TvType.Movie) {
                posterUrl = poster
                this.year = year
                this.quality = getQualityFromString(selectFirst("span.post-ql")?.text())
                this.score = Score.from10(ratingText)
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro toSearchResult: ${e.message}")
            null
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            val document = app.get(url).document
            val title = document.selectFirst("aside.fg1 header.entry-header h1.entry-title")?.text() ?: return null
            val poster = document.selectPoster("div.bghd img.TPostBg", "/w1280/")
            val year = document.extractInt("span.year")
            val durationText = document.extractText("span.duration")
            val score = document.selectFirst("div.vote-cn span.vote span.num")?.text()?.toDoubleOrNull()
            val plot = document.selectFirst("aside.fg1 div.description p")?.text()
            val genres = document.select("span.genres a").map { it.text() }
            val actors = document.selectActors()
            val trailer = document.selectFirst("div.mdl-cn iframe")?.attr("src")
            
            val iframeUrl = document.selectFirst("iframe[src*='seriesboa.live']")?.attr("src")
            val isSerie = url.contains("/serie/")

            return if (isSerie) {
                val episodes = if (iframeUrl != null) {
                    parseEpisodes(app.get(iframeUrl).document)
                } else emptyList()

                newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                    posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                    this.score = Score.from10(score)
                    if (!actors.isNullOrEmpty()) addActors(actors)
                    addTrailer(trailer)
                }
            } else {
                newMovieLoadResponse(title, url, TvType.Movie, iframeUrl ?: "") {
                    posterUrl = poster
                    this.year = year
                    this.plot = plot
                    this.tags = genres
                    this.duration = parseDuration(durationText)
                    this.score = Score.from10(score)
                    if (!actors.isNullOrEmpty()) addActors(actors)
                    addTrailer(trailer)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro load: ${e.message}")
            null
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        if (data.isBlank()) return false

        val idOnly = Regex("""(\d+)$""").find(data.trimEnd('/'))?.value
        
        if (idOnly == null) {
            Log.e(TAG, "❌ Não conseguiu extrair ID da URL: $data")
            return false
        }

        val playerPageUrl = "https://seriesboa.live/episodio/$idOnly"

        return try {
            Log.d(TAG, "🎬 Carregando links de: $playerPageUrl")
            val response = app.get(playerPageUrl)
            val playerDoc = response.document
            val links = extractEmbedLinks(playerDoc)
            
            Log.d(TAG, "🔗 Links encontrados: ${links.size}")

            links.forEach { link ->
                Log.d(TAG, "  → Processando: $link")
                
                when {
                    link.contains("embedplay.upns") ->
                        EmbedPlayUpnsPro().getUrl(link, playerPageUrl, subtitleCallback, callback)

                    link.contains("embedplay.upn.one") ->
                        EmbedPlayUpnOne().getUrl(link, playerPageUrl, subtitleCallback, callback)

                    link.contains("playembedapi") -> {
                        // Skip - não funciona bem
                        Log.d(TAG, "  ⚠️ Pulando playembedapi")
                    }

                    else ->
                        loadExtractor(link, playerPageUrl, subtitleCallback, callback)
                }
            }
            
            links.isNotEmpty()
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro loadLinks: ${e.message}")
            false
        }
    }

    private fun parseEpisodes(doc: Document): List<Episode> {
        val episodes = mutableListOf<Episode>()
        val seasons = doc.select("ul.header-navigation li[data-season-id]")

        seasons.forEach { season ->
            val seasonNumber = season.attr("data-season-number").toIntOrNull() ?: 1
            val seasonId = season.attr("data-season-id")

            doc.select("li[data-season-id='$seasonId']").forEach { ep ->
                val epId = ep.attr("data-episode-id")
                if (epId.isBlank()) return@forEach

                val name = ep.selectFirst("a")?.text().orEmpty()
                val number = Regex("\\d+").find(name)?.value?.toIntOrNull() ?: 1

                episodes += newEpisode(epId) {
                    this.name = name.trim()
                    this.season = seasonNumber
                    this.episode = number
                }
            }
        }
        return episodes.distinctBy { it.data }
    }

    private fun extractEmbedLinks(doc: Document): List<String> {
        val buttons = doc.select("button[data-source]").mapNotNull { it.attr("data-source") }
        val iframes = doc.select("div#player iframe, div.play-overlay iframe").mapNotNull { it.attr("src") }
        return (buttons + iframes).distinct().filter { it.isNotBlank() }
    }

    private fun Document.selectActors(): List<Pair<Actor, ActorRole?>>? {
        val actors = select("ul.cast-lst a").map {
            Actor(it.text(), it.attr("href")) to null
        }
        return actors.ifEmpty { null }
    }

    private fun Element.selectPoster(selector: String, replace: String): String? {
        val img = selectFirst(selector) ?: return null
        val src = img.attr("src").ifBlank { img.attr("data-src") }
        return src.takeIf { it.isNotBlank() }
            ?.let { if (it.startsWith("//")) "https:$it" else it }
            ?.replace(replace, "/original/")
    }

    private fun Document.selectPoster(selector: String, replace: String): String? = 
        (this as Element).selectPoster(selector, replace)

    private fun Document.extractInt(selector: String): Int? =
        selectFirst(selector)?.text()?.filter { it.isDigit() }?.toIntOrNull()

    private fun Document.extractText(selector: String): String? =
        selectFirst(selector)?.text()

    private fun parseDuration(text: String?): Int? {
        if (text == null) return null
        Regex("(\\d+)h\\s*(\\d+)m").find(text)?.let {
            return (it.groupValues[1].toIntOrNull() ?: 0) * 60 +
                    (it.groupValues[2].toIntOrNull() ?: 0)
        }
        return Regex("(\\d+)m").find(text)?.groupValues?.get(1)?.toIntOrNull()
    }
}
