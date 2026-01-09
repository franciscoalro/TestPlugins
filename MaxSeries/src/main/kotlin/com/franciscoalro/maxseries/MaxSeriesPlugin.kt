package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin

@CloudstreamPlugin
class MaxSeriesPlugin: Plugin() {
    override fun load() {
        // Registra o provedor de séries
        registerMainAPI(MaxSeriesProvider())
    }
}
