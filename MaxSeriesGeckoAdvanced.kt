package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    // Baseado na análise GeckoDriver: 0 episódios detectados
    // Players encontrados: 0 botões data-source
    // Interações testadas: 0 cliques simulados

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
            
            Log.d("MaxSeries", "📺 Analisando série (GeckoDriver): $title")
            
            // Método 1: Estrutura detectada pelo GeckoDriver
            
            // Nenhum episódio detectado pelo GeckoDriver - usando fallback
            episodes.add(newEpisode(url) {
                this.name = "Episódio 1"
                this.episode = 1
                this.season = 1
            })
            
            Log.d("MaxSeries", "✅ Total episódios: ${episodes.size}")

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
        Log.d("MaxSeries", "📺 Processando links (GeckoDriver): $data")
        
        var linksFound = 0
        val doc = app.get(data).document
        
        // Método baseado nas interações GeckoDriver
        
            // Nenhum player data-source detectado - usando método padrão
            doc.select("iframe").forEach { iframe ->
                val src = iframe.attr("src")
                if (src.isNotEmpty() && src.startsWith("http")) {
                    if (loadExtractor(src, data, subtitleCallback, callback)) {
                        linksFound++
                    }
                }
            }
        
        Log.d("MaxSeries", "✅ Links encontrados: $linksFound")
        return linksFound > 0
    }
}