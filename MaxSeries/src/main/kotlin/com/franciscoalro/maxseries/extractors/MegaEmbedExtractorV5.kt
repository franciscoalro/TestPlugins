package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v5 - Direct CDN Construction (Simplificado)
 * 
 * Descoberta Jan 2026:
 * - O CDN aceita QUALQUER timestamp (não precisa do exato do JS)
 * - Todos os CDNs conhecidos funcionam
 * - Não precisa decriptar a API nem usar WebView
 * 
 * Padrão: https://{cdn}/v4/x6b/{videoId}/cf-master.{timestamp}.txt
 */
class MegaEmbedExtractorV5 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedV5"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz", 
            "megaembed.to"
        )
        
        // CDNs testados e funcionando (Jan 2026)
        private val CDNS = listOf(
            "s6p9.marvellaholdings.sbs",
            "sipt.marvellaholdings.sbs",
            "stzm.marvellaholdings.sbs",
            "srcf.marvellaholdings.sbs",
            "sbi6.marvellaholdings.sbs"
        )
        
        // Shard padrão (funciona para todos os vídeos testados)
        private const val DEFAULT_SHARD = "x6b"
        
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
        Log.d(TAG, "=== MegaEmbed Extractor v5 ===")
        Log.d(TAG, "URL: $url")
        
        val videoId = extractVideoId(url)
        if (videoId == null) {
            Log.e(TAG, "VideoId não encontrado na URL")
            return
        }
        
        Log.d(TAG, "VideoId: $videoId")
        
        // Timestamp atual
        val timestamp = System.currentTimeMillis() / 1000
        
        // Tentar cada CDN até encontrar um que funcione
        for (cdn in CDNS) {
            val m3u8Url = "https://$cdn/v4/$DEFAULT_SHARD/$videoId/cf-master.$timestamp.txt"
            
            Log.d(TAG, "Testando: $m3u8Url")
            
            try {
                val response = app.get(
                    m3u8Url,
                    headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
                        "Referer" to mainUrl,
                        "Origin" to mainUrl
                    ),
                    timeout = 10
                )
                
                if (response.isSuccessful && response.text.contains("#EXTM3U")) {
                    Log.d(TAG, "CDN funcionando: $cdn")
                    
                    // Gerar links M3U8 com qualidades
                    M3u8Helper.generateM3u8(
                        name,
                        m3u8Url,
                        mainUrl
                    ).forEach(callback)
                    
                    Log.d(TAG, "Links emitidos com sucesso!")
                    return
                }
            } catch (e: Exception) {
                Log.d(TAG, "CDN $cdn falhou: ${e.message}")
                continue
            }
        }
        
        Log.e(TAG, "Nenhum CDN funcionou para videoId: $videoId")
    }

    private fun extractVideoId(url: String): String? {
        // Padrão: https://megaembed.link/#3wnuij
        val hashPattern = Regex("""#([a-zA-Z0-9]+)""")
        hashPattern.find(url)?.let { return it.groupValues[1] }
        
        // Padrão: https://megaembed.link/3wnuij
        val pathPattern = Regex("""/([a-zA-Z0-9]{5,10})/?$""")
        pathPattern.find(url)?.let { return it.groupValues[1] }
        
        // Padrão: ?id=3wnuij
        val queryPattern = Regex("""[?&]id=([a-zA-Z0-9]+)""")
        queryPattern.find(url)?.let { return it.groupValues[1] }
        
        return null
    }
}
