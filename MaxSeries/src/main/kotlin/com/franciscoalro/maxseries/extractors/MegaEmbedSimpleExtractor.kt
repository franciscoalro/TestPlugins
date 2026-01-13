package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

/**
 * MegaEmbed Simple Extractor - Com Headers HAR (Jan 2026)
 *
 * Melhorias:
 * - Headers do HAR (mais compatível)
 * - Corrige hash (#videoId)
 * - Força WebView interna com type=VIDEO
 * - Headers completos para capturar .txt camuflado (M3U8)
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed Simple (Interno)"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    private val userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        // Corrige URL com hash se perdido
        val finalUrl = if (url.contains("#")) url else url

        // Headers do HAR para imitar navegador real e capturar .txt camuflado
        val extraHeaders = mapOf(
            "User-Agent" to userAgent,
            "Accept" to "*/*",
            "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With" to "XMLHttpRequest",
            "Sec-Fetch-Dest" to "empty",
            "Sec-Fetch-Mode" to "cors",
            "Sec-Fetch-Site" to "same-origin"
        )

        // Retorna embed para WebView interna capturar HLS
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed HLS (Player Interno)",
                url = finalUrl,
                type = ExtractorLinkType.VIDEO  // Força WebView interna
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
                this.headers = extraHeaders
            }
        )
    }
}
