package com.animesonlinecc

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.AppUtils.tryParseJson
import android.util.Log
import java.util.EnumSet

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

    // REVERTIDO PARA HOME SIMPLES (VERTICAL) PARA CORRIGIR BUG DE CARREGAMENTO
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
        return try {
            val document = app.get(request.data + page).document
            val home = document.select("div.items article.item").mapNotNull {
                it.toSearchResult()
            }
            if (home.isEmpty()) {
                Log.d("AnimesOnlineCC", "⚠️ Nenhum resultado encontrado na página ${request.name} (página $page)")
            }
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e("AnimesOnlineCC", "❌ Erro ao carregar página principal ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

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
        if (query.isBlank()) {
            Log.d("AnimesOnlineCC", "⚠️ Pesquisa vazia, retornando lista vazia")
            return emptyList()
        }
        
        return try {
            Log.d("AnimesOnlineCC", "🔍 Pesquisando por: $query")
            val document = app.get("$mainUrl/?s=$query").document
            
            // FIX: Página de pesquisa usa div.items2, não div.items
            val results = document.select("div.items2 article.item").mapNotNull {
                it.toSearchResult()
            }
            
            Log.d("AnimesOnlineCC", "✅ Encontrados ${results.size} resultados para '$query'")
            results
        } catch (e: Exception) {
            Log.e("AnimesOnlineCC", "❌ Erro na pesquisa '$query': ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse {
        return try {
            Log.d("AnimesOnlineCC", "📖 Carregando detalhes: $url")
            val document = app.get(url).document
            
            val title = document.selectFirst("h1")?.text()?.trim()
            if (title.isNullOrBlank()) {
                Log.e("AnimesOnlineCC", "❌ Título não encontrado em: $url")
                throw ErrorLoadingException("Não foi possível encontrar o título do anime")
            }
            
            // BLINDAGEM NO LOAD: Tenta pegar de várias tags
            val img = document.selectFirst("div.poster img, .sheader .poster img")
            val poster = img?.attr("src")
                ?: img?.attr("data-src")
                ?: img?.attr("data-lazy-src")
                ?: img?.attr("data-original")
                ?: document.selectFirst("meta[property=og:image]")?.attr("content")
            
            if (poster == null) {
                Log.d("AnimesOnlineCC", "⚠️ Poster não encontrado para: $title")
            }
            
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
            
            Log.d("AnimesOnlineCC", "✅ Carregado '$title' com ${episodes.size} episódios")

            newAnimeLoadResponse(title, url, TvType.Anime) {
                this.posterUrl = poster
                this.plot = description
                this.tags = genres
                this.year = year
                addEpisodes(dubStatus, episodes)
            }
        } catch (e: ErrorLoadingException) {
            throw e
        } catch (e: Exception) {
            Log.e("AnimesOnlineCC", "❌ Erro ao carregar detalhes de $url: ${e.message}")
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
            Log.d("AnimesOnlineCC", "🎬 Carregando links de: $data")
            val document = app.get(data).document
            var linksFound = 0
            
            // Procura por iframes de vídeo
            document.select("iframe").forEach { iframe ->
                val iframeUrl = iframe.attr("src").ifBlank { iframe.attr("data-src") }
                if (iframeUrl.isNotBlank()) {
                    try {
                        loadExtractor(iframeUrl, data, subtitleCallback, callback)
                        linksFound++
                        Log.d("AnimesOnlineCC", "✅ Iframe encontrado: $iframeUrl")
                    } catch (e: Exception) {
                        Log.e("AnimesOnlineCC", "⚠️ Erro ao extrair iframe $iframeUrl: ${e.message}")
                    }
                }
            }
            
            // Procura por links diretos de vídeo
            document.select("div.player a, div.playeroptions a, ul.options a").forEach { option ->
                val videoUrl = option.attr("href")
                if (videoUrl.isNotBlank() && videoUrl.startsWith("http")) {
                    try {
                        loadExtractor(videoUrl, data, subtitleCallback, callback)
                        linksFound++
                        Log.d("AnimesOnlineCC", "✅ Link direto encontrado: $videoUrl")
                    } catch (e: Exception) {
                        Log.e("AnimesOnlineCC", "⚠️ Erro ao extrair link $videoUrl: ${e.message}")
                    }
                }
            }
            
            if (linksFound == 0) {
                Log.e("AnimesOnlineCC", "❌ Nenhum link de vídeo encontrado em: $data")
            } else {
                Log.d("AnimesOnlineCC", "✅ Total de $linksFound links encontrados")
            }
            
            linksFound > 0
        } catch (e: Exception) {
            Log.e("AnimesOnlineCC", "❌ Erro crítico ao carregar links de $data: ${e.message}")
            false
        }
    }
}
