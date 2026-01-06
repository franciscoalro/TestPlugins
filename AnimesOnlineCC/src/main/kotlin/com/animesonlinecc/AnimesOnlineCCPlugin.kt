package com.animesonlinecc

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class AnimesOnlineCCPlugin: BasePlugin() {
    override fun load() {
        // Registra o provedor de animes
        registerMainAPI(AnimesOnlineCCProvider())
    }
}
