package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v3.7 - DIRECT BASE64 DECODE (Jan 2026)
 * 
 * v3.7 Changes (26 Jan 2026):
 * - 🚀 DECODE base64 diretamente do HTML!
 * - ⚡ Não precisa de WebView, clicks ou espera
 * - 🎯 Extrai `const datas = "base64..."` do código
 * - ✅ Decripta usando AES-CTR (já existente)
 * 
 * DESCOBERTA IMPORTANTE:
 * - PlayerEmbedAPI armazena dados do vídeo em base64 no HTML
 * - Formato: const datas = "eyJ...base64...";
 * - Contém: slug, md5_id, user_id, media (encriptado)
 * - Solução: Decodificar base64 + decriptar media = URL do vídeo!
 * 
 * SOLUÇÃO v3.7:
 * - PRIORIDADE 1: Direct Base64 Decode (NOVO! Mais rápido!)
 * - PRIORIDADE 2: Direct API Extraction
 * - PRIORIDADE 3: AES-CTR decryption (fallback)
 * - PRIORIDADE 4: JsUnpacker
 * - PRIORIDADE 5: HTML Regex fallback
 * 
 * Exemplo do código fonte:
 * const datas = "eyJzbHVnIjoia0JKTHR4Q0QzIiwibWQ1X2lkIjoyODkzMDY0NywidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6Ir...";
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
        
        // 1. DIRECT BASE64 DECODE (v3.7 - MELHOR SOLUÇÃO!)
        // PlayerEmbedAPI armazena dados do vídeo em base64 no HTML
        // Não precisa de WebView, clicks ou espera!
        runCatching {
            Log.d(TAG, "[1/5] Tentando Direct Base64 Decode...")
            
            // Buscar o base64 no HTML
            val base64Regex = Regex("""const datas = "([A-Za-z0-9+/=]+)";""")
            val base64Match = base64Regex.find(html)
            
            if (base64Match != null) {
                val base64Data = base64Match.groupValues[1]
                Log.d(TAG, "Base64 encontrado: ${base64Data.take(50)}...")
                
                try {
                    // Decodificar base64
                    val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
                    val decodedJson = String(decodedBytes, Charsets.UTF_8)
                    Log.d(TAG, "JSON decodificado: ${decodedJson.take(200)}...")
                    
                    // Parse JSON
                    val mapper = com.fasterxml.jackson.databind.ObjectMapper()
                    val dataNode = mapper.readTree(decodedJson)
                    
                    // Extrair media (está encriptado)
                    val mediaEncrypted = dataNode.get("media")?.asText()
                    val userId = dataNode.get("user_id")?.asText()
                    val slug = dataNode.get("slug")?.asText()
                    val md5Id = dataNode.get("md5_id")?.asText()
                    
                    if (!mediaEncrypted.isNullOrEmpty() && !userId.isNullOrEmpty() && 
                        !slug.isNullOrEmpty() && !md5Id.isNullOrEmpty()) {
                        
                        Log.d(TAG, "Decriptando media... UserID: $userId, Slug: $slug")
                        val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaEncrypted, userId, slug, md5Id)
                        
                        if (decrypted != null) {
                            var found = false
                            
                            decrypted.hls?.let { hlsUrl ->
                                Log.d(TAG, "Base64 Decode capturou HLS: $hlsUrl")
                                
                                val quality = QualityDetector.detectFromUrl(hlsUrl)
                                VideoUrlCache.put(url, hlsUrl, quality, name)
                                
                                callback.invoke(
                                    newExtractorLink(
                                        source = name,
                                        name = "$name ${QualityDetector.getQualityLabel(quality)} (Direct)",
                                        url = hlsUrl,
                                        type = ExtractorLinkType.VIDEO
                                    ) {
                                        this.referer = "https://playerembedapi.link/"
                                        this.quality = quality
                                    }
                                )
                                found = true
                            }
                            
                            decrypted.mp4?.let { mp4Url ->
                                Log.d(TAG, "Base64 Decode capturou MP4: $mp4Url")
                                
                                val quality = QualityDetector.detectFromUrl(mp4Url)
                                
                                callback.invoke(
                                    newExtractorLink(
                                        source = name,
                                        name = "$name MP4 ${QualityDetector.getQualityLabel(quality)} (Direct)",
                                        url = mp4Url,
                                        type = ExtractorLinkType.VIDEO
                                    ) {
                                        this.referer = "https://playerembedapi.link/"
                                        this.quality = quality
                                    }
                                )
                                found = true
                            }
                            
                            if (found) {
                                Log.d(TAG, "Base64 Decode: SUCESSO")
                                ErrorLogger.logPerformance("PlayerEmbedAPI Base64", 
                                    System.currentTimeMillis() - startTime)
                                return
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Erro ao decodificar base64: ${e.message}")
                }
            }
            
            Log.d(TAG, "Base64 Decode: Não encontrou dados")
        }.onFailure { e ->
            Log.e(TAG, "Base64 Decode falhou: ${e.message}")
        }
        
        // 2. DIRECT API EXTRACTION (v125 - Baseado em analise Postman)
        // Fluxo descoberto:
        // 1. GET playerembedapi.link/?v={videoId} -> HTML/JS
        // 2. Extrair: host sssrr.org + video id
        // 3. GET {host}.sssrr.org/?timestamp=&id={id} -> metadata
        // 4. Extrair URL final: {host}.sssrr.org/sora/{streamId}/{token}
        runCatching {
            Log.d(TAG, "[2/5] Tentando Direct API Extraction...")
            
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

        // 3. NATIVE DECRYPTION (v103 - AES-CTR)
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
        
        // 4. STEALTH FALLBACK (JsUnpacker)
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

        // 5. HTML REGEX FALLBACK (v104 - saimuelrepo pattern)
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

        // v3.5: Se WebView com overlay click não funcionou, falha rápido
        // Deixa outros extractors (MegaEmbed, MyVidPlay, DoodStream) tentarem
        
        Log.d(TAG, "PlayerEmbedAPI: Todas as técnicas falharam (incluindo WebView com overlay)")
        Log.d(TAG, "Tempo total: ${System.currentTimeMillis() - startTime}ms")
        
        // Não lançar exception - deixar outros extractors tentarem
        ErrorLogger.w(TAG, "PlayerEmbedAPI não conseguiu extrair", mapOf(
            "URL" to url,
            "Tempo" to "${System.currentTimeMillis() - startTime}ms"
        ))
    }
}
