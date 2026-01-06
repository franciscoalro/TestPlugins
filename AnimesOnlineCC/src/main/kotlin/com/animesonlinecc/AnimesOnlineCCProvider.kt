package com.animesonlinecc

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import java.util.EnumSet

class AnimesOnlineCCProvider : MainAPI() {
    override var mainUrl = "https://animesonlinecc.to"
// ... (código intermediário omitido, mantendo o original)

    private fun org.jsoup.nodes.Element.toSearchResult(): AnimeSearchResponse? {
        val title = this.selectFirst("h3")?.text()?.trim() ?: return null
        val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
        
        // BLINDAGEM DE IMAGENS: Busca em todos os lugares possíveis
        val img = this.selectFirst("img")
        val posterUrl = fixUrlNull(
            img?.attr("src")
                ?: img?.attr("data-src")
                ?: img?.attr("data-lazy-src")
                ?: img?.attr("data-original")
                ?: img?.attr("srcset")?.substringBefore(" ") // Pega a primeira url do srcset
        )
        
        val isDubbed = title.contains("Dublado", ignoreCase = true)
        
        return newAnimeSearchResponse(title, href, TvType.Anime) {
            this.posterUrl = posterUrl
            this.dubStatus = if (isDubbed) {
                EnumSet.of(DubStatus.Dubbed)
            } else {
                EnumSet.of(DubStatus.Subbed)
            }
        }
    }

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
        
        // BLINDAGEM NO LOAD: Tenta pegar de várias tags
        val img = document.selectFirst("div.poster img, .sheader .poster img")
        val poster = img?.attr("src")
            ?: img?.attr("data-src")
            ?: img?.attr("data-lazy-src")
            ?: img?.attr("data-original")
            ?: document.selectFirst("meta[property=og:image]")?.attr("content") // Último recurso: imagem do meta tag
        
        val description = document.selectFirst("div.description, div.wp-content")?.text()?.trim()
        
        val genres = document.select("div.sgeneros a").map { it.text() }
        
        val year = document.selectFirst("span.date, span.year, .extra span")?.text()
            ?.replace("\\D".toRegex(), "")?.take(4)?.toIntOrNull()
        
        val isDubbed = title.contains("Dublado", ignoreCase = true)
        val dubStatus = if (isDubbed) DubStatus.Dubbed else DubStatus.Subbed
        
        val episodes = document.select("ul.episodios li").mapNotNull { ep ->
            val epTitle = ep.selectFirst(".episodiotitle a")?.text() ?: return@mapNotNull null
            val epHref = fixUrl(ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null)
            val epNum = epTitle.replace("\\D".toRegex(), "").toIntOrNull()
            
            newEpisode(epHref) {
                this.name = epTitle
                this.episode = epNum
            }
        }.reversed()

        return newAnimeLoadResponse(title, url, TvType.Anime) {
            this.posterUrl = poster
            this.plot = description
            this.tags = genres
            this.year = year
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
