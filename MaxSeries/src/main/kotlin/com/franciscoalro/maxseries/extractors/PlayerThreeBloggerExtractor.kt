package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache

/**
 * PlayerThree Blogger Extractor v1.0 (Jan 2026)
 * 
 * Extrai vídeos do fluxo:
 * playerthree.online/embed/xxx → tason.me/blogger → googlevideo.com
 * 
 * Fluxo:
 * 1. Acessa página de embed no playerthree.online
 * 2. Extrai contentId do HTML (16+ caracteres hex)
 * 3. Monta URL do tason.me/blogger/video-play.mp4
 * 4. Segue redirect 302 para obter URL do googlevideo
 * 5. Retorna link direto MP4
 * 
 * Exemplo de URL final:
 * https://rr4---sn-vgqsrnsr.googlevideo.com/videoplayback?expire=...&id=f8e5870c999ea89a...
 */
class PlayerThreeBloggerExtractor : ExtractorApi() {
    override var name = "PlayerThreeBlogger"
    override var mainUrl = "https://playerthree.online"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "PlayerThreeBlogger"
        private const val BLOGGER_BASE = "https://tason.me/blogger/video-play.mp4"
        
        // Mapeamento de itags para qualidades
        private val ITAG_QUALITY = mapOf(
            "5" to Pair(Qualities.P240.value, "240p"),
            "17" to Pair(Qualities.P144.value, "144p"),
            "18" to Pair(Qualities.P360.value, "360p"),   // Mais comum
            "22" to Pair(Qualities.P720.value, "720p"),
            "37" to Pair(Qualities.P1080.value, "1080p"),
            "43" to Pair(Qualities.P360.value, "360p"),
            "44" to Pair(Qualities.P480.value, "480p"),
            "45" to Pair(Qualities.P720.value, "720p"),
            "46" to Pair(Qualities.P1080.value, "1080p"),
            "160" to Pair(Qualities.P144.value, "144p"),
            "133" to Pair(Qualities.P240.value, "240p"),
            "134" to Pair(Qualities.P360.value, "360p"),
            "135" to Pair(Qualities.P480.value, "480p"),
            "136" to Pair(Qualities.P720.value, "720p"),
            "137" to Pair(Qualities.P1080.value, "1080p")
        )
    }
    
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        Log.d(TAG, "=== PlayerThreeBlogger v1.0 - Extraction Started ===")
        Log.d(TAG, "URL: $url")
        
        // 1. Verificar cache
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "✅ Cache HIT")
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)} (Cached)",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "$BLOGGER_BASE/"
                    this.quality = cached.quality
                }
            )
            return
        }
        
        try {
            // 2. Buscar página do embed
            Log.d(TAG, "[1/4] Buscando página de embed...")
            
            val headers = mapOf(
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding" to "gzip, deflate, br",
                "DNT" to "1",
                "Connection" to "keep-alive",
                "Upgrade-Insecure-Requests" to "1",
                "Sec-Fetch-Dest" to "document",
                "Sec-Fetch-Mode" to "navigate",
                "Sec-Fetch-Site" to "none",
                "Sec-Fetch-User" to "?1",
                "Cache-Control" to "max-age=0"
            )
            
            val response = app.get(url, headers = headers)
            val html = response.text
            
            Log.d(TAG, "📄 HTML recebido: ${html.length} chars")
            
            // 3. Extrair contentId
            Log.d(TAG, "[2/4] Extraindo contentId...")
            
            val contentId = extractContentId(html)
            if (contentId == null) {
                Log.e(TAG, "❌ contentId não encontrado no HTML")
                return
            }
            
            Log.d(TAG, "🆔 contentId: $contentId")
            
            // 4. Construir URL do blogger e seguir redirect
            Log.d(TAG, "[3/4] Seguindo redirect do blogger...")
            
            val bloggerUrl = "$BLOGGER_BASE/?contentId=$contentId"
            Log.d(TAG, "🔗 Blogger URL: $bloggerUrl")
            
            // Headers específicos para o blogger
            val bloggerHeaders = mapOf(
                "User-Agent" to headers["User-Agent"]!!,
                "Referer" to "https://playerthree.online/",
                "Accept" to "*/*",
                "Accept-Language" to "pt-BR,pt;q=0.9",
                "Origin" to "https://playerthree.online"
            )
            
            // Fazer HEAD request para seguir redirect
            val headResponse = app.get(
                bloggerUrl,
                headers = bloggerHeaders,
                allowRedirects = true,
                timeout = 30
            )
            
            val videoUrl = headResponse.url
            Log.d(TAG, "🎬 URL final: ${videoUrl.take(80)}...")
            
            // 5. Detectar qualidade do itag
            val (quality, qualityLabel) = detectQualityFromUrl(videoUrl)
            Log.d(TAG, "📊 Qualidade detectada: $qualityLabel (itag: ${extractItag(videoUrl)})")
            
            // 6. Salvar no cache e retornar
            VideoUrlCache.put(url, videoUrl, quality, name)
            
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name $qualityLabel (Direct)",
                    url = videoUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "$BLOGGER_BASE/"
                    this.quality = quality
                    this.headers = mapOf(
                        "User-Agent" to headers["User-Agent"]!!,
                        "Referer" to "$BLOGGER_BASE/"
                    )
                }
            )
            
            val duration = System.currentTimeMillis() - startTime
            Log.d(TAG, "✅ SUCESSO em ${duration}ms: $qualityLabel")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na extração: ${e.message}")
            e.printStackTrace()
        }
    }
    
    /**
     * Extrai contentId do HTML da página
     * Procura por padrões comuns de contentId (16+ caracteres hex)
     */
    private fun extractContentId(html: String): String? {
        // Padrões para extrair contentId
        val patterns = listOf(
            // Padrão mais comum: contentId = "f8e5870c999ea89a"
            Regex("""contentId["']?\s*[=:]\s*["']?([a-f0-9]{16,})["']?""", RegexOption.IGNORE_CASE),
            // URL do blogger: /blogger/video-play.mp4/?contentId=xxx
            Regex("""blogger/video-play\.mp4/\?contentId=([a-f0-9]+)""", RegexOption.IGNORE_CASE),
            // No iframe src
            Regex("""<iframe[^>]+src=["']([^"']*contentId=([a-f0-9]+))["']""", RegexOption.IGNORE_CASE),
            // Variável JavaScript
            Regex("""var\s+(?:videoId|contentId|id)\s*=\s*["']([a-f0-9]+)["']""", RegexOption.IGNORE_CASE),
            // JSON: "videoId": "xxx"
            Regex(""""videoId"\s*:\s*"([a-f0-9]+)"""", RegexOption.IGNORE_CASE),
            // JSON: "id": "xxx" (com 16+ chars)
            Regex(""""id"\s*:\s*"([a-f0-9]{16,})"""", RegexOption.IGNORE_CASE),
            // Qualquer string hex de 16+ chars que pareça um ID
            Regex("""["']([a-f0-9]{16})["']""", RegexOption.IGNORE_CASE)
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                // Pega o último grupo (geralmente o ID em si)
                val contentId = match.groupValues.last()
                if (contentId.length >= 16) {
                    Log.d(TAG, "🎯 Pattern matched: ${pattern.pattern.take(50)}...")
                    return contentId
                }
            }
        }
        
        return null
    }
    
    /**
     * Extrai itag da URL do googlevideo
     */
    private fun extractItag(url: String): String {
        val itagPattern = Regex("""[?&]itag=(\d+)""")
        return itagPattern.find(url)?.groupValues?.get(1) ?: "18" // Default 360p
    }
    
    /**
     * Detecta qualidade baseada no itag da URL
     */
    private fun detectQualityFromUrl(url: String): Pair<Int, String> {
        val itag = extractItag(url)
        val (quality, label) = ITAG_QUALITY[itag] ?: Pair(Qualities.P360.value, "360p")
        return Pair(quality, label)
    }
    
    /**
     * Extrai título do vídeo do HTML (para logging)
     */
    private fun extractTitle(html: String): String {
        val titlePatterns = listOf(
            Regex("""<title>([^<]+)</title>"""),
            Regex(""""title"\s*:\s*"([^"]+)""""),
            Regex("""property="og:title"\s+content="([^"]+)""")
        )
        
        for (pattern in titlePatterns) {
            val match = pattern.find(html)
            if (match != null) {
                return match.groupValues[1].trim()
            }
        }
        
        return "Unknown"
    }
}
