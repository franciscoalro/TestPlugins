package com.franciscoalro.maxseries.network

import android.util.Log
import com.lagradost.cloudstream3.app
import com.franciscoalro.maxseries.crypto.AesCtrDecryptor
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import org.json.JSONObject
import java.net.URL

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CDN CONSTRUCTOR - Construção Inteligente de URLs CDN
 * Baseado em padrões descobertos via fuzzing e engenharia reversa
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * DESCobertas de Pentest (Fuzzing & Endpoint Discovery):
 * 
 * 1. Padrão SSSRR (PlayerEmbedAPI):
 *    https://{slug}.sssrr.org/sora/{md5_id}/
 *    https://cdn.sssrr.org/sora/{md5_id}/
 *    https://{slug}.sssrr.org/future
 * 
 * 2. Padrão Marvella Holdings (MegaEmbed):
 *    https://{shard}.{cdn_domain}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt
 *    Domínios: stzm.marvellaholdings.sbs, srcf.marvellaholdings.sbs
 * 
 * 3. Padrão Google Cloud Storage:
 *    https://storage.googleapis.com/mediastorage/{timestamp}/{hash}/{filename}.mp4
 * 
 * 4. Padrão CloudAtaCDN:
 *    https://{subdomain}.cloudatacdn.com/{path}/{video_id}/{quality}.{ext}
 * 
 * Vantagens:
 * - ⚡ Construção offline (sem HTTP requests)
 * - 🎯 Múltiplas URLs candidatas
 * - 🔍 Validação paralela de URLs
 * - 📊 Fallback automático entre CDNs
 * 
 * @version 1.0
 * @since 2026-02-03
 */
object CDNConstructor {
    
    private const val TAG = "CDNConstructor"
    private fun safeLogD(msg: String) = runCatching { Log.d(TAG, msg) }
    private fun safeLogE(msg: String, t: Throwable? = null) = runCatching { Log.e(TAG, msg, t) }
    
    /**
     * Domínios CDN conhecidos (descobertos via fuzzing)
     */
    object KnownCDNs {
        // PlayerEmbedAPI / SSSRR
        val SSSRR_DOMAINS = listOf(
            "sssrr.org",
            "cdn.sssrr.org", 
            "statics.sssrr.org",
            "cache.sssrr.org"
        )
        
        // MegaEmbed / Marvella Holdings
        val MARVELLA_DOMAINS = listOf(
            "marvellaholdings.sbs",
            "stzm.marvellaholdings.sbs",
            "srcf.marvellaholdings.sbs",
            "sbi6.marvellaholdings.sbs",
            "s6p9.marvellaholdings.sbs",
            "scdn.marvellaholdings.sbs"
        )
        
        // Shards para Marvella (descobertos via análise)
        val MARVELLA_SHARDS = listOf(
            "x6b", "x7c", "x8d", "x9e", "xa1", "xb2",
            "xc3", "xd4", "xe5", "xf6", "x0a", "x1b"
        )
        
        // Google Cloud Storage
        const val GCS_DOMAIN = "storage.googleapis.com"
        const val GCS_BUCKET = "mediastorage"
        
        // CloudAtaCDN
        val CLOUDATA_DOMAINS = listOf(
            "cloudatacdn.com",
            "cdn.cloudatacdn.com",
            "media.cloudatacdn.com"
        )
        
        // Outros CDNs populares
        val OTHER_CDNS = listOf(
            "akamaized.net",
            "cloudfront.net", 
            "fastly.net",
            "bunnycdn.com",
            "cdn77.org"
        )
    }
    
    /**
     * Padrões de URL descobertos
     */
    object URLPatterns {
        // PlayerEmbedAPI - Padrão SSSRR
        const val SSSRR_PATTERN = "https://{slug}.sssrr.org/sora/{md5_id}/"
        const val SSSRR_CDN_PATTERN = "https://cdn.sssrr.org/sora/{md5_id}/"
        const val SSSRR_STATIC_PATTERN = "https://statics.sssrr.org/sora/{md5_id}/playlist.m3u8"
        const val SSSRR_FUTURE_PATTERN = "https://{slug}.sssrr.org/future"
        
        // MegaEmbed - Padrão Marvella
        const val MARVELLA_PATTERN = "https://{shard}.{domain}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
        const val MARVELLA_ALT_PATTERN = "https://{domain}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
        
        // Google Cloud Storage
        const val GCS_PATTERN = "https://storage.googleapis.com/{bucket}/{timestamp}/{hash}/{filename}.mp4"
        
        // CloudAtaCDN
        const val CLOUDATA_PATTERN = "https://{subdomain}.cloudatacdn.com/{path}/{video_id}/{quality}.{ext}"
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // ESTRUTURAS DE DADOS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Dados de vídeo extraídos do HTML
     */
    data class VideoData(
        val slug: String,
        val md5Id: String,
        val userId: String = "",
        val videoId: String = "",
        val source: VideoSource = VideoSource.UNKNOWN
    ) {
        enum class VideoSource {
            PLAYEREMBEDAPI,  // slug + md5_id
            MEGAEMBED,       // video_id hash
            GOOGLE_STORAGE,  // gcs path
            CLOUDATA,        // cloudatacdn
            UNKNOWN
        }
    }
    
    /**
     * Resultado da construção CDN
     */
    data class CDNResult(
        val urls: List<String>,
        val source: VideoData.VideoSource,
        val isValidated: Boolean = false,
        val validUrl: String? = null
    )
    
    /**
     * Status de validação de URL
     */
    data class ValidationResult(
        val url: String,
        val isValid: Boolean,
        val statusCode: Int,
        val contentType: String?,
        val responseTime: Long
    )
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS PÚBLICOS PRINCIPAIS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Extrai dados de vídeo do HTML completo
     * Combina múltiplas estratégias de extração
     */
    fun extractVideoData(html: String): VideoData? {
        safeLogD("🔍 Extraindo dados de vídeo do HTML...")
        
        // Estratégia 1: Usar AesCtrDecryptor para extrair metadata
        AesCtrDecryptor.extractMetadata(html)?.let { metadata ->
            safeLogD("✅ Dados extraídos via AesCtrDecryptor")
            return VideoData(
                slug = metadata.slug,
                md5Id = metadata.md5Id.toString(),
                userId = metadata.userId.toString(),
                source = VideoData.VideoSource.PLAYEREMBEDAPI
            )
        }
        
        // Estratégia 2: Extrair de variáveis JavaScript
        extractFromJavaScript(html)?.let {
            safeLogD("✅ Dados extraídos de JavaScript")
            return it
        }
        
        // Estratégia 3: Extrair de atributos data-*
        extractFromDataAttributes(html)?.let {
            safeLogD("✅ Dados extraídos de atributos data-*")
            return it
        }
        
        // Estratégia 4: Extrair de meta tags
        extractFromMetaTags(html)?.let {
            safeLogD("✅ Dados extraídos de meta tags")
            return it
        }
        
        // Estratégia 5: Regex direto no HTML
        extractViaRegex(html)?.let {
            safeLogD("✅ Dados extraídos via regex")
            return it
        }
        
        safeLogD("❌ Não foi possível extrair dados de vídeo")
        return null
    }
    
    /**
     * Constrói múltiplas URLs CDN a partir dos dados extraídos
     * Retorna lista de candidatos para validação
     */
    fun constructCDNUrls(videoData: VideoData): List<String> {
        safeLogD("🏗️ Construindo URLs CDN para: ${videoData.slug}/${videoData.md5Id}")
        
        if (videoData.slug.isBlank() && videoData.md5Id.isBlank() && videoData.videoId.isBlank()) {
            return emptyList()
        }
        
        val urls = mutableListOf<String>()
        
        when (videoData.source) {
            VideoData.VideoSource.PLAYEREMBEDAPI -> {
                urls.addAll(constructSSSRUrls(videoData))
            }
            VideoData.VideoSource.MEGAEMBED -> {
                urls.addAll(constructMarvellaUrls(videoData))
            }
            VideoData.VideoSource.GOOGLE_STORAGE -> {
                urls.addAll(constructGCSUrls(videoData))
            }
            VideoData.VideoSource.CLOUDATA -> {
                urls.addAll(constructCloudataUrls(videoData))
            }
            VideoData.VideoSource.UNKNOWN -> {
                // Tentar todos os padrões
                urls.addAll(constructSSSRUrls(videoData))
                urls.addAll(constructMarvellaUrls(videoData))
            }
        }
        
        safeLogD("📊 ${urls.size} URLs CDN construídas")
        return urls.distinct()
    }
    
    /**
     * Constrói e valida URLs CDN em paralelo
     * Retorna a primeira URL válida encontrada
     */
    suspend fun constructAndValidate(
        html: String,
        maxConcurrent: Int = 5,
        timeoutMs: Long = 5000
    ): CDNResult? {
        val startTime = System.currentTimeMillis()
        
        // Extrair dados
        val videoData = extractVideoData(html) ?: run {
            safeLogD("❌ Falha ao extrair dados de vídeo")
            return null
        }
        
        // Construir URLs
        val urls = constructCDNUrls(videoData)
        if (urls.isEmpty()) {
            safeLogD("❌ Nenhuma URL CDN construída")
            return null
        }
        
        safeLogD("🔍 Validando ${urls.size} URLs em paralelo...")
        
        // Validar em paralelo
        val validationResults = validateUrlsParallel(urls.take(maxConcurrent), timeoutMs)
        
        // Encontrar primeira URL válida
        val firstValid = validationResults.find { it.isValid }
        
        val duration = System.currentTimeMillis() - startTime
        
        return if (firstValid != null) {
            Log.wtf(TAG, "✅ URL válida encontrada em ${duration}ms: ${firstValid.url.take(60)}...")
            CDNResult(
                urls = urls,
                source = videoData.source,
                isValidated = true,
                validUrl = firstValid.url
            )
        } else {
            safeLogD("⚠️ Nenhuma URL válida encontrada após ${duration}ms")
            CDNResult(
                urls = urls,
                source = videoData.source,
                isValidated = false,
                validUrl = null
            )
        }
    }
    
    /**
     * Versão rápida - apenas constrói URLs sem validar
     * Útil quando a validação será feita posteriormente
     */
    fun constructQuick(videoData: VideoData): String? {
        return when (videoData.source) {
            VideoData.VideoSource.PLAYEREMBEDAPI -> {
                "https://${videoData.slug}.sssrr.org/sora/${videoData.md5Id}/"
            }
            else -> constructCDNUrls(videoData).firstOrNull()
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // CONSTRUTORES ESPECÍFICOS POR CDN
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Constrói URLs para CDN SSSRR (PlayerEmbedAPI)
     */
    private fun constructSSSRUrls(videoData: VideoData): List<String> {
        val urls = mutableListOf<String>()
        
        if (videoData.slug.isEmpty() || videoData.md5Id.isEmpty()) {
            return urls
        }
        
        // Padrão principal
        urls.add("https://${videoData.slug}.sssrr.org/sora/${videoData.md5Id}/")
        
        // CDN alternativo
        urls.add("https://cdn.sssrr.org/sora/${videoData.md5Id}/")
        
        // Statics com playlist
        urls.add("https://statics.sssrr.org/sora/${videoData.md5Id}/playlist.m3u8")
        urls.add("https://statics.sssrr.org/sora/${videoData.md5Id}/master.m3u8")
        
        // Cache
        urls.add("https://cache.sssrr.org/sora/${videoData.md5Id}/")
        
        // Padrão /future (descoberto via fuzzing)
        urls.add("https://${videoData.slug}.sssrr.org/future")
        urls.add("https://cdn.sssrr.org/future/${videoData.md5Id}")
        
        // Variações com index
        urls.add("https://${videoData.slug}.sssrr.org/sora/${videoData.md5Id}/index.m3u8")
        urls.add("https://cdn.sssrr.org/sora/${videoData.md5Id}/index.m3u8")
        
        // Variações com video.mp4
        urls.add("https://${videoData.slug}.sssrr.org/sora/${videoData.md5Id}/video.mp4")
        urls.add("https://cdn.sssrr.org/sora/${videoData.md5Id}/video.mp4")
        
        return urls
    }
    
    /**
     * Constrói URLs para CDN Marvella (MegaEmbed)
     */
    private fun constructMarvellaUrls(videoData: VideoData): List<String> {
        val urls = mutableListOf<String>()
        val timestamp = System.currentTimeMillis()
        
        val videoId = videoData.videoId.ifEmpty { videoData.md5Id }
        if (videoId.isEmpty()) return urls
        
        // Gerar URLs para cada combinação de shard e domínio
        for (domain in KnownCDNs.MARVELLA_DOMAINS) {
            for (shard in KnownCDNs.MARVELLA_SHARDS) {
                // Padrão principal
                val url = "https://$domain/v4/$shard/$videoId/cf-master.$timestamp.txt"
                urls.add(url)
                
                // Variações
                urls.add("https://$domain/v4/$shard/$videoId/master.m3u8")
                urls.add("https://$domain/v4/$shard/$videoId/playlist.m3u8")
                urls.add("https://$domain/v4/$shard/$videoId/video.mp4")
            }
        }
        
        return urls
    }
    
    /**
     * Constrói URLs para Google Cloud Storage
     */
    private fun constructGCSUrls(videoData: VideoData): List<String> {
        val urls = mutableListOf<String>()
        val timestamp = System.currentTimeMillis()
        
        // Padrão GCS (requer hash específico, geralmente extraído da resposta)
        // Estes são placeholders - GCS URLs geralmente vêm da API
        urls.add("https://${KnownCDNs.GCS_DOMAIN}/${KnownCDNs.GCS_BUCKET}/$timestamp/${videoData.md5Id}.mp4")
        
        return urls
    }
    
    /**
     * Constrói URLs para CloudAtaCDN
     */
    private fun constructCloudataUrls(videoData: VideoData): List<String> {
        val urls = mutableListOf<String>()
        
        for (domain in KnownCDNs.CLOUDATA_DOMAINS) {
            urls.add("https://$domain/media/${videoData.md5Id}/720p.mp4")
            urls.add("https://$domain/media/${videoData.md5Id}/1080p.mp4")
            urls.add("https://$domain/media/${videoData.md5Id}/playlist.m3u8")
        }
        
        return urls
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS DE EXTRAÇÃO DO HTML
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Extrai dados de variáveis JavaScript
     */
    private fun extractFromJavaScript(html: String): VideoData? {
        // Padrão: window.videoData, window.__DATA__, etc.
        val patterns = listOf(
            Regex("""window\.videoData\s*=\s*(\{[^}]+\})"""),
            Regex("""window\.__DATA__\s*=\s*(\{[^}]+\})"""),
            Regex("""window\.__INITIAL_STATE__\s*=\s*(\{[^}]+\})"""),
            Regex("""var\s+videoData\s*=\s*(\{[^}]+\})""")
        )
        
        for (pattern in patterns) {
            pattern.find(html)?.let { match ->
                try {
                    val json = JSONObject(match.groupValues[1])
                    return VideoData(
                        slug = json.optString("slug", ""),
                        md5Id = json.optString("md5_id", json.optInt("md5_id", 0).toString()),
                        userId = json.optString("user_id", json.optInt("user_id", 0).toString()),
                        videoId = json.optString("video_id", json.optString("id", "")),
                        source = detectSource(json)
                    )
                } catch (e: Exception) {
                    Log.v(TAG, "Falha ao parsear JSON de JS: ${e.message}")
                }
            }
        }
        
        return null
    }
    
    /**
     * Extrai dados de atributos data-*
     */
    private fun extractFromDataAttributes(html: String): VideoData? {
        val slugPattern = Regex("""data-slug\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        val md5Pattern = Regex("""data-md5-id\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        val idPattern = Regex("""data-video-id\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        
        val slug = slugPattern.find(html)?.groupValues?.get(1) ?: ""
        val md5Id = md5Pattern.find(html)?.groupValues?.get(1) ?: ""
        val videoId = idPattern.find(html)?.groupValues?.get(1) ?: ""
        
        return if (slug.isNotEmpty() || md5Id.isNotEmpty()) {
            VideoData(
                slug = slug,
                md5Id = md5Id.ifEmpty { videoId },
                videoId = videoId,
                source = if (slug.isNotEmpty()) VideoData.VideoSource.PLAYEREMBEDAPI 
                        else VideoData.VideoSource.UNKNOWN
            )
        } else null
    }
    
    /**
     * Extrai dados de meta tags
     */
    private fun extractFromMetaTags(html: String): VideoData? {
        // Procurar meta tags com informações do vídeo
        val metaPattern = Regex("""<meta\s+(?:property|name)\s*=\s*["']([^"']+)["']\s+content\s*=\s*["']([^"']+)["']""")
        
        var slug = ""
        var videoId = ""
        
        metaPattern.findAll(html).forEach { match ->
            val property = match.groupValues[1].lowercase()
            val content = match.groupValues[2]
            
            when {
                property.contains("video:id") -> videoId = content
                property.contains("slug") -> slug = content
            }
        }
        
        return if (slug.isNotEmpty() || videoId.isNotEmpty()) {
            VideoData(
                slug = slug,
                md5Id = videoId,
                videoId = videoId,
                source = VideoData.VideoSource.UNKNOWN
            )
        } else null
    }
    
    /**
     * Extrai dados via regex direto no HTML
     */
    private fun extractViaRegex(html: String): VideoData? {
        // Padrão combinado: slug + md5_id próximos no HTML
        val combinedPattern = Regex(
            """["']([a-zA-Z0-9]{9,11})["']\s*[:\s,]+\s*["']?(\d{7,9})["']?""",
            RegexOption.IGNORE_CASE
        )
        
        combinedPattern.find(html)?.let { match ->
            return VideoData(
                slug = match.groupValues[1],
                md5Id = match.groupValues[2],
                source = VideoData.VideoSource.PLAYEREMBEDAPI
            )
        }
        
        // Padrão de hash longo (MegaEmbed)
        val hashPattern = Regex("""[/#]([a-f0-9]{6,8})["'\s>]""")
        hashPattern.find(html)?.let { match ->
            return VideoData(
                slug = "",
                md5Id = match.groupValues[1],
                videoId = match.groupValues[1],
                source = VideoData.VideoSource.MEGAEMBED
            )
        }
        
        return null
    }
    
    /**
     * Detecta a fonte do vídeo baseado no JSON
     */
    private fun detectSource(json: JSONObject): VideoData.VideoSource {
        return when {
            json.has("slug") && json.has("md5_id") -> VideoData.VideoSource.PLAYEREMBEDAPI
            json.has("hash") || json.has("video_hash") -> VideoData.VideoSource.MEGAEMBED
            json.optString("cdn", "").contains("google") -> VideoData.VideoSource.GOOGLE_STORAGE
            json.optString("cdn", "").contains("cloudata") -> VideoData.VideoSource.CLOUDATA
            else -> VideoData.VideoSource.UNKNOWN
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // VALIDAÇÃO DE URLs
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Valida múltiplas URLs em paralelo
     */
    suspend fun validateUrlsParallel(
        urls: List<String>,
        timeoutMs: Long = 5000
    ): List<ValidationResult> = coroutineScope {
        urls.map { url ->
            async {
                validateUrl(url, timeoutMs)
            }
        }.awaitAll()
    }
    
    /**
     * Valida uma única URL
     */
    suspend fun validateUrl(url: String, timeoutMs: Long = 5000): ValidationResult {
        val startTime = System.currentTimeMillis()
        
        return try {
            // Usar HEAD request para ser mais rápido
            val response = app.head(url, timeout = timeoutMs / 1000)
            
            val isValid = response.isSuccessful && 
                         isValidContentType(response.headers["Content-Type"])
            
            ValidationResult(
                url = url,
                isValid = isValid,
                statusCode = response.code,
                contentType = response.headers["Content-Type"],
                responseTime = System.currentTimeMillis() - startTime
            )
            
        } catch (e: Exception) {
            ValidationResult(
                url = url,
                isValid = false,
                statusCode = 0,
                contentType = null,
                responseTime = System.currentTimeMillis() - startTime
            )
        }
    }
    
    /**
     * Valida se o Content-Type indica vídeo/playlist válido
     */
    private fun isValidContentType(contentType: String?): Boolean {
        if (contentType == null) return false
        
        val validTypes = listOf(
            "video/",
            "application/x-mpegURL",  // m3u8
            "application/vnd.apple.mpegurl",
            "text/plain",  // Alguns CDNs retornam txt
            "application/octet-stream"
        )
        
        return validTypes.any { contentType.contains(it, ignoreCase = true) }
    }
    
    /**
     * Verifica se uma URL parece ser de vídeo (heurística)
     */
    fun isVideoUrl(url: String): Boolean {
        val lower = url.lowercase()
        return lower.contains(".m3u8") ||
               lower.contains(".mp4") ||
               lower.contains(".mkv") ||
               lower.contains(".webm") ||
               lower.contains("/video/") ||
               lower.contains("/sora/") ||
               lower.contains("cf-master")
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // UTILITÁRIOS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Extrai o host de uma URL
     */
    fun extractHost(url: String): String? {
        return try {
            URL(url).host
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Detecta qual CDN uma URL pertence
     */
    fun detectCDN(url: String): String {
        val lower = url.lowercase()
        return when {
            lower.contains("sssrr") -> "SSSRR"
            lower.contains("marvella") -> "Marvella"
            lower.contains("googleapis") -> "GCS"
            lower.contains("cloudata") -> "CloudAta"
            lower.contains("akamaized") -> "Akamai"
            lower.contains("cloudfront") -> "CloudFront"
            else -> "Unknown"
        }
    }
    
    /**
     * Gera relatório de debug completo
     */
    fun generateDebugReport(html: String): String {
        val sb = StringBuilder()
        sb.appendLine("=== CDN Constructor Debug Report ===")
        sb.appendLine()
        
        // Extrair dados
        val videoData = extractVideoData(html)
        if (videoData == null) {
            sb.appendLine("❌ Falha ao extrair dados de vídeo")
            return sb.toString()
        }
        
        sb.appendLine("✅ Dados extraídos:")
        sb.appendLine("  - Source: ${videoData.source}")
        sb.appendLine("  - Slug: ${videoData.slug}")
        sb.appendLine("  - MD5 ID: ${videoData.md5Id}")
        sb.appendLine("  - Video ID: ${videoData.videoId}")
        sb.appendLine()
        
        // Construir URLs
        val urls = constructCDNUrls(videoData)
        sb.appendLine("📊 URLs construídas: ${urls.size}")
        urls.take(10).forEachIndexed { index, url ->
            sb.appendLine("  ${index + 1}. [${detectCDN(url)}] ${url.take(70)}...")
        }
        if (urls.size > 10) {
            sb.appendLine("  ... e ${urls.size - 10} mais")
        }
        
        return sb.toString()
    }
}

/**
 * Extensões Kotlin para facilitar uso
 */
fun String.constructCDN(): List<String> {
    return CDNConstructor.extractVideoData(this)?.let {
        CDNConstructor.constructCDNUrls(it)
    } ?: emptyList()
}

suspend fun String.validateCDNs(): CDNConstructor.CDNResult? {
    return CDNConstructor.constructAndValidate(this)
}
