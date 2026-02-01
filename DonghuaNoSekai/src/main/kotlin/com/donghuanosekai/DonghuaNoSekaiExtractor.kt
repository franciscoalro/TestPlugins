package com.donghuanosekai

import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.extractors.VidStack
import android.util.Log

/**
 * Extractor de vídeos do DonghuaNoSekai
 */
object DonghuaNoSekaiExtractor {
    private const val TAG = "DonghuaExtractor"

    suspend fun extractVideoLinks(
        url: String,
        mainUrl: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🎬 Extraindo links de: $url")
            
            val document = app.get(url).document
            var linksFound = 0
            
            // Procura por iframes de vídeo
            document.select("iframe[src]").forEach { iframe ->
                val src = iframe.attr("src").ifBlank { iframe.attr("data-src") }
                if (src.isNotBlank()) {
                    try {
                        loadExtractor(src, url, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Iframe: $src")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro iframe: ${e.message}")
                    }
                }
            }
            
            // Procura por botões com data-source (players do tipo dooplay)
            document.select("ul#playeroptionsul li").forEach { option ->
                val dataType = option.attr("data-type")
                val dataPost = option.attr("data-post")
                val dataNume = option.attr("data-nume")
                
                if (dataType.isNotEmpty() && dataPost.isNotEmpty() && dataNume.isNotEmpty()) {
                    try {
                        val ajaxUrl = "$mainUrl/wp-json/dooplayer/v2/$dataPost/$dataType/$dataNume"
                        val response = app.get(ajaxUrl, headers = mapOf("Referer" to url))
                        
                        // Extrai a URL do embed
                        val embedUrl = Regex(""""embed_url":"([^"]+)""")
                            .find(response.text)?.groupValues?.get(1)
                            ?.replace("\\/", "/")
                        
                        if (!embedUrl.isNullOrBlank()) {
                            loadExtractor(embedUrl, url, subtitleCallback, callback)
                            linksFound++
                            Log.d(TAG, "✅ Player option: $embedUrl")
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro player option: ${e.message}")
                    }
                }
            }
            
            Log.d(TAG, "📊 Total de links: $linksFound")
            linksFound > 0
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair vídeos: ${e.message}")
            false
        }
    }
}

/**
 * Extractor para players VidStack usados em donghuas
 */
class DonghuaPlayer : VidStack() {
    override var name = "DonghuaPlayer"
    override var mainUrl = "https://player.donghuanosekai.com"
    override var requiresReferer = true
}
