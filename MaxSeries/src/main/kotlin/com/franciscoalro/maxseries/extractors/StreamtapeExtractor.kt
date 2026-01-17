package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.BRExtractorUtils
import android.util.Log

/**
 * Streamtape Extractor - PRIORITY 1
 * Baseado nos padrões do PobreFlixExtractor (saimuelrepo)
 * 
 * Streamtape usa um sistema de token rotativo que precisa ser
 * extraído do HTML e concatenado com a URL base
 */
class StreamtapeExtractor : ExtractorApi() {
    override var name = "Streamtape"
    override var mainUrl = "https://streamtape.com"
    override val requiresReferer = true

    companion object {
        private const val TAG = "StreamtapeExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        fun canHandle(url: String): Boolean = BRExtractorUtils.isStreamtape(url)
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Iniciando extração Streamtape: $url")
        
        try {
            val response = app.get(
                url,
                referer = referer ?: mainUrl,
                headers = mapOf("User-Agent" to USER_AGENT)
            )
            
            val html = response.text
            
            // Padrão 1: Extrair URL do div#videolink
            val tokenPattern = Regex("""'robotlink'\)\.innerHTML = '([^']+)'\+ \('([^']+)'\)""")
            val match = tokenPattern.find(html)
            
            val videoUrl = if (match != null) {
                val part1 = match.groupValues[1]
                val part2 = match.groupValues[2]
                "https:$part1$part2"
            } else {
                // Padrão alternativo
                val altPattern = Regex("""document\.getElementById\('norobotlink'\)\.innerHTML = '([^']+)'""")
                val altMatch = altPattern.find(html)
                if (altMatch != null) {
                    "https:${altMatch.groupValues[1]}"
                } else {
                    // Fallback: tentar extrair direto
                    val directPattern = Regex("""(https?://[^/]+/get_video\?[^"'\s]+)""")
                    directPattern.find(html)?.value
                }
            }
            
            if (videoUrl != null && videoUrl.contains("/get_video")) {
                Log.d(TAG, "✅ URL capturada: $videoUrl")
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name HD",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = url
                        this.quality = Qualities.P720.value
                        this.headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Referer" to url
                        )
                    }
                )
            } else {
                Log.e(TAG, "❌ Não foi possível extrair URL de vídeo")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro Streamtape: ${e.message}")
        }
    }
}
