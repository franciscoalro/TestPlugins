package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed Simple Extractor v2
 * 
 * Solução: retorna o embed URL para o WebView interno do CloudStream.
 * Corrige problemas com hash (#) e URLs incompletas.
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedSimple"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MegaEmbed Simple Extractor v2 ===")
        Log.d(TAG, "URL recebida: $url")
        Log.d(TAG, "Referer: $referer")
        
        // Manter URL original se tiver hash (importante!)
        val finalUrl = if (url.contains("#")) {
            // URL já tem hash, usar como está
            Log.d(TAG, "✅ URL tem hash, mantendo original")
            url
        } else {
            // Tentar extrair videoId de outros padrões
            val videoId = extractVideoId(url)
            if (!videoId.isNullOrBlank()) {
                // Construir URL com hash
                val constructed = "https://megaembed.link/#$videoId"
                Log.d(TAG, "🔧 Construindo URL com hash: $constructed")
                constructed
            } else {
                // Usar URL original como fallback
                Log.d(TAG, "⚠️ Sem videoId, usando URL original")
                url
            }
        }
        
        Log.d(TAG, "📺 URL final: $finalUrl")
        
        // Retornar embed para o WebView interno do CloudStream
        callback(
            newExtractorLink(
                source = name,
                name = "$name Auto",
                url = finalUrl
            ) {
                this.referer = "https://megaembed.link/"
                this.quality = Qualities.Unknown.value
            }
        )
        
        Log.d(TAG, "✅ ExtractorLink emitido!")
    }
    
    /**
     * Extrai videoId de diferentes formatos de URL
     */
    private fun extractVideoId(url: String): String? {
        val patterns = listOf(
            Regex("""#([a-zA-Z0-9]+)"""),           // #3wnuij
            Regex("""/embed/([a-zA-Z0-9]+)"""),     // /embed/3wnuij
            Regex("""[?&]v=([a-zA-Z0-9]+)"""),      // ?v=3wnuij
            Regex("""[?&]id=([a-zA-Z0-9]+)"""),     // ?id=3wnuij
            Regex("""megaembed\.[^/]+/([a-zA-Z0-9]{4,10})/?$""") // /3wnuij
        )
        
        for (pattern in patterns) {
            val match = pattern.find(url)
            if (match != null) {
                val id = match.groupValues[1]
                Log.d(TAG, "🔍 VideoId extraído: $id (padrão: ${pattern.pattern})")
                return id
            }
        }
        
        return null
    }
}
