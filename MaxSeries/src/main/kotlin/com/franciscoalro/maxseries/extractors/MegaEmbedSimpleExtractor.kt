package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed Simple Extractor
 * 
 * Solução simples: retorna o embed URL para o WebView interno do CloudStream.
 * O CloudStream abre em WebView e extrai o HLS automaticamente.
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
        Log.d(TAG, "=== MegaEmbed Simple Extractor ===")
        Log.d(TAG, "URL: $url")
        
        // Extrair videoId do hash
        val videoId = url.substringAfterLast("#", "").ifBlank {
            // Tentar outros padrões
            Regex("""/embed/([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
                ?: Regex("""[?&]v=([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
        }
        
        // Construir URL do embed
        val embedUrl = if (!videoId.isNullOrBlank() && !url.contains("/embed/")) {
            "https://megaembed.link/embed/$videoId"
        } else {
            url.substringBefore("#")
        }
        
        Log.d(TAG, "VideoId: $videoId")
        Log.d(TAG, "Embed URL: $embedUrl")
        
        // Retornar embed para o WebView interno do CloudStream
        callback(
            newExtractorLink(
                source = name,
                name = "$name (WebView)",
                url = embedUrl
            ) {
                this.referer = referer ?: "https://playerthree.online/"
                this.quality = Qualities.Unknown.value
            }
        )
        
        Log.d(TAG, "✅ Embed retornado para WebView interno")
    }
}
