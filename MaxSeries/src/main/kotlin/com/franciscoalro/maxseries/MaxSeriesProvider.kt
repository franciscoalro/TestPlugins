package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class MaxSeriesProvider: BasePlugin() {
    override fun load() {
        registerMainAPI(MaxSeries())
    }
}
