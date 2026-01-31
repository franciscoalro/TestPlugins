package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import org.json.JSONObject
import org.json.JSONArray
import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache

/**
 * PlayerEmbedAPI Extractor v8 - PURE HTTP (NO WEBVIEW)
 * 
 * Elimina dependência de WebView através de engenharia reversa do fluxo JWPlayer.
 * 
 * MÉTODOS DE EXTRAÇÃO:
 * 1. JWPlayer Setup Parsing - Extrai configuração do player do HTML
 * 2. Direct Regex - Busca padrões de URL conhecidos
 * 3. API Endpoint Discovery - Descobre e chama endpoints de API
 * 
 * VANTAGENS vs V7 (WebView):
 * - ⚡ 10x mais rápido (sem inicialização de WebView)
 * - 🔋 Menor consumo de bateria (sem engine JS)
 * - 🎯 Mais confiável (sem race conditions de timing)
 * - 📦 Menor uso de memória
 * 
 * @author MaxSeries Team
 * @version 8.0
 * @since 2026-01-31
 */
class PlayerEmbedAPIExtractorV8 : ExtractorApi() {
    override val name = "PlayerEmbedAPI"
    override val mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "PlayerEmbedAPI-v8"
        
        // Padrões de URL de vídeo conhecidos
        private val VIDEO_URL_PATTERNS = listOf(
            Regex("""https?://[^"\s]+\.m3u8[^"\s]*"""),
            Regex("""https?://[^"\s]*cloudatacdn[^"\s]+"""),
            Regex("""https?://[^"\s]*googleapis[^"\s]+\.mp4"""),
            Regex("""https?://[^"\s]*sssrr[^"\s]+"""),
            Regex("""https?://[^"\s]*storage\.googleapis[^"\s]+"""),
            // CDNs populares
            Regex("""https?://[^"\s]*akamaized\.net[^"\s]+"""),        // Akamai CDN
            Regex("""https?://[^"\s]*cloudfront\.net[^"\s]+"""),       // AWS CloudFront
            Regex("""https?://[^"\s]*fastly\.net[^"\s]+"""),           // Fastly
            Regex("""https?://[^"\s]*bunnycdn\.com[^"\s]+"""),         // BunnyCDN
            Regex("""https?://[^"\s]*cdn77\.org[^"\s]+"""),            // CDN77
            Regex("""https?://[^"\s]*mp4[^"\s]*"""),                    // MP4 direto
            Regex("""https?://[^"\s]*\.ts[^"\s]*""")                    // Transport Stream
        )
    }

    private val headers = mapOf(
        "Referer" to "$mainUrl/",
        "Origin" to mainUrl,
        "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.wtf(TAG, "=== PlayerEmbedAPI v8.0 - Pure HTTP Extraction ===")
        Log.d(TAG, "URL: $url")
        
        // Verificar cache primeiro
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "✅ Cache HIT - returning cached URL")
            emitLink(cached.url, cached.quality, callback, isCached = true)
            return
        }
        
        try {
            // FASE 1: Obter HTML
            val startTime = System.currentTimeMillis()
            val response = app.get(url, headers = headers)
            val html = response.text
            val fetchTime = System.currentTimeMillis() - startTime
            
            Log.d(TAG, "📄 HTML fetched in ${fetchTime}ms (${html.length} bytes)")
            
            // FASE 2: Método 1 - JWPlayer Setup
            extractFromJWPlayerSetup(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via JWPlayer Setup")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback)
                return
            }
            
            // FASE 3: Método 2 - Regex Direto
            extractViaRegex(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via Direct Regex")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback)
                return
            }
            
            // FASE 4: Método 3 - API Endpoints
            extractViaAPI(html, url)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via API Discovery")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback)
                return
            }
            
            Log.e(TAG, "❌ All extraction methods failed")
            
            // Debug: Salvar HTML para análise
            if (html.length < 10000) {
                Log.d(TAG, "HTML Preview: ${html.take(500)}...")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Error: ${e.message}", e)
        }
    }
    
    /**
     * MÉTODO 1: Extrai URL do setup do JWPlayer no HTML
     * 
     * Procura por padrões como:
     * jwplayer('player').setup({ file: 'https://...' })
     * jwplayer('player').setup({ sources: [{ file: 'https://...' }] })
     */
    private fun extractFromJWPlayerSetup(html: String): String? {
        Log.d(TAG, "[Method 1] Trying JWPlayer setup extraction...")
        
        // Regex: jwplayer('player').setup({...})
        val setupRegex = Regex(
            """jwplayer\s*\(\s*['"]?[\w_-]+['"]?\s*\)\s*\.setup\s*\(\s*(\{[\s\S]*?\})\s*\)""",
            setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE)
        )
        
        val match = setupRegex.find(html)
        if (match == null) {
            Log.d(TAG, "  ✗ No JWPlayer setup found")
            return null
        }
        
        try {
            var setupJson = match.groupValues[1]
            
            // Limpar JSON para parsing
            setupJson = setupJson
                .replace(Regex("""//.*?\n"""), "") // Remove comentários
                .replace(Regex(""",\s*}"""), "}") // Remove vírgulas extras
                .replace(Regex(""",\s*]"""), "]")
            
            // Tentar parsear como JSON
            val config = JSONObject(setupJson)
            
            // Tentar 'file' direto
            if (config.has("file")) {
                val fileUrl = config.getString("file")
                if (isValidVideoUrl(fileUrl)) {
                    Log.d(TAG, "  ✓ Found 'file': ${fileUrl.take(60)}...")
                    return fileUrl
                }
            }
            
            // Tentar 'sources' array
            if (config.has("sources")) {
                val sources = config.getJSONArray("sources")
                for (i in 0 until sources.length()) {
                    val source = sources.getJSONObject(i)
                    if (source.has("file")) {
                        val fileUrl = source.getString("file")
                        if (isValidVideoUrl(fileUrl)) {
                            Log.d(TAG, "  ✓ Found in 'sources[${i}]': ${fileUrl.take(60)}...")
                            return fileUrl
                        }
                    }
                }
            }
            
        } catch (e: org.json.JSONException) {
            Log.d(TAG, "  ⚠ JSON parse failed, trying regex fallback...")
            
            // Fallback: Regex para extrair 'file' sem parsing JSON
            val fileRegex = Regex("""['"]file['"]\s*:\s*['"]([^'"]+)['"]""")
            val fileMatch = fileRegex.find(match.groupValues[1])
            if (fileMatch != null) {
                val fileUrl = fileMatch.groupValues[1]
                if (isValidVideoUrl(fileUrl)) {
                    Log.d(TAG, "  ✓ Found via regex fallback: ${fileUrl.take(60)}...")
                    return fileUrl
                }
            }
        } catch (e: Exception) {
            Log.d(TAG, "  ✗ Error: ${e.message}")
        }
        
        Log.d(TAG, "  ✗ No valid URL in JWPlayer setup")
        return null
    }
    
    /**
     * MÉTODO 2: Extrai URL via regex de padrões conhecidos
     * 
     * Busca diretamente no HTML por URLs que correspondam a padrões de vídeo.
     */
    private fun extractViaRegex(html: String): String? {
        Log.d(TAG, "[Method 2] Trying direct regex extraction...")
        
        for ((index, pattern) in VIDEO_URL_PATTERNS.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val videoUrl = match.value
                    .replace("\\", "") // Remove escapes
                    .trim('"', '\'', ' ') // Remove quotes
                
                if (isValidVideoUrl(videoUrl)) {
                    Log.d(TAG, "  ✓ Found via pattern ${index + 1}: ${videoUrl.take(60)}...")
                    return videoUrl
                }
            }
        }
        
        Log.d(TAG, "  ✗ No video URLs found via regex")
        return null
    }
    
    /**
     * MÉTODO 3: Descobre e chama endpoints de API
     * 
     * Procura por chamadas fetch/ajax no JavaScript e tenta chamar os endpoints.
     */
    private suspend fun extractViaAPI(html: String, pageUrl: String): String? {
        Log.d(TAG, "[Method 3] Trying API endpoint discovery...")
        
        // Padrões de chamadas de API no JavaScript
        val apiPatterns = listOf(
            Regex("""fetch\s*\(\s*['"]([^'"]+)['"]"""),
            Regex("""\.get\s*\(\s*['"]([^'"]+)['"]"""),
            Regex("""\.post\s*\(\s*['"]([^'"]+)['"]"""),
            Regex("""url\s*:\s*['"]([^'"]+)['"]"""),
            Regex("""ajax\s*\(\s*\{[^}]*url\s*:\s*['"]([^'"]+)['"]""", RegexOption.DOT_MATCHES_ALL),
            // Padrões adicionais
            Regex("""axios\.(?:get|post)\s*\(\s*['"]([^'"]+)['"]"""),  // axios
            Regex("""XMLHttpRequest.*?open\s*\(\s*['"][^'"]+['"]\s*,\s*['"]([^'"]+)['"]""", RegexOption.DOT_MATCHES_ALL),  // XHR
            Regex("""\.ajax\s*\(\s*\{[^}]*url\s*:\s*['"]([^'"]+)['"]""", RegexOption.DOT_MATCHES_ALL)  // jQuery
        )
        
        val apiUrls = mutableSetOf<String>()
        
        for (pattern in apiPatterns) {
            val matches = pattern.findAll(html)
            for (match in matches) {
                val apiPath = match.groupValues[1]
                
                // Filtrar apenas APIs relevantes
                if (apiPath.contains("api", ignoreCase = true) ||
                    apiPath.contains("playlist", ignoreCase = true) ||
                    apiPath.contains("source", ignoreCase = true) ||
                    apiPath.contains("video", ignoreCase = true)) {
                    apiUrls.add(apiPath)
                }
            }
        }
        
        if (apiUrls.isEmpty()) {
            Log.d(TAG, "  ✗ No API endpoints found")
            return null
        }
        
        Log.d(TAG, "  Found ${apiUrls.size} potential API endpoints")
        
        for (apiPath in apiUrls) {
            // Construir URL completa
            val apiUrl = if (apiPath.startsWith("http")) {
                apiPath
            } else if (apiPath.startsWith("/")) {
                "$mainUrl$apiPath"
            } else {
                "$mainUrl/$apiPath"
            }
            
            try {
                Log.d(TAG, "  Trying: ${apiUrl.take(60)}...")
                val apiResponse = app.get(apiUrl, headers = headers, timeout = 5L)
                
                // Tentar parsear como JSON
                try {
                    val json = JSONObject(apiResponse.text)
                    val videoUrl = findVideoUrlInJson(json)
                    if (videoUrl != null) {
                        Log.d(TAG, "  ✓ Found in JSON response: ${videoUrl.take(60)}...")
                        return videoUrl
                    }
                } catch (e: org.json.JSONException) {
                    // Não é JSON, tentar como texto
                }
                
                // Tentar buscar URL diretamente no texto
                for (pattern in VIDEO_URL_PATTERNS) {
                    val match = pattern.find(apiResponse.text)
                    if (match != null) {
                        val videoUrl = match.value.trim('"', '\'', ' ')
                        if (isValidVideoUrl(videoUrl)) {
                            Log.d(TAG, "  ✓ Found in text response: ${videoUrl.take(60)}...")
                            return videoUrl
                        }
                    }
                }
                
            } catch (e: Exception) {
                Log.d(TAG, "  ✗ API call failed: ${e.message}")
                continue
            }
        }
        
        Log.d(TAG, "  ✗ No video URLs in API responses")
        return null
    }
    
    /**
     * Resolve URL relativa para absoluta
     */
    private fun resolveUrl(path: String, baseUrl: String): String {
        return when {
            path.startsWith("http") -> path
            path.startsWith("//") -> "https:$path"
            path.startsWith("/") -> "$mainUrl$path"
            else -> "$baseUrl/$path"
        }
    }

    /**
     * Busca recursiva por URL de vídeo em estrutura JSON
     */
    private fun findVideoUrlInJson(json: JSONObject, depth: Int = 0): String? {
        if (depth > 5) return null
        
        // Chaves comuns que podem conter URLs de vídeo
        val videoKeys = listOf("file", "url", "source", "src", "stream", "video", "playlist", "hls", "m3u8")
        
        for (key in videoKeys) {
            if (json.has(key)) {
                val value = json.get(key)
                if (value is String && isValidVideoUrl(value)) {
                    return value
                }
            }
        }
        
        // Busca recursiva em objetos aninhados
        for (key in json.keys()) {
            val value = json.get(key)
            
            when (value) {
                is JSONObject -> {
                    val result = findVideoUrlInJson(value, depth + 1)
                    if (result != null) return result
                }
                is JSONArray -> {
                    for (i in 0 until value.length()) {
                        val item = value.get(i)
                        if (item is JSONObject) {
                            val result = findVideoUrlInJson(item, depth + 1)
                            if (result != null) return result
                        }
                    }
                }
            }
        }
        
        return null
    }
    
    /**
     * Valida se a URL é um vídeo válido
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        if (url.length < 10) return false
        
        // Validar estrutura básica de URL
        val urlRegex = Regex("""^https?://[^\s/$.?#].[^\s]*$""", RegexOption.IGNORE_CASE)
        if (!urlRegex.matches(url)) return false
        
        val lowerUrl = url.lowercase()
        
        // Extensões e CDNs conhecidos
        return lowerUrl.contains(".m3u8") ||
               lowerUrl.contains(".mp4") ||
               lowerUrl.contains(".mkv") ||
               lowerUrl.contains(".webm") ||
               lowerUrl.contains(".mpd") ||
               lowerUrl.contains(".ts") ||
               lowerUrl.contains("cloudatacdn") ||
               lowerUrl.contains("googleapis") ||
               lowerUrl.contains("sssrr") ||
               lowerUrl.contains("akamaized") ||
               lowerUrl.contains("cloudfront") ||
               lowerUrl.contains("fastly") ||
               lowerUrl.contains("bunnycdn") ||
               lowerUrl.contains("cdn77")
    }
    
    /**
     * Emite link de vídeo para o callback
     */
    private suspend fun emitLink(
        url: String,
        quality: Int,
        callback: (ExtractorLink) -> Unit,
        isCached: Boolean = false
    ) {
        val type = if (url.contains(".m3u8", ignoreCase = true)) {
            ExtractorLinkType.M3U8
        } else {
            ExtractorLinkType.VIDEO
        }
        
        val qualityLabel = QualityDetector.getQualityLabel(quality)
        val sourceName = if (isCached) {
            "$name $qualityLabel (Cached)"
        } else {
            "$name $qualityLabel (Pure v8)"
        }
        
        callback.invoke(
            newExtractorLink(
                source = name,
                name = sourceName,
                url = url,
                type = type
            ) {
                this.referer = headers["Referer"]!!
                this.headers = headers
                this.quality = quality
            }
        )
        
        Log.d(TAG, "✓ Link emitted: $sourceName")
    }
}
