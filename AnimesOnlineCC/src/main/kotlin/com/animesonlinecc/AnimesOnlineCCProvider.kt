package com.animesonlinecc

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import java.util.EnumSet
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Animes Online CC - Versão 2.0
 * 
 * Melhorias:
 * - Posters em alta qualidade via Kitsu.io e Jikan (MyAnimeList) APIs
 * - Fallback inteligente quando não encontra na API
 * - Rate limiting para não sobrecarregar as APIs
 * - Detecção automática de Dublado/Legendado/OVA/Filme
 */
class AnimesOnlineCCProvider : MainAPI() {
    override var mainUrl = "https://animesonlinecc.to"
    override var name = "Animes Online CC v2"
    override val hasMainPage = true
    override var lang = "pt-BR"
    override val hasDownloadSupport = true
    override val hasQuickSearch = true
    
    override val supportedTypes = setOf(
        TvType.Anime,
        TvType.OVA,
        TvType.AnimeMovie
    )

    companion object {
        private const val TAG = "AnimesOnlineCC"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        // Controle de rate limiting para APIs
        private val posterLock = Mutex()
        private var requestCounter = 0
    }

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
        "$mainUrl/genero/suspense/page/" to "Suspense",
        "$mainUrl/genero/terror/page/" to "Terror",
        "$mainUrl/genero/misterio/page/" to "Mistério"
    )

    /**
     * Busca posters em alta qualidade via Kitsu.io ou Jikan API
     * Alterna entre as APIs para distribuir a carga
     */
    private suspend fun getHighQualityPoster(title: String?): String? {
        if (title.isNullOrBlank()) return null
        
        // Limpa o título para busca
        val cleanTitle = title
            .replace(Regex("(?i)(Dublado|Legendado|Online|HD|TV|Todos os Episódios|Filme|Completo)"), "")
            .replace(Regex("\\d+ª Temporada|\\d+ª|Season\\s*\\d+"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
        
        if (cleanTitle.isBlank()) return null
        
        return posterLock.withLock {
            // Delay para não sobrecarregar as APIs
            kotlinx.coroutines.delay(100)
            
            // Alterna entre Kitsu (60%) e Jikan (40%)
            val turn = requestCounter % 10
            requestCounter++
            val useKitsu = turn < 6
            
            val posterUrl = if (useKitsu) {
                searchKitsuPoster(cleanTitle)
            } else {
                searchJikanPoster(cleanTitle)
            }
            
            posterUrl
        }
    }
    
    /**
     * Busca poster na API do Kitsu.io
     */
    private suspend fun searchKitsuPoster(title: String): String? {
        return try {
            val encodedTitle = title.replace(" ", "%20")
            val url = "https://kitsu.io/api/edge/anime?filter[text]=$encodedTitle"
            
            val response = app.get(url, timeout = 8, headers = mapOf("User-Agent" to USER_AGENT))
            
            if (response.code == 200) {
                // Extrai a URL da imagem original
                val regex = Regex("""posterImage[^}]*original":"(https:[^"]+)""")
                regex.find(response.text)?.groupValues?.get(1)?.replace("\\/", "/")
            } else null
        } catch (e: Exception) {
            Log.d(TAG, "Kitsu API falhou: ${e.message}")
            null
        }
    }
    
    /**
     * Busca poster na API do Jikan (MyAnimeList)
     */
    private suspend fun searchJikanPoster(title: String): String? {
        return try {
            val encodedTitle = title.replace(" ", "%20")
            val url = "https://api.jikan.moe/v4/anime?q=$encodedTitle&limit=1"
            
            val response = app.get(url, timeout = 8, headers = mapOf("User-Agent" to USER_AGENT))
            
            if (response.code == 200) {
                // Extrai a URL da imagem grande
                val regex = Regex("""large_image_url":"(https:[^"]+)""")
                regex.find(response.text)?.groupValues?.get(1)?.replace("\\/", "/")
            } else null
        } catch (e: Exception) {
            Log.d(TAG, "Jikan API falhou: ${e.message}")
            null
        }
    }

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val document = app.get(request.data + page).document
            val home = document.select("div.items article.item").mapNotNull {
                it.toSearchResult()
            }
            if (home.isEmpty()) {
                Log.d(TAG, "⚠️ Nenhum resultado encontrado na página ${request.name} (página $page)")
            }
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao carregar página principal ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private suspend fun org.jsoup.nodes.Element.toSearchResult(): AnimeSearchResponse? {
        val title = this.selectFirst("h3")?.text()?.trim() ?: return null
        val href = fixUrl(this.selectFirst("a")?.attr("href") ?: return null)
        
        // Tenta pegar imagem do site primeiro
        val img = this.selectFirst("img")
        val sitePoster = fixUrlNull(
            img?.attr("src")
                ?: img?.attr("data-src")
                ?: img?.attr("data-lazy-src")
                ?: img?.attr("data-original")
        )
        
        // Busca poster em alta qualidade via API (fallback para imagem do site)
        val posterUrl = getHighQualityPoster(title) ?: sitePoster
        
        val isDubbed = title.contains("Dublado", ignoreCase = true)
        val isMovie = title.contains("Filme", ignoreCase = true) || 
                      href.contains("/filme/", ignoreCase = true)
        
        val tvType = when {
            isMovie -> TvType.AnimeMovie
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
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) {
            Log.d(TAG, "⚠️ Pesquisa vazia")
            return emptyList()
        }
        
        return try {
            Log.d(TAG, "🔍 Pesquisando por: $query")
            val document = app.get("$mainUrl/?s=$query").document
            
            val results = document.select("div.items2 article.item").mapNotNull {
                it.toSearchResult()
            }
            
            Log.d(TAG, "✅ Encontrados ${results.size} resultados para '$query'")
            results
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na pesquisa '$query': ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse {
        return try {
            Log.d(TAG, "📖 Carregando detalhes: $url")
            val document = app.get(url).document
            
            val title = document.selectFirst("h1")?.text()?.trim()
            if (title.isNullOrBlank()) {
                Log.e(TAG, "❌ Título não encontrado em: $url")
                throw ErrorLoadingException("Não foi possível encontrar o título do anime")
            }
            
            // Tenta pegar imagem do site primeiro
            val img = document.selectFirst("div.poster img, .sheader .poster img")
            val sitePoster = img?.attr("src")
                ?: img?.attr("data-src")
                ?: img?.attr("data-lazy-src")
                ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            
            // Busca poster em alta qualidade via API
            val poster = getHighQualityPoster(title) ?: sitePoster
            
            val description = document.selectFirst("div.description, div.wp-content")?.text()?.trim()
            val genres = document.select("div.sgeneros a").map { it.text() }
            val year = document.selectFirst("span.date, span.year, .extra span")?.text()
                ?.replace("\\D".toRegex(), "")?.take(4)?.toIntOrNull()
            
            val isDubbed = title.contains("Dublado", ignoreCase = true)
            val dubStatus = if (isDubbed) DubStatus.Dubbed else DubStatus.Subbed
            
            val isMovie = title.contains("Filme", ignoreCase = true) || 
                          url.contains("/filme/", ignoreCase = true)
            
            val tvType = when {
                isMovie -> TvType.AnimeMovie
                title.contains("OVA", ignoreCase = true) -> TvType.OVA
                else -> TvType.Anime
            }
            
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

            newAnimeLoadResponse(title, url, tvType) {
                this.posterUrl = poster
                this.plot = description
                this.tags = genres
                this.year = year
                addEpisodes(dubStatus, episodes)
            }
        } catch (e: ErrorLoadingException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao carregar detalhes de $url: ${e.message}")
            throw ErrorLoadingException("Erro ao carregar informações do anime")
        }
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🎬 Carregando links de: $data")
            val document = app.get(data).document
            var linksFound = 0
            
            // Procura por iframes de vídeo
            document.select("iframe").forEach { iframe: org.jsoup.nodes.Element ->
                val iframeUrl = iframe.attr("src").ifBlank { iframe.attr("data-src") }
                if (iframeUrl.isNotBlank()) {
                    try {
                        loadExtractor(iframeUrl, data, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Iframe encontrado: $iframeUrl")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro ao extrair iframe $iframeUrl: ${e.message}")
                    }
                }
            }
            
            // Procura por links diretos de vídeo
            document.select("div.player a, div.playeroptions a, ul.options a").forEach { option: org.jsoup.nodes.Element ->
                val videoUrl = option.attr("href")
                if (videoUrl.isNotBlank() && videoUrl.startsWith("http")) {
                    try {
                        loadExtractor(videoUrl, data, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Link direto encontrado: $videoUrl")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro ao extrair link $videoUrl: ${e.message}")
                    }
                }
            }
            
            if (linksFound == 0) {
                Log.e(TAG, "❌ Nenhum link de vídeo encontrado em: $data")
            } else {
                Log.d(TAG, "✅ Total de $linksFound links encontrados")
            }
            
            linksFound > 0
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico ao carregar links de $data: ${e.message}")
            false
        }
    }
}
