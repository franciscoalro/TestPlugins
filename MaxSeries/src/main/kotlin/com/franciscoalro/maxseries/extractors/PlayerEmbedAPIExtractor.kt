package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v2 - OPTIMIZED (FASE 4)
 * 
 * Handles AES-CTR encrypted sources ("core.bundle.js") by running the actual Page logic
 * and intercepting the final video request.
 * 
 * Melhorias v2:
 * - ✅ Cache de URLs extraídas (5min)
 * - ✅ Retry logic (3 tentativas)
 * - ✅ Quality detection automática
 * - ✅ Logs estruturados com ErrorLogger
 * - ✅ Performance tracking
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        // 1. VERIFICAR CACHE
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            ErrorLogger.logCache(url, hit = true, VideoUrlCache.getStats())
            
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)}",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = url
                    this.quality = cached.quality
                }
            )
            
            ErrorLogger.logPerformance("PlayerEmbedAPI Extraction (Cached)", 
                System.currentTimeMillis() - startTime)
            return
        }
        
        ErrorLogger.logCache(url, hit = false, VideoUrlCache.getStats())
        
        // 0. FETCH HTML (Shared)
        val html = try {
            app.get(url, headers = HeadersBuilder.playerEmbed(url)).text
        } catch (e: Exception) {
            ErrorLogger.e(TAG, "Falha ao obter HTML inicial", error = e)
            return
        }

        // 2. NATIVE DECRYPTION (v103 - AES-CTR)
        runCatching {
            ErrorLogger.d(TAG, "Tentando Decriptação Nativa (AES-CTR)...", mapOf("URL" to url))
            
            // 2. Extrair o objeto 'datas' ou buscar via API /info/
            val datasRegex = Regex("""datas\s*=\s*(\{.*?\})\s*;""", RegexOption.DOT_MATCHES_ALL)
            var datasJson = datasRegex.find(html)?.groupValues?.get(1)
            
            if (datasJson != null) {
                 Log.d(TAG, "📦 Objeto 'datas' encontrado!")
                 val mapper = JsonHelper.mapper
                 val datasNode = mapper.readTree(datasJson)
                 
                 val mediaEncrypted = datasNode.get("media")?.asText()
                 // user_id ou res_id
                 val userId = datasNode.get("user_id")?.asText() ?: datasNode.get("res_id")?.asText()
                 val slug = datasNode.get("slug")?.asText()
                 val md5Id = datasNode.get("md5_id")?.asText()
                 
                 if (!mediaEncrypted.isNullOrEmpty() && !userId.isNullOrEmpty() && !slug.isNullOrEmpty() && !md5Id.isNullOrEmpty()) {
                     Log.d(TAG, "🔑 Decriptando media... UserID: $userId, Slug: $slug")
                     val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaEncrypted, userId, slug, md5Id)
                     
                     if (decrypted != null) {
                         var found = false
                         
                         decrypted.hls?.let { hlsUrl ->
                             Log.d(TAG, "🎯 AES-CTR capturou HLS: $hlsUrl")
                             VideoUrlCache.put(url, hlsUrl, Qualities.Unknown.value, name)
                             callback.invoke(
                                newExtractorLink(name, "$name Auto (AES)", hlsUrl, ExtractorLinkType.VIDEO) {
                                    this.referer = url
                                }
                             )
                             found = true
                         }
                         
                         decrypted.mp4?.let { mp4Url ->
                              Log.d(TAG, "🎯 AES-CTR capturou MP4: $mp4Url")
                              callback.invoke(
                                newExtractorLink(name, "$name MP4 (AES)", mp4Url, ExtractorLinkType.VIDEO) {
                                    this.referer = url
                                }
                              )
                              found = true
                         }
                         
                         if (found) return
                     }
                 }
            }
        }
        
        // 3. STEALTH FALLBACK (JsUnpacker)
        runCatching {
            ErrorLogger.d(TAG, "Tentando Stealth Extraction (JsUnpackerUtil)...", mapOf("URL" to url))
            
            val packedRegex = Regex("""eval\s*\(\s*function\s*\(p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[rd]\s*\).+?\}\s*\(\s*(.+?)\s*\)\s*\)\s*;?""", RegexOption.DOT_MATCHES_ALL)
            val packedMatch = packedRegex.find(html)
            
            if (packedMatch != null) {
                val unpacked = JsUnpackerUtil.unpack(packedMatch.value)
                if (!unpacked.isNullOrEmpty()) {
                    Log.d(TAG, "🔓 Stealth descompactou script (${unpacked.length} chars)")
                    
                    val videoRegex = Regex("""https?://[^"'\s]+\.(?:m3u8|mp4|txt|sbs|online|cyou|googleapis|cloudatacdn|iamcdn|sssrr)[^"'\s]*""")
                    val videoMatch = videoRegex.find(unpacked)
                    
                    if (videoMatch != null) {
                        val videoUrl = videoMatch.value
                        Log.d(TAG, "🎯 Stealth capturou URL: $videoUrl")
                        
                        val quality = QualityDetector.detectFromUrl(videoUrl)
                        VideoUrlCache.put(url, videoUrl, quality, name)
                        
                        callback.invoke(
                            newExtractorLink(
                                source = name,
                                name = "$name ${QualityDetector.getQualityLabel(quality)} (Stealth)",
                                url = videoUrl,
                                type = ExtractorLinkType.VIDEO
                            ) {
                                this.referer = url
                                this.quality = quality
                            }
                        )
                        return
                    }
                }
            }
        }

        // 3.5 HTML REGEX FALLBACK (v104 - saimuelrepo pattern)
        runCatching {
            ErrorLogger.d(TAG, "Tentando HTML Regex Fallback...", mapOf("URL" to url))
            
            // Padrões para extrair URLs diretas do HTML
            val directUrlPatterns = listOf(
                Regex(""""(https?://[^"]+\.m3u8[^"]*)""""),
                Regex(""""(https?://[^"]+\.mp4[^"]*)""""),
                Regex(""""(https?://storage\.googleapis\.com[^"]+)""""),
                Regex(""""(https?://[^"]*sssrr\.org[^"]+)""""),
                Regex(""""(https?://[^"]*iamcdn\.net[^"]+)""""),
                Regex(""""(https?://[^"]*cloudatacdn\.com[^"]+)""""),
                Regex(""""(https?://[^"]*valenium\.shop[^"]+)""""),
                Regex("""file\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""source\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""src\s*:\s*["']([^"']+\.(?:m3u8|mp4)[^"']*)["']""")
            )
            
            for (pattern in directUrlPatterns) {
                val match = pattern.find(html)
                if (match != null) {
                    val videoUrl = match.groupValues[1].replace("\\/", "/")
                    // Filtrar URLs de analytics e scripts
                    if (!videoUrl.contains("google-analytics") && 
                        !videoUrl.contains("googletagmanager") &&
                        !videoUrl.contains(".js") &&
                        !videoUrl.contains("jwplayer") &&
                        videoUrl.startsWith("http")) {
                        
                        Log.d(TAG, "🎯 HTML Regex capturou URL: $videoUrl")
                        
                        val quality = QualityDetector.detectFromUrl(videoUrl)
                        VideoUrlCache.put(url, videoUrl, quality, name)
                        
                        callback.invoke(
                            newExtractorLink(
                                source = name,
                                name = "$name ${QualityDetector.getQualityLabel(quality)} (Direct)",
                                url = videoUrl,
                                type = ExtractorLinkType.VIDEO
                            ) {
                                this.referer = url
                                this.quality = quality
                            }
                        )
                        return
                    }
                }
            }
            Log.d(TAG, "⚠️ HTML Regex: Nenhuma URL válida encontrada")
        }

        // 4. EXTRAIR COM RETRY LOGIC (WebView Fallback)
        RetryHelper.withRetry(maxAttempts = 2) { attempt ->
            runCatching {
                ErrorLogger.d(TAG, "Iniciando extração PlayerEmbedAPI (WebView)...", mapOf(
                    "URL" to url,
                    "Attempt" to "$attempt/2"
                ))
                
                // Script de captura de vídeo avançado (v99)
                val captureScript = """
                    (function() {
                        return new Promise(function(resolve) {
                            var attempts = 0;
                            var maxAttempts = 80; // 8 segundos
                            
                            function tryPlayVideo() {
                                // 1. Forçar play em elementos video
                                var vids = document.getElementsByTagName('video');
                                for(var i=0; i<vids.length; i++){
                                    var v = vids[i];
                                    if(v.paused) {
                                        v.muted = true;
                                        v.play().catch(function(e){});
                                    }
                                }
                                
                                // 2. Clicar em botões de play/overlays
                                var overlays = document.querySelectorAll('.play-button, .vjs-big-play-button, .jw-display-icon-container, [class*="play"]');
                                for(var j=0; j<overlays.length; j++) { 
                                    try { overlays[j].click(); } catch(e) {} 
                                }
                                
                                // 3. Forçar JWPlayer se existir
                                if (window.jwplayer && typeof window.jwplayer === 'function') {
                                    try {
                                        var players = document.querySelectorAll('[id*="player"]');
                                        for(var k=0; k<players.length; k++) {
                                            var playerId = players[k].id;
                                            if(playerId) {
                                                var player = window.jwplayer(playerId);
                                                if(player && player.play) {
                                                    player.setMute(true);
                                                    player.play().catch(function(e){});
                                                }
                                            }
                                        }
                                    } catch(e) {}
                                }
                            }

                            var interval = setInterval(function() {
                                attempts++;
                                tryPlayVideo();
                                
                                var result = '';
                                
                                // A. Procurar em elementos video
                                var videos = document.querySelectorAll('video');
                                for (var i = 0; i < videos.length; i++) {
                                    var video = videos[i];
                                    if (video.src && video.src.startsWith('http')) {
                                        result = video.src;
                                        break;
                                    }
                                    if (video.currentSrc && video.currentSrc.startsWith('http')) {
                                        result = video.currentSrc;
                                        break;
                                    }
                                }
                                
                                // B. Procurar em elementos source
                                if (!result) {
                                    var sources = document.querySelectorAll('source[src]');
                                    for (var j = 0; j < sources.length; j++) {
                                        var src = sources[j].src;
                                        if (src && (src.includes('.m3u8') || src.includes('.mp4') || src.includes('googleapis') || src.includes('sssrr.org') || src.includes('iamcdn.net') || src.includes('valenium.shop'))) {
                                            result = src;
                                            break;
                                        }
                                    }
                                }
                                
                                // C. Procurar variáveis globais comuns
                                if (!result) {
                                    var globals = ['videoUrl', 'playlistUrl', 'source', 'file', 'src', 'url', 'config', 'playerConfig', 'sources'];
                                    for (var k = 0; k < globals.length; k++) {
                                        var val = window[globals[k]];
                                        if (val) {
                                            if (typeof val === 'string' && val.startsWith('http')) {
                                                result = val; break;
                                            } else if (typeof val === 'object') {
                                                if (val.file) { result = val.file; break; }
                                                if (Array.isArray(val) && val.length > 0) {
                                                    result = val[0].file || val[0].src || val[0].url;
                                                    if (result) break;
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                // D. Procurar em jwplayer diretamente
                                if (!result && window.jwplayer) {
                                    try {
                                        var jw = window.jwplayer();
                                        if (jw && jw.getPlaylistItem) {
                                            var item = jw.getPlaylistItem();
                                            if (item && item.file) result = item.file;
                                        }
                                    } catch(e) {}
                                }

                                if (result && result.length > 0 && result.startsWith('http')) {
                                    clearInterval(interval);
                                    resolve(result);
                                } else if (attempts >= maxAttempts) {
                                    clearInterval(interval);
                                    resolve('');
                                }
                            }, 100);
                        });
                    })()
                """.trimIndent()

                // URL Interception - v106: Padrões melhorados baseados em Playwright
                // Playwright capturou: storage.googleapis.com/mediastorage/.../81347747.mp4
                val resolver = WebViewResolver(
                    interceptUrl = Regex("""\.mp4|\.m3u8|storage\.googleapis\.com|mediastorage|googlevideo\.com|cloudatacdn\.com|abyss\.to|sssrr\.org|iamcdn\.net|valenium\.shop|/hls/|/video/|\.txt$"""),
                    script = captureScript,
                    scriptCallback = { result ->
                        if (result.isNotEmpty() && result.startsWith("http")) {
                            ErrorLogger.d(TAG, "JS Capture Success", mapOf("URL" to result))
                        }
                    },
                    timeout = 20_000L // v106: Aumentado para 20s - Playwright precisou de ~10s
                )

                // Configurar headers robustos (v101) - MATCH EXATO COM LOGS
                val headers = HeadersBuilder.playerEmbed(url)
                
                ErrorLogger.d(TAG, "Iniciando captura WebView (v101)", mapOf(
                    "Target" to url,
                    "UA" to (headers["User-Agent"] ?: "N/A"),
                    "Referer" to (headers["Referer"] ?: "N/A")
                ))

                // Executar WebView request com headers v101
                val response = app.get(
                    url, 
                    headers = headers, 
                    interceptor = resolver
                )
                
                val captured = response.url
                
                // Sucesso se capturou um vídeo ou chegou em um host final válido
                val isVideo = captured.contains(".mp4") || captured.contains(".m3u8") || 
                             captured.contains("googleapis") || captured.contains("cloudatacdn") ||
                             captured.contains("iamcdn.net") || captured.contains("sssrr.org") ||
                             captured.contains("valenium.shop") ||
                             captured.contains("master.txt")
                             
                val isHost = captured.contains("abyss.to")

                if (isVideo || isHost) {
                    // 3. DETECTAR QUALIDADE
                    val quality = QualityDetector.detectFromUrl(captured)
                    ErrorLogger.logQualityDetection(captured, quality, "URL")
                    
                    // 4. SALVAR NO CACHE
                    VideoUrlCache.put(url, captured, quality, name)
                    
                    // 5. INVOCAR CALLBACK
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name ${QualityDetector.getQualityLabel(quality)}",
                            url = captured,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = url
                            this.quality = quality
                        }
                    )
                    
                    // Log de sucesso
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = true,
                        videoUrl = captured,
                        quality = quality
                    )
                    
                    ErrorLogger.logPerformance("PlayerEmbedAPI Extraction", 
                        System.currentTimeMillis() - startTime,
                        mapOf("Quality" to QualityDetector.getQualityLabel(quality))
                    )
                } else {
                    val error = Exception("Falha ao interceptar URL de vídeo. Final: $captured")
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = false,
                        error = error
                    )
                    throw error
                }

            }.getOrElse { error ->
                if (attempt < 2) {
                    ErrorLogger.logRetry(
                        operation = "PlayerEmbedAPI Extraction",
                        attempt = attempt,
                        maxAttempts = 2,
                        nextDelayMs = RetryHelper.calculateDelay(attempt),
                        error = error
                    )
                } else {
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = false,
                        error = error
                    )
                }
                throw error
            }
        }
    }
}
