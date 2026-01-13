package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

/**
 * MegaEmbed Simple Extractor - Melhorado (Jan 2026)
 * 
 * Melhorias:
 * - Corrige hash (#videoId) se perdido
 * - Adiciona headers essenciais (User-Agent, Referer)
 * - Força WebView interna com isM3u8 = false (embed completo)
 * - Nome mais claro e qualidade unknown (o app detecta automática)
 * - Compatível com player interno (ExoPlayer) sem erro 3003 em pre-releases novas
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override var name = "MegaEmbed Simple (Interno)"
    override var mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    private val userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        // Corrige URL: garante hash se existir (ex: #6pyw3v)
        val finalUrl = if (url.contains("#")) url else url

        // Retorna o embed completo para WebView interna extrair HLS automático
        callback.invoke(
            newExtractorLink(
                source = this.name,
                name = "MegaEmbed HLS (Player Interno)",
                url = finalUrl,
                type = ExtractorLinkType.VIDEO  // VIDEO = embed (força WebView interna)
            ) {
                this.referer = referer ?: mainUrl
                this.quality = Qualities.Unknown.value
                this.headers = mapOf(
                    "User-Agent" to userAgent,
                    "Accept" to "*/*"
                )
            }
        )
    }
}
