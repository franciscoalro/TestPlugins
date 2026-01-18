package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v3.4 - DIRECT HTML EXTRACTION (Jan 2026)
 * 
 * Baseado em análise Burp Suite (18/01/2026) e logs ADB v124.
 * 
 * PROBLEMA v124:
 * - WebView carrega página mas NÃO faz requisições para sssrr.org
 * - Timeout após 30s sem capturar nada
 * - JavaScript não executa ou é bloqueado
 * 
 * SOLUÇÃO v3.4:
 * - PRIORIDADE 1: Direct HTML/Regex extraction (SEM WebView)
 * - PRIORIDADE 2: AES-CTR decryption (já existente)
 * - PRIORIDADE 3: JsUnpacker (já existente)
 * - PRIORIDADE 4: WebView (fallback final)
 * 
 * Melhorias v3.4:
 * - Nova estratégia: Buscar URLs sssrr.org diretamente no HTML
 * - Padrões baseados em Burp Suite: sora/, future, .fd files
 * - WebView movido para último fallback
 * - Timeout reduzido para 20s (já que é fallback)
 * - Logs melhorados para debug
 * 
 * Analise completa: brcloudstream/PLAYEREMBEDAPI_BURP_ANALYSIS_V123.md
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
        
        Log.d(TAG, "=== PlayerEmbedAPI v3.4 - Direct API Extraction ===")
        Log.d(TAG, "URL: $url")
        
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
        
        // 2. DIRECT API EXTRACTION (v125 - Baseado em analise Postman)
        // Fluxo descoberto:
        // 1. GET playerembedapi.link/?v={videoId} -> HTML/JS
        // 2. Extrair: host sssrr.org + video id
        // 3. GET {host}.sssrr.org/?timestamp=&id={id} -> metadata
        // 4. Extrair URL final: {host}.sssrr.org/sora/{streamId}/{token}
        runCatching {
            Log.d(TAG, "[1/4] Tentando Direct API Extraction...")
            
            val response = app.get(url, headers = HeadersBuilder.playerEmbed(url))
            val html = response.text
            
            Log.d(TAG, "HTML baixado: ${html.length} chars")
            
            // Extrair host sssrr.org (ex: htm4jbxon18)
            val hostRegex = Regex("""https?://([a-z0-9]+)\.sssrr\.org""")
            val hostMatch = hostRegex.find(html)
            val sssrrHost = hostMatch?.groupValues?.get(1)
            
            // Extrair video ID (ex: qx5haz5c0wg)
            val idRegex = Regex("""id["\s:=]+["']?([a-z0-9]+)["']?""", RegexOption.IGNORE_CASE)
            val idMatch = idRegex.find(html)
            val videoId = idMatch?.groupValues?.get(1)
            
            if (sssrrHost != null && videoId != null) {
                Log.d(TAG, "Extraido - Host: $sssrrHost, VideoID: $videoId")
                
                // Fazer requisicao para API metadata
                val metadataUrl = "https://$sssrrHost.sssrr.org/?timestamp=&id=$videoId"
                Log.d(TAG, "Buscando metadata: $metadataUrl")
                
                val metadataResponse = app.get(
                    metadataUrl,
                    headers = mapOf(
                        "Referer" to "https://playerembedapi.link/",
                        "Origin" to "https://playerembedapi.link",
                        "User-Agent" to USER_AGENT,
                        "Accept" to "*/*"
                    )
                )
                
                val metadataText = metadataResponse.text
                Log.d(TAG, "Metadata recebida: ${metadataText.take(200)}...")
                
                // Extrair URL final do video (sora API ou direct file)
                val videoUrlRegex = Regex("""https?://[a-z0-9]+\.sssrr\.org/(?:sora/\d+/[A-Za-z0-9+/=]+|future|[\d/a-f]+\.fd)""")
                val videoUrlMatch = videoUrlRegex.find(metadataText)
                
                if (videoUrlMatch != null) {
                    val videoUrl = videoUrlMatch.value
                    Log.d(TAG, "Direct API capturou: $videoUrl")
                    
                    val quality = QualityDetector.detectFromUrl(videoUrl)
                    VideoUrlCache.put(url, videoUrl, quality, name)
                    
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name ${QualityDetector.getQualityLabel(quality)} (Direct)",
                            url = videoUrl,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = "https://playerembedapi.link/"
                            this.quality = quality
                        }
                    )
                    
                    Log.d(TAG, "Direct API Extraction: SUCESSO")
                    return
                }
            }
            
            Log.d(TAG, "Direct API: Nao encontrou host/id ou video URL")
        }.onFailure { e ->
            Log.e(TAG, "Direct API falhou: ${e.message}")
        }
        
        // 0. FETCH HTML (Shared) - v115: Detecção de 404
        val html = try {
            val response = app.get(url, headers = HeadersBuilder.playerEmbed(url))
            
            // v115: Falha rápida em 404 (vídeo não existe)
            if (response.code == 404) {
                ErrorLogger.w(TAG, "Vídeo não encontrado (404) - Pulando para próximo extractor", mapOf("URL" to url))
                return // Falha rápida, sem retry
            }
            
            // v115: Falha rápida em erros de servidor
            if (response.code >= 500) {
                ErrorLogger.w(TAG, "Servidor indisponível (${response.code}) - Pulando", mapOf("URL" to url))
                return
            }
            
            response.text
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
                 Log.d(TAG, "Objeto 'datas' encontrado!")
                 val mapper = JsonHelper.mapper
                 val datasNode = mapper.readTree(datasJson)
                 
                 val mediaEncrypted = datasNode.get("media")?.asText()
                 // user_id ou res_id
                 val userId = datasNode.get("user_id")?.asText() ?: datasNode.get("res_id")?.asText()
                 val slug = datasNode.get("slug")?.asText()
                 val md5Id = datasNode.get("md5_id")?.asText()
                 
                 if (!mediaEncrypted.isNullOrEmpty() && !userId.isNullOrEmpty() && !slug.isNullOrEmpty() && !md5Id.isNullOrEmpty()) {
                     Log.d(TAG, "Decriptando media... UserID: $userId, Slug: $slug")
                     val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaEncrypted, userId, slug, md5Id)
                     
                     if (decrypted != null) {
                         var found = false
                         
                         decrypted.hls?.let { hlsUrl ->
                             Log.d(TAG, "AES-CTR capturou HLS: $hlsUrl")
                             VideoUrlCache.put(url, hlsUrl, Qualities.Unknown.value, name)
                             callback.invoke(
                                newExtractorLink(name, "$name Auto (AES)", hlsUrl, ExtractorLinkType.VIDEO) {
                                    this.referer = url
                                }
                             )
                             found = true
                         }
                         
                         decrypted.mp4?.let { mp4Url ->
                              Log.d(TAG, "AES-CTR capturou MP4: $mp4Url")
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
                    Log.d(TAG, "Stealth descompactou script (${unpacked.length} chars)")
                    
                    val videoRegex = Regex("""https?://[^"'\s]+\.(?:m3u8|mp4|txt|sbs|online|cyou|googleapis|cloudatacdn|iamcdn|sssrr)[^"'\s]*""")
                    val videoMatch = videoRegex.find(unpacked)
                    
                    if (videoMatch != null) {
                        val videoUrl = videoMatch.value
                        Log.d(TAG, "Stealth capturou URL: $videoUrl")
                        
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
                        
                        Log.d(TAG, "HTML Regex capturou URL: $videoUrl")
                        
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
            Log.d(TAG, "HTML Regex: Nenhuma URL valida encontrada")
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
                            var maxAttempts = 80;
                            
                            function tryPlayVideo() {
                                var vids = document.getElementsByTagName('video');
                                for(var i=0; i<vids.length; i++){
                                    var v = vids[i];
                                    if(v.paused) {
                                        v.muted = true;
                                        v.play().catch(function(e){});
                                    }
                                }
                                
                                var overlays = document.querySelectorAll('.play-button, .vjs-big-play-button, .jw-display-icon-container, [class*="play"]');
                                for(var j=0; j<overlays.length; j++) { 
                                    try { overlays[j].click(); } catch(e) {} 
                                }
                                
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

                // URL Interception - v124: REGEX CORRIGIDO PARA SSSRR.ORG
                // Analise Burp Suite (18/01/2026) revelou que PlayerEmbedAPI usa sssrr.org, NAO googleapis.com!
                // Padroes descobertos: sora API, direct file, future endpoint
                // v124: Regex atualizado para capturar sssrr.org (CDN real)
                val resolver = WebViewResolver(
                    interceptUrl = Regex("""(?i)sssrr\.org/(?:sora/|future|\d+/[a-f0-9])"""),
                    script = captureScript,
                    scriptCallback = { result ->
                        if (result.isNotEmpty() && result.startsWith("http")) {
                            ErrorLogger.d(TAG, "JS Capture Success", mapOf("URL" to result))
                        }
                    },
                    timeout = 30_000L // 30s - v123: Aumentado de 15s
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
                // v124: Priorizar sssrr.org + FILTRO .JS
                val isJsFile = captured.endsWith(".js") || captured.contains(".js?") || 
                              captured.contains("core.bundle") || captured.contains("jwplayer")
                              
                val isVideo = !isJsFile && (
                             captured.contains("sssrr.org/sora/") || // PRIORIDADE 1 - v124
                             captured.contains("sssrr.org/future") || // PRIORIDADE 2 - v124
                             captured.contains(".sssrr.org/") && captured.contains(".fd") || // PRIORIDADE 3 - v124
                             captured.contains(".mp4") || captured.contains(".m3u8") || 
                             captured.contains("googleapis") || captured.contains("cloudatacdn") ||
                             captured.contains("iamcdn.net") || captured.contains("valenium.shop") ||
                             captured.contains("master.txt")
                )
                             
                val isHost = !isJsFile && captured.contains("abyss.to")

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
