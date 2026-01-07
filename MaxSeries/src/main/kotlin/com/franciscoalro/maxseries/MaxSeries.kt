package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import org.jsoup.nodes.Element

@CloudstreamPlugin
class MaxSeries : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override suspend fun search(query: String): List<SearchResponse> {
        val url = "$mainUrl/?s=$query"
        val doc = app.get(url).document
        return doc.select(".result-item").mapNotNull {
            val title = it.selectFirst(".details .title a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".details .title a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".image img")?.attr("src")
            val typeText = it.selectFirst(".image span")?.text() ?: ""
            val type = if (typeText.contains("TV", true)) TvType.TvSeries else TvType.Movie

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

        val iframeSrc = doc.select("iframe").map { it.attr("src") }
            .find { it.contains("playerthree.online") }

        val episodes = ArrayList<Episode>()
        
        if (iframeSrc != null) {
            val iframeDoc = app.get(iframeSrc).document
            // Parse seasons and episodes
            // Expecting ul#list-seasons for season tabs and ul.list-episodes for items
            // But usually in these players, all episodes might be loaded in separate divs matchin the season
            
            // Generic approach for PlayerThree/DooPlay embedded:
            // S1 is visible, others might be hidden.
            // Let's grab all .list-episodes a
            
            // Check if there are multiple lists or if they are fetched.
            // Based on subagent, clicking season updated the list. 
            // It might be using AJAX or just switching hidden classes.
            // I'll assume they are all in the DOM for now or try to extract from script.
            
            val seasonElements = iframeDoc.select("ul#list-seasons li")
            if (seasonElements.isNotEmpty()) {
                // If we have seasons, we might need to iterate or check how they work.
                // For V1, let's just grab what is visible or common patterns.
                // Inspecting standard PlayerThree:
                // usually <div id="seasons"><div class="se-c" id="season-1">...</div></div>
                
                val seasonDivs = iframeDoc.select("div.se-c, div[id^=season-]")
                // If divs exist, mapped by season
                if (seasonDivs.isNotEmpty()) {
                   seasonDivs.forEach { sDiv ->
                       val seasonNum = sDiv.attr("data-season").toIntOrNull() 
                           ?: sDiv.attr("id").replace("season-","").toIntOrNull() ?: 1
                       sDiv.select("ul.list-episodes li a").forEach { ep ->
                           val epNum = ep.select("div.numerando").text().split("-").lastOrNull()?.trim()?.toIntOrNull()
                           val epName = ep.text()
                           val epUrl = ep.attr("href") // Likely #id
                           episodes.add(
                               newEpisode(iframeSrc) {
                                   this.name = epName
                                   this.season = seasonNum
                                   this.episode = epNum
                                   this.data = "$iframeSrc|$epUrl" // Pass iframeUrl and the target ID
                               }
                           )
                       }
                   }
                } else {
                    // Fallback: just finding all links
                     iframeDoc.select("ul.list-episodes li a").forEach { ep ->
                        val epName = ep.text()
                        val epUrl = ep.attr("href")
                        episodes.add(
                            newEpisode(iframeSrc) {
                                this.name = epName
                                this.data = "$iframeSrc|$epUrl"
                            }
                        )
                    }
                }
            } else {
                 // No season list, maybe movie or single season
                 iframeDoc.select("ul.list-episodes li a").forEach { ep ->
                    episodes.add(newEpisode(iframeSrc) {
                        this.name = ep.text()
                        this.data = "$iframeSrc|${ep.attr("href")}"
                    })
                 }
            }
        }

        return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
            this.posterUrl = poster
            this.plot = desc
            this.backgroundPosterUrl = bg
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // Data format: iframeSrc|epUrl (epUrl is like #1234)
        val parts = data.split("|")
        if (parts.size < 2) return false
        val iframeSrc = parts[0]
        val epId = parts[1] // e.g. #1234_5678

        val doc = app.get(iframeSrc).document
        
        // The id in href usually corresponds to a div id showing the players
        // e.g. <div id="1234_5678" class="play-ex"> ... buttons ... </div>
        // Or it triggers a JS function.
        // If it's a standard ID reference:
        
        val targetId = epId.removePrefix("#")
        val playerDiv = doc.selectFirst("div[id='$targetId']") ?: doc.selectFirst("div#$targetId")
        
        playerDiv?.select(".btn")?.forEach { btn ->
            // The button usually has 'data-player' or 'onclick' or 'href'
            // If href is javascript:..., look for data attributes.
            // Subagent said: "Selecting a player loads a nested iframe... Player #1... video source"
            
            // Common pattern: data-link or data-src
            // Or an onclick that calls a function with a URL.
            
            // Let's look for known attributes
            var playerUrl = btn.attr("data-src").ifEmpty { btn.attr("href") }
            
            // If it's a relative URL or needs fixing
            if (playerUrl.contains("playerembedapi.link")) {
                loadExtractor(playerUrl, "$mainUrl/", subtitleCallback, callback)
            } else if(playerUrl.startsWith("http")) {
                 loadExtractor(playerUrl, "$mainUrl/", subtitleCallback, callback)
            }
        }

        return true
    }
}
