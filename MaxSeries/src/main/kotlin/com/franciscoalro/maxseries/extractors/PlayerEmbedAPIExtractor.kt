package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v4.1 - ENHANCED BASE64 DETECTION (Jan 2026)
 * 
 * v4.1 Changes (30 Jan 2026):
 * - 🔧 Múltiplos padrões de regex para encontrar base64 'datas'
 * - 🎯 Validação de base64 antes de usar
 * - 📄 Log do HTML quando não encontra (para debug)
 * - ⚡ Fallback para qualquer base64 grande no HTML
 * 
 * v4.0 Changes (30 Jan 2026):
 * - 🐍 PORTE: Algoritmo AES-CTR do PlayerEmbedAPI portado do Python
 * - 🎯 MULTI-QUALITY: Suporte a 360p, 720p, 1080p simultâneos
 * - 🚀 FALLBACK: Múltiplos métodos de extração
 * - ⚡ CACHE: Cache por qualidade individual
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        
        // Mapeamento de res_id para qualidade
        private val RES_ID_QUALITY = mapOf(
            2 to Qualities.P360,
            4 to Qualities.P720,
            5 to Qualities.P1080
        )
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        Log.wtf(TAG, "=== PlayerEmbedAPI v4.1 - Enhanced Detection ===")
        Log.d(TAG, "URL: $url")
        
        // 1. VERIFICAR CACHE
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
                    this.referer = "https://playerembedapi.link/"
                    this.quality = cached.quality
                }
            )
            return
        }
        
        // 2. FETCH HTML
        Log.d(TAG, "[1/5] Buscando HTML...")
        val html = try {
            val response = app.get(url, headers = HeadersBuilder.playerEmbed(url))
            
            if (response.code == 404) {
                Log.w(TAG, "❌ Vídeo não encontrado (404)")
                return
            }
            
            if (response.code >= 500) {
                Log.w(TAG, "❌ Servidor indisponível (${response.code})")
                return
            }
            
            Log.d(TAG, "✅ HTML carregado: ${response.text.length} chars")
            response.text
        } catch (e: Exception) {
            Log.e(TAG, "❌ Falha ao obter HTML: ${e.message}")
            return
        }
        
        // 3. ENHANCED BASE64 DETECTION (v4.1)
        Log.d(TAG, "[2/5] Procurando base64 'datas'...")
        
        val base64Data = findBase64Datas(html)
        
        if (base64Data == null) {
            Log.w(TAG, "⚠️ Base64 'datas' não encontrado em nenhum padrão")
            Log.d(TAG, "📄 HTML preview (primeiros 800 chars):")
            Log.d(TAG, html.take(800))
            
            // Fallback: tentar regex direto de URLs
            tryRegexFallback(html, url, callback)
            return
        }
        
        Log.d(TAG, "✅ Base64 encontrado: ${base64Data.take(50)}...")
        
        // 4. DECODIFICAR E DECRIPTAR
        try {
            // Decodificar base64
            val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
            val decodedJson = String(decodedBytes, Charsets.UTF_8)
            Log.d(TAG, "✅ JSON decodificado: ${decodedJson.take(200)}...")
            
            // Parse JSON
            val mapper = com.fasterxml.jackson.databind.ObjectMapper()
            val dataNode = mapper.readTree(decodedJson)
            
            // Extrair campos
            val mediaEncrypted = dataNode.get("media")?.asText()
            val userId = dataNode.get("user_id")?.asText()
            val slug = dataNode.get("slug")?.asText()
            val md5Id = dataNode.get("md5_id")?.asText()
            
            Log.d(TAG, "📋 Campos extraídos:")
            Log.d(TAG, "   - userId: $userId")
            Log.d(TAG, "   - slug: $slug")
            Log.d(TAG, "   - md5Id: $md5Id")
            Log.d(TAG, "   - media: ${mediaEncrypted?.length} chars")
            
            if (mediaEncrypted.isNullOrEmpty() || userId.isNullOrEmpty() || 
                slug.isNullOrEmpty() || md5Id.isNullOrEmpty()) {
                Log.w(TAG, "⚠️ Campos obrigatórios faltantes")
                return
            }
            
            Log.d(TAG, "🔓 Decriptando media com AES-CTR...")
            val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaEncrypted, userId, slug, md5Id)
            
            if (decrypted == null) {
                Log.e(TAG, "❌ Falha na decriptação AES-CTR")
                return
            }
            
            // 5. EXTRAIR URLs
            var foundAny = false
            
            // Extrair múltiplas qualidades do sources[]
            decrypted.sources?.let { sources ->
                Log.d(TAG, "📺 Encontradas ${sources.size} fontes:")
                
                sources.forEachIndexed { index, source ->
                    Log.d(TAG, "   [$index] ${source.label} - ${source.file.take(60)}...")
                    
                    val quality = when (source.label) {
                        "360p" -> Qualities.P360
                        "720p" -> Qualities.P720
                        "1080p" -> Qualities.P1080
                        else -> Qualities.Unknown
                    }
                    
                    VideoUrlCache.put("${url}_${source.label}", source.file, quality.value, name)
                    
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name ${source.label ?: "Auto"}",
                            url = source.file,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = "https://playerembedapi.link/"
                            this.quality = quality.value
                        }
                    )
                    foundAny = true
                }
            }
            
            // Fallback: HLS direto
            decrypted.hls?.let { hlsUrl ->
                Log.d(TAG, "📺 HLS: ${hlsUrl.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(hlsUrl)
                VideoUrlCache.put(url, hlsUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (HLS)",
                        url = hlsUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
            
            // Fallback: MP4 direto
            decrypted.mp4?.let { mp4Url ->
                Log.d(TAG, "📺 MP4: ${mp4Url.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(mp4Url)
                VideoUrlCache.put(url, mp4Url, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (MP4)",
                        url = mp4Url,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
            
            if (foundAny) {
                Log.wtf(TAG, "✅✅✅ SUCESSO: ${System.currentTimeMillis() - startTime}ms ✅✅✅")
            } else {
                Log.w(TAG, "⚠️ Nenhuma URL encontrada no JSON decriptado")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no processamento: ${e.message}")
            e.printStackTrace()
        }
    }
    
    /**
     * V4.1: Procura base64 'datas' com múltiplos padrões
     */
    private fun findBase64Datas(html: String): String? {
        val patterns = listOf(
            // Padrão 1: const datas = "..."
            Regex("""const\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 2: var datas = "..."
            Regex("""var\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 3: let datas = "..."
            Regex("""let\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 4: datas = "..." (sem const/var)
            Regex("""datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 5: data="..." (atributo)
            Regex("""data[=:]\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 6: Qualquer string base64 grande que comece com eyJ (eyJ = {")
            Regex(""""(eyJ[A-Za-z0-9+/=]{100,})"""),
        )
        
        for ((index, pattern) in patterns.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val candidate = match.groupValues[1]
                // Validar se é base64 válido
                try {
                    android.util.Base64.decode(candidate, android.util.Base64.DEFAULT)
                    Log.d(TAG, "✅ Pattern $index funcionou! Base64 válido.")
                    return candidate
                } catch (e: Exception) {
                    Log.d(TAG, "⚠️ Pattern $index encontrou match mas não é base64 válido")
                    continue
                }
            }
        }
        
        return null
    }
    
    /**
     * Fallback: Extrair URLs direto do HTML via regex
     */
    private suspend fun tryRegexFallback(
        html: String, 
        url: String, 
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "[3/5] Tentando HTML Regex fallback...")
        
        val patterns = listOf(
            Regex(""""(https?://[^"]+\.sssrr\.org/[^"]+)"""),
            Regex(""""(https?://[^"]+\.m3u8[^"]*)"""),
            Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""src:\s*["']([^"']+\.m3u8[^"']*)["']"""),
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                val videoUrl = match.groupValues[1]
                Log.d(TAG, "✅ Regex capturou: ${videoUrl.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (Regex)",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                
                Log.d(TAG, "✅ Regex fallback funcionou!")
                return
            }
        }
        
        Log.e(TAG, "❌ Todas as técnicas falharam")
    }
}
