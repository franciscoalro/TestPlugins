package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

/**
 * MegaEmbed Simple Extractor - PreRelease (Jan 2026)
 *
 * Para funcionar 100%, use CloudStream pre-release (jan/2026+)
 * que tem parser atualizado para HLS ofuscado (.woff2)
 * 
 * - Headers HAR completos
 * - type=VIDEO força WebView interna
 * - Compatível com .txt camuflado (M3U8)
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed Simple (PreRelease)"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    private val userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val finalUrl = if (url.contains("#")) url else url

        // Headers HAR completos para imitar navegador real
        val extraHeaders = mapOf(
            "User-Agent" to userAgent,
            "Accept" to "*/*",
            "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding" to "gzip, deflate, br, zstd",
            "X-Requested-With" to "XMLHttpRequest",
            "Sec-Fetch-Dest" to "empty",
            "Sec-Fetch-Mode" to "cors",
            "Sec-Fetch-Site" to "same-origin"
        )

        // type=VIDEO força WebView interna (player interno do CloudStream)
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed HLS (Player Interno)",
                url = finalUrl,
                type = ExtractorLinkType.VIDEO
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
                this.headers = extraHeaders
            }
        )
    }
}
