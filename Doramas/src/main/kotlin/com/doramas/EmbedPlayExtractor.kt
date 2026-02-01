package com.doramas

import com.lagradost.cloudstream3.extractors.VidStack

/**
 * Extractores para players EmbedPlay usados em sites de dorama
 */

class EmbedPlayUpnsPro : VidStack() {
    override var name = "EmbedPlay Ink"
    override var mainUrl = "https://embedplay.upns.ink"
    override var requiresReferer = true
}

class EmbedPlayUpnOne : VidStack() {
    override var name = "EmbedPlay UpnOne"
    override var mainUrl = "https://embedplay.upn.one"
    override var requiresReferer = true
}
