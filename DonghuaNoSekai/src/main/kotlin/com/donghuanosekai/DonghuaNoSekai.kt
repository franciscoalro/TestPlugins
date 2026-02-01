package com.donghuanosekai

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element
import android.util.Log
import java.util.EnumSet
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * DonghuaNoSekai - Provider de animes chineses (Donghuas)
 * 
 * Suporte a:
 * - Donghuas (animes chineses)
 * - Animes 3D chineses
 * - Cultivo, Xianxia, Wuxia
 */
class DonghuaNoSekai : MainAPI() {
    override var mainUrl = "https://donghuanosekai.com"
    override var name = "Donghua No Sekai"
    override val hasMainPage = true
    override var lang = "pt-br"
    override val hasDownloadSupport = true
    override val hasQuickSearch = true
    override val supportedTypes = setOf(TvType.Anime, TvType.AnimeMovie, TvType.OVA)

    companion object {
        private const val TAG = "DonghuaNoSekai"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        // Controle de rate limiting para APIs
        private val posterLock = Mutex()
        private var requestCounter = 0
    }

    override val mainPage = mainPageOf(
        "" to "🆕 Lançamentos",
        "genero/acao/" to "💥 Ação",
        "genero/aventura/" to "🏔️ Aventura",
        "genero/comedia/" to "😂 Comédia",
        "genero/drama/" to "🎭 Drama",
        "genero/fantasia/" to "🔮 Fantasia",
        "genero/cultivo/" to "☯️ Cultivo",
        "genero/xianxia/" to "⚔️ Xianxia",
        "genero/wuxia/" to "🥋 Wuxia",
        "genero/romance/" to "❤️ Romance",
        "genero/artes-marciais/" to "🗡️ Artes Marciais"
    )

    /**
     * Busca posters em alta qualidade via APIs de anime
     */
    private suspend fun getHighQualityPoster(title: String?): String? {
        if (title.isNullOrBlank()) return null
        
        // Limpa o título para busca
        val cleanTitle = title
            .replace(Regex("(?i)(Dublado|Legendado|Online|HD|Completo|Donghua|Anime)"), "")
            .replace(Regex("\\d+ª Temporada|\\d+ª|Season\\s*\\d+"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
        
        if (cleanTitle.isBlank()) return null
        
        return posterLock.withLock {
            kotlinx.coroutines.delay(100)
            
            // Alterna entre Kitsu e Jikan
            val turn = requestCounter % 10
            requestCounter++
            val useKitsu = turn < 5
            
            if (useKitsu) {
                searchKitsuPoster(cleanTitle)
            } else {
                searchJikanPoster(cleanTitle)
            }
        }
    }
    
    private suspend fun searchKitsuPoster(title: String): String? {
        return try {
            val encodedTitle = title.replace(" ", "%20")
            val url = "https://kitsu.io/api/edge/anime?filter[text]=$encodedTitle"
            
            val response = app.get(url, timeout = 8, headers = mapOf("User-Agent" to USER_AGENT))
            
            if (response.code == 200) {
                val regex = Regex("""posterImage[^}]*original":"(https:[^"]+)""")
                regex.find(response.text)?.groupValues?.get(1)?.replace("\\/", "/")
            } else null
        } catch (e: Exception) {
            null
        }
    }
    
    private suspend fun searchJikanPoster(title: String): String? {
        return try {
            val encodedTitle = title.replace(" ", "%20")
            val url = "https://api.jikan.moe/v4/anime?q=$encodedTitle&limit=1"
            
            val response = app.get(url, timeout = 8, headers = mapOf("User-Agent" to USER_AGENT))
            
            if (response.code == 200) {
                val regex = Regex("""large_image_url":"(https:[^"]+)""")
                regex.find(response.text)?.groupValues?.get(1)?.replace("\\/", "/")
            } else null
        } catch (e: Exception) {
            null
        }
    }

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val url = if (request.data.isEmpty()) {
                mainUrl
            } else {
                "$mainUrl/${request.data}"
            }
            
            val document = app.get(url).document
            val home = document.select("div.items article.item")
                .mapNotNull { it.toSearchResult() }

            Log.d(TAG, "✅ ${request.name}: ${home.size} items")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private suspend fun Element.toSearchResult(): AnimeSearchResponse? {
        return try {
            val title = selectFirst("h3")?.text()?.trim() ?: return null
            val href = fixUrl(selectFirst("a")?.attr("href") ?: return null)
            
            // Tenta pegar imagem do site primeiro
            val img = selectFirst("img")
            val sitePoster = fixUrlNull(
                img?.attr("src")
                    ?: img?.attr("data-src")
                    ?: img?.attr("data-lazy-src")
            )
            
            // Busca poster em alta qualidade via API
            val posterUrl = getHighQualityPoster(title) ?: sitePoster
            
            val isDubbed = title.contains("Dublado", ignoreCase = true)
            
            // Detecta tipo
            val tvType = when {
                title.contains("Filme", ignoreCase = true) -> TvType.AnimeMovie
                title.contains("OVA", ignoreCase = true) -> TvType.OVA
                else -> TvType.Anime
            }
            
            return newAnimeSearchResponse(title, href, tvType) {
                this.posterUrl = posterUrl
                this.dubStatus = if (isDubbed) {
                    EnumSet.of(DubStatus.Dubbed)
                } else {
                    EnumSet.of(DubStatus.Subbed)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro toSearchResult: ${e.message}")
            null
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) return emptyList()
        
        return try {
            Log.d(TAG, "🔍 Buscando: $query")
            val document = app.get("$mainUrl/?s=$query").document
            
            val results = document.select("div.items article.item")
                .mapNotNull { it.toSearchResult() }
            
            Log.d(TAG, "✅ Busca '$query': ${results.size} resultados")
            results
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro busca: ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            val document = app.get(url).document
            val title = document.selectFirst("h1")?.text()?.trim() ?: return null
            
            // Tenta pegar imagem do site primeiro
            val img = document.selectFirst("div.poster img, .sheader .poster img")
            val sitePoster = img?.attr("src")
                ?: img?.attr("data-src")
                ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            
            // Busca poster em alta qualidade via API
            val poster = getHighQualityPoster(title) ?: sitePoster
            
            val description = document.selectFirst("div.description, div.wp-content")?.text()?.trim()
            val genres = document.select("div.sgeneros a").map { it.text() }
            val year = document.selectFirst("span.date, span.year")?.text()
                ?.replace("\\D".toRegex(), "")?.take(4)?.toIntOrNull()
            
            val isDubbed = title.contains("Dublado", ignoreCase = true)
            val dubStatus = if (isDubbed) DubStatus.Dubbed else DubStatus.Subbed
            
            // Detecta tipo
            val isMovie = title.contains("Filme", ignoreCase = true) || 
                          url.contains("/filme/", ignoreCase = true)
            
            val tvType = when {
                isMovie -> TvType.AnimeMovie
                title.contains("OVA", ignoreCase = true) -> TvType.OVA
                else -> TvType.Anime
            }
            
            // Extrai episódios
            val episodes = document.select("ul.episodios li").mapNotNull { ep ->
                val epTitle = ep.selectFirst(".episodiotitle a")?.text() ?: return@mapNotNull null
                val epHref = fixUrl(ep.selectFirst("a")?.attr("href") ?: return@mapNotNull null)
                val epNum = epTitle.replace("\\D".toRegex(), "").toIntOrNull()
                
                newEpisode(epHref) {
                    this.name = epTitle
                    this.episode = epNum
                }
            }.reversed()
            
            Log.d(TAG, "✅ Carregado '$title' com ${episodes.size} episódios")

            if (isMovie) {
                newMovieLoadResponse(title, url, tvType, url) {
                    this.posterUrl = poster
                    this.plot = description
                    this.tags = genres
                    this.year = year
                }
            } else {
                newAnimeLoadResponse(title, url, tvType) {
                    this.posterUrl = poster
                    this.plot = description
                    this.tags = genres
                    this.year = year
                    addEpisodes(dubStatus, episodes)
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
        return DonghuaNoSekaiExtractor.extractVideoLinks(data, mainUrl, subtitleCallback, callback)
    }
}
