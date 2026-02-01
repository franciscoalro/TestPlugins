package com.doramas

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class DoramasPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(Doramas())
    }
}
