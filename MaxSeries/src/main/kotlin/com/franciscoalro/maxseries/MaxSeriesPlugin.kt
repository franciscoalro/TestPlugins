package com.franciscoalro.maxseries

import android.content.Context
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin

@CloudstreamPlugin
class MaxSeriesPlugin: Plugin() {
    override fun load(context: Context) {
        registerMainAPI(MaxSeriesProvider())
    }
}
