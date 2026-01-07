package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        // Registra o provedor de séries
        registerMainAPI(MaxSeriesProvider())
    }
}
