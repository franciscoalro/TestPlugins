package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import kotlinx.coroutines.delay

/**
 * MegaEmbed Simple Extractor v3
 * 
 * Baseado na análise do Burp Suite (Jan 2026):
 * - playerthree.online/episodio/{id} → megaembed.link/#videoId
 * - megaembed.link gera token JWT via /api/v1/player
 * - CDN rotativo: sbi6/s6p9/srcf.marvellaholdings.sbs
 * - HLS: cf-master.txt → index-f1/f2.txt → segmentos
 * 
 * Solução: retorna embed para WebView interno do CloudStream
 * com headers corretos e delay para JS gerar token.
 */
class MegaEmbedSimpleExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MegaEmbedSimple"
        private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MegaEmbed Simple Extractor v3 ===")
        Log.d(TAG, "URL recebida: $url")
        Log.d(TAG, "Referer: $referer")
        
        // 1. Corrigir URL - manter hash se existir
        val finalUrl = if (url.contains("#")) {
            Log.d(TAG, "✅ URL tem hash, mantendo original")
            url
        } else {
            val videoId = extractVideoId(url)
            if (!videoId.isNullOrBlank()) {
                val constructed = "https://megaembed.link/#$videoId"
                Log.d(TAG, "🔧 Construindo URL com hash: $constructed")
                constructed
            } else {
                Log.d(TAG, "⚠️ Sem videoId, usando URL original")
                url
            }
        }
        
        Log.d(TAG, "📺 URL final para WebView: $finalUrl")
        
        // 2. Retornar embed para WebView interno do CloudStream
        // O CloudStream abre em WebView, executa JS, e extrai HLS automaticamente
        callback(
            newExtractorLink(
                source = name,
                name = "$name - WebView",
                url = finalUrl
            ) {
                this.referer = "https://megaembed.link/"
                this.quality = Qualities.Unknown.value
                this.headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                )
            }
        )
        
        Log.d(TAG, "✅ ExtractorLink emitido com headers!")
        
        // 3. Delay para dar tempo do WebView carregar e JS gerar token
        delay(5000)
        Log.d(TAG, "⏱️ Delay concluído")
    }
    
    /**
     * Extrai videoId de diferentes formatos de URL
     */
    private fun extractVideoId(url: String): String? {
        val patterns = listOf(
            Regex("""#([a-zA-Z0-9]+)"""),           // #3wnuij
            Regex("""/embed/([a-zA-Z0-9]+)"""),     // /embed/3wnuij
            Regex("""[?&]v=([a-zA-Z0-9]+)"""),      // ?v=3wnuij
            Regex("""[?&]id=([a-zA-Z0-9]+)"""),     // ?id=3wnuij
            Regex("""megaembed\.[^/]+/([a-zA-Z0-9]{4,10})/?$""") // /3wnuij
        )
        
        for (pattern in patterns) {
            val match = pattern.find(url)
            if (match != null) {
                val id = match.groupValues[1]
                Log.d(TAG, "🔍 VideoId extraído: $id")
                return id
            }
        }
        
        return null
    }
}
