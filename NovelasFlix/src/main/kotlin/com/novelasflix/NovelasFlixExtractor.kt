package com.novelasflix

import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import android.util.Log

/**
 * Extractor de vídeos do NovelasFlix
 */
object NovelasFlixExtractor {
    private const val TAG = "NovelasFlixExtractor"

    suspend fun extractVideoLinks(
        url: String,
        mainUrl: String,
        name: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🎬 Extraindo links de: $url")
            
            val document = app.get(url).document
            var linksFound = 0
            
            // Procura por iframes de vídeo
            document.select("iframe[src]").forEach { iframe ->
                val src = iframe.attr("src")
                if (src.isNotBlank() && !src.contains("youtube", ignoreCase = true)) {
                    try {
                        loadExtractor(src, url, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Link encontrado: $src")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro ao extrair iframe: ${e.message}")
                    }
                }
            }
            
            // Procura por botões com data-source
            document.select("[data-source]").forEach { btn ->
                val src = btn.attr("data-source")
                if (src.isNotBlank()) {
                    try {
                        loadExtractor(src, url, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Link data-source: $src")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro ao extrair data-source: ${e.message}")
                    }
                }
            }
            
            // Procura por links diretos de player
            val playerLinks = document.select("div.playeroptions a, ul.playeroptions li a")
            playerLinks.forEach { link ->
                val href = link.attr("href")
                if (href.isNotBlank() && href.startsWith("http")) {
                    try {
                        loadExtractor(href, url, subtitleCallback, callback)
                        linksFound++
                        Log.d(TAG, "✅ Link player: $href")
                    } catch (e: Exception) {
                        Log.e(TAG, "⚠️ Erro ao extrair player link: ${e.message}")
                    }
                }
            }
            
            Log.d(TAG, "📊 Total de links encontrados: $linksFound")
            linksFound > 0
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair vídeos: ${e.message}")
            false
        }
    }
}
