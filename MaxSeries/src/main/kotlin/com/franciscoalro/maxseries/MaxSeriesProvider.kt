package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import android.util.Log
import org.jsoup.nodes.Element

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
            ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text() 
            ?: doc.selectFirst(".entry-content")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        val bg = doc.selectFirst(".backdrop img")?.attr("src")
        
        val isSeries = url.contains("/series/")

        if (isSeries) {
            val episodes = mutableListOf<Episode>()
            
            // Standard DooPlay episode extraction
            doc.select("ul.episodios li").forEach { ep ->
                val epA = ep.selectFirst("a") ?: return@forEach
                val epTitle = epA.text().ifEmpty { ep.selectFirst(".episodiotiitle")?.text() ?: "Episódio" }
                val epHref = epA.attr("href")
                
                // Try to extract season/episode from structure or title
                val seasonNum = ep.parents().select(".se-c").attr("id").replace("season-", "").toIntOrNull() 
                    ?: ep.parents().select("div[id^=season-]").attr("id").replace("season-", "").toIntOrNull()
                    ?: 1
                
                val epNum = ep.selectFirst(".numerando")?.text()?.split("-")?.lastOrNull()?.trim()?.toIntOrNull()
                    ?: epTitle.replace(Regex(".*?(\\d+).*"), "$1").toIntOrNull()

                episodes.add(newEpisode(epHref) {
                    this.name = epTitle
                    this.episode = epNum
                    this.season = seasonNum
                })
            }

            // Fallback for different DooPlay structures
            if (episodes.isEmpty()) {
                doc.select("div.se-c").forEach { sDiv ->
                    val sNum = sDiv.attr("id").replace("season-", "").toIntOrNull() ?: 1
                    sDiv.select("ul.list-episodes li a, ul.episodios li a").forEach { ep ->
                        val epTitle = ep.text()
                        val epHref = ep.attr("href")
                        val epNum = ep.selectFirst(".numerando")?.text()?.split("-")?.lastOrNull()?.trim()?.toIntOrNull()
                        
                        episodes.add(newEpisode(epHref) {
                            this.name = epTitle
                            this.episode = epNum
                            this.season = sNum
                        })
                    }
                }
            }

            Log.d("MaxSeries", "✅ Encontrados ${episodes.size} episódios para $title")

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
        // Data can be the episode URL or movie URL
        val doc = app.get(data).document
        var linksFound = 0
        
        // 1. Look for iframes
        doc.select("iframe").forEach { iframe ->
            val src = iframe.attr("src").ifEmpty { iframe.attr("data-src") }
            if (src.isNotEmpty() && !src.contains("facebook.com") && !src.contains("twitter.com") && !src.contains("google.com")) {
                val fixedSrc = if (src.startsWith("//")) "https:$src" else src
                if (fixedSrc.startsWith("http")) {
                    try {
                        loadExtractor(fixedSrc, data, subtitleCallback, callback)
                        linksFound++
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "Erro ao carregar extractor para $fixedSrc: ${e.message}")
                    }
                }
            }
        }
        
        // 2. Look for DooPlay player options
        doc.select("li[data-link], li[data-url]").forEach { li ->
            val link = li.attr("data-link").ifEmpty { li.attr("data-url") }
            if (link.isNotEmpty()) {
                val fixedLink = if (link.startsWith("//")) "https:$link" else link
                try {
                    loadExtractor(fixedLink, data, subtitleCallback, callback)
                    linksFound++
                } catch (e: Exception) {
                    Log.e("MaxSeries", "Erro ao carregar extractor para $fixedLink: ${e.message}")
                }
            }
        }

        // 3. Look for buttons with data-source (primary), onclick/data-player
        doc.select(".btn, .player-option, button.btn").forEach { btn ->
            // MaxSeries primarily uses 'data-source' attribute
            val link = btn.attr("data-source")
                .ifEmpty { btn.attr("data-player") }
                .ifEmpty { btn.attr("data-link") }
                .ifEmpty { btn.attr("data-src") }
            
            if (link.isNotEmpty()) {
                val fixedLink = if (link.startsWith("//")) "https:$link" else link
                if (fixedLink.startsWith("http")) {
                    try {
                        loadExtractor(fixedLink, data, subtitleCallback, callback)
                        linksFound++
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "Erro ao carregar extractor para $fixedLink: ${e.message}")
                    }
                }
            }
        }

        return linksFound > 0
    }
}
