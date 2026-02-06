package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import org.json.JSONObject
import org.json.JSONArray
import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache
import com.franciscoalro.maxseries.crypto.AesCtrDecryptor
import com.franciscoalro.maxseries.network.CDNConstructor
import com.franciscoalro.maxseries.session.SessionManager
import com.franciscoalro.maxseries.session.SessionManager.Companion.BYPASS_HEADERS

/**
 * PlayerEmbedAPI Extractor v8.7 - PURE HTTP + AES + CDN + SESSION
 * 
 * NOVO na v8.7:
 * - 💾 Session Manager - Cache persistente de sessões
 * - 🔄 Renovação automática de tokens expirados
 * - ⏰ TTL configurável por URL
 * 
 * NOVO na v8.6:
 * - 🏗️ CDN Construction - Constrói URLs offline via fuzzing
 * - 🔐 AES-CTR Decryption via engenharia reversa  
 * - ⚡ Extração em ~50-100ms (sem WebView)
 * - 🎯 Múltiplas CDNs: SSSRR, Marvella, GCS, CloudAta
 * 
 * MÉTODOS DE EXTRAÇÃO (ordem de prioridade):
 * 1. Cache Check (Session Manager) ← NOVO v8.7
 * 2. AES-CTR Decryption - Decripta campo 'media' criptografado
 * 3. CDN Construction - Constrói URLs CDN offline
 * 4. JWPlayer Setup Parsing - Extrai configuração do player
 * 5. Direct Regex - Busca padrões de URL conhecidos
 * 6. API Endpoint Discovery - Descobre endpoints
 * 
 * @author MaxSeries Team
 * @version 8.7
 * @since 2026-02-03
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

        // Extensões que NÃO são vídeo e devem ser bloqueadas
        private val NON_VIDEO_EXTENSIONS = listOf(
            ".js",
            ".css",
            ".html",
            ".woff",
            ".woff2",
            ".ttf",
            ".svg",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp"
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
        Log.wtf(TAG, "=== PlayerEmbedAPI v8.7 - Session + AES + CDN ===")
        Log.d(TAG, "URL: $url")
        
        // ═══════════════════════════════════════════════════════════════════
        // NOVO v8.7: FASE 0 - Verificar Cache de URL
        // ═══════════════════════════════════════════════════════════════════
        val cached = VideoUrlCache.get(url)
        if (cached != null && !cached.isExpired()) {
            Log.d(TAG, "✅ Cache HIT - returning cached URL")
            if (!isValidVideoUrl(cached.url)) {
                Log.w(TAG, "⚠️ Cached URL invalid, clearing cache entry")
                VideoUrlCache.remove(url)
            } else {
                try {
                    emitLink(cached.url, cached.quality, callback, isCached = true)
                    return
                } catch (e: Exception) {
                    Log.e(TAG, "❌ Cache emit failed, clearing entry: ${e.message}", e)
                    VideoUrlCache.remove(url)
                }
            }
        }
        
        try {
            // ═══════════════════════════════════════════════════════════════════
            // NOVO v8.7: Obter sessão válida
            // ═══════════════════════════════════════════════════════════════════
            val domain = "playerembedapi.link"
            val sessionHeaders = headers + BYPASS_HEADERS
            
            // FASE 1: Obter HTML com sessão
            val startTime = System.currentTimeMillis()
            val response = app.get(url, headers = sessionHeaders)
            val html = response.text
            val fetchTime = System.currentTimeMillis() - startTime
            
            Log.d(TAG, "📄 HTML fetched in ${fetchTime}ms (${html.length} bytes) with session")
            
            // ═══════════════════════════════════════════════════════════════════
            // FASE 2: AES-CTR Decryption (Prioridade Máxima)
            // ═══════════════════════════════════════════════════════════════════
            extractViaAesDecryption(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅✅✅ SUCCESS via AES-CTR Decryption ✅✅✅")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback, method = "AES-CTR")
                return
            }
            
            // ═══════════════════════════════════════════════════════════════════
            // NOVO v8.6: FASE 3 - CDN Construction
            // ═══════════════════════════════════════════════════════════════════
            extractViaCDNConstruction(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅✅✅ SUCCESS via CDN Construction (v8.6) ✅✅✅")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback, method = "CDN")
                return
            }
            
            // FASE 4: Método 1 - JWPlayer Setup
            extractFromJWPlayerSetup(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via JWPlayer Setup")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback, method = "JWPlayer")
                return
            }
            
            // FASE 4: Método 2 - Regex Direto
            extractViaRegex(html)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via Direct Regex")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback, method = "Regex")
                return
            }
            
            // FASE 5: Método 3 - API Endpoints
            extractViaAPI(html, url)?.let { videoUrl ->
                Log.wtf(TAG, "✅ SUCCESS via API Discovery")
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                emitLink(videoUrl, quality, callback, method = "API")
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
     * ═══════════════════════════════════════════════════════════════════════════
     * NOVO MÉTODO v8.5: AES-CTR Decryption
     * ═══════════════════════════════════════════════════════════════════════════
     * 
     * Decripta o campo 'media' criptografado usando AES-CTR.
     * Baseado em engenharia reversa do código JavaScript SoTrym().
     * 
     * Fluxo:
     * 1. Extrair campo 'datas' em base64 do HTML
     * 2. Decodificar para JSON
     * 3. Extrair slug, md5_id, user_id, media (criptografado)
     * 4. Derivar chave AES das credenciais
     * 5. Decriptar campo 'media' com AES-CTR
     * 6. Extrair URL do vídeo do JSON resultante
     */
    private fun extractViaAesDecryption(html: String): String? {
        Log.d(TAG, "[Method AES-CTR v8.5] Trying AES-CTR decryption...")
        
        val startTime = System.currentTimeMillis()
        
        return try {
            // Usar o novo AesCtrDecryptor
            val videoUrl = AesCtrDecryptor.extractVideoUrl(html)
            
            if (videoUrl != null) {
                val duration = System.currentTimeMillis() - startTime
                Log.d(TAG, "  ✓ AES-CTR decryption successful in ${duration}ms")
                videoUrl
            } else {
                Log.d(TAG, "  ✗ AES-CTR decryption failed (all key strategies failed)")
                null
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "  ✗ AES-CTR error: ${e.message}")
            null
        }
    }
    
    /**
     * ═══════════════════════════════════════════════════════════════════════════
     * NOVO MÉTODO v8.6: CDN Construction
     * ═══════════════════════════════════════════════════════════════════════════
     * 
     * Constrói URLs CDN a partir de padrões descobertos via fuzzing.
     * Permite extração offline sem necessidade de decriptação ou WebView.
     * 
     * CDNs Suportados:
     * - SSSRR (PlayerEmbedAPI): https://{slug}.sssrr.org/sora/{md5_id}/
     * - Marvella (MegaEmbed): https://{shard}.{domain}/v4/{shard}/{video_id}/
     * - Google Cloud Storage: https://storage.googleapis.com/...
     * 
     * Fluxo:
     * 1. Extrair slug/md5_id do HTML
     * 2. Construir múltiplas URLs candidatas
     * 3. Validar URLs em paralelo
     * 4. Retornar primeira URL válida
     */
    private suspend fun extractViaCDNConstruction(html: String): String? {
        Log.d(TAG, "[Method CDN v8.6] Trying CDN construction...")
        
        val startTime = System.currentTimeMillis()
        
        return try {
            // Usar CDNConstructor para construir e validar
            val result = CDNConstructor.constructAndValidate(
                html = html,
                maxConcurrent = 3,  // Limitar para não sobrecarregar
                timeoutMs = 3000
            )
            
            if (result?.validUrl != null) {
                val duration = System.currentTimeMillis() - startTime
                Log.d(TAG, "  ✓ CDN construction successful in ${duration}ms")
                result.validUrl
            } else {
                Log.d(TAG, "  ✗ CDN construction failed (no valid URLs)")
                null
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "  ✗ CDN construction error: ${e.message}")
            null
        }
    }
    
    /**
     * MÉTODO 4: Extrai URL via regex de padrões conhecidos
     * 
     * Busca diretamente no HTML por URLs que correspondam a padrões de vídeo.
     */
    private fun extractViaRegex(html: String): String? {
        Log.d(TAG, "[Method 4] Trying direct regex extraction...")
        
        for ((index, pattern) in VIDEO_URL_PATTERNS.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val videoUrl = match.value
                    .replace("\\", "") // Remove escapes
                    .trim('"', '\'', ' ') // Remove quotes
                val lowerUrl = videoUrl.lowercase()
                if (NON_VIDEO_EXTENSIONS.any { lowerUrl.contains(it) }) {
                    Log.d(TAG, "  ✗ Ignored non-video URL via pattern ${index + 1}: ${videoUrl.take(60)}...")
                    continue
                }
                
                if (isValidVideoUrl(videoUrl)) {
                    Log.d(TAG, "  ✓ Found via pattern ${index + 1}: ${videoUrl.take(60)}...")
                    return videoUrl
                } else {
                    Log.d(TAG, "  ✗ Ignored non-video URL via pattern ${index + 1}: ${videoUrl.take(60)}...")
                }
            }
        }
        
        Log.d(TAG, "  ✗ No video URLs found via regex")
        return null
    }
    
    /**
     * MÉTODO 5: Descobre e chama endpoints de API
     * 
     * Procura por chamadas fetch/ajax no JavaScript e tenta chamar os endpoints.
     */
    private suspend fun extractViaAPI(html: String, pageUrl: String): String? {
        Log.d(TAG, "[Method 5] Trying API endpoint discovery...")
        
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

        // Bloquear assets e arquivos não-vídeo
        for (ext in NON_VIDEO_EXTENSIONS) {
            if (lowerUrl.contains(ext)) return false
        }
        
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
        isCached: Boolean = false,
        method: String = "Pure"
    ) {
        if (!isValidVideoUrl(url)) {
            Log.d(TAG, "  ✗ emitLink blocked non-video URL: ${url.take(80)}")
            return
        }
        val type = if (url.contains(".m3u8", ignoreCase = true)) {
            ExtractorLinkType.M3U8
        } else {
            ExtractorLinkType.VIDEO
        }
        
        val qualityLabel = QualityDetector.getQualityLabel(quality)
        val sourceName = when {
            isCached -> "$name $qualityLabel (Cached)"
            method == "AES-CTR" -> "$name $qualityLabel 🔐 AES)"
            else -> "$name $qualityLabel ($method)"
        }
        
        callback.invoke(
            newExtractorLink(
                source = "${name}_${System.currentTimeMillis() % 10000}",
                name = sourceName,
                url = url,
                type = type
            ) {
                val referer = headers["Referer"] ?: mainUrl
                this.referer = referer
                this.headers = if (headers.isEmpty()) mapOf("Referer" to referer) else headers
                this.quality = quality
            }
        )
        
        Log.d(TAG, "✓ Link emitted: $sourceName")
    }
}
