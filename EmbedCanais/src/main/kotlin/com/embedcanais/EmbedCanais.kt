package com.embedcanais

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import org.jsoup.nodes.Element
import android.util.Log

/**
 * EmbedCanais - Provider de TV Ao Vivo
 * 
 * Suporte a:
 * - Canais abertos brasileiros
 * - Canais de esportes
 * - Canais de notícias
 * - Canais de entretenimento
 * - Canais infantis
 */
class EmbedCanais : MainAPI() {
    override var mainUrl = "https://embedcanais.com"
    override var name = "EmbedCanais TV"
    override val hasMainPage = true
    override var lang = "pt-br"
    override val hasDownloadSupport = false // TV Ao Vivo não tem download
    override val hasQuickSearch = true
    override val supportedTypes = setOf(TvType.Movie) // Usamos Movie para TV Ao Vivo

    companion object {
        private const val TAG = "EmbedCanais"
    }

    override val mainPage = mainPageOf(
        "/categoria/canais-abertos" to "📺 Canais Abertos",
        "/categoria/esportes" to "⚽ Esportes",
        "/categoria/noticias" to "📰 Notícias",
        "/categoria/entretenimento" to "🎬 Entretenimento",
        "/categoria/infantil" to "🧒 Infantil",
        "/categoria/documentarios" to "📚 Documentários",
        "/categoria/variedades" to "🎪 Variedades"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        return try {
            val url = "$mainUrl${request.data}"
            val document = app.get(url).document
            
            val home = document.select("div.channel-item, .canal-item, .channel, article.item").mapNotNull { 
                it.toSearchResult() 
            }
            
            Log.d(TAG, "✅ ${request.name}: ${home.size} canais")
            newHomePageResponse(request.name, home)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ${request.name}: ${e.message}")
            newHomePageResponse(request.name, emptyList())
        }
    }

    private fun Element.toSearchResult(): MovieSearchResponse? {
        return try {
            val title = selectFirst(".channel-name, .canal-nome, h3, .title, h2")?.text()?.trim() 
                ?: return null
            val href = selectFirst("a")?.attr("href")?.let { fixUrl(it) } ?: return null
            val posterUrl = selectFirst("img")?.attr("src")?.let { fixUrl(it) }
            
            newMovieSearchResponse(title, href, TvType.Movie) {
                this.posterUrl = posterUrl
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro toSearchResult: ${e.message}")
            null
        }
    }

    override suspend fun search(query: String): List<SearchResponse> {
        if (query.isBlank()) return emptyList()
        
        return try {
            Log.d(TAG, "🔍 Buscando canal: $query")
            val document = app.get("$mainUrl/?s=$query").document
            
            val results = document.select("div.channel-item, .canal-item, .channel, article.item").mapNotNull { 
                it.toSearchResult() 
            }
            
            Log.d(TAG, "✅ Busca '$query': ${results.size} canais")
            results
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro busca: ${e.message}")
            emptyList()
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        return try {
            val document = app.get(url).document
            
            val title = document.selectFirst("h1.channel-title, .canal-titulo, h1")?.text()?.trim() 
                ?: "Canal Ao Vivo"
            val poster = document.selectFirst("div.channel-logo img, .canal-logo img, div.poster img")?.attr("src")
                ?.let { fixUrl(it) }
            val plot = document.selectFirst("div.channel-description, .canal-descricao")?.text()?.trim()
                ?: "Transmissão ao vivo de $title"
            
            // Para TV Ao Vivo, usamos MovieLoadResponse
            newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster
                this.plot = plot
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
        return try {
            Log.d(TAG, "📺 Carregando stream de: $data")
            val document = app.get(data).document
            var linksFound = 0
            
            // Procura por iframes do player
            document.select("iframe[src]").forEach { iframe ->
                val src = iframe.attr("src").ifBlank { iframe.attr("data-src") }
                if (src.isNotBlank()) {
                    try {
                        loadExtractor(src, data, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Stream iframe: $src")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro iframe: ${e.message}")
                    }
                }
            }
            
            // Procura por links diretos de stream (m3u8, mp4)
            document.select("video source, video").forEach { video ->
                val src = video.attr("src").ifBlank { video.attr("data-src") }
                if (src.isNotBlank()) {
                    try {
                        callback(
                            newExtractorLink(
                                source = "EmbedCanais",
                                name = "EmbedCanais Live",
                                url = src,
                                type = ExtractorLinkType.VIDEO
                            ) {
                                referer = data
                            }
                        )
                        linksFound++
                        Log.d(TAG, "✅ Stream direto: $src")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro stream: ${e.message}")
                    }
                }
            }
            
            // Procura por scripts com URLs de stream
            document.select("script").forEach { script ->
                val scriptText = script.html()
                
                // Procura por URLs m3u8
                val m3u8Pattern = Regex("""(https?://[^"'\\s]+\\.m3u8[^"'\\s]*)""")
                m3u8Pattern.findAll(scriptText).forEach { match ->
                    val streamUrl = match.groupValues[1]
                    try {
                        callback(
                            newExtractorLink(
                                source = "EmbedCanais",
                                name = "EmbedCanais HLS",
                                url = streamUrl,
                                type = ExtractorLinkType.M3U8
                            ) {
                                referer = data
                            }
                        )
                        linksFound++
                        Log.d(TAG, "✅ Stream m3u8: $streamUrl")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro m3u8: ${e.message}")
                    }
                }
            }
            
            Log.d(TAG, "📊 Total de streams: $linksFound")
            linksFound > 0
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro loadLinks: ${e.message}")
            false
        }
    }
}
