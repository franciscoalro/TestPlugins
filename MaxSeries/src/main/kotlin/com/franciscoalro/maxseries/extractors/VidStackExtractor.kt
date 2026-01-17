package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * VidStack Extractor - Para players EmbedPlay
 * Baseado no padrão do UltraCine/Doramas (saimuelrepo)
 * 
 * Suporta:
 * - embedplay.upns.ink
 * - embedplay.upn.one
 * - Outros VidStack-based players
 */
open class VidStackExtractor : ExtractorApi() {
    override var name = "VidStack"
    override var mainUrl = "https://embedplay.upns.ink"
    override val requiresReferer = true

    companion object {
        private const val TAG = "VidStackExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        val SUPPORTED_DOMAINS = listOf(
            "embedplay.upns.ink",
            "embedplay.upn.one",
            "embed.upns.ink",
            "embed.upn.one"
        )
        
        fun canHandle(url: String): Boolean = 
            SUPPORTED_DOMAINS.any { url.contains(it, ignoreCase = true) }
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Iniciando extração VidStack: $url")
        
        try {
            val response = app.get(
                url,
                referer = referer,
                headers = mapOf("User-Agent" to USER_AGENT)
            )
            
            val html = response.text
            
            // VidStack pattern: sources array no JavaScript
            val patterns = listOf(
                Regex("""sources\s*:\s*\[\s*\{\s*(?:src|file)\s*:\s*["']([^"']+)["']"""),
                Regex("""file\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex("""source\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
                Regex(""""([^"]+\.m3u8[^"]*)"""")
            )
            
            var videoUrl: String? = null
            
            for (pattern in patterns) {
                val match = pattern.find(html)
                if (match != null) {
                    videoUrl = match.groupValues[1].replace("\\/", "/")
                    if (videoUrl.startsWith("http")) break
                }
            }
            
            if (videoUrl != null) {
                Log.d(TAG, "✅ URL capturada: $videoUrl")
                
                val links = if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(
                        name, videoUrl, url,
                        headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Referer" to url
                        )
                    )
                } else {
                    listOf(
                        newExtractorLink(
                            source = name,
                            name = "$name HD",
                            url = videoUrl,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = url
                            this.quality = Qualities.P720.value
                        }
                    )
                }
                
                links.forEach { callback(it) }
            } else {
                Log.e(TAG, "❌ Não foi possível extrair URL de vídeo")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro VidStack: ${e.message}")
        }
    }
}

/**
 * EmbedPlay variantes para registro individual
 */
class EmbedPlayUpnsInk : VidStackExtractor() {
    override var name = "EmbedPlay Ink"
    override var mainUrl = "https://embedplay.upns.ink"
}

class EmbedPlayUpnOne : VidStackExtractor() {
    override var name = "EmbedPlay One"
    override var mainUrl = "https://embedplay.upn.one"
}
