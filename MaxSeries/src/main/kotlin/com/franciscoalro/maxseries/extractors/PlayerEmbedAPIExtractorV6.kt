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
 * PlayerEmbedAPI Extractor v6.0 - Multi-Source Extraction (Feb 2026)
 * 
 * v6.0 Changes:
 * - 🔥 MULTI-SOURCE: Extrai TODAS as sources disponíveis, não apenas a primeira
 * - 🔄 ACUMULAÇÃO: Executa todas as estratégias e coleta todos os links
 * - 🎯 DEDUPLICAÇÃO: Remove links duplicados por URL antes de retornar
 * - 📊 COBERTURA: API + ShortIcu + Regex + WebView em sequência
 * - 🔒 SEGURANÇA: Mantém proteção de dados sensíveis do v5
 * - 📺 QUALIDADES: Suporte a 360p, 480p, 720p, 1080p, 4K
 * - ⚡ PERFORMANCE: Regex compilados em companion object
 * - 🛡️ VALIDAÇÃO: Validação de URLs antes de retornar
 * - 🌐 DOMÍNIOS: Suporte a múltiplos domínios (sssrr, googleapis, cdns)
 */
class PlayerEmbedAPIExtractorV6 : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI-v6"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        private const val EXTRACTION_TIMEOUT_MS = 15000L
        
        // Regex compilados para melhor performance
        private val DATA_SOURCE_PATTERN = Regex("""data-source\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        private val DATA_SRC_PATTERN = Regex("""data-src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        private val HREF_PATTERN = Regex("""href\s*=\s*["']([^"']+playerembedapi[^"']*)["']""", RegexOption.IGNORE_CASE)
        private val IFRAME_SRC_PATTERN = Regex("""<iframe[^>]+src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        
        // Padrões para base64 'datas'
        private val BASE64_PATTERNS = listOf(
            Regex("""const\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex("""var\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex("""let\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex("""datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex("""data[=:]\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex(""""(eyJ[A-Za-z0-9+/=]{100,})"""),
            Regex("""window\.__DATA__\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            Regex("""encryptedData\s*=\s*"([A-Za-z0-9+/=]{200,})""")
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
        
        Log.wtf(TAG, "=== PlayerEmbedAPI v6.0 - Multi-Source Extraction ===")
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
            // Mesmo com cache, continua para buscar mais sources
        }
        
        // 2. EXTRAIR TODAS AS SOURCES
        val allLinks = extractAllSources(url, referer)
        
        val elapsedTime = System.currentTimeMillis() - startTime
        Log.wtf(TAG, "=== EXTRAÇÃO COMPLETA: ${allLinks.size} links em ${elapsedTime}ms ===")
        
        // 3. CHAMAR CALLBACK PARA CADA LINK ÚNICO
        if (allLinks.isNotEmpty()) {
            allLinks.forEach { link ->
                callback.invoke(link)
            }
        } else if (cached == null) {
            Log.e(TAG, "FALHA: Nenhuma estratégia funcionou")
        }
    }
    
    /**
     * Extrai TODAS as sources disponíveis executando todas as estratégias
     * @return Lista de todos os links encontrados (sem duplicatas)
     */
    private suspend fun extractAllSources(
        url: String,
        referer: String?
    ): List<ExtractorLink> {
        val allLinks = mutableListOf<ExtractorLink>()
        val foundUrls = mutableSetOf<String>() // Para deduplicação
        
        // ESTRATÉGIA 1: Extração via API (base64 + AES-CTR)
        try {
            Log.d(TAG, "[1/4] Executando extração via API...")
            val apiLinks = extractViaApi(url, referer)
            apiLinks.forEach { link ->
                if (foundUrls.add(link.url)) {
                    allLinks.add(link)
                    Log.d(TAG, "✓ API: ${link.name} - ${link.url.take(60)}...")
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via API falhou: ${e.message}")
        }
        
        // ESTRATÉGIA 2: Extração via ShortIcu
        try {
            Log.d(TAG, "[2/4] Executando extração via ShortIcu...")
            val shortIcuLinks = extractViaShortIcu(url, referer)
            shortIcuLinks.forEach { link ->
                if (foundUrls.add(link.url)) {
                    allLinks.add(link)
                    Log.d(TAG, "✓ ShortIcu: ${link.name} - ${link.url.take(60)}...")
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via ShortIcu falhou: ${e.message}")
        }
        
        // ESTRATÉGIA 3: Regex direto no HTML
        try {
            Log.d(TAG, "[3/4] Executando extração via Regex...")
            val regexLinks = extractViaRegexFallback(url, referer)
            regexLinks.forEach { link ->
                if (foundUrls.add(link.url)) {
                    allLinks.add(link)
                    Log.d(TAG, "✓ Regex: ${link.name} - ${link.url.take(60)}...")
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via Regex falhou: ${e.message}")
        }
        
        // ESTRATÉGIA 4: WebView
        try {
            Log.d(TAG, "[4/4] Executando extração via WebView...")
            val webViewLinks = extractViaWebView(url, referer)
            webViewLinks.forEach { link ->
                if (foundUrls.add(link.url)) {
                    allLinks.add(link)
                    Log.d(TAG, "✓ WebView: ${link.name} - ${link.url.take(60)}...")
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Extração via WebView falhou: ${e.message}")
        }
        
        Log.d(TAG, "Total de links únicos encontrados: ${allLinks.size}")
        return allLinks
    }

    /**
     * Estratégia 1: Extração via API (base64 + AES-CTR)
     * Extrai dados criptografados do HTML, decodifica base64 e decripta AES-CTR
     * @return Lista de links encontrados
     */
    private suspend fun extractViaApi(
        url: String,
        referer: String?
    ): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
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
            return links
        }
        
        // Encontrar base64 'datas'
        val base64Data = findBase64Datas(html) ?: run {
            Log.w(TAG, "Não encontrou base64 'datas'")
            return links
        }
        
        return processBase64Data(base64Data, url)
    }
    
    /**
     * Processa dados base64 e extrai URLs de vídeo
     * @return Lista de links encontrados
     */
    private suspend fun processBase64Data(
        base64Data: String,
        originalUrl: String
    ): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
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
                return links
            }
            
            // Processar escapes JSON
            val mediaBytes = processJsonStringToBytes(mediaEscaped)
            
            // Decriptar com AES-CTR
            val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaBytes, userId, slug, md5Id)
            
            if (decrypted == null) {
                Log.w(TAG, "Falha na decriptação AES-CTR")
                return links
            }
            
            // Extrair e retornar URLs
            extractUrlsFromDecrypted(decrypted, originalUrl)
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no processamento: ${e.message}")
            links
        }
    }
    
    /**
     * Extrai URLs do objeto decriptado
     * @return Lista de links encontrados
     */
    private suspend fun extractUrlsFromDecrypted(
        decrypted: PlayerEmbedMedia,
        originalUrl: String
    ): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
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
                    
                    links.add(
                        newExtractorLink(
                            source = name,
                            name = "$name ${source.label ?: "Auto"} (API)",
                            url = source.file,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = "https://playerembedapi.link/"
                            this.quality = quality.value
                        }
                    )
                }
            }
        }
        
        // Fallback: HLS direto
        decrypted.hls?.let { hlsUrl ->
            if (isValidVideoUrl(hlsUrl)) {
                val quality = QualityDetector.detectFromUrl(hlsUrl)
                VideoUrlCache.put(originalUrl, hlsUrl, quality, name)
                
                links.add(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (HLS/API)",
                        url = hlsUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
            }
        }
        
        // Fallback: MP4 direto
        decrypted.mp4?.let { mp4Url ->
            if (isValidVideoUrl(mp4Url)) {
                val quality = QualityDetector.detectFromUrl(mp4Url)
                VideoUrlCache.put(originalUrl, mp4Url, quality, name)
                
                links.add(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (MP4/API)",
                        url = mp4Url,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
            }
        }
        
        return links
    }
    
    /**
     * Estratégia 2: Extração via ShortIcu
     * @return Lista de links encontrados
     */
    private suspend fun extractViaShortIcu(
        url: String,
        referer: String?
    ): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
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
            val shortIcuUrl = extractShortIcuUrl(html) ?: return links
            
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
            
            // Extrair todas as URLs de vídeo do HTML
            val videoUrls = extractAllVideoUrlsFromHtml(shortHtml)
            
            videoUrls.forEach { videoUrl ->
                if (isValidVideoUrl(videoUrl)) {
                    val quality = QualityDetector.detectFromUrl(videoUrl)
                    VideoUrlCache.put(url, videoUrl, quality, name)
                    
                    links.add(
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
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Erro na extração ShortIcu: ${e.message}")
        }
        
        return links
    }

    /**
     * Estratégia 3: Regex direto no HTML
     * @return Lista de links encontrados
     */
    private suspend fun extractViaRegexFallback(
        url: String,
        referer: String?
    ): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
        try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl)
                ),
                timeout = 10
            )
            
            val html = response.text
            val videoUrls = extractAllVideoUrlsFromHtml(html)
            
            videoUrls.forEach { videoUrl ->
                if (isValidVideoUrl(videoUrl)) {
                    val quality = QualityDetector.detectFromUrl(videoUrl)
                    VideoUrlCache.put(url, videoUrl, quality, name)
                    
                    links.add(
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
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Erro no regex fallback: ${e.message}")
        }
        
        return links
    }
    
    /**
     * Estratégia 4: WebView
     * @return Lista de links encontrados
     */
    private suspend fun extractViaWebView(
        url: String,
        referer: String?
    ): List<ExtractorLink> {
        return try {
            // Nota: WebView pode precisar de uma versão V6 também para consistência
            // Por enquanto, usa a V5 mas os links serão marcados adequadamente
            PlayerEmbedAPIWebViewExtractorV5().extractFromUrl(url, referer ?: url)
                .map { link ->
                    // Renomear para indicar origem WebView
                    newExtractorLink(
                        source = name,
                        name = link.name.replace("(WebView)", "(WebView/V6)"),
                        url = link.url,
                        type = link.type
                    ) {
                        this.referer = link.referer
                        this.quality = link.quality
                        this.headers = link.headers
                    }
                }
        } catch (e: Exception) {
            Log.w(TAG, "Erro no WebView: ${e.message}")
            emptyList()
        }
    }
    
    /**
     * Extrai URL do short.icu do HTML
     */
    private fun extractShortIcuUrl(html: String): String? {
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
    
    /**
     * Extrai URL de vídeo do HTML usando múltiplos padrões (primeira encontrada)
     */
    private fun extractVideoUrlFromHtml(html: String): String? {
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
     * Extrai TODAS as URLs de vídeo do HTML usando múltiplos padrões
     * @return Lista de todas as URLs válidas encontradas
     */
    private fun extractAllVideoUrlsFromHtml(html: String): List<String> {
        val foundUrls = mutableSetOf<String>()
        
        for (pattern in VIDEO_URL_PATTERNS) {
            pattern.findAll(html).forEach { match ->
                val url = match.groupValues[1].replace("\\/", "/")
                if (isValidVideoUrl(url)) {
                    foundUrls.add(url)
                }
            }
        }
        
        return foundUrls.toList()
    }
    
    /**
     * Procura base64 'datas' no HTML
     */
    private fun findBase64Datas(html: String): String? {
        for ((index, pattern) in BASE64_PATTERNS.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val candidate = match.groupValues[1]
                try {
                    android.util.Base64.decode(candidate, android.util.Base64.DEFAULT)
                    Log.d(TAG, "Pattern $index funcionou")
                    return candidate
                } catch (e: Exception) {
                    continue
                }
            }
        }
        return null
    }
    
    /**
     * Valida se uma URL é um vídeo válido
     */
    private fun isValidVideoUrl(url: String): Boolean {
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
    private fun processJsonStringToBytes(escaped: String): ByteArray {
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
    private val MEDIA_PATTERN = Regex(""""media"\s*:\s*"((?:[^"\\\\]|\\\\.)*)""")
}
