package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.BasePlugin
import com.franciscoalro.maxseries.extractors.*

@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        // Registrar provider principal
        registerMainAPI(MaxSeriesProvider())
        
        // Registrar extractors principais (Prioridade 1 e 10)
        registerExtractorAPI(PlayerEmbedAPIExtractor())
        registerExtractorAPI(MegaEmbedSimpleExtractor())
        
        // Registrar extractors adicionais (Prioridade 2-9)
        registerExtractorAPI(MyVidPlayExtractor())
        registerExtractorAPI(StreamtapeExtractor())
        registerExtractorAPI(FilemoonExtractor())
        registerExtractorAPI(DoodStreamExtractor())
        registerExtractorAPI(MixdropExtractor())
        registerExtractorAPI(VidStackExtractor())
        registerExtractorAPI(MediaFireExtractor())
        // AjaxPlayerExtractor é um helper, não um ExtractorApi
    }
}
