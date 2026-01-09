package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log
import org.json.JSONObject
import org.json.JSONArray

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

    // DoodStream Extractor (igual ao oficial do CloudStream)
    private suspend fun extractDoodStream(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            val embedUrl = url.replace("/d/", "/e/")
            val req = app.get(embedUrl)
            val host = getBaseUrl(req.url)
            val html = req.text
            
            val md5Path = Regex("/pass_md5/[^']*").find(html)?.value ?: return false
            val md5Url = host + md5Path
            
            val trueUrl = app.get(md5Url, referer = req.url).text + 
                          createHashTable() + 
                          "?token=" + md5Path.substringAfterLast("/")
            
            val quality = Regex("\\d{3,4}p")
                .find(html.substringAfter("<title>").substringBefore("</title>"))
                ?.value
            
            val sourceName = when {
                url.contains("myvidplay") -> "MyVidPlay"
                url.contains("bysebuho") -> "Bysebuho"
                url.contains("g9r6") -> "G9R6"
                else -> "DoodStream"
            }
            
            callback(
                newExtractorLink(
                    sourceName,
                    sourceName,
                    trueUrl,
                ) {
                    this.referer = "$host/"
                    this.quality = getQualityFromName(quality)
                }
            )
            
            return true
        } catch (e: Exception) {
            Log.e("MaxSeries", "DoodStream erro: ${e.message}")
            return false
        }
    }
    
    // StreamWish-like Extractor (usa JsUnpacker)
    private suspend fun extractWithUnpack(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            val response = app.get(url)
            val html = response.text
            
            // Tentar desempacotar JavaScript P.A.C.K.E.R.
            val packed = getPacked(html)
            val unpacked = if (!packed.isNullOrEmpty()) {
                JsUnpacker(packed).unpack()
            } else {
                html
            }
            
            if (unpacked == null) return false
            
            // Procurar URL do vídeo
            val videoUrl = Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']""").find(unpacked)?.groupValues?.get(1)
                ?: Regex("""sources:\s*\[\s*\{\s*file:\s*["']([^"']+)["']""").find(unpacked)?.groupValues?.get(1)
                ?: Regex("""source:\s*["']([^"']+\.m3u8[^"']*)["']""").find(unpacked)?.groupValues?.get(1)
            
            if (videoUrl != null) {
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    else -> "Unpacked"
                }
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(
                        sourceName,
                        videoUrl,
                        url
                    ).forEach(callback)
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
            
            return false
        } catch (e: Exception) {
            Log.e("MaxSeries", "Unpack erro: ${e.message}")
            return false
        }
    }
    
    // Extrator direto para MegaEmbed/PlayerEmbedAPI - Tenta API antes do WebView
    private suspend fun extractDirectAPI(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "Tentando API direta: $url")
            
            // Extrair ID do vídeo da URL
            val videoId = when {
                url.contains("#") -> url.substringAfter("#").takeIf { it.isNotEmpty() }
                url.contains("?v=") -> Regex("[?&]v=([^&]+)").find(url)?.groupValues?.get(1)
                url.contains("/embed/") -> url.substringAfter("/embed/").substringBefore("?")
                else -> null
            }
            
            if (videoId.isNullOrEmpty()) {
                Log.d("MaxSeries", "ID não encontrado na URL")
                return false
            }
            
            Log.d("MaxSeries", "Video ID: $videoId")
            
            // Determinar qual API chamar
            val apiUrl = when {
                url.contains("megaembed") -> "https://megaembed.link/api/v1/info?id=$videoId"
                url.contains("playerembedapi") -> "https://playerembedapi.link/api/source?v=$videoId"
                else -> return false
            }
            
            // Fazer requisição à API
            val apiResponse = app.get(
                apiUrl,
                headers = mapOf(
                    "Referer" to url,
                    "Accept" to "application/json",
                    "X-Requested-With" to "XMLHttpRequest"
                )
            )
            
            if (!apiResponse.isSuccessful) {
                Log.d("MaxSeries", "API retornou ${apiResponse.code}")
                return false
            }
            
            val jsonText = apiResponse.text
            Log.d("MaxSeries", "API Response: ${jsonText.take(200)}")
            
            // Tentar parsear JSON e encontrar URL
            try {
                val json = JSONObject(jsonText)
                
                // Procurar campos comuns de URL de vídeo
                val possibleKeys = listOf("file", "url", "source", "src", "stream", "hls", "mp4", "video", "link")
                
                for (key in possibleKeys) {
                    if (json.has(key)) {
                        val value = json.optString(key)
                        if (value.isNotEmpty() && (value.contains(".m3u8") || value.contains(".mp4"))) {
                            Log.d("MaxSeries", "URL encontrada via API: $value")
                            
                            val sourceName = when {
                                url.contains("megaembed") -> "MegaEmbed"
                                url.contains("playerembedapi") -> "PlayerEmbedAPI"
                                else -> "DirectAPI"
                            }
                            
                            if (value.contains(".m3u8")) {
                                M3u8Helper.generateM3u8(sourceName, value, url).forEach(callback)
                            } else {
                                callback(
                                    newExtractorLink(sourceName, sourceName, value) {
                                        this.referer = url
                                        this.quality = Qualities.Unknown.value
                                    }
                                )
                            }
                            return true
                        }
                    }
                }
                
                // Procurar em arrays
                if (json.has("sources")) {
                    val sources = json.optJSONArray("sources")
                    if (sources != null && sources.length() > 0) {
                        for (i in 0 until sources.length()) {
                            val source = sources.optJSONObject(i)
                            if (source != null) {
                                val file = source.optString("file") 
                                    ?: source.optString("src")
                                    ?: source.optString("url")
                                    
                                if (!file.isNullOrEmpty() && (file.contains(".m3u8") || file.contains(".mp4"))) {
                                    Log.d("MaxSeries", "URL encontrada em sources: $file")
                                    
                                    val quality = source.optString("label") ?: "Unknown"
                                    
                                    callback(
                                        newExtractorLink("DirectAPI", "DirectAPI - $quality", file) {
                                            this.referer = url
                                            this.quality = getQualityFromName(quality)
                                        }
                                    )
                                    return true
                                }
                            }
                        }
                    }
                }
                
            } catch (e: Exception) {
                Log.d("MaxSeries", "Erro parseando JSON: ${e.message}")
            }
            
            return false
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "DirectAPI erro: ${e.message}")
            return false
        }
    }
    
    // WebView Extractor (fallback final) - com script AGRESSIVO para capturar vídeo
    private suspend fun extractWithWebView(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        try {
            Log.d("MaxSeries", "WebView iniciando: $url")
            
            // Script JS MUITO AGRESSIVO que:
            // 1. Clica em TUDO que parece um botão de play
            // 2. Aguarda e tenta repetidamente
            // 3. Captura de múltiplas fontes
            val captureScript = """
                (function() {
                    var videoUrl = '';
                    
                    // Função para capturar URL do vídeo de várias fontes
                    function getVideoUrl() {
                        // 1. Elemento video direto
                        var video = document.querySelector('video');
                        if (video) {
                            if (video.src && video.src.length > 20 && !video.src.startsWith('blob:')) return video.src;
                            if (video.currentSrc && video.currentSrc.length > 20 && !video.currentSrc.startsWith('blob:')) return video.currentSrc;
                        }
                        
                        // 2. Source dentro de video
                        var sources = document.querySelectorAll('video source');
                        for (var i = 0; i < sources.length; i++) {
                            if (sources[i].src && sources[i].src.length > 20) return sources[i].src;
                        }
                        
                        // 3. JWPlayer
                        try {
                            if (typeof jwplayer !== 'undefined') {
                                var jw = jwplayer();
                                if (jw && jw.getPlaylistItem) {
                                    var item = jw.getPlaylistItem();
                                    if (item && item.file) return item.file;
                                    if (item && item.sources && item.sources[0]) return item.sources[0].file;
                                }
                            }
                        } catch(e) {}
                        
                        // 4. HLS.js
                        try {
                            if (window.hls && window.hls.url) return window.hls.url;
                        } catch(e) {}
                        
                        // 5. Video.js
                        try {
                            var vjs = document.querySelector('.video-js');
                            if (vjs && vjs.player && vjs.player.src) return vjs.player.src();
                        } catch(e) {}
                        
                        // 6. Plyr
                        try {
                            if (window.player && window.player.source) {
                                var src = window.player.source;
                                if (typeof src === 'string') return src;
                                if (src.sources && src.sources[0]) return src.sources[0].src;
                            }
                        } catch(e) {}
                        
                        // 7. Procurar em variáveis globais comuns
                        try {
                            if (window.videoSource) return window.videoSource;
                            if (window.hlsUrl) return window.hlsUrl;
                            if (window.videoUrl) return window.videoUrl;
                            if (window.streamUrl) return window.streamUrl;
                            if (window.source) return window.source;
                        } catch(e) {}
                        
                        return '';
                    }
                    
                    // Função para clicar em botões de play
                    function clickPlayButtons() {
                        // Lista EXTENSA de seletores de botões de play
                        var selectors = [
                            '.play-btn', '.btn-play', '.play-button', '.playButton',
                            '[class*="play"]', '[id*="play"]',
                            '.vjs-big-play-button', '.jw-icon-display',
                            '.plyr__control--overlaid', '.ytp-large-play-button',
                            'button[aria-label*="play"]', 'button[aria-label*="Play"]',
                            '.player-play', '#play', '.play', '[data-action="play"]',
                            '.mejs__button--playpause', '.mejs__overlay-play',
                            '.video-play-button', '.video__play',
                            'svg[class*="play"]', '.icon-play',
                            '.fp-play', '.flowplayer .fp-ui'
                        ];
                        
                        selectors.forEach(function(selector) {
                            try {
                                var buttons = document.querySelectorAll(selector);
                                buttons.forEach(function(btn) {
                                    try { 
                                        btn.click();
                                        btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                                    } catch(e) {}
                                });
                            } catch(e) {}
                        });
                        
                        // Clicar no centro do player/video
                        var containers = document.querySelectorAll('.player, #player, .video-container, .video-wrapper, .embed-responsive, video, .plyr, .jw-wrapper, .vjs-tech');
                        containers.forEach(function(container) {
                            try {
                                var rect = container.getBoundingClientRect();
                                if (rect.width > 50 && rect.height > 50) {
                                    var event = new MouseEvent('click', {
                                        bubbles: true, cancelable: true, view: window,
                                        clientX: rect.left + rect.width/2,
                                        clientY: rect.top + rect.height/2
                                    });
                                    container.dispatchEvent(event);
                                }
                            } catch(e) {}
                        });
                    }
                    
                    // Executar cliques imediatamente
                    clickPlayButtons();
                    
                    // Tentar capturar imediatamente
                    videoUrl = getVideoUrl();
                    if (videoUrl) return videoUrl;
                    
                    // Se não encontrou, retornar vazio (o interceptor vai pegar via rede)
                    return '';
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                // Interceptar URLs de vídeo incluindo Google Storage
                interceptUrl = Regex("""\\.m3u8|\\.mp4|storage\\.googleapis\\.com|master\\.txt|/hls/|/video/|googlevideo|akamaized"""),
                additionalUrls = listOf(Regex("""\\.m3u8|\\.mp4|\\.ts|storage\\.googleapis""")),
                useOkhttp = false,  // IMPORTANTE: false para bypass Cloudflare
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"" && result.length > 10) {
                        capturedUrl = result.trim('"')
                        Log.d("MaxSeries", "Script capturou: $capturedUrl")
                    }
                },
                timeout = 30_000L  // Aumentar timeout para dar tempo ao JS
            )
            
            val response = app.get(url, interceptor = resolver)
            val interceptedUrl = response.url
            
            Log.d("MaxSeries", "URL interceptada: $interceptedUrl")
            
            // Usar URL interceptada ou capturada pelo script
            val videoUrl = when {
                interceptedUrl.contains(".m3u8") || interceptedUrl.contains(".mp4") || interceptedUrl.contains("storage.googleapis.com") -> interceptedUrl
                !capturedUrl.isNullOrEmpty() && (capturedUrl!!.contains(".m3u8") || capturedUrl!!.contains(".mp4") || capturedUrl!!.contains("storage.googleapis.com")) -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d("MaxSeries", "Vídeo encontrado: $videoUrl")
                
                val sourceName = when {
                    url.contains("megaembed") -> "MegaEmbed"
                    url.contains("playerembedapi") -> "PlayerEmbedAPI"
                    videoUrl.contains("googleapis") -> "GoogleStorage"
                    else -> "WebView"
                }
                
                // Extrair qualidade da URL se disponível
                val quality = Regex("(\\d{3,4})p").find(videoUrl)?.groupValues?.get(1)?.toIntOrNull()
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(sourceName, videoUrl, url).forEach(callback)
                } else {
                    callback(
                        newExtractorLink(sourceName, sourceName, videoUrl) {
                            this.referer = url
                            this.quality = quality ?: Qualities.Unknown.value
                        }
                    )
                }
                return true
            }
            
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
        "myvidplay.com", "bysebuho.com", "g9r6.com",
        "doodstream.com", "dood.to", "dood.watch", "dood.pm",
        "dood.wf", "dood.re", "dood.so", "dood.cx",
        "dood.la", "dood.ws", "dood.sh", "doodstream.co",
        "d0000d.com", "d000d.com", "dooood.com", "ds2play.com"
    )
    
    private val hardHosts = listOf("megaembed.link", "playerembedapi.link")
    
    // Domínios de trailer/YouTube que devem ser IGNORADOS
    private val youtubeTrailerDomains = listOf(
        "youtube.com", "youtu.be", "youtube-nocookie.com",
        "ytimg.com", "googlevideo.com/videoplayback" // YouTube domains
    )
    
    private fun isDoodStreamClone(url: String) = doodStreamDomains.any { url.contains(it, true) }
    private fun isHardHost(url: String) = hardHosts.any { url.contains(it, true) }
    
    // Verifica se é URL do YouTube (trailers) - deve ser IGNORADO
    private fun isYoutubeOrTrailer(url: String): Boolean {
        val urlLower = url.lowercase()
        return youtubeTrailerDomains.any { urlLower.contains(it) } ||
               urlLower.contains("trailer") ||
               urlLower.contains("/embed/") && urlLower.contains("youtube")
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
            val playerUrls = mutableListOf<String>()
            
            if (data.contains("#") && data.contains("playerthree")) {
                val epId = Regex("#\\d+_(\\d+)").find(data)?.groupValues?.get(1) ?: return false
                
                val ajax = app.get(
                    "https://playerthree.online/episodio/$epId",
                    headers = mapOf("Referer" to data, "X-Requested-With" to "XMLHttpRequest")
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
                val doc = app.get(data).document
                val iframe = doc.selectFirst("iframe")?.attr("src")
                if (!iframe.isNullOrEmpty()) {
                    val iframeFull = if (iframe.startsWith("//")) "https:$iframe" else iframe
                    // IGNORAR YouTube/trailers
                    if (!isYoutubeOrTrailer(iframeFull)) {
                        playerUrls.add(iframeFull)
                    } else {
                        Log.d("MaxSeries", "Ignorando trailer/YouTube: $iframeFull")
                    }
                }
            }
            
            // Ordenar: DoodStream primeiro (mais confiável)
            val sortedUrls = playerUrls.sortedByDescending { isDoodStreamClone(it) }
            
            for (playerUrl in sortedUrls) {
                // Pular URLs do YouTube/trailers
                if (isYoutubeOrTrailer(playerUrl)) {
                    Log.d("MaxSeries", "Pulando trailer: $playerUrl")
                    continue
                }
                Log.d("MaxSeries", "Processando: $playerUrl")
                
                // 1. DoodStream clones
                if (isDoodStreamClone(playerUrl)) {
                    if (extractDoodStream(playerUrl, callback)) { found++; continue }
                }
                
                // 2. Extractor padrão do CloudStream
                try {
                    if (loadExtractor(playerUrl, data, subtitleCallback, callback)) { found++; continue }
                } catch (_: Exception) {}
                
                // 3. Tentar desempacotar JavaScript
                if (extractWithUnpack(playerUrl, callback)) { found++; continue }
                
                // 4. Tentar API direta (mais rápido que WebView)
                if (isHardHost(playerUrl)) {
                    if (extractDirectAPI(playerUrl, callback)) { found++; continue }
                }
                
                // 5. WebView como fallback final
                if (isHardHost(playerUrl)) {
                    if (extractWithWebView(playerUrl, callback)) { found++; continue }
                }
            }
            
        } catch (e: Exception) {
            Log.e("MaxSeries", "Erro: ${e.message}")
        }
        
        return found > 0
    }
}
