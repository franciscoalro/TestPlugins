package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MediaFire Extractor
 * Inspirado no padrão FilmesOn
 * 
 * Extrai links diretos de download do MediaFire
 */
class MediaFireExtractor : ExtractorApi() {
    override val name = "MediaFire"
    override val mainUrl = "https://www.mediafire.com"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MediaFireExtractor"
        
        fun canHandle(url: String): Boolean {
            return url.contains("mediafire.com", ignoreCase = true)
        }
    }
    
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🔗 Extraindo MediaFire: $url")
        
        runCatching {
            // Buscar página do MediaFire com headers customizados
            val headers = HeadersBuilder.standard(referer)
            val document = app.get(url, headers = headers).document
            
            // Extrair botão de download
            val downloadButton = document.select("a#downloadButton").attr("href")
            
            if (downloadButton.isNotEmpty() && LinkDecryptor.isUrl(downloadButton)) {
                Log.d(TAG, "✅ Link direto encontrado: $downloadButton")
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name - Direct Download",
                        url = downloadButton,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = mainUrl
                        this.quality = Qualities.P1080.value
                        this.headers = HeadersBuilder.mediaFire(url)
                    }
                )
            } else {
                Log.w(TAG, "⚠️ Botão de download não encontrado")
            }
        }.getOrElse { error ->
            Log.e(TAG, "❌ Erro ao extrair MediaFire: ${error.message}")
        }
    }
}
