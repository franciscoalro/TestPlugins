package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV4
import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractor

class MaxSeriesProvider : MainAPI() {
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    private val megaEmbedExtractor = MegaEmbedExtractorV4()
    private val playerEmbedExtractor = PlayerEmbedAPIExtractor()

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

    // DoodStream Extractor - HTTP puro (validado via engenharia reversa)
    private suspend fun extractDoodStream(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            val sourceName = when {
                url.contains("myvidplay", true) -> "MyVidPlay"
                url.contains("bysebuho", true) -> "Bysebuho"
                url.contains("g9r6", true) -> "G9R6"
                url.contains("vidplay", true) -> "VidPlay"
                url.contains("doodstream", true) -> "DoodStream"
                url.contains("dood.", true) -> "Dood"
                else -> "DoodClone"
            }
            
            Log.d("MaxSeries", "[$sourceName] Iniciando extração: $url")
            val embedUrl = url.replace("/d/", "/e/")
            val req = app.get(embedUrl)
            val host = getBaseUrl(req.url)
            val html = req.text
            
            // Regex melhorado para capturar pass_md5 path completo
            val md5Path = Regex("""/pass_md5/[^'"\s]+""").find(html)?.value
            if (md5Path == null) {
                Log.e("MaxSeries", "[$sourceName] pass_md5 não encontrado")
                return false
            }
            
            val md5Url = host + md5Path
            Log.d("MaxSeries", "[$sourceName] pass_md5: $md5Url")
            
            // Obter URL base do vídeo
            val baseUrl = app.get(md5Url, referer = req.url).text.trim()
            if (baseUrl.isEmpty() || !baseUrl.startsWith("http")) {
                Log.e("MaxSeries", "[$sourceName] baseUrl inválida: $baseUrl")
                return false
            }
            
            // Montar URL final com hash, token e expiry (igual ao JavaScript makePlay())
            val token = md5Path.substringAfterLast("/")
            val expiry = System.currentTimeMillis()
            val trueUrl = "$baseUrl${createHashTable()}?token=$token&expiry=$expiry"
            
            Log.d("MaxSeries", "[$sourceName] URL final gerada com sucesso")
            
            // Extrair qualidade do título
            val quality = Regex("""\d{3,4}p""")
                .find(html.substringAfter("<title>").substringBefore("</title>"))
                ?.value
            
            callback(
                newExtractorLink(
                    sourceName,
                    "$sourceName - ${quality ?: "HD"}",
                    trueUrl,
                ) {
                    this.referer = "$host/"
                    this.quality = Qualities.Unknown.value
                }
            )
            
            Log.d("MaxSeries", "[$sourceName] Extração bem-sucedida!")
            return true
        } catch (e: Exception) {
            Log.e("MaxSeries", "Erro na extração DoodStream: ${e.message}")
            return false
        }
    }
    

    
    // WebView Extractor (fallback para players que requerem JS)
    private suspend fun extractWithWebView(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "WebView fallback: $url")
            
            // Script JS avançado: auto-click no play + captura de múltiplos players
            val captureScript = """
                (function() {
                    // Auto-click em botões de play
                    var playButtons = ['.vjs-big-play-button', '.play-button', '#play-button', '[class*="play"]', 'button[data-show-player]', '.jw-icon-playback', '#overlay'];
                    for (var i = 0; i < playButtons.length; i++) {
                        var btn = document.querySelector(playButtons[i]);
                        if (btn) { btn.click(); break; }
                    }
                    
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 50; // 5 segundos max
                        
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';
                            
                            // 1. Video element
                            var video = document.querySelector('video');
                            if (video && video.src && video.src.startsWith('http')) {
                                result = video.src;
                            }
                            
                            // 2. JWPlayer
                            if (!result && window.jwplayer) {
                                try {
                                    var jw = window.jwplayer();
                                    if (jw) {
                                        var item = jw.getPlaylistItem && jw.getPlaylistItem();
                                        if (item && item.file) result = item.file;
                                    }
                                } catch(e) {}
                            }
                            
                            // 3. Source elements
                            if (!result) {
                                var sources = document.querySelectorAll('source[src]');
                                for (var j = 0; j < sources.length; j++) {
                                    var s = sources[j].src;
                                    if (s && (s.includes('.m3u8') || s.includes('.mp4'))) {
                                        result = s;
                                        break;
                                    }
                                }
                            }
                            
                            if (result && result.length > 0) {
                                clearInterval(interval);
                                resolve(result);
                            } else if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                resolve(''); // Timeout
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                // Interceptar múltiplos padrões de URL de vídeo
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|/hls/|/video/|cloudatacdn|abyss\.to.*\.mp4"""),
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4"""),
                    Regex("""\.ts\?"""),
                    Regex("""cloudatacdn\.com"""),
                    Regex("""sssrr\.org.*\.m3u8""")
                ),
                useOkhttp = false,  // IMPORTANTE: false para bypass Cloudflare
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result.startsWith("http")) {
                        capturedUrl = result.trim('"')
                        Log.d("MaxSeries", "WebView script capturou: $capturedUrl")
                    }
                },
                timeout = 35_000L  // Timeout maior para players com JS pesado
            )
            
            val response = app.get(url, interceptor = resolver)
            val interceptedUrl = response.url
            
            Log.d("MaxSeries", "WebView intercepted: $interceptedUrl")
            
            // Usar URL interceptada ou capturada pelo script
            val videoUrl = when {
                interceptedUrl.contains(".m3u8") -> interceptedUrl
                interceptedUrl.contains(".mp4") && interceptedUrl.contains("cloudatacdn") -> interceptedUrl
                interceptedUrl.contains(".mp4") && !interceptedUrl.contains("playerembedapi") -> interceptedUrl
                !capturedUrl.isNullOrEmpty() && capturedUrl!!.contains(".m3u8") -> capturedUrl!!
                !capturedUrl.isNullOrEmpty() && capturedUrl!!.contains(".mp4") -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d("MaxSeries", "WebView video URL: $videoUrl")
                
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbed"
                    url.contains("abyss") -> "Abyss"
                    else -> "WebView"
                }
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(sourceName, videoUrl, url).forEach(callback)
                } else {
                    callback(
                        newExtractorLink(sourceName, sourceName, videoUrl) {
                            this.referer = url
                            this.quality = Qualities.Unknown.value
                        }
                    )
                }
                return true
            }
            
            Log.w("MaxSeries", "WebView: nenhum vídeo encontrado")
            return false
        } catch (e: Exception) {
            Log.e("MaxSeries", "WebView erro: ${e.message}")
            return false
        }
    }
    
    // Helpers
    private fun createHashTable(): String {
        val alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return buildString { repeat(10) { append(alphabet.random()) } }
    }
    
    private fun getBaseUrl(url: String): String {
        return Regex("""^(https?://[^/]+)""").find(url)?.value ?: url
    }
    

    
    private val doodStreamDomains = listOf(
        // Principais clones ativos no MaxSeries
        "myvidplay.com", "bysebuho.com", "g9r6.com",
        
        // DoodStream oficiais
        "doodstream.com", "dood.to", "dood.watch", "dood.pm",
        "dood.wf", "dood.re", "dood.so", "dood.cx",
        "dood.la", "dood.ws", "dood.sh", "doodstream.co",
        
        // Variantes e mirrors
        "d0000d.com", "d000d.com", "dooood.com", "ds2play.com",
        "dood.yt", "dood.stream", "doodcdn.com", "doodcdn.co",
        
        // Novos domínios encontrados (2026)
        "dood.li", "dood.video", "doodstream.tv", "dood.one",
        "vidplay.com", "vidplay.site", "vidplay.online"
    )
    
    private val hardHosts = listOf("megaembed.link", "playerembedapi.link")
    
    private fun isDoodStreamClone(url: String) = doodStreamDomains.any { url.contains(it, true) }
    private fun isHardHost(url: String) = hardHosts.any { url.contains(it, true) }

    // ==================== LOAD LINKS ====================

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var found = 0
        
        try {
            val playerUrls = mutableListOf<String>()
            
            if (data.contains("#") && data.contains("playerthree")) {
                // Formato antigo: #123_456
                val epId = Regex("#\\d+_(\\d+)").find(data)?.groupValues?.get(1) ?: return false
                
                val ajax = app.get(
                    "https://playerthree.online/episodio/$epId",
                    headers = mapOf("Referer" to data, "X-Requested-With" to "XMLHttpRequest")
                )
                
                if (ajax.isSuccessful) {
                    // Procurar botões com data-source (padrão antigo)
                    ajax.document.select("button[data-source]").forEach { btn ->
                        val src = btn.attr("data-source")
                        if (src.startsWith("http") && !src.contains("youtube", true)) {
                            playerUrls.add(src)
                        }
                    }
                    
                    // NOVO: Procurar botões com data-show-player (padrão atual do PlayterThree)
                    ajax.document.select("button[data-show-player]").forEach { btn ->
                        val src = btn.attr("data-source")
                        if (src.startsWith("http") && !src.contains("youtube", true)) {
                            playerUrls.add(src)
                            Log.d("MaxSeries", "🎬 Fonte encontrada via data-show-player: $src")
                        }
                    }
                }
            } else {
                // Carregar página principal para obter iframe
                val doc = app.get(data).document
                val iframe = doc.selectFirst("iframe")?.attr("src")
                if (!iframe.isNullOrEmpty()) {
                    val iframeSrc = if (iframe.startsWith("//")) "https:$iframe" else iframe
                    
                    // Se é playerthree, tentar extrair IDs de episódio do iframe
                    if (iframeSrc.contains("playerthree")) {
                        Log.d("MaxSeries", "🔍 Carregando PlayterThree iframe: $iframeSrc")
                        
                        try {
                            val iframeResponse = app.get(iframeSrc, headers = mapOf("Referer" to data))
                            val iframeHtml = iframeResponse.text
                            
                            // Procurar IDs de episódio no iframe
                            val episodeIds = Regex("data-episode-id[\"\\s]*=[\"\\s]*[\"']?(\\d+)").findAll(iframeHtml)
                                .map { it.groupValues[1] }
                                .toList()
                            
                            Log.d("MaxSeries", "🆔 Episode IDs encontrados: ${episodeIds.size}")
                            
                            // Testar alguns IDs para encontrar fontes
                            for (epId in episodeIds.take(5)) { // Testar apenas os primeiros 5
                                Log.d("MaxSeries", "🧪 Testando Episode ID: $epId")
                                
                                val ajax = app.get(
                                    "https://playerthree.online/episodio/$epId",
                                    headers = mapOf("Referer" to data, "X-Requested-With" to "XMLHttpRequest")
                                )
                                
                                if (ajax.isSuccessful) {
                                    val buttons = ajax.document.select("button[data-show-player]")
                                    Log.d("MaxSeries", "🔘 Botões encontrados para ID $epId: ${buttons.size}")
                                    
                                    buttons.forEach { btn ->
                                        val src = btn.attr("data-source")
                                        if (src.startsWith("http") && !src.contains("youtube", true)) {
                                            playerUrls.add(src)
                                            Log.d("MaxSeries", "✅ Fonte adicionada: $src")
                                        }
                                    }
                                    
                                    // Se encontrou fontes, parar de procurar
                                    if (buttons.isNotEmpty()) {
                                        break
                                    }
                                }
                            }
                            
                        } catch (e: Exception) {
                            Log.e("MaxSeries", "❌ Erro ao processar PlayterThree iframe: ${e.message}")
                        }
                    }
                    
                    // Fallback: adicionar o próprio iframe se não encontrou fontes específicas
                    if (playerUrls.isEmpty()) {
                        playerUrls.add(iframeSrc)
                    }
                }
            }
            
            // Ordenar: DoodStream primeiro (mais confiável)
            val sortedUrls = playerUrls.sortedByDescending { isDoodStreamClone(it) }
            
            Log.d("MaxSeries", "=== Iniciando extração de ${sortedUrls.size} fontes ===")
            sortedUrls.forEachIndexed { index, url ->
                val sourceType = when {
                    isDoodStreamClone(url) -> "DoodStream"
                    isHardHost(url) -> "Hard"
                    else -> "Other"
                }
                Log.d("MaxSeries", "${index + 1}. [$sourceType] $url")
            }
            
            for (playerUrl in sortedUrls) {
                val sourceType = when {
                    isDoodStreamClone(playerUrl) -> "DoodStream Clone"
                    MegaEmbedExtractorV4.canHandle(playerUrl) -> "MegaEmbed"
                    PlayerEmbedAPIExtractor.canHandle(playerUrl) -> "PlayerEmbedAPI"
                    else -> "Unknown"
                }
                
                Log.d("MaxSeries", "🎬 Processando [$sourceType]: $playerUrl")
                
                // 1. DoodStream clones (HTTP puro - prioridade máxima)
                if (isDoodStreamClone(playerUrl)) {
                    Log.d("MaxSeries", "🔄 Tentando extração DoodStream...")
                    if (extractDoodStream(playerUrl, callback)) { 
                        found++
                        Log.d("MaxSeries", "✅ DoodStream extraído com sucesso!")
                        continue 
                    }
                    Log.d("MaxSeries", "❌ DoodStream falhou")
                }
                // 2. Extractor padrão do CloudStream (tentar primeiro)
                Log.d("MaxSeries", "🔄 Tentando extrator padrão CloudStream...")
                try {
                    if (loadExtractor(playerUrl, data, subtitleCallback, callback)) { 
                        found++
                        Log.d("MaxSeries", "✅ Extrator padrão funcionou!")
                        continue 
                    }
                    Log.d("MaxSeries", "❌ Extrator padrão falhou")
                } catch (e: Exception) {
                    Log.d("MaxSeries", "❌ Extrator padrão erro: ${e.message}")
                }

                // 3. Extratores Dedicados como fallback (MegaEmbed / PlayerEmbedAPI)
                try {
                    if (MegaEmbedExtractorV4.canHandle(playerUrl)) {
                        Log.d("MaxSeries", "🔄 Tentando MegaEmbed v4 (CDN Dinâmico)...")
                        megaEmbedExtractor.getUrl(playerUrl, data, subtitleCallback, callback)
                        Log.d("MaxSeries", "⚠️ MegaEmbed v4 executado (sucesso não confirmado)")
                    }
                } catch (e: Exception) {
                    Log.d("MaxSeries", "❌ MegaEmbed v4 erro: ${e.message}")
                }

                try {
                    if (PlayerEmbedAPIExtractor.canHandle(playerUrl)) {
                        Log.d("MaxSeries", "🔄 Tentando PlayerEmbedAPI...")
                        playerEmbedExtractor.getUrl(playerUrl, data, subtitleCallback, callback)
                        Log.d("MaxSeries", "⚠️ PlayerEmbedAPI executado (sucesso não confirmado)")
                    }
                } catch (e: Exception) {
                    Log.d("MaxSeries", "❌ PlayerEmbedAPI erro: ${e.message}")
                }
                
                // 4. WebView como fallback UNIVERSAL para qualquer player restante
                Log.d("MaxSeries", "🔄 Tentando WebView fallback...")
                if (extractWithWebView(playerUrl, callback)) { 
                    found++
                    Log.d("MaxSeries", "✅ WebView funcionou!")
                    continue 
                }
                Log.d("MaxSeries", "❌ WebView falhou")
                
                Log.w("MaxSeries", "❌ Nenhum extrator funcionou para: $playerUrl")
            }
            
            Log.d("MaxSeries", "=== RESUMO DA EXTRAÇÃO ===")
            Log.d("MaxSeries", "📊 Fontes processadas: ${sortedUrls.size}")
            Log.d("MaxSeries", "✅ Fontes extraídas: $found")
            Log.d("MaxSeries", "📈 Taxa de sucesso: ${if (sortedUrls.isNotEmpty()) (found * 100 / sortedUrls.size) else 0}%")
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "❌ Erro crítico: ${e.message}")
        }
        
        return found > 0
    }
}
