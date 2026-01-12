package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * MegaEmbed Extractor v6 - WebView Interception
 * 
 * Baseado na descoberta que o HLS só é gerado após:
 * 1. WebView carrega a página
 * 2. JavaScript executa
 * 3. CDN libera o cf-master.txt
 * 
 * Padrão interceptado: marvellaholdings.sbs/v4/.../cf-master.{timestamp}.txt
 */
class MegaEmbedExtractorV6 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedV6"
        
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
        Log.d(TAG, "=== MegaEmbed Extractor v6 - WebView Interception ===")
        Log.d(TAG, "URL: $url")
        Log.d(TAG, "Referer: $referer")
        
        try {
            // Usar WebViewResolver para interceptar o cf-master.txt
            val resolver = WebViewResolver(
                // Interceptar URLs do CDN marvellaholdings que contenham cf-master
                interceptUrl = Regex("""marvellaholdings\.sbs.*cf-master.*\.txt"""),
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""master\.txt""")
                ),
                timeout = 30_000L
            )
            
            Log.d(TAG, "Iniciando WebView para: $url")
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
                    "Referer" to (referer ?: "https://playerthree.online/")
                ),
                interceptor = resolver
            )
            
            val interceptedUrl = response.url
            Log.d(TAG, "URL interceptada: $interceptedUrl")
            
            // Verificar se capturou o cf-master.txt
            if (interceptedUrl.contains("cf-master") && interceptedUrl.contains("marvellaholdings")) {
                Log.d(TAG, "✅ HLS capturado via WebView: $interceptedUrl")
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name HLS",
                        url = interceptedUrl,
                        type = ExtractorLinkType.M3U8
                    ) {
                        this.referer = "https://megaembed.link/"
                        this.quality = Qualities.P1080.value
                        this.headers = mapOf(
                            "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
                            "Referer" to "https://megaembed.link/",
                            "Origin" to "https://megaembed.link"
                        )
                    }
                )
                
                Log.d(TAG, "✅ ExtractorLink emitido!")
                return
            }
            
            // Fallback: tentar construção direta do CDN
            Log.d(TAG, "WebView não capturou, tentando CDN direto...")
            if (tryDirectCdn(url, referer, callback)) {
                return
            }
            
            Log.e(TAG, "❌ Nenhum método funcionou")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro: ${e.message}")
            e.printStackTrace()
            
            // Fallback em caso de erro
            tryDirectCdn(url, referer, callback)
        }
    }
    
    /**
     * Fallback: tentar CDN direto (funciona em alguns casos)
     */
    private suspend fun tryDirectCdn(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val videoId = extractVideoId(url) ?: return false
        
        val cdns = listOf(
            "s6p9.marvellaholdings.sbs",
            "sipt.marvellaholdings.sbs",
            "stzm.marvellaholdings.sbs"
        )
        
        val timestamp = System.currentTimeMillis() / 1000
        
        for (cdn in cdns) {
            val m3u8Url = "https://$cdn/v4/x6b/$videoId/cf-master.$timestamp.txt"
            
            try {
                val response = app.get(
                    m3u8Url,
                    headers = mapOf(
                        "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
                        "Referer" to "https://megaembed.link/",
                        "Origin" to "https://megaembed.link"
                    ),
                    timeout = 10
                )
                
                if (response.isSuccessful && response.text.contains("#EXTM3U")) {
                    Log.d(TAG, "✅ CDN direto funcionou: $cdn")
                    
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name Direct",
                            url = m3u8Url,
                            type = ExtractorLinkType.M3U8
                        ) {
                            this.referer = "https://megaembed.link/"
                            this.quality = Qualities.P1080.value
                            this.headers = mapOf(
                                "User-Agent" to "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
                                "Referer" to "https://megaembed.link/",
                                "Origin" to "https://megaembed.link"
                            )
                        }
                    )
                    return true
                }
            } catch (e: Exception) {
                continue
            }
        }
        
        return false
    }

    private fun extractVideoId(url: String): String? {
        val hashPattern = Regex("""#([a-zA-Z0-9]+)""")
        hashPattern.find(url)?.let { return it.groupValues[1] }
        
        val pathPattern = Regex("""/([a-zA-Z0-9]{5,10})/?$""")
        pathPattern.find(url)?.let { return it.groupValues[1] }
        
        return null
    }
}
