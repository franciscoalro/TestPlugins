package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.BasePlugin
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV6
import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractor

@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        // Registrar provider principal
        registerMainAPI(MaxSeriesProvider())
        
        // Registrar extractors customizados
        registerExtractorAPI(MegaEmbedExtractorV6())
        registerExtractorAPI(PlayerEmbedAPIExtractor())
    }
}
