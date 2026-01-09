package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.BasePlugin

@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(MaxSeriesProvider())
    }
}
