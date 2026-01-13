package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

/**
 * PlayerEmbedAPI Extractor - Extrai MP4 direto, evita erro 3003
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI (MP4)"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val response = app.get(url, referer = referer)
        val json = response.parsedSafe<Map<String, Any>>() ?: return
        val sources = json["sources"] as? List<Map<String, Any>> ?: return
        
        sources.forEach { source ->
            val file = source["file"] as? String ?: return@forEach
            val label = source["label"] as? String ?: "Auto"
            
            val linkType = if (file.contains(".m3u8")) ExtractorLinkType.M3U8 else ExtractorLinkType.VIDEO
            
            callback.invoke(
                newExtractorLink(
                    source = this.name,
                    name = "$name $label",
                    url = file,
                    type = linkType
                ) {
                    this.referer = referer ?: mainUrl
                    this.quality = getQualityFromName(label)
                }
            )
        }
    }
}
