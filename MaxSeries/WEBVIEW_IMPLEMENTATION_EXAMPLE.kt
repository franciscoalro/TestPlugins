// Exemplo de uso no MaxSeriesProvider.kt

// 1. No método loadLinks, adicionar:
override suspend fun loadLinks(
    data: String,
    isCasting: Boolean,
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
): Boolean {
    val loadData = parseJson<LoadData>(data)
    
    // Tentar PlayerEmbedAPI via WebView
    if (loadData.imdbId != null) {
        try {
            val extractor = PlayerEmbedAPIWebViewExtractor()
            val links = extractor.extract(loadData.imdbId)
            
            links.forEach { link ->
                callback(link)
            }
            
            if (links.isNotEmpty()) {
                return true
            }
        } catch (e: Exception) {
            Log.e("MaxSeries", "PlayerEmbedAPI failed: ${e.message}")
        }
    }
    
    // Fallback para outros extractors...
    return false
}
