package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*
import java.net.URL
import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec
import android.util.Base64

/**
 * PlayerEmbedAPI Extractor v6.0 - Full Source Extraction
 * Extrai TODAS as sources disponiveis, nao apenas a primeira
 */
class PlayerEmbedAPIExtractorV6 : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI-v6"
        private const val TIMEOUT_MS = 20000L
        
        private val USER_AGENTS = listOf(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
    }

    override suspend fun getUrl(url: String, referer: String?, subtitleCallback: (SubtitleFile) -> Unit, callback: (ExtractorLink) -> Unit) {
        try {
            withTimeout(TIMEOUT_MS) {
                extractAllSources(url, referer ?: mainUrl, callback)
            }
        } catch (e: Exception) {
            android.util.Log.e(TAG, "Erro: ${e.message}")
        }
    }

    private suspend fun extractAllSources(sourceUrl: String, referer: String, callback: (ExtractorLink) -> Unit) {
        val allLinks = mutableListOf<ExtractorLink>()
        
        // === ESTRATEGIA 1: API ===
        val apiLinks = extractViaApi(sourceUrl, referer)
        allLinks.addAll(apiLinks)
        android.util.Log.d(TAG, "API: ${apiLinks.size} links")
        
        // === ESTRATEGIA 2: ShortIcu ===
        val shortIcuLinks = extractViaShortIcu(sourceUrl, referer)
        shortIcuLinks.forEach { link ->
            if (!allLinks.any { it.url == link.url }) {
                allLinks.add(link)
            }
        }
        android.util.Log.d(TAG, "ShortIcu: ${shortIcuLinks.size} links (novos: ${shortIcuLinks.count { s -> !allLinks.any { it.url == s.url } }})")
        
        // === ESTRATEGIA 3: Regex ===
        val regexLinks = extractViaRegex(sourceUrl, referer)
        regexLinks.forEach { link ->
            if (!allLinks.any { it.url == link.url }) {
                allLinks.add(link)
            }
        }
        android.util.Log.d(TAG, "Regex: ${regexLinks.size} links")
        
        android.util.Log.i(TAG, "TOTAL: ${allLinks.size} links unicos")
        
        // Retorna TODOS os links
        allLinks.forEach { callback(it) }
    }

    private suspend fun extractViaApi(sourceUrl: String, referer: String): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
        try {
            val response = app.get(sourceUrl, headers = mapOf(
                "User-Agent" to USER_AGENTS.random(),
                "Referer" to referer
            ), timeout = 15)
            
            val html = response.text
            
            // Padrões base64
            val base64Patterns = listOf(
                Regex("const\\s+datas\\s*=\\s*\"([A-Za-z0-9+/=]{200,})\""),
                Regex("var\\s+datas\\s*=\\s*\"([A-Za-z0-9+/=]{200,})\""),
                Regex("\"datas\"\\s*:\\s*\"([A-Za-z0-9+/=]{200,})\"")
            )
            
            // Extrai parametros
            val userId = Regex("userId\\s*[=:]\\s*[\"']([^\"']+)[\"']").find(html)?.groupValues?.get(1)
            val slug = Regex("slug\\s*[=:]\\s*[\"']([^\"']+)[\"']").find(html)?.groupValues?.get(1)
            val md5Id = Regex("md5Id\\s*[=:]\\s*[\"']([^\"']+)[\"']").find(html)?.groupValues?.get(1)
            
            if (userId == null || slug == null || md5Id == null) return links
            
            for (pattern in base64Patterns) {
                val match = pattern.find(html) ?: continue
                val base64Data = match.groupValues[1]
                
                try {
                    val encrypted = Base64.decode(base64Data, Base64.DEFAULT)
                    val decrypted = decryptAES(encrypted, userId, slug, md5Id)
                    
                    if (decrypted != null) {
                        // Extrai URLs do JSON
                        val filePattern = Regex("\"file\"\\s*:\\s*\"([^\"]+)\"").find(decrypted)
                        filePattern?.let {
                            val url = it.groupValues[1]
                            if (url.startsWith("http")) {
                                links.add(createLink(url, "API", referer, url.contains("m3u8")))
                            }
                        }
                        
                        // File2
                        val file2Pattern = Regex("\"file2\"\\s*:\\s*\"([^\"]+)\"").find(decrypted)
                        file2Pattern?.let {
                            val url = it.groupValues[1]
                            if (url.startsWith("http") && !links.any { l -> l.url == url }) {
                                links.add(createLink(url, "API-Fallback", referer, url.contains("m3u8")))
                            }
                        }
                    }
                } catch (e: Exception) { }
            }
        } catch (e: Exception) { }
        
        return links
    }
    
    private suspend fun extractViaShortIcu(sourceUrl: String, referer: String): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
        try {
            val response = app.get(sourceUrl, headers = mapOf(
                "User-Agent" to USER_AGENTS.random(),
                "Referer" to referer
            ), timeout = 15, allowRedirects = true)
            
            val html = response.text
            val finalUrl = response.url
            
            // Procura URLs de video
            val patterns = listOf(
                Regex("\"file\"\\s*:\\s*\"([^\"]+\\.m3u8[^\"]*)\""),
                Regex("\"src\"\\s*:\\s*\"([^\"]+\\.m3u8[^\"]*)\""),
                Regex("https?://[^\"'<>\\s]+\\.m3u8[^\"'<>\\s]*"),
                Regex("https?://[^\"'<>\\s]+\\.mp4[^\"'<>\\s]*")
            )
            
            for (pattern in patterns) {
                pattern.findAll(html).forEach { match ->
                    val url = match.value.trim()
                    if (url.startsWith("http") && !links.any { it.url == url }) {
                        val quality = detectQuality(url)
                        links.add(createLink(url, "ShortIcu-$quality", finalUrl, url.contains("m3u8")))
                    }
                }
            }
        } catch (e: Exception) { }
        
        return links
    }
    
    private suspend fun extractViaRegex(sourceUrl: String, referer: String): List<ExtractorLink> {
        val links = mutableListOf<ExtractorLink>()
        
        try {
            val response = app.get(sourceUrl, headers = mapOf(
                "User-Agent" to USER_AGENTS.random(),
                "Referer" to referer
            ), timeout = 15)
            
            val html = response.text
            
            // Padroes de qualidade
            val qualityPatterns = mapOf(
                "1080p" to Regex("(?:1080p|1080)[^\"'<>]*?(https?://[^\"'<>\\s]+)"),
                "720p" to Regex("(?:720p|720)[^\"'<>]*?(https?://[^\"'<>\\s]+)"),
                "480p" to Regex("(?:480p|480)[^\"'<>]*?(https?://[^\"'<>\\s]+)"),
                "360p" to Regex("(?:360p|360)[^\"'<>]*?(https?://[^\"'<>\\s]+)")
            )
            
            qualityPatterns.forEach { (quality, pattern) ->
                pattern.findAll(html).forEach { match ->
                    val url = match.groupValues[1].trim()
                    if (url.startsWith("http") && !links.any { it.url == url }) {
                        links.add(createLink(url, "Regex-$quality", response.url, url.contains("m3u8")))
                    }
                }
            }
            
            // URLs gerais de video
            val generalPattern = Regex("https?://[^\"'<>\\s]+\\.(?:m3u8|mp4|webm)[^\"'<>\\s]*")
            generalPattern.findAll(html).forEach { match ->
                val url = match.value.trim()
                if (!links.any { it.url == url }) {
                    val quality = detectQuality(url)
                    links.add(createLink(url, "Regex-$quality", response.url, url.contains("m3u8")))
                }
            }
        } catch (e: Exception) { }
        
        return links
    }

    private fun decryptAES(encrypted: ByteArray, userId: String, slug: String, md5Id: String): String? {
        return try {
            val keyStr = MessageDigest.getInstance("MD5").run {
                update("$userId:$slug:$md5Id".toByteArray())
                digest().joinToString("") { "%02x".format(it) }
            }
            val key = keyStr.toByteArray()
            val iv = key.copyOfRange(0, 16)
            
            val cipher = Cipher.getInstance("AES/CTR/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(iv))
            String(cipher.doFinal(encrypted))
        } catch (e: Exception) { null }
    }
    
    private fun detectQuality(url: String): String {
        return when {
            url.contains("1080") -> "1080p"
            url.contains("720") -> "720p"
            url.contains("480") -> "480p"
            url.contains("360") -> "360p"
            else -> "Auto"
        }
    }
    
    private suspend fun createLink(url: String, quality: String, referer: String, isM3u8: Boolean): ExtractorLink {
        val type = if (isM3u8) ExtractorLinkType.M3U8 else ExtractorLinkType.VIDEO
        val qualValue = when {
            quality.contains("1080") -> Qualities.P1080.value
            quality.contains("720") -> Qualities.P720.value
            quality.contains("480") -> Qualities.P480.value
            quality.contains("360") -> Qualities.P360.value
            else -> Qualities.Unknown.value
        }
        
        return newExtractorLink(
            source = name,
            name = "$name [$quality]",
            url = url,
            type = type
        ) {
            this.referer = referer
            this.quality = qualValue
            this.headers = mapOf("User-Agent" to USER_AGENTS.random(), "Referer" to referer)
        }
    }
}
