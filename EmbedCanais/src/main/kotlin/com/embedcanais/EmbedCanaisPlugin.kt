package com.embedcanais

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class EmbedCanaisPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(EmbedCanais())
    }
}
