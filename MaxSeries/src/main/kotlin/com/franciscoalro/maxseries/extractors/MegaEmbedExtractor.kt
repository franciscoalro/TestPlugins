package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.JsUnpacker
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log
import org.json.JSONObject

/**
 * MegaEmbed Extractor para CloudStream
 * 
 * Fluxo de extração:
 * 1. Extrair ID do hash da URL (megaembed.link/#ID)
 * 2. Chamar API /api/v1/info?id=ID
 * 3. Se API retornar dados criptografados, usar WebView como fallback
 * 4. Retornar ExtractorLink com m3u8/mp4
 */
class MegaEmbedExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractor"
        private const val API_ENDPOINT = "/api/v1/info"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        // Domínios conhecidos do MegaEmbed
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz",
            "megaembed.to"
        )
        
        fun canHandle(url: String): Boolean {
            return DOMAINS.any { url.contains(it, ignoreCase = true) }
        }
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "Extraindo: $url")
        
        // Extrair ID do hash
        val videoId = extractVideoId(url)
        if (videoId.isNullOrEmpty()) {
            Log.e(TAG, "ID não encontrado na URL: $url")
            return
        }
        
        Log.d(TAG, "Video ID: $videoId")
        
        // Tentar método 1: API direta
        if (tryApiExtraction(videoId, url, callback)) {
            return
        }
        
        // Tentar método 2: Parse HTML direto
        if (tryHtmlExtraction(url, callback)) {
            return
        }
        
        // Fallback: WebView
        tryWebViewExtraction(url, callback)
    }

    /**
     * Extrai o ID do vídeo da URL
     * Formatos suportados:
     * - megaembed.link/#ID
     * - megaembed.link/?v=ID
     * - megaembed.link/embed/ID
     */
    private fun extractVideoId(url: String): String? {
        return when {
            url.contains("#") -> url.substringAfter("#").takeIf { it.isNotEmpty() }
            url.contains("?v=") -> Regex("[?&]v=([^&]+)").find(url)?.groupValues?.get(1)
            url.contains("/embed/") -> url.substringAfter("/embed/").substringBefore("?")
            else -> null
        }
    }

    /**
     * Método 1: Tentar extrair via API JSON
     */
    private suspend fun tryApiExtraction(
        videoId: String,
        originalUrl: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            val apiUrl = "$mainUrl$API_ENDPOINT?id=$videoId"
            Log.d(TAG, "Chamando API: $apiUrl")
            
            val response = app.get(
                apiUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to originalUrl,
                    "Accept" to "application/json",
                    "Origin" to mainUrl
                )
            )
            
            if (!response.isSuccessful) {
                Log.w(TAG, "API retornou ${response.code}")
                return false
            }
            
            val json = response.text
            Log.d(TAG, "API Response: ${json.take(500)}")
            
            // Tentar parsear JSON
            val jsonObj = JSONObject(json)
            
            // Procurar URL do vídeo em campos comuns
            val videoUrl = findVideoUrlInJson(jsonObj)
            
            if (!videoUrl.isNullOrEmpty()) {
                Log.d(TAG, "URL encontrada via API: $videoUrl")
                emitExtractorLink(videoUrl, originalUrl, callback)
                return true
            }
            
            // Se tiver dados criptografados, logar para análise
            if (jsonObj.has("data") || jsonObj.has("encrypted")) {
                Log.w(TAG, "API retornou dados criptografados - necessário WebView")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro na API: ${e.message}")
        }
        
        return false
    }

    /**
     * Procura URL de vídeo em objeto JSON
     */
    private fun findVideoUrlInJson(json: JSONObject): String? {
        val possibleKeys = listOf(
            "file", "url", "source", "src", "stream", "video",
            "hls", "m3u8", "mp4", "link", "playUrl", "videoUrl"
        )
        
        for (key in possibleKeys) {
            if (json.has(key)) {
                val value = json.optString(key)
                if (isValidVideoUrl(value)) {
                    return value
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
                        val url = source.optString("file") 
                            ?: source.optString("src")
                            ?: source.optString("url")
                        if (isValidVideoUrl(url)) {
                            return url
                        }
                    }
                }
            }
        }
        
        return null
    }

    /**
     * Método 2: Tentar extrair via HTML parsing
     */
    private suspend fun tryHtmlExtraction(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml"
                )
            )
            
            val html = response.text
            
            // Procurar URLs de vídeo no HTML/JS
            val patterns = listOf(
                Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""source:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""src:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""["'](https?://[^"']+\.m3u8[^"']*)["']"""),
                Regex("""["'](https?://[^"']+\.mp4[^"']*)["']"""),
                Regex("""hls:\s*["']([^"']+)["']"""),
                Regex("""playUrl:\s*["']([^"']+)["']""")
            )
            
            for (pattern in patterns) {
                val match = pattern.find(html)
                if (match != null) {
                    val videoUrl = match.groupValues[1]
                    if (isValidVideoUrl(videoUrl)) {
                        Log.d(TAG, "URL encontrada via HTML: $videoUrl")
                        emitExtractorLink(videoUrl, url, callback)
                        return true
                    }
                }
            }
            
            // Tentar desempacotar JavaScript P.A.C.K.E.R.
            val packed = getPackedCode(html)
            if (!packed.isNullOrEmpty()) {
                val unpacked = JsUnpacker(packed).unpack() ?: ""
                if (unpacked.isNotEmpty()) {
                    for (pattern in patterns) {
                        val match = pattern.find(unpacked)
                        if (match != null) {
                            val videoUrl = match.groupValues[1]
                            if (isValidVideoUrl(videoUrl)) {
                                Log.d(TAG, "URL encontrada via unpack: $videoUrl")
                                emitExtractorLink(videoUrl, url, callback)
                                return true
                            }
                        }
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no HTML parsing: ${e.message}")
        }
        
        return false
    }
    
    /**
     * Extrai código P.A.C.K.E.R. do HTML
     */
    private fun getPackedCode(html: String): String? {
        return Regex("""eval\(function\(p,a,c,k,e,[dr]\).*?\)\)""", RegexOption.DOT_MATCHES_ALL)
            .find(html)?.value
    }

    /**
     * Método 3: WebView como fallback final
     */
    private suspend fun tryWebViewExtraction(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            Log.d(TAG, "Usando WebView para: $url")
            
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';
                            
                            // Tentar capturar do player VidStack
                            if (window.player && window.player.src) result = window.player.src;
                            
                            // Tentar capturar de elemento video
                            if (!result) {
                                var video = document.querySelector('video');
                                if (video && video.src) result = video.src;
                            }
                            
                            if (!result) {
                                var source = document.querySelector('video source');
                                if (source && source.src) result = source.src;
                            }
                            
                            // Tentar capturar de HLS.js
                            if (!result && window.hls && window.hls.url) result = window.hls.url;
                            
                            if (result && result.length > 0) {
                                clearInterval(interval);
                                resolve(result);
                            } else if (attempts > 50) { // 5s timeout
                                clearInterval(interval);
                                resolve('');
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = Regex("""\.m3u8|\.mp4|master\.txt|/hls/|/video/|/stream/"""),
                additionalUrls = listOf(Regex("""\.m3u8|\.mp4|\.ts""")),
                useOkhttp = false,
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"") {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "WebView capturou: $capturedUrl")
                    }
                },
                timeout = 30_000L
            )
            
            val response = app.get(url, interceptor = resolver)
            val interceptedUrl = response.url
            
            val videoUrl = when {
                isValidVideoUrl(interceptedUrl) -> interceptedUrl
                !capturedUrl.isNullOrEmpty() && isValidVideoUrl(capturedUrl!!) -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d(TAG, "WebView extraiu: $videoUrl")
                emitExtractorLink(videoUrl, url, callback)
                return true
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no WebView: ${e.message}")
        }
        
        return false
    }

    /**
     * Emite ExtractorLink para o CloudStream
     */
    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        if (videoUrl.contains(".m3u8")) {
            // HLS - usar M3u8Helper para múltiplas qualidades
            M3u8Helper.generateM3u8(name, videoUrl, referer).forEach(callback)
        } else {
            // MP4 direto
            callback(
                newExtractorLink(
                    name,
                    name,
                    videoUrl
                ) {
                    this.referer = referer
                    this.quality = Qualities.Unknown.value
                }
            )
        }
    }


    /**
     * Valida se é uma URL de vídeo válida
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        return url.startsWith("http") && 
               (url.contains(".m3u8") || url.contains(".mp4") || 
                url.contains("/hls/") || url.contains("/video/"))
    }

}
