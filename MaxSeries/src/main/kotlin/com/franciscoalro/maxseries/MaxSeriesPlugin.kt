package com.franciscoalro.maxseries

import android.content.Context
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin

// Importar TODOS os extractors necessários
import com.franciscoalro.maxseries.extractors.MegaEmbedExtractorV9
import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractorV8
import com.franciscoalro.maxseries.extractors.PlayerThreeBloggerExtractor
import com.franciscoalro.maxseries.extractors.MyVidPlayExtractor
import com.franciscoalro.maxseries.extractors.DoodStreamExtractor
import com.franciscoalro.maxseries.extractors.StreamtapeExtractor
import com.franciscoalro.maxseries.extractors.MixdropExtractor
import com.franciscoalro.maxseries.extractors.FilemoonExtractor

@CloudstreamPlugin
class MaxSeriesPlugin: Plugin() {
    override fun load(context: Context) {
        // Registrar provider principal
        registerMainAPI(MaxSeriesProvider())
        
        // Registrar TODOS os extractors necessários
        registerExtractorAPI(MegaEmbedExtractorV9())
        registerExtractorAPI(PlayerEmbedAPIExtractorV8())
        registerExtractorAPI(PlayerThreeBloggerExtractor())
        registerExtractorAPI(MyVidPlayExtractor())
        registerExtractorAPI(DoodStreamExtractor())
        registerExtractorAPI(StreamtapeExtractor())
        registerExtractorAPI(MixdropExtractor())
        registerExtractorAPI(FilemoonExtractor())
    }
}
