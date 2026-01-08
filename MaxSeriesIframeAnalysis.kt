package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// Gerado por análise de iframes GeckoDriver
// Iframes analisados: 1
// Total episódios detectados: 5
// Total players detectados: 10
// Melhor seletor episódios: li[data-season-id][data-episode-id] a
// Melhor seletor players: button[data-source]

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
            
            Log.d("MaxSeries", "📺 Processando série (Análise Iframe): $title")
            
            // Método baseado na análise de iframes
            val mainIframe = doc.selectFirst("iframe")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {
                try {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "🖼️ Carregando iframe: $iframeSrc")
                    
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Extrair temporadas da navegação
                    val seasons = mutableMapOf<String, Int>()
                    iframeDoc.select("ul.header-navigation li[data-season-id]").forEach { seasonLi ->
                        val seasonId = seasonLi.attr("data-season-id")
                        val seasonNumber = seasonLi.attr("data-season-number").toIntOrNull() ?: 1
                        if (seasonId.isNotEmpty()) {
                            seasons[seasonId] = seasonNumber
                            Log.d("MaxSeries", "🎬 Temporada: $seasonNumber (ID: $seasonId)")
                        }
                    }
                    
                    // Extrair episódios com dados reais de temporada/episódio
                    iframeDoc.select("li[data-season-id][data-episode-id] a").forEach { epLi ->
                        val seasonId = epLi.attr("data-season-id")
                        val episodeId = epLi.attr("data-episode-id")
                        val epLink = epLi.selectFirst("a") ?: epLi
                        
                        if (seasonId.isNotEmpty() && episodeId.isNotEmpty()) {
                            val epTitle = epLink.text().trim()
                            val epHref = epLink.attr("href") // Formato: #12956_255628
                            
                            // Extrair número do episódio do título (formato: "1 - Título do Episódio")
                            val epNum = epTitle.split(" - ").firstOrNull()?.trim()?.toIntOrNull() ?: 1
                            val seasonNum = seasons[seasonId] ?: 1
                            
                            // Criar URL do episódio que inclui o iframe URL e referência do episódio
                            val episodeUrl = "$iframeSrc$epHref"
                            
                            episodes.add(newEpisode(episodeUrl) {
                                this.name = epTitle
                                this.episode = epNum
                                this.season = seasonNum
                            })
                            
                            Log.d("MaxSeries", "✅ Episódio: T${seasonNum}E${epNum} - $epTitle")
                        }
                    }
                    
                } catch (e: Exception) {
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
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
            
            Log.d("MaxSeries", "✅ Total: ${episodes.size} episódios em ${episodes.map { it.season }.distinct().size} temporadas")

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
        Log.d("MaxSeries", "📺 Processando links (Análise Iframe): $data")
        
        var linksFound = 0
        
        try {
            // Verificar se é uma URL de episódio do iframe (contém #)
            if (data.contains("#")) {
                Log.d("MaxSeries", "🎯 Processando episódio do iframe")
                
                // Carregar a página do iframe com o fragmento do episódio
                val doc = app.get(data).document
                
                // Procurar botões de seleção de player (como "Player #1", "Player #2")
                val playerButtons = doc.select("button[data-source]")
                
                if (playerButtons.isNotEmpty()) {
                    Log.d("MaxSeries", "🎮 Encontrados ${playerButtons.size} players")
                    
                    playerButtons.forEach { button ->
                        val playerName = button.text().trim()
                        Log.d("MaxSeries", "🔄 Testando player: $playerName")
                        
                        try {
                            // Procurar atributos de dados que podem conter informações do vídeo
                            val dataSource = button.attr("data-source")
                            val dataUrl = button.attr("data-url")
                            val dataPlayer = button.attr("data-player")
                            
                            val videoUrl = dataSource.ifEmpty { dataUrl.ifEmpty { dataPlayer } }
                            
                            if (videoUrl.isNotEmpty() && videoUrl.startsWith("http")) {
                                Log.d("MaxSeries", "🎯 URL encontrada no botão: $videoUrl")
                                
                                if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {
                                    linksFound++
                                }
                            }
                            
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${e.message}")
                        }
                    }
                }
                
                // Procurar gleam.config nos scripts (como mostrado no HTML)
                doc.select("script").forEach { script ->
                    val scriptContent = script.html()
                    
                    if (scriptContent.contains("gleam.config", ignoreCase = true)) {
                        Log.d("MaxSeries", "🎬 Script gleam.config encontrado")
                        
                        // Extrair URL do gleam.config
                        val gleamUrlRegex = Regex(""""url"\s*:\s*"([^"]+)""")
                        val gleamMatch = gleamUrlRegex.find(scriptContent)
                        
                        if (gleamMatch != null) {
                            val gleamUrl = gleamMatch.groupValues[1].replace("\\/", "/")
                            Log.d("MaxSeries", "🎯 Gleam URL: $gleamUrl")
                            
                            if (gleamUrl.startsWith("http")) {
                                try {
                                    if (loadExtractor(gleamUrl, data, subtitleCallback, callback)) {
                                        linksFound++
                                    }
                                } catch (e: Exception) {
                                    Log.e("MaxSeries", "❌ Erro ao processar gleam URL: ${e.message}")
                                }
                            }
                        }
                    }
                }
                
            } else {
                // Processamento padrão para URLs que não são de iframe
                Log.d("MaxSeries", "🔄 Processamento padrão")
                val doc = app.get(data).document
                
                val mainIframe = doc.selectFirst("iframe")?.attr("src")
                if (!mainIframe.isNullOrEmpty()) {
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "📺 Carregando iframe principal: $iframeSrc")
                    
                    try {
                        if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {
                            linksFound++
                        }
                    } catch (e: Exception) {
                        Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${e.message}")
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro geral no loadLinks: ${e.message}")
        }
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }
}