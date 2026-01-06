package com.cinebrasil

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin
import android.content.Context

@CloudstreamPlugin
class CineBrasilPlugin: Plugin() {
    override fun load(context: Context) {
        // Registra o provedor principal
        registerMainAPI(CineBrasilProvider())
    }
}
