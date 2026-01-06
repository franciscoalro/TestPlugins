package com.animesonlinecc

import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin
import android.content.Context

@CloudstreamPlugin
class AnimesOnlineCCPlugin: Plugin() {
    override fun load(context: Context) {
        // Registra o provedor de animes
        registerMainAPI(AnimesOnlineCCProvider())
    }
}
