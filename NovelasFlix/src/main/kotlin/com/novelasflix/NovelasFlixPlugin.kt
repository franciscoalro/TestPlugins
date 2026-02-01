package com.novelasflix

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class NovelasFlixPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(NovelasFlix())
    }
}
