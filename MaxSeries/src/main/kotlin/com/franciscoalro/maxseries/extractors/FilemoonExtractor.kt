package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.BRExtractorUtils
import com.franciscoalro.maxseries.utils.JsUnpacker
import android.util.Log

/**
 * Filemoon Extractor - PRIORITY 2
 * Baseado nos padrões do OverFlixExtractor (saimuelrepo)
 * 
 * Filemoon usa JavaScript packed (eval) que precisa ser
 * descompactado para extrair a URL do vídeo HLS
 */
class FilemoonExtractor : ExtractorApi() {
    override var name = "Filemoon"
    override var mainUrl = "https://filemoon.sx"
    override val requiresReferer = true

    companion object {
        private const val TAG = "FilemoonExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        fun canHandle(url: String): Boolean = BRExtractorUtils.isFilemoon(url)
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Iniciando extração Filemoon: $url")
        
        try {
            val response = app.get(
                url,
                referer = referer ?: mainUrl,
                headers = mapOf("User-Agent" to USER_AGENT)
            )
            
            val html = response.text
            
            // Tentar extrair direto primeiro
            var videoUrl = extractDirectUrl(html)
            
            // Se não encontrou, tentar descompactar JS
            if (videoUrl == null && JsUnpacker.isPacked(html)) {
                Log.d(TAG, "🔓 Detectado JS packed, descompactando...")
                
                val packedRegex = Regex(
                    """eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\).+?\}\s*\(.+?\)\s*\)""",
                    RegexOption.DOT_MATCHES_ALL
                )
                
                val packedMatch = packedRegex.find(html)
                if (packedMatch != null) {
                    val unpacked = JsUnpacker.unpack(packedMatch.value)
                    if (!unpacked.isNullOrEmpty()) {
                        Log.d(TAG, "✅ JS descompactado (${unpacked.length} chars)")
                        videoUrl = extractVideoFromUnpacked(unpacked)
                    }
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
            Log.e(TAG, "❌ Erro Filemoon: ${e.message}")
        }
    }
    
    private fun extractDirectUrl(html: String): String? {
        val patterns = listOf(
            Regex("""file\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""source\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""sources\s*:\s*\[\s*\{\s*file\s*:\s*["']([^"']+)["']""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                return match.groupValues[1].replace("\\/", "/")
            }
        }
        return null
    }
    
    private fun extractVideoFromUnpacked(unpacked: String): String? {
        val patterns = listOf(
            Regex("""file\s*:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""sources\s*:\s*\[\s*\{[^}]*file\s*:\s*["']([^"']+)["']"""),
            Regex(""""([^"]+\.m3u8[^"]*)"""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(unpacked)
            if (match != null) {
                val url = match.groupValues[1].replace("\\/", "/")
                if (url.startsWith("http")) return url
            }
        }
        return null
    }
}
