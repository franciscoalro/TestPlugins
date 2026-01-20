package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.BasePlugin
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV7

@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        // Registrar provider principal
        registerMainAPI(MaxSeriesProvider())
        
        // Registrar apenas MegaEmbed V7 (único extractor necessário)
        registerExtractorAPI(MegaEmbedExtractorV7())
    }
}
