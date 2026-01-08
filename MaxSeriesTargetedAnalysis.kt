package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// Gerado por análise direcionada GeckoDriver
// Séries analisadas: 2
// Total episódios detectados: 0
// Total players detectados: 0
// Melhor seletor: ul.episodios li a

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
            
            Log.d("MaxSeries", "📺 Processando série (Análise Direcionada): $title")
            
            // Método baseado na análise direcionada
            doc.select("ul.episodios li a").forEachIndexed { index, element ->
                val epTitle = element.text().trim()
                val epHref = element.attr("href")
                
                if (epHref.isNotEmpty()) {
                    // Extrair número do episódio
                    val epNum = extractEpisodeNumberAdvanced(element, index + 1)
                    val seasonNum = extractSeasonNumberAdvanced(element, 1)
                    
                    episodes.add(newEpisode(epHref) {
                        this.name = if (epTitle.isNotEmpty()) epTitle else "Episódio $epNum"
                        this.episode = epNum
                        this.season = seasonNum
                    })
                    
                    Log.d("MaxSeries", "✅ Episódio: T${seasonNum}E${epNum} - $epTitle")
                }
            }
            
            // Fallback se nenhum episódio for encontrado
            if (episodes.isEmpty()) {
                Log.d("MaxSeries", "⚠️ Fallback: criando episódio único")
                episodes.add(newEpisode(url) {
                    this.name = "Episódio 1"
                    this.episode = 1
                    this.season = 1
                })
            }
            
            Log.d("MaxSeries", "✅ Total: ${episodes.size} episódios")

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

    private fun extractEpisodeNumberAdvanced(element: Element, fallback: Int): Int {
        // Método 1: .numerando
        try {
            val numerando = element.parent()?.selectFirst(".numerando")?.text()
            if (numerando != null) {
                val match = Regex("""(\d+)\s*-\s*(\d+)|E(\d+)""").find(numerando)
                if (match != null) {
                    return (match.groupValues[2].ifEmpty { match.groupValues[3] }).toInt()
                }
            }
        } catch (e: Exception) { }
        
        // Método 2: Texto do elemento
        try {
            val text = element.text()
            val match = Regex("""episódio\s*(\d+)|episode\s*(\d+)|ep\s*(\d+)""", RegexOption.IGNORE_CASE).find(text)
            if (match != null) {
                return (match.groupValues[1].ifEmpty { match.groupValues[2].ifEmpty { match.groupValues[3] } }).toInt()
            }
        } catch (e: Exception) { }
        
        // Método 3: URL
        try {
            val href = element.attr("href")
            val match = Regex("""episodio-(\d+)|episode-(\d+)""").find(href)
            if (match != null) {
                return (match.groupValues[1].ifEmpty { match.groupValues[2] }).toInt()
            }
        } catch (e: Exception) { }
        
        return fallback
    }

    private fun extractSeasonNumberAdvanced(element: Element, fallback: Int): Int {
        try {
            val seasonParent = element.parents().find { it.hasClass("se-c") }
            if (seasonParent != null) {
                val seasonId = seasonParent.id()
                if (seasonId.startsWith("season-")) {
                    return seasonId.replace("season-", "").toInt()
                }
            }
        } catch (e: Exception) { }
        
        return fallback
    }

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d("MaxSeries", "📺 Processando links (Análise Direcionada): $data")
        
        var linksFound = 0
        val doc = app.get(data).document
        
        // Método 1: Botões data-source (confirmado pela análise)
        doc.select("button[data-source], .btn[data-source]").forEach { button ->
            val source = button.attr("data-source")
            val playerName = button.text().trim()
            
            if (source.isNotEmpty() && source.startsWith("http")) {
                Log.d("MaxSeries", "🎯 Player detectado: $playerName -> $source")
                
                try {
                    if (loadExtractor(source, data, subtitleCallback, callback)) {
                        linksFound++
                        Log.d("MaxSeries", "✅ Sucesso: $playerName")
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro player $playerName: ${e.message}")
                }
            }
        }
        
        // Método 2: Iframe principal
        if (linksFound == 0) {
            Log.d("MaxSeries", "🔄 Tentando iframe principal")
            
            val mainIframe = doc.selectFirst("iframe.metaframe, iframe[src*=viewplayer], iframe[src*=embed]")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                
                try {
                    if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {
                        linksFound++
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro iframe: ${e.message}")
                }
            }
        }
        
        // Método 3: AJAX DooPlay (fallback)
        if (linksFound == 0) {
            Log.d("MaxSeries", "🔄 Tentando AJAX DooPlay")
            
            doc.select("#playeroptionsul li, .playeroptionsul li").forEach { option ->
                val playerId = option.attr("data-post")
                val playerNum = option.attr("data-nume")
                val playerType = option.attr("data-type").ifEmpty { "movie" }
                
                if (playerId.isNotEmpty() && playerNum.isNotEmpty()) {
                    try {
                        val ajaxUrl = "$mainUrl/wp-admin/admin-ajax.php"
                        val ajaxData = mapOf(
                            "action" to "doo_player_ajax",
                            "post" to playerId,
                            "nume" to playerNum,
                            "type" to playerType
                        )
                        
                        val ajaxResponse = app.post(ajaxUrl, data = ajaxData).text
                        val iframeRegex = Regex("""src=["']([^"']+)["']""")
                        val iframeMatch = iframeRegex.find(ajaxResponse)
                        
                        if (iframeMatch != null) {
                            val iframeUrl = iframeMatch.groupValues[1]
                            val cleanUrl = if (iframeUrl.startsWith("//")) "https:$iframeUrl" else iframeUrl
                            
                            if (loadExtractor(cleanUrl, data, subtitleCallback, callback)) {
                                linksFound++
                            }
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro AJAX: ${e.message}")
                    }
                }
            }
        }
        
        Log.d("MaxSeries", "✅ Total links encontrados: $linksFound")
        return linksFound > 0
    }
}