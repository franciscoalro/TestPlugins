
/**
 * PlayerThree Extractor - Auto-generated from pentest
 * Target: playerthree.online
 */
class PlayerThreeExtractor : ExtractorApi() {
    override val name = "PlayerThree"
    override val mainUrl = "https://playerthree.online"
    override val requiresReferer = true
    
    private val headers = mapOf(
        "Referer" to "https://playerthree.online/",
        "Origin" to "https://playerthree.online",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "PlayerThree URL: $url")
        
        // MÉTODO 1: Extrair iframes
        val html = app.get(url, headers = headers).text
        
        val iframeRegex = """<iframe[^>]+src=["']([^"']+)["']""".toRegex()
        val iframes = iframeRegex.findAll(html).map { it.groupValues[1] }.toList()
        
        iframes.forEach { iframeUrl ->
            when {
                "playerembedapi" in iframeUrl.lowercase() -> {
                    // Usar PlayerEmbedAPIExtractorV7 (WebView)
                    val extractor = PlayerEmbedAPIExtractorV7()
                    extractor.getUrl(iframeUrl, referer, subtitleCallback, callback)
                }
                "megaembed" in iframeUrl.lowercase() -> {
                    // Usar MegaEmbedExtractor
                    loadExtractor(iframeUrl, referer, subtitleCallback, callback)
                }
                else -> {
                    // Tentar extração genérica
                    loadExtractor(iframeUrl, referer, subtitleCallback, callback)
                }
            }
        }
    }
}
