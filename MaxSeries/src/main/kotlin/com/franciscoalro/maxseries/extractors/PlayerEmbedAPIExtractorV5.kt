package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import android.util.Log
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.*

/**
 * PlayerEmbedAPI Extractor v5.0 - Enhanced Detection & Security (Feb 2026)
 * 
 * v5.0 Changes:
 * - 🔒 SEGURANÇA: Removido logging de dados sensíveis (chaves, hashes)
 * - 🎯 DETECÇÃO: Mais padrões de URL de vídeo (Google Storage, CDN, etc.)
 * - 📺 QUALIDADES: Suporte a 360p, 480p, 720p, 1080p, 4K
 * - ⚡ PERFORMANCE: Regex compilados em companion object
 * - 🔄 FALLBACK: Sistema de fallback hierárquico mais robusto
 * - 🛡️ VALIDAÇÃO: Validação de URLs antes de retornar
 * - 🌐 DOMÍNIOS: Suporte a múltiplos domínios (sssrr, googleapis, cdns)
 */
class PlayerEmbedAPIExtractorV5 : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true
    
    fun canHandle(url: String): Boolean = Companion.canHandle(url)

    companion object {
        private const val TAG = "PlayerEmbedAPI-v5"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        private const val EXTRACTION_TIMEOUT_MS = 15000L
        
        // Regex compilados para melhor performance
        private val DATA_SOURCE_PATTERN = Regex("""data-source\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        private val DATA_SRC_PATTERN = Regex("""data-src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        private val HREF_PATTERN = Regex("""href\s*=\s*["']([^"']+playerembedapi[^"']*)["']""", RegexOption.IGNORE_CASE)
        private val IFRAME_SRC_PATTERN = Regex("""<iframe[^>]+src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        
        // Padrões para base64 'datas'
        private val BASE64_PATTERNS = listOf(
            Regex("""const\s+datas\s*=\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex("""var\s+datas\s*=\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex("""let\s+datas\s*=\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex("""datas\s*=\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex("""data[=:]\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex(""""(eyJ[A-Za-z0-9+/=]{10,})"""),
            Regex("""window\.__DATA__\s*=\s*"([A-Za-z0-9+/=]{10,})"""),
            Regex("""encryptedData\s*=\s*"([A-Za-z0-9+/=]{10,})""")
        )
        
        // Padrões de URL de vídeo - expandido
        private val VIDEO_URL_PATTERNS = listOf(
            // Google Cloud Storage
            Regex("""(https://storage\.googleapis\.com/[^"'<>\s]+\.mp4[^"'<>\s]*)"""),
            Regex("""(https://storage\.googleapis\.com/[^"'<>\s]+)"""),
            // SSSRR CDN
            Regex("""(https?://[^/]*sssrr\.org/[^"'<>\s]+\.mp4[^"'<>\s]*)"""),
            Regex("""(https?://[^/]*sssrr\.org/[^"'<>\s]+\.m3u8[^"'<>\s]*)"""),
            Regex("""(https?://[^/]*sssrr\.org/[^"'<>\s]+)"""),
            // Players de vídeo genéricos
            Regex("""["'](https?://[^"'<>]+\.mp4[^"'<>]*)["']"""),
            Regex("""["'](https?://[^"'<>]+\.m3u8[^"'<>]*)["']"""),
            Regex("""["'](https?://[^"'<>]+\.mkv[^"'<>]*)["']"""),
            Regex("""["'](https?://[^"'<>]+\.webm[^"'<>]*)["']"""),
            // JWPlayer / VideoJS
            Regex("""file\s*:\s*["']([^"']+)["']"""),
            Regex("""src\s*:\s*["']([^"']+)["']""")
        )
        
        // Mapeamento de res_id para qualidade
        private val RES_ID_QUALITY = mapOf(
            1 to Qualities.P360,
            2 to Qualities.P480,
            3 to Qualities.P720,
            4 to Qualities.P1080,
            5 to Qualities.P2160 // 4K
        )

        fun canHandle(url: String): Boolean {
            val lower = url.lowercase()
            return lower.contains("playerembedapi") || lower.contains("short.icu")
        }
        
        // Domínios permitidos para validação
        private val ALLOWED_VIDEO_DOMAINS = listOf(
            "googleapis.com",
            "sssrr.org",
            "cdn",
            "video",
            "stream",
            "media",
            "content"
        )
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        Log.wtf(TAG, "=== PlayerEmbedAPI v5.0 - Enhanced Detection ===")
        Log.d(TAG, "URL: $url")
        
        // 1. VERIFICAR CACHE
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "Cache HIT")
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)} (Cached)",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "https://playerembedapi.link/"
                    this.quality = cached.quality
                }
            )
            return
        }
        
        // 2. ESTRATÉGIA PRIMÁRIA: Extração via API (base64 + AES-CTR)
        try {
            val success = extractViaApi(url, referer, callback)
            if (success) {
                Log.wtf(TAG, "SUCESSO via API: ${System.currentTimeMillis() - startTime}ms")
                return
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via API falhou: ${e.message}")
        }
        
        // 3. ESTRATÉGIA SECUNDÁRIA: Extração via ShortIcu
        try {
            val success = extractViaShortIcu(url, referer, callback)
            if (success) {
                Log.wtf(TAG, "SUCESSO via ShortIcu: ${System.currentTimeMillis() - startTime}ms")
                return
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via ShortIcu falhou: ${e.message}")
        }
        
        // 4. ESTRATÉGIA TERCIÁRIA: Regex direto no HTML
        try {
            val success = extractViaRegexFallback(url, referer, callback)
            if (success) {
                Log.wtf(TAG, "SUCESSO via Regex: ${System.currentTimeMillis() - startTime}ms")
                return
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via Regex falhou: ${e.message}")
        }
        
        // 5. ESTRATÉGIA FINAL: WebView
        try {
            val success = extractViaWebView(url, referer, callback)
            if (success) {
                Log.wtf(TAG, "SUCESSO via WebView: ${System.currentTimeMillis() - startTime}ms")
                return
            }
        } catch (e: Exception) {
            Log.e(TAG, "Todas as estratégias falharam: ${e.message}")
        }
        
        Log.e(TAG, "FALHA: Nenhuma estratégia funcionou")
    }

    /**
     * Estratégia 1: Extração via API (base64 + AES-CTR)
     * Extrai dados criptografados do HTML, decodifica base64 e decripta AES-CTR
     */
    private suspend fun extractViaApi(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "[1/4] Tentando extração via API...")
        
        // Buscar HTML
        val html = try {
            val response = app.get(url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "en-US,en;q=0.5",
                    "Referer" to (referer ?: mainUrl)
                )
            )
            response.text
        } catch (e: Exception) {
            Log.e(TAG, "Erro no request: ${e.message}")
            return false
        }
        
        // Encontrar base64 'datas'
        val base64Data = findBase64Datas(html) ?: run {
            Log.w(TAG, "Não encontrou base64 'datas'")
            return false
        }
        
        return processBase64Data(base64Data, url, callback)
    }
    
    /**
     * Processa dados base64 e extrai URLs de vídeo
     */
    private suspend fun processBase64Data(
        base64Data: String,
        originalUrl: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            // Decodificar base64 -> bytes
            val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
            val decodedString = String(decodedBytes, Charsets.ISO_8859_1)
            
            // Extrair campos via regex
            val userId = USER_ID_PATTERN.find(decodedString)?.groupValues?.get(1)
            val slug = SLUG_PATTERN.find(decodedString)?.groupValues?.get(1)
            val md5Id = MD5_ID_PATTERN.find(decodedString)?.groupValues?.get(1)
            
            // Extrair campo 'media' criptografado
            val mediaMatch = MEDIA_PATTERN.find(decodedString)
            val mediaEscaped = mediaMatch?.groupValues?.get(1)
            
            if (userId == null || slug == null || md5Id == null || mediaEscaped == null) {
                Log.w(TAG, "Campos obrigatórios faltantes")
                return false
            }
            
            // Processar escapes JSON
            val mediaBytes = processJsonStringToBytes(mediaEscaped)
            
            // Decriptar com AES-CTR
            val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaBytes, userId, slug, md5Id)
            
            if (decrypted == null) {
                Log.w(TAG, "Falha na decriptação AES-CTR")
                return false
            }
            
            // Extrair e retornar URLs
            extractUrlsFromDecrypted(decrypted, originalUrl, callback)
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no processamento: ${e.message}")
            false
        }
    }
    
    /**
     * Extrai URLs do objeto decriptado
     */
    private suspend fun extractUrlsFromDecrypted(
        decrypted: PlayerEmbedMedia,
        originalUrl: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var foundAny = false
        
        // Extrair múltiplas qualidades do sources[]
        decrypted.sources?.let { sources ->
            sources.forEach { source ->
                val quality = when (source.label?.lowercase()) {
                    "360p" -> Qualities.P360
                    "480p" -> Qualities.P480
                    "720p" -> Qualities.P720
                    "1080p" -> Qualities.P1080
                    "4k", "2160p" -> Qualities.P2160
                    else -> Qualities.Unknown
                }
                
                if (isValidVideoUrl(source.file)) {
                    VideoUrlCache.put("${originalUrl}_${source.label}", source.file, quality.value, name)
                    
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name ${source.label ?: "Auto"}",
                            url = source.file,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = "https://playerembedapi.link/"
                            this.quality = quality.value
                        }
                    )
                    foundAny = true
                }
            }
        }
        
        // Fallback: HLS direto
        decrypted.hls?.let { hlsUrl ->
            if (isValidVideoUrl(hlsUrl)) {
                val quality = QualityDetector.detectFromUrl(hlsUrl)
                VideoUrlCache.put(originalUrl, hlsUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (HLS)",
                        url = hlsUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
        }
        
        // Fallback: MP4 direto
        decrypted.mp4?.let { mp4Url ->
            if (isValidVideoUrl(mp4Url)) {
                val quality = QualityDetector.detectFromUrl(mp4Url)
                VideoUrlCache.put(originalUrl, mp4Url, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (MP4)",
                        url = mp4Url,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
        }
        
        return foundAny
    }
    
    /**
     * Estratégia 2: Extração via ShortIcu
     */
    private suspend fun extractViaShortIcu(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "[2/4] Tentando extração via ShortIcu...")
        
        try {
            // Obter HTML do PlayerEmbedAPI
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                ),
                timeout = 15
            )
            
            val html = response.text
            
            // Extrair iframe short.icu
            val shortIcuUrl = extractShortIcuUrl(html) ?: return false
            
            Log.d(TAG, "ShortIcu URL encontrada: $shortIcuUrl")
            
            // Acessar short.icu
            val shortResponse = app.get(
                shortIcuUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to url,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                timeout = 15
            )
            
            val shortHtml = shortResponse.text
            
            // Extrair URL do vídeo
            val videoUrl = extractVideoUrlFromHtml(shortHtml) ?: return false
            
            Log.d(TAG, "Vídeo encontrado via ShortIcu: $videoUrl")
            
            if (isValidVideoUrl(videoUrl)) {
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (ShortIcu)",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = shortIcuUrl
                        this.quality = quality
                    }
                )
                return true
            }
            
            return false
        } catch (e: Exception) {
            Log.w(TAG, "Erro na extração ShortIcu: ${e.message}")
            return false
        }
    }

    /**
     * Estratégia 3: Regex direto no HTML
     */
    private suspend fun extractViaRegexFallback(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "[3/4] Tentando extração via Regex...")
        
        return try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl)
                ),
                timeout = 10
            )
            
            val html = response.text
            val videoUrl = extractVideoUrlFromHtml(html)
            
            if (videoUrl != null && isValidVideoUrl(videoUrl)) {
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (Regex)",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                true
            } else {
                false
            }
        } catch (e: Exception) {
            Log.w(TAG, "Erro no regex fallback: ${e.message}")
            false
        }
    }
    
    /**
     * Estratégia 4: WebView
     */
    private suspend fun extractViaWebView(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "[4/4] Tentando extração via WebView...")
        
        return try {
            val links = PlayerEmbedAPIWebViewExtractorV5().extractFromUrl(url, referer ?: url)
            
            if (links.isNotEmpty()) {
                links.forEach { callback(it) }
                true
            } else {
                false
            }
        } catch (e: Exception) {
            Log.w(TAG, "Erro no WebView: ${e.message}")
            false
        }
    }
    
    /**
     * Extrai URL do short.icu do HTML
     */
    internal fun extractShortIcuUrl(html: String): String? {
        val patterns = listOf(
            Regex("""<iframe[^>]+src\s*=\s*["'](https://short\.icu/[^"']+)["']"""),
            Regex("""src\s*=\s*["'](https://short\.icu/[^"']+)["']"""),
            Regex("""(https://short\.icu/[a-zA-Z0-9]+)""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                return match.groupValues[1]
            }
        }
        return null
    }

    internal fun detectQualityFromUrl(url: String): String {
        return when {
            url.contains("2160") || url.contains("4k", ignoreCase = true) -> "4K"
            url.contains("1080") -> "1080p"
            url.contains("720") -> "720p"
            url.contains("480") -> "480p"
            url.contains("360") -> "360p"
            else -> "HD"
        }
    }
    
    /**
     * Extrai URL de vídeo do HTML usando múltiplos padrões
     */
    internal fun extractVideoUrlFromHtml(html: String): String? {
        for (pattern in VIDEO_URL_PATTERNS) {
            val match = pattern.find(html)
            if (match != null) {
                val url = match.groupValues[1].replace("\\/", "/")
                if (isValidVideoUrl(url)) {
                    return url
                }
            }
        }
        return null
    }
    
    /**
     * Procura base64 'datas' no HTML
     */
    internal fun findBase64Datas(html: String): String? {
        for ((index, pattern) in BASE64_PATTERNS.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val candidate = match.groupValues[1]
                return candidate
            }
        }
        return null
    }
    
    /**
     * Valida se uma URL é um vídeo válido
     */
    internal fun isValidVideoUrl(url: String): Boolean {
        // Verificar se é uma URL válida
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            return false
        }
        
        // Verificar domínios permitidos
        val hasAllowedDomain = ALLOWED_VIDEO_DOMAINS.any { domain ->
            url.contains(domain, ignoreCase = true)
        }
        
        // Verificar extensões de vídeo
        val hasVideoExtension = url.contains(".mp4", ignoreCase = true) ||
                               url.contains(".m3u8", ignoreCase = true) ||
                               url.contains(".mkv", ignoreCase = true) ||
                               url.contains(".webm", ignoreCase = true) ||
                               url.contains("/video", ignoreCase = true) ||
                               url.contains("/stream", ignoreCase = true)
        
        return hasAllowedDomain || hasVideoExtension
    }
    
    /**
     * Processa string JSON escapada e retorna bytes
     */
    internal fun processJsonStringToBytes(escaped: String): ByteArray {
        val result = ByteArrayOutputStream()
        var i = 0
        
        while (i < escaped.length) {
            when {
                escaped[i] == '\\' && i + 1 < escaped.length -> {
                    when (escaped[i + 1]) {
                        '"' -> { result.write(0x22); i += 2 }
                        '\\' -> { result.write(0x5C); i += 2 }
                        '/' -> { result.write(0x2F); i += 2 }
                        'b' -> { result.write(0x08); i += 2 }
                        'f' -> { result.write(0x0C); i += 2 }
                        'n' -> { result.write(0x0A); i += 2 }
                        'r' -> { result.write(0x0D); i += 2 }
                        't' -> { result.write(0x09); i += 2 }
                        'u' -> {
                            if (i + 5 < escaped.length) {
                                val hex = escaped.substring(i + 2, i + 6)
                                try {
                                    val code = hex.toInt(16)
                                    result.write(code and 0xFF)
                                } catch (e: Exception) {
                                    result.write(0x5C)
                                    result.write(0x75)
                                }
                                i += 6
                            } else {
                                result.write(escaped[i].code)
                                i++
                            }
                        }
                        else -> {
                            result.write(escaped[i + 1].code)
                            i += 2
                        }
                    }
                }
                else -> {
                    result.write(escaped[i].code and 0xFF)
                    i++
                }
            }
        }
        
        return result.toByteArray()
    }
    
    // Regex patterns para extração de campos (compilados uma vez)
    private val USER_ID_PATTERN = Regex(""""user_id"\s*:\s*(\d+)""")
    private val SLUG_PATTERN = Regex(""""slug"\s*:\s*"([^"]+)"""")
    private val MD5_ID_PATTERN = Regex(""""md5_id"\s*:\s*(\d+)""")
    private val MEDIA_PATTERN = Regex(""""media"\s*:\s*"((?:[^"\\\\]|\\\\.)*)"""")
}
