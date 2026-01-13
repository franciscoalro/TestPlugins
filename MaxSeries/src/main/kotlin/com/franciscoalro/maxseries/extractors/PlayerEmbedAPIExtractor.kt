package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v75 - MP4 direto do Google Cloud Storage
 * 
 * PRIORIDADE 1 - Melhor opção:
 * - MP4 direto sem JavaScript
 * - Compatível com ExoPlayer (Media3 2024+)
 * - Evita erro 3003
 * - Usa NiceHttp (wrapper moderno do OkHttp 4.12)
 * 
 * Fluxo:
 * 1. GET playerembedapi.link/?v=xxx
 * 2. Resposta JSON com sources[].file
 * 3. URL final: storage.googleapis.com/...mp4
 * 
 * Atualizado: Janeiro 2026
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI"
        // User-Agent Firefox 146 (Jan 2026)
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 PlayerEmbedAPI: $url")
        
        try {
            val response = app.get(
                url, 
                referer = referer,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "application/json, text/plain, */*"
                )
            )
            
            val text = response.text
            Log.d(TAG, "📄 Resposta (${text.length} chars): ${text.take(500)}")
            
            // Tentar parsear como JSON
            try {
                val json = response.parsedSafe<PlayerEmbedResponse>()
                if (json != null && json.sources.isNotEmpty()) {
                    Log.d(TAG, "✅ JSON parseado: ${json.sources.size} sources")
                    
                    json.sources.forEach { source ->
                        val file = source.file
                        val label = source.label ?: "Auto"
                        
                        if (file.isNotEmpty()) {
                            val linkType = if (file.contains(".m3u8")) ExtractorLinkType.M3U8 else ExtractorLinkType.VIDEO
                            
                            callback.invoke(
                                newExtractorLink(
                                    source = this.name,
                                    name = "$name $label",
                                    url = file,
                                    type = linkType
                                ) {
                                    this.referer = referer ?: mainUrl
                                    this.quality = getQualityFromName(label)
                                    this.headers = mapOf("User-Agent" to USER_AGENT)
                                }
                            )
                            Log.d(TAG, "✅ Link adicionado: $label -> $file")
                        }
                    }
                    return
                }
            } catch (e: Exception) {
                Log.d(TAG, "⚠️ Não é JSON válido, tentando regex...")
            }
            
            // Fallback: extrair URLs via regex
            val filePattern = Regex(""""file"\s*:\s*"([^"]+)"""")
            val labelPattern = Regex(""""label"\s*:\s*"([^"]+)"""")
            
            val files = filePattern.findAll(text).map { it.groupValues[1] }.toList()
            val labels = labelPattern.findAll(text).map { it.groupValues[1] }.toList()
            
            if (files.isNotEmpty()) {
                Log.d(TAG, "✅ Regex encontrou ${files.size} files")
                
                files.forEachIndexed { index, file ->
                    val label = labels.getOrNull(index) ?: "Auto"
                    val linkType = if (file.contains(".m3u8")) ExtractorLinkType.M3U8 else ExtractorLinkType.VIDEO
                    
                    callback.invoke(
                        newExtractorLink(
                            source = this.name,
                            name = "$name $label",
                            url = file,
                            type = linkType
                        ) {
                            this.referer = referer ?: mainUrl
                            this.quality = getQualityFromName(label)
                            this.headers = mapOf("User-Agent" to USER_AGENT)
                        }
                    )
                    Log.d(TAG, "✅ Link (regex): $label -> $file")
                }
                return
            }
            
            // Último fallback: URL direta de storage.googleapis.com
            val gcsPattern = Regex("""https?://storage\.googleapis\.com/[^"'\s]+\.mp4""")
            gcsPattern.findAll(text).forEach { match ->
                val gcsUrl = match.value
                callback.invoke(
                    newExtractorLink(
                        source = this.name,
                        name = "$name (GCS Direct)",
                        url = gcsUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = referer ?: mainUrl
                        this.quality = Qualities.Unknown.value
                        this.headers = mapOf("User-Agent" to USER_AGENT)
                    }
                )
                Log.d(TAG, "✅ Link (GCS): $gcsUrl")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro: ${e.message}")
        }
    }
    
    // Data classes para parsing JSON
    data class PlayerEmbedResponse(
        val sources: List<Source> = emptyList()
    )
    
    data class Source(
        val file: String = "",
        val label: String? = null,
        val type: String? = null
    )
}
