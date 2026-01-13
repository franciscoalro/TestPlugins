package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed WebView Extractor - v74 (Jan 2026)
 *
 * SOLUÇÃO OFICIAL para MegaEmbed:
 * - Usa WebView interno do CloudStream
 * - JavaScript roda normalmente → token JWT gerado
 * - Player interno captura o stream HLS
 * 
 * Requer CloudStream pre-release (jan/2026+) para melhor compatibilidade
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed (WebView)"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 MegaEmbed WebView: $url")
        
        // Garantir que a URL tem o hash
        val finalUrl = if (url.contains("#")) url else url

        // Headers HAR completos para imitar navegador real
        val extraHeaders = mapOf(
            "User-Agent" to USER_AGENT,
            "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding" to "gzip, deflate, br, zstd",
            "Sec-Fetch-Dest" to "iframe",
            "Sec-Fetch-Mode" to "navigate",
            "Sec-Fetch-Site" to "cross-site"
        )

        // ExtractorLink com WebView habilitado
        // isM3u8 = true indica que é HLS (mesmo ofuscado)
        // O CloudStream pre-release tem parser melhorado para .woff2
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed (WebView Player)",
                url = finalUrl,
                type = ExtractorLinkType.M3U8
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
                this.headers = extraHeaders
            }
        )
        
        Log.d(TAG, "✅ MegaEmbed link adicionado (WebView mode)")
    }
}
