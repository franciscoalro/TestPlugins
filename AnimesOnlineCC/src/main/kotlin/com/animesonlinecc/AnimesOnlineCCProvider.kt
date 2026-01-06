package com.animesonlinecc

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

class AnimesOnlineCCProvider : MainAPI() {
    override var mainUrl = "https://animesonlinecc.to"
    override var name = "Animes Online CC"
    override val hasMainPage = true
    override var lang = "pt-BR"
    
    // Melhoria 6: Suporte a OVA e Filmes
    override val supportedTypes = setOf(
        TvType.Anime,
        TvType.OVA,
        TvType.AnimeMovie
    )

    // Melhoria 1: Mais gêneros na página principal
    override val mainPage = mainPageOf(
        "$mainUrl/page/" to "Animes Recentes",
        "$mainUrl/genero/acao/page/" to "Ação",
        "$mainUrl/genero/aventura/page/" to "Aventura",
        "$mainUrl/genero/comedia/page/" to "Comédia",
        "$mainUrl/genero/romance/page/" to "Romance",
        "$mainUrl/genero/fantasia/page/" to "Fantasia",
        "$mainUrl/genero/drama/page/" to "Drama",
        "$mainUrl/genero/escolar/page/" to "Escolar",
        "$mainUrl/genero/seinen/page/" to "Seinen",
        "$mainUrl/genero/shounen/page/" to "Shounen",
        "$mainUrl/genero/sobrenatural/page/" to "Sobrenatural",
        "$mainUrl/genero/suspense/page/" to "Suspense"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        val document = app.get(request.data + page).document
        val home = document.select("div.items article.item").mapNotNull {
            it.toSearchResult()
        }
        return newHomePageResponse(request.name, home)
    }

    private fun org.jsoup.nodes.Element.toSearchResult(): AnimeSearchResponse? {
        val title = this.selectFirst("h3")?.text()?.trim() ?: return null
        val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
        
        // Melhoria 3: Fallback para poster
        val posterUrl = fixUrlNull(
            this.selectFirst("img")?.attr("src")
                ?: this.selectFirst("img")?.attr("data-src")
                ?: this.selectFirst("img")?.attr("data-lazy-src")
        )
        
        // Melhoria 2: Detectar se é dublado
        val isDubbed = title.contains("Dublado", ignoreCase = true)
        
        return newAnimeSearchResponse(title, href, TvType.Anime) {
            this.posterUrl = posterUrl
            this.dubStatus = if (isDubbed) {
                setOf(DubStatus.Dubbed)
            } else {
                setOf(DubStatus.Subbed)
            }
        }
    }

    // Melhoria 5: Tratamento de erros na busca
    override suspend fun search(query: String): List<SearchResponse> {
        return try {
            val document = app.get("$mainUrl/?s=$query").document
            document.select("div.items article.item").mapNotNull {
                it.toSearchResult()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse {
        val document = app.get(url).document
        
        val title = document.selectFirst("h1")?.text()?.trim() ?: ""
        
        // Melhoria 3: Fallback para poster com múltiplas fontes
        val poster = document.selectFirst("div.poster img")?.attr("src")
            ?: document.selectFirst("div.poster img")?.attr("data-src")
            ?: document.selectFirst("meta[property=og:image]")?.attr("content")
        
        val description = document.selectFirst("div.description, div.wp-content")?.text()?.trim()
        
        val genres = document.select("div.sgeneros a").map { it.text() }
        
        // Melhoria 4: Extrair ano de lançamento
        val year = document.selectFirst("span.date, span.year, .extra span")?.text()
            ?.replace("\\D".toRegex(), "")?.take(4)?.toIntOrNull()
        
        // Melhoria 2: Detectar se é dublado pelo título
        val isDubbed = title.contains("Dublado", ignoreCase = true)
        val dubStatus = if (isDubbed) DubStatus.Dubbed else DubStatus.Subbed
        
        val episodes = document.select("ul.episodios li").mapNotNull { ep ->
            val epTitle = ep.selectFirst(".episodiotitle a")?.text() ?: return@mapNotNull null
            val epHref = fixUrl(ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null)
            
            // Extrai o número do episódio do título
            val epNum = epTitle.replace("\\D".toRegex(), "").toIntOrNull()
            
            newEpisode(epHref) {
                this.name = epTitle
                this.episode = epNum
            }
        }.reversed() // Inverte para ordem crescente

        return newAnimeLoadResponse(title, url, TvType.Anime) {
            this.posterUrl = poster
            this.plot = description
            this.tags = genres
            this.year = year  // Melhoria 4: Ano de lançamento
            addEpisodes(dubStatus, episodes)
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // Melhoria 5: Tratamento de erros
        return try {
            val document = app.get(data).document
            
            // Procura por iframes de vídeo
            document.select("iframe").forEach { iframe ->
                val iframeUrl = iframe.attr("src").ifBlank { iframe.attr("data-src") }
                if (iframeUrl.isNotBlank()) {
                    loadExtractor(iframeUrl, data, subtitleCallback, callback)
                }
            }
            
            // Procura por links diretos de vídeo
            document.select("div.player a, div.playeroptions a, ul.options a").forEach { option ->
                val videoUrl = option.attr("href")
                if (videoUrl.isNotBlank() && videoUrl.startsWith("http")) {
                    loadExtractor(videoUrl, data, subtitleCallback, callback)
                }
            }
            
            true
        } catch (e: Exception) {
            false
        }
    }
}
