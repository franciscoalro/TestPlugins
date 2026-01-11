package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor para CloudStream
 * 
 * Versão simplificada para resolver problemas de compilação
 */
class MegaEmbedExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedExtractor"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        fun canHandle(url: String): Boolean {
            return DOMAINS.any { url.contains(it, ignoreCase = true) }
        }
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MegaEmbed Extractor v45 ===")
        Log.d(TAG, "URL: $url")
        
        try {
            // Tentativa de extração usando MegaEmbedLinkFetcher
            val videoId = MegaEmbedLinkFetcher.extractVideoId(url)
            if (videoId != null) {
                val playlistUrl = MegaEmbedLinkFetcher.fetchPlaylistUrl(videoId)
                if (playlistUrl != null) {
                    Log.d(TAG, "Playlist encontrada: $playlistUrl")
                    
                    // Usar M3u8Helper para HLS ou ExtractorLink direto para MP4
                    if (playlistUrl.contains(".m3u8")) {
                        M3u8Helper.generateM3u8(name, playlistUrl, referer ?: mainUrl).forEach(callback)
                    } else {
                        callback.invoke(
                            newExtractorLink(
                                name,
                                name,
                                playlistUrl
                            ) {
                                this.referer = referer ?: mainUrl
                                this.quality = Qualities.Unknown.value
                            }
                        )
                    }
                    return
                }
            }
            
            Log.e(TAG, "Falha ao extrair URL do MegaEmbed")
        } catch (e: Exception) {
            Log.e(TAG, "Erro na extração: ${e.message}")
        }
    }
}