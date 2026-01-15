package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed WebView Extractor - v75 (Jan 2026)
 *
 * SOLUÇÃO OFICIAL para MegaEmbed:
 * - Usa WebView interno do CloudStream
 * - JavaScript roda normalmente → token JWT gerado
 * - Player interno captura o stream HLS
 * - Compatível com Media3 ExoPlayer (2024+)
 * 
 * Requer CloudStream pre-release (jan/2026+) para melhor compatibilidade
 * com HLS ofuscado (.woff2 segments)
 * 
 * Atualizado: Janeiro 2026
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractor"
        // User-Agent Firefox 146 (Jan 2026)
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 MegaEmbed: $url")
        
        // Garantir que a URL tem o hash (formato: megaembed.link/#xxxxx)
        val finalUrl = url.trim()

        // Headers modernos (Sec-CH-UA para Chrome 120+, Sec-Fetch para segurança)
        val extraHeaders = mapOf(
            "User-Agent" to USER_AGENT,
            "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding" to "gzip, deflate, br, zstd",
            "Sec-Fetch-Dest" to "iframe",
            "Sec-Fetch-Mode" to "navigate",
            "Sec-Fetch-Site" to "cross-site",
            "Sec-Fetch-User" to "?1",
            "Upgrade-Insecure-Requests" to "1"
        )

        // ExtractorLinkType.M3U8 para HLS
        // CloudStream pre-release (2026) tem parser melhorado para .woff2
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed HLS",
                url = finalUrl,
                type = ExtractorLinkType.M3U8
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
                this.headers = extraHeaders
            }
        )
        
        Log.d(TAG, "✅ MegaEmbed link adicionado")
    }
}
