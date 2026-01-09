package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override val mainPage = mainPageOf(
        "$mainUrl/" to "Home",
        "$mainUrl/series/" to "Series",
        "$mainUrl/filmes/" to "Filmes"
    )

    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        val url = if (page > 1) {
            if (request.data.endsWith("/")) "${request.data}page/$page/" else "${request.data}/page/$page/"
        } else { request.data }
        val doc = app.get(url).document
        val home = doc.select("article.item").mapNotNull {
            val title = it.selectFirst(".data h3 a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".data h3 a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".poster img")?.attr("src")
            if (href.contains("/series/")) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) { this.posterUrl = image }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) { this.posterUrl = image }
            }
        }
        return newHomePageResponse(request.name, home)
    }

    override suspend fun search(query: String): List<SearchResponse> {
        val doc = app.get("$mainUrl/?s=$query").document
        return doc.select(".result-item").mapNotNull {
            val title = it.selectFirst(".details .title a")?.text() ?: return@mapNotNull null
            val href = it.selectFirst(".details .title a")?.attr("href") ?: return@mapNotNull null
            val image = it.selectFirst(".image img")?.attr("src")
            if (href.contains("/series/")) {
                newTvSeriesSearchResponse(title, href, TvType.TvSeries) { this.posterUrl = image }
            } else {
                newMovieSearchResponse(title, href, TvType.Movie) { this.posterUrl = image }
            }
        }
    }

    override suspend fun load(url: String): LoadResponse? {
        val doc = app.get(url).document
        val title = doc.selectFirst(".data h1")?.text() ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        val bg = doc.selectFirst(".backdrop img")?.attr("src")
        
        if (url.contains("/series/")) {
            val episodes = mutableListOf<Episode>()
            val iframe = doc.selectFirst("iframe")?.attr("src")
            if (!iframe.isNullOrEmpty()) {
                val iframeSrc = if (iframe.startsWith("//")) "https:$iframe" else iframe
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    iframeDoc.select("li[data-episode-id] a").forEachIndexed { i, ep ->
                        val href = ep.attr("href")
                        if (href.isNotEmpty()) {
                            val epUrl = if (href.startsWith("#")) "$iframeSrc$href" else href
                            episodes.add(newEpisode(epUrl) { name = "Ep ${i+1}"; episode = i+1; season = 1 })
                        }
                    }
                } catch (_: Exception) {}
            }
            if (episodes.isEmpty()) episodes.add(newEpisode(url) { name = "Ep 1"; episode = 1; season = 1 })
            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {
                this.posterUrl = poster; this.plot = desc; this.backgroundPosterUrl = bg
            }
        } else {
            return newMovieLoadResponse(title, url, TvType.Movie, url) {
                this.posterUrl = poster; this.plot = desc; this.backgroundPosterUrl = bg
            }
        }
    }

    // ==================== EXTRACTORS ====================

    // Extractor para DoodStream clones (myvidplay, bysebuho, g9r6)
    private suspend fun extractDoodStream(url: String, referer: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "🔍 Extraindo DoodStream clone: $url")
            
            val response = app.get(url, referer = referer)
            val html = response.text
            
            // Extrair pass_md5 path
            val passMd5Regex = Regex("""\$\.get\(['"](/pass_md5/[^'"]+)['"]""")
            val passMd5Match = passMd5Regex.find(html)
            
            val passMd5Path = if (passMd5Match != null) {
                passMd5Match.groupValues[1]
            } else {
                val altRegex = Regex("""pass_md5/([^'"]+)""")
                val altMatch = altRegex.find(html) ?: return false
                "/pass_md5/${altMatch.groupValues[1]}"
            }
            
            // Extrair token
            val tokenRegex = Regex("""token=([a-zA-Z0-9]+)""")
            val tokenMatch = tokenRegex.find(html)
            val token = tokenMatch?.groupValues?.get(1) ?: generateRandomToken()
            
            // Determinar base URL
            val baseUrl = url.substringBefore("/e/").substringBefore("/d/")
            
            // Fazer request para pass_md5
            val passUrl = "$baseUrl$passMd5Path"
            val passResponse = app.get(passUrl, referer = url)
            if (!passResponse.isSuccessful) return false
            
            val videoBase = passResponse.text.trim()
            
            // Construir URL final do vídeo
            val randomToken = generateRandomToken()
            val expiry = System.currentTimeMillis()
            val videoUrl = "$videoBase$randomToken?token=$token&expiry=$expiry"
            
            Log.d("MaxSeries", "🎬 DoodStream URL: $videoUrl")
            
            val sourceName = when {
                url.contains("myvidplay") -> "MyVidPlay"
                url.contains("bysebuho") -> "Bysebuho"
                url.contains("g9r6") -> "G9R6"
                url.contains("dood") -> "DoodStream"
                else -> "DoodStream"
            }
            
            callback(
                ExtractorLink(
                    source = sourceName,
                    name = sourceName,
                    url = videoUrl,
                    referer = url,
                    quality = Qualities.Unknown.value,
                    isM3u8 = false
                )
            )
            
            return true
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro DoodStream: ${e.message}")
            return false
        }
    }
    
    // WebView Extractor para hosts difíceis (megaembed, playerembedapi)
    private suspend fun extractWithWebView(url: String, referer: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "🌐 WebView Extractor: $url")
            
            // Usar o WebViewResolver do CloudStream para interceptar requests
            val interceptedUrls = mutableListOf<String>()
            
            // Padrões de URL de vídeo para interceptar
            val videoPatterns = listOf(
                Regex("""https?://[^\s"'<>]+\.m3u8[^\s"'<>]*"""),
                Regex("""https?://[^\s"'<>]+\.mp4[^\s"'<>]*"""),
                Regex("""https?://[^\s"'<>]+/video/[^\s"'<>]+"""),
                Regex("""https?://[^\s"'<>]+/stream/[^\s"'<>]+"""),
                Regex("""https?://[^\s"'<>]+cloudatacdn[^\s"'<>]+"""),
            )
            
            // Fazer request e analisar resposta
            val response = app.get(url, referer = referer, timeout = 30)
            val html = response.text
            
            // Procurar URLs de vídeo no HTML
            for (pattern in videoPatterns) {
                val matches = pattern.findAll(html)
                for (match in matches) {
                    val videoUrl = match.value
                    if (!videoUrl.contains("advertisement") && 
                        !videoUrl.contains("tracking") &&
                        !videoUrl.contains("analytics")) {
                        interceptedUrls.add(videoUrl)
                    }
                }
            }
            
            // Procurar em scripts inline
            val scriptRegex = Regex("""<script[^>]*>(.*?)</script>""", RegexOption.DOT_MATCHES_ALL)
            val scripts = scriptRegex.findAll(html)
            
            for (script in scripts) {
                val scriptContent = script.groupValues[1]
                
                // Procurar por file: "url" ou source: "url"
                val fileRegex = Regex("""(?:file|source|src)\s*[=:]\s*["']([^"']+\.(?:m3u8|mp4)[^"']*)["']""")
                val fileMatches = fileRegex.findAll(scriptContent)
                
                for (match in fileMatches) {
                    interceptedUrls.add(match.groupValues[1])
                }
                
                // Procurar por sources: [{file: "url"}]
                val sourcesRegex = Regex("""sources\s*:\s*\[\s*\{[^}]*file\s*:\s*["']([^"']+)["']""")
                val sourcesMatches = sourcesRegex.findAll(scriptContent)
                
                for (match in sourcesMatches) {
                    interceptedUrls.add(match.groupValues[1])
                }
            }
            
            // Processar URLs encontradas
            val uniqueUrls = interceptedUrls.distinct()
            Log.d("MaxSeries", "🔍 URLs encontradas: ${uniqueUrls.size}")
            
            var found = false
            for (videoUrl in uniqueUrls) {
                val cleanUrl = if (videoUrl.startsWith("//")) "https:$videoUrl" else videoUrl
                
                // Determinar qualidade e tipo
                val isM3u8 = cleanUrl.contains(".m3u8")
                val quality = when {
                    cleanUrl.contains("1080") -> Qualities.P1080.value
                    cleanUrl.contains("720") -> Qualities.P720.value
                    cleanUrl.contains("480") -> Qualities.P480.value
                    cleanUrl.contains("360") -> Qualities.P360.value
                    else -> Qualities.Unknown.value
                }
                
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    else -> "WebView"
                }
                
                Log.d("MaxSeries", "🎬 WebView URL: $cleanUrl")
                
                callback(
                    ExtractorLink(
                        source = sourceName,
                        name = sourceName,
                        url = cleanUrl,
                        referer = url,
                        quality = quality,
                        isM3u8 = isM3u8
                    )
                )
                found = true
            }
            
            return found
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro WebView: ${e.message}")
            return false
        }
    }
    
    // Extractor genérico que tenta múltiplos métodos
    private suspend fun extractVideo(url: String, referer: String, subtitleCallback: (SubtitleFile) -> Unit, callback: (ExtractorLink) -> Unit): Boolean {
        Log.d("MaxSeries", "🎯 Extraindo: $url")
        
        // 1. Verificar se é DoodStream clone
        if (isDoodStreamClone(url)) {
            if (extractDoodStream(url, referer, callback)) {
                return true
            }
        }
        
        // 2. Tentar extractor padrão do CloudStream
        try {
            if (loadExtractor(url, referer, subtitleCallback, callback)) {
                return true
            }
        } catch (e: Exception) {
            Log.d("MaxSeries", "⚠️ Extractor padrão falhou: ${e.message}")
        }
        
        // 3. Tentar WebView Extractor para hosts difíceis
        if (isHardHost(url)) {
            if (extractWithWebView(url, referer, callback)) {
                return true
            }
        }
        
        return false
    }
    
    private fun generateRandomToken(): String {
        val chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return (1..10).map { chars.random() }.joinToString("")
    }
    
    // Lista de domínios DoodStream clones
    private val doodStreamDomains = listOf(
        "myvidplay.com", "bysebuho.com", "g9r6.com",
        "doodstream.com", "dood.to", "dood.watch", "dood.pm",
        "dood.wf", "dood.re", "dood.so", "dood.cx",
        "dood.la", "dood.ws", "dood.sh", "doodstream.co"
    )
    
    // Lista de hosts difíceis que precisam de WebView
    private val hardHosts = listOf(
        "megaembed.link",
        "playerembedapi.link",
        "embedsito.com",
        "playersb.com"
    )
    
    private fun isDoodStreamClone(url: String): Boolean {
        return doodStreamDomains.any { url.contains(it, ignoreCase = true) }
    }
    
    private fun isHardHost(url: String): Boolean {
        return hardHosts.any { url.contains(it, ignoreCase = true) }
    }

    // ==================== LOAD LINKS ====================

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var found = 0
        
        try {
            Log.d("MaxSeries", "🎬 Carregando links: $data")
            
            // Coletar todas as URLs de players
            val playerUrls = mutableListOf<String>()
            
            if (data.contains("#") && data.contains("playerthree")) {
                // Extrair episódio do playerthree
                val epId = Regex("#\\d+_(\\d+)").find(data)?.groupValues?.get(1) ?: return false
                Log.d("MaxSeries", "📺 Episódio ID: $epId")
                
                val ajax = app.get(
                    "https://playerthree.online/episodio/$epId",
                    headers = mapOf(
                        "Referer" to data,
                        "X-Requested-With" to "XMLHttpRequest"
                    )
                )
                
                if (ajax.isSuccessful) {
                    ajax.document.select("button[data-source]").forEach { btn ->
                        val src = btn.attr("data-source")
                        if (src.startsWith("http") && !src.contains("youtube", true)) {
                            playerUrls.add(src)
                        }
                    }
                }
            } else {
                // Página normal - buscar iframe
                val doc = app.get(data).document
                val iframe = doc.selectFirst("iframe")?.attr("src")
                
                if (!iframe.isNullOrEmpty()) {
                    val src = if (iframe.startsWith("//")) "https:$iframe" else iframe
                    playerUrls.add(src)
                }
            }
            
            Log.d("MaxSeries", "🔗 Players encontrados: ${playerUrls.size}")
            
            // Ordenar: DoodStream clones primeiro (funcionam melhor)
            val sortedUrls = playerUrls.sortedByDescending { isDoodStreamClone(it) }
            
            // Extrair de cada player
            for (playerUrl in sortedUrls) {
                Log.d("MaxSeries", "🎯 Processando: $playerUrl")
                
                if (extractVideo(playerUrl, data, subtitleCallback, callback)) {
                    found++
                }
            }
            
            Log.d("MaxSeries", "✅ Total links encontrados: $found")
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro: ${e.message}")
        }
        
        return found > 0
    }
}
