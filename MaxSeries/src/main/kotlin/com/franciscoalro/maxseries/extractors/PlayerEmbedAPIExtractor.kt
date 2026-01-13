package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v76 - WebView Required (Jan 2026)
 * 
 * MUDANÇA IMPORTANTE (Jan 2026):
 * - PlayerEmbedAPI agora usa criptografia AES-CTR no campo "media"
 * - A descriptografia acontece via JavaScript (core.bundle.js)
 * - NÃO é possível extrair via HTTP simples
 * - Solução: usar WebView interno do CloudStream
 * 
 * Fluxo atual:
 * 1. GET playerembedapi.link/?v=xxx → HTML com dados Base64
 * 2. JavaScript descriptografa campo "media" com AES-CTR
 * 3. JWPlayer carrega o vídeo (MP4 do Google Cloud Storage)
 * 
 * Prioridade mantida como 1 porque:
 * - Quando funciona, é MP4 direto (melhor qualidade)
 * - WebView do CloudStream executa o JS automaticamente
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
            // Primeiro, tentar extrair via HTTP (caso volte ao formato antigo)
            val response = app.get(
                url, 
                referer = referer,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                )
            )
            
            val text = response.text
            Log.d(TAG, "📄 Resposta (${text.length} chars)")
            
            // Verificar se é o novo formato (HTML com dados criptografados)
            val isNewFormat = text.contains("SoTrym") || text.contains("iamcdn.net") || text.contains("core.bundle.js")
            
            if (isNewFormat) {
                Log.d(TAG, "🔐 Formato novo detectado (AES-CTR) - usando WebView")
                
                // Headers modernos para WebView
                val extraHeaders = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Sec-Fetch-Dest" to "iframe",
                    "Sec-Fetch-Mode" to "navigate",
                    "Sec-Fetch-Site" to "cross-site"
                )
                
                // Retornar link para WebView processar
                // CloudStream vai executar o JavaScript e capturar o vídeo
                callback.invoke(
                    newExtractorLink(
                        source = this.name,
                        name = "$name (WebView)",
                        url = url,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = referer ?: mainUrl
                        this.quality = Qualities.Unknown.value
                        this.headers = extraHeaders
                    }
                )
                Log.d(TAG, "✅ Link WebView adicionado: $url")
                return
            }
            
            // Formato antigo: tentar parsear JSON
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
                Log.d(TAG, "⚠️ Não é JSON válido")
            }
            
            // Fallback: extrair URLs via regex
            val filePattern = Regex(""""file"\s*:\s*"([^"]+)"""")
            val files = filePattern.findAll(text).map { it.groupValues[1] }.toList()
            
            if (files.isNotEmpty()) {
                Log.d(TAG, "✅ Regex encontrou ${files.size} files")
                
                files.forEach { file ->
                    val linkType = if (file.contains(".m3u8")) ExtractorLinkType.M3U8 else ExtractorLinkType.VIDEO
                    
                    callback.invoke(
                        newExtractorLink(
                            source = this.name,
                            name = "$name",
                            url = file,
                            type = linkType
                        ) {
                            this.referer = referer ?: mainUrl
                            this.quality = Qualities.Unknown.value
                            this.headers = mapOf("User-Agent" to USER_AGENT)
                        }
                    )
                    Log.d(TAG, "✅ Link (regex): $file")
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
    
    // Data classes para parsing JSON (formato antigo)
    data class PlayerEmbedResponse(
        val sources: List<Source> = emptyList()
    )
    
    data class Source(
        val file: String = "",
        val label: String? = null,
        val type: String? = null
    )
}
