// Código gerado automaticamente baseado na análise do site
import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override suspend fun load(url: String): LoadResponse? {
        val doc = app.get(url).document
        val title = doc.selectFirst(".data h1")?.text() 
            ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text() 
            ?: doc.selectFirst(".entry-content")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        
        val isSeries = url.contains("/series/")

        if (isSeries) {
            val episodes = mutableListOf<Episode>()
            
            // Método baseado na análise: 0 seletores encontrados
            
            
            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster
                this.plot = desc
            }
        } else {
            return newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster
                this.plot = desc
            }
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val doc = app.get(data).document
        var linksFound = 0

        // Método baseado na análise: 0 tipos de players encontrados
        // Using loadExtractor to handle all supported extractors
        try {
            // Try to find iframe sources
            val iframes = doc.select("iframe")
            for (iframe in iframes) {
                val src = iframe.attr("src")
                if (src.isNotEmpty()) {
                    if (loadExtractor(src, data, subtitleCallback, callback)) {
                        linksFound++
                    }
                }
            }
            
            // Also try to find direct video links
            val links = doc.select("a[href*='.mp4'], a[href*='.m3u8']")
            for (link in links) {
                val href = link.attr("href")
                if (href.isNotEmpty()) {
                    if (loadExtractor(href, data, subtitleCallback, callback)) {
                        linksFound++
                    }
                }
            }
        } catch (e: Exception) {
            println("Error loading links: ${e.message}")
        }
        
        return linksFound > 0
    }
    
    override suspend fun search(query: String): List<SearchResponse> {
        return emptyList()
    }
    
    override suspend fun getMainPage(
        page: Int,
        request: MainPageRequest
    ): HomePageResponse {
        return HomePageResponse(emptyList())
    }
}