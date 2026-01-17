package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.BRExtractorUtils
import com.franciscoalro.maxseries.utils.JsUnpacker
import android.util.Log

/**
 * Mixdrop Extractor - PRIORITY 4
 * Baseado nos padrões do saimuelrepo
 * 
 * Mixdrop usa JavaScript packed (eval) para ofuscar a URL do vídeo
 */
class MixdropExtractor : ExtractorApi() {
    override var name = "Mixdrop"
    override var mainUrl = "https://mixdrop.co"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MixdropExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        fun canHandle(url: String): Boolean = BRExtractorUtils.isMixdrop(url)
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Iniciando extração Mixdrop: $url")
        
        try {
            val response = app.get(
                url,
                referer = referer ?: mainUrl,
                headers = mapOf("User-Agent" to USER_AGENT)
            )
            
            val html = response.text
            var videoUrl: String? = null
            
            // Tentar encontrar URL diretamente
            videoUrl = extractDirectUrl(html)
            
            // Se não encontrou, tentar descompactar JS
            if (videoUrl == null && JsUnpacker.isPacked(html)) {
                Log.d(TAG, "🔓 Detectado JS packed, descompactando...")
                
                val packedRegex = Regex(
                    """eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\).+?\}\s*\(.+?\)\s*\)""",
                    RegexOption.DOT_MATCHES_ALL
                )
                
                packedRegex.findAll(html).forEach { match ->
                    val unpacked = JsUnpacker.unpack(match.value)
                    if (!unpacked.isNullOrEmpty()) {
                        Log.d(TAG, "✅ JS descompactado (${unpacked.length} chars)")
                        videoUrl = extractVideoFromUnpacked(unpacked)
                        if (videoUrl != null) return@forEach
                    }
                }
            }
            
            if (videoUrl != null) {
                // Mixdrop às vezes retorna URL relativa
                val finalUrl = if (videoUrl!!.startsWith("//")) {
                    "https:$videoUrl"
                } else if (!videoUrl!!.startsWith("http")) {
                    // Extrair domínio da URL original
                    val domain = Regex("""https?://([^/]+)""").find(url)?.groupValues?.get(1) ?: "mixdrop.co"
                    "https://$domain$videoUrl"
                } else {
                    videoUrl!!
                }
                
                Log.d(TAG, "✅ URL capturada: $finalUrl")
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name HD",
                        url = finalUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = url
                        this.quality = Qualities.P720.value
                        this.headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Referer" to url
                        )
                    }
                )
            } else {
                Log.e(TAG, "❌ Não foi possível extrair URL de vídeo")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro Mixdrop: ${e.message}")
        }
    }
    
    private fun extractDirectUrl(html: String): String? {
        val patterns = listOf(
            Regex("""MDCore\.vsrc\s*=\s*["']([^"']+)["']"""),
            Regex("""MDCore\.wurl\s*=\s*["']([^"']+)["']"""),
            Regex("""source\s*:\s*["']([^"']+\.mp4[^"']*)["']"""),
            Regex(""""([^"]+deliverycdn[^"]+)"""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                return match.groupValues[1].replace("\\/", "/")
            }
        }
        return null
    }
    
    private fun extractVideoFromUnpacked(unpacked: String): String? {
        val patterns = listOf(
            Regex("""MDCore\.vsrc\s*=\s*["']([^"']+)["']"""),
            Regex("""MDCore\.wurl\s*=\s*["']([^"']+)["']"""),
            Regex("""vsrc\s*=\s*["']([^"']+)["']"""),
            Regex("""wurl\s*=\s*["']([^"']+)["']"""),
            Regex(""""(\/\/[^"]+deliverycdn[^"]+)""""),
            Regex("""(https?://[^"'\s]+\.mp4[^"'\s]*)""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(unpacked)
            if (match != null) {
                return match.groupValues[1].replace("\\/", "/")
            }
        }
        return null
    }
}
