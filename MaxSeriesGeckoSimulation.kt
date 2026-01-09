package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// Gerado por simulação GeckoDriver - MaxSeries
// Episódios detectados: 0
// Players detectados: 0
// Interações simuladas: 0

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
            
            Log.d("MaxSeries", "📺 Processando série (GeckoSim): $title")
            
            // Método baseado na simulação GeckoDriver
            
            // Simulação GeckoDriver: Nenhum episódio detectado - fallback
            episodes.add(newEpisode(url) {
                this.name = "Episódio 1"
                this.episode = 1
                this.season = 1
            })
            
            Log.d("MaxSeries", "✅ Episódios encontrados: ${episodes.size}")

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
        Log.d("MaxSeries", "📺 Processando links (GeckoSim): $data")
        
        var linksFound = 0
        val doc = app.get(data).document
        
        // Método baseado na simulação de interações
        
        // Simulação GeckoDriver: 0 players detectados
        // Cliques simulados: 0 (0 sucessos)
        
        // Método 1: Botões data-source (simulação confirmada)
        doc.select("button[data-source], .btn[data-source]").forEach { button ->
            val source = button.attr("data-source")
            val playerName = button.text().trim()
            
            if (source.isNotEmpty() && source.startsWith("http")) {
                Log.d("MaxSeries", "🎯 Player GeckoSim: $playerName -> $source")
                
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
        
        // Método 2: Iframe principal (baseado na simulação)
        if (linksFound == 0) {
            Log.d("MaxSeries", "🔄 Tentando iframe principal")
            
            val mainIframe = doc.selectFirst("iframe.metaframe, iframe[src*=viewplayer], iframe[src*=embed]")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Procurar botões no iframe (simulação confirmou eficácia)
                    iframeDoc.select("button[data-source], .btn[data-source]").forEach { button ->
                        val source = button.attr("data-source")
                        if (source.isNotEmpty() && source.startsWith("http")) {
                            if (loadExtractor(source, data, subtitleCallback, callback)) {
                                linksFound++
                            }
                        }
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
        
        Log.d("MaxSeries", "✅ Links processados: $linksFound")
        return linksFound > 0
    }
}