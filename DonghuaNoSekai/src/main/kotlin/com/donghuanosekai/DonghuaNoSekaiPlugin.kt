package com.donghuanosekai

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class DonghuaNoSekaiPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(DonghuaNoSekai())
    }
}
