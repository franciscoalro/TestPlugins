package com.animesonlinecc

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element

class AnimesOnlineCCProvider : MainAPI() {
    override var mainUrl = "https://animesonlinecc.to"
    override var name = "Animes Online CC"
    override val hasMainPage = true
    override var lang = "pt-BR"
    override val supportedTypes = setOf(TvType.Anime)

    override val mainPage = mainPageOf(
        "$mainUrl/page/" to "Animes Recentes",
        "$mainUrl/genero/acao/page/" to "Ação",
        "$mainUrl/genero/aventura/page/" to "Aventura",
        "$mainUrl/genero/comedia/page/" to "Comédia"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        val document = app.get(request.data + page).document
        val home = document.select("div.items article.item").mapNotNull {
            it.toSearchResult()
        }
        return newHomePageResponse(request.name, home)
    }

    private fun Element.toSearchResult(): AnimeSearchResponse? {
        val title = this.selectFirst("h3")?.text()?.trim() ?: return null
        val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
        val posterUrl = fixUrlNull(this.selectFirst("img")?.attr("src"))
        
        return newAnimeSearchResponse(title, href, TvType.Anime) {
            this.posterUrl = posterUrl
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        val document = app.get("$mainUrl/?s=$query").document
        return document.select("div.items article.item").mapNotNull {
            it.toSearchResult()
        }
    }

    override suspend fun load(url: String): LoadResponse {
        val document = app.get(url).document
        
        val title = document.selectFirst("h1")?.text()?.trim() ?: ""
        val poster = document.selectFirst("div.poster img")?.attr("src")
        val description = document.selectFirst("div.description, div.wp-content")?.text()?.trim()
        
        val genres = document.select("div.sgeneros a").map { it.text() }
        
        val episodes = document.select("ul.episodios li").mapNotNull { ep ->
            val epTitle = ep.selectFirst(".episodiotitle a")?.text() ?: return@mapNotNull null
            val epHref = fixUrl(ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null)
            
            // Extrai o número do episódio do título
            val epNum = epTitle.replace("\\D".toRegex(), "").toIntOrNull()
            
            Episode(
                data = epHref,
                name = epTitle,
                episode = epNum
            )
        }.reversed() // Inverte para ordem crescente

        return newAnimeLoadResponse(title, url, TvType.Anime) {
            this.posterUrl = poster
            this.plot = description
            this.tags = genres
            addEpisodes(DubStatus.Subbed, episodes)
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val document = app.get(data).document
        
        // Procura por iframes de vídeo
        document.select("iframe").forEach { iframe ->
            val iframeUrl = iframe.attr("src")
            if (iframeUrl.isNotBlank()) {
                loadExtractor(iframeUrl, data, subtitleCallback, callback)
            }
        }
        
        // Procura por links diretos de vídeo
        document.select("div.player a, div.playeroptions a").forEach { option ->
            val videoUrl = option.attr("href")
            if (videoUrl.isNotBlank() && videoUrl.startsWith("http")) {
                loadExtractor(videoUrl, data, subtitleCallback, callback)
            }
        }
        
        return true
    }
}
