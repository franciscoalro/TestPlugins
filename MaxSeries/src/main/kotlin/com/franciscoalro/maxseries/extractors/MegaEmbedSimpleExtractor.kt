package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

/**
 * MegaEmbed Simple Extractor - Tenta HLS, fallback para WebView interna
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed Simple"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        // Retorna o embed para WebView interna (o app tenta extrair HLS sozinho)
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed HLS (Interno)",
                url = url,
                type = ExtractorLinkType.VIDEO
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
            }
        )
    }
}
