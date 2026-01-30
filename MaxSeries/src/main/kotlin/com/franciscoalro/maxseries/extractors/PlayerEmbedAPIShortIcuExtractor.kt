package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.QualityDetector
import com.franciscoalro.maxseries.utils.VideoUrlCache
import com.franciscoalro.maxseries.utils.ErrorLogger
import android.util.Log

/**
 * PlayerEmbedAPI ShortIcu Extractor v1.0 (Jan 2026)
 * 
 * ESTRATÉGIA:
 * 1. Acessa playerembedapi.link/?v={id}
 * 2. Extrai iframe short.icu do HTML
 * 3. Acessa short.icu e extrai vídeo direto do Google Cloud Storage
 * 
 * VANTAGENS:
 * - Não precisa de WebView
 * - Não precisa decriptar nada
 * - Extrai URL direta do vídeo MP4
 * - Mais rápido que métodos anteriores
 */
class PlayerEmbedAPIShortIcuExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI-ShortIcu"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        Log.d(TAG, "=== PlayerEmbedAPI ShortIcu Extractor v1.0 ===")
        Log.d(TAG, "URL: $url")
        
        // 1. VERIFICAR CACHE
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "Usando cache: ${cached.url}")
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)} (Cached)",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = url
                    this.quality = cached.quality
                }
            )
            return
        }

        try {
            // 2. OBTER HTML DO PLAYEREMBEDAPI
            Log.d(TAG, "[1/3] Obtendo HTML do PlayerEmbedAPI...")
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding" to "gzip, deflate, br",
                    "Connection" to "keep-alive",
                    "Upgrade-Insecure-Requests" to "1"
                ),
                timeout = 15
            )
            
            val html = response.text
            Log.d(TAG, "HTML recebido: ${html.length} chars")
            
            // 3. EXTRAIR IFRAME SHORT.ICU
            Log.d(TAG, "[2/3] Procurando iframe short.icu...")
            
            // Regex para extrair URL do short.icu
            val shortIcuPatterns = listOf(
                Regex("""<iframe[^>]+src\s*=\s*["'](https://short\.icu/[^"']+)["']"""),
                Regex("""src\s*=\s*["'](https://short\.icu/[^"']+)["']"""),
                Regex("""(https://short\.icu/[a-zA-Z0-9]+)""")
            )
            
            var shortIcuUrl: String? = null
            
            for (pattern in shortIcuPatterns) {
                val match = pattern.find(html)
                if (match != null) {
                    shortIcuUrl = match.groupValues[1]
                    Log.d(TAG, "Short.icu encontrado: $shortIcuUrl")
                    break
                }
            }
            
            if (shortIcuUrl == null) {
                Log.e(TAG, "❌ Não encontrou iframe short.icu")
                // Fallback: tentar extractor antigo
                tryLegacyExtractors(url, referer, subtitleCallback, callback)
                return
            }
            
            // 4. ACESSAR SHORT.ICU E EXTRAIR VÍDEO
            Log.d(TAG, "[3/3] Acessando short.icu...")
            
            val shortResponse = app.get(
                shortIcuUrl,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to url,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.7"
                ),
                timeout = 15
            )
            
            val shortHtml = shortResponse.text
            Log.d(TAG, "Short.icu HTML: ${shortHtml.length} chars")
            
            // 5. EXTRAIR URL DO VÍDEO DO GOOGLE CLOUD STORAGE
            val videoPatterns = listOf(
                // Google Cloud Storage MP4
                Regex("""(https://storage\.googleapis\.com/[^"'<>\s]+\.mp4[^"'<>\s]*)"""),
                Regex("""(https://storage\.googleapis\.com/[^"'<>\s]+)"""),
                // Outros padrões de vídeo
                Regex("""["'](https?://[^"'<>]+\.mp4[^"'<>]*)["']"""),
                Regex("""["'](https?://[^"'<>]+\.m3u8[^"'<>]*)["']"""),
                Regex("""file\s*:\s*["']([^"']+)["']"""),
                Regex("""src\s*:\s*["']([^"']+\.mp4[^"']*)["']""")
            )
            
            var videoUrl: String? = null
            
            for (pattern in videoPatterns) {
                val match = pattern.find(shortHtml)
                if (match != null) {
                    videoUrl = match.groupValues[1].replace("\\/", "/")
                    Log.d(TAG, "Vídeo encontrado: $videoUrl")
                    break
                }
            }
            
            // 6. TENTAR IFRAME DENTRO DO SHORT.ICU
            if (videoUrl == null) {
                Log.d(TAG, "Procurando iframe interno no short.icu...")
                
                val iframePattern = Regex("""<iframe[^>]+src\s*=\s*["']([^"']+)["']""")
                val iframeMatch = iframePattern.find(shortHtml)
                
                if (iframeMatch != null) {
                    var iframeUrl = iframeMatch.groupValues[1]
                    if (!iframeUrl.startsWith("http")) {
                        iframeUrl = "https:$iframeUrl"
                    }
                    
                    Log.d(TAG, "Iframe encontrado: $iframeUrl")
                    
                    // Acessar iframe
                    val iframeResponse = app.get(
                        iframeUrl,
                        headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Referer" to shortIcuUrl
                        ),
                        timeout = 10
                    )
                    
                    val iframeHtml = iframeResponse.text
                    
                    // Procurar vídeo no iframe
                    for (pattern in videoPatterns) {
                        val match = pattern.find(iframeHtml)
                        if (match != null) {
                            videoUrl = match.groupValues[1].replace("\\/", "/")
                            Log.d(TAG, "Vídeo encontrado no iframe: $videoUrl")
                            break
                        }
                    }
                }
            }
            
            // 7. RETORNAR RESULTADO
            if (videoUrl != null) {
                val quality = QualityDetector.detectFromUrl(videoUrl)
                
                // Salvar no cache
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                Log.d(TAG, "✅ SUCESSO: $videoUrl")
                Log.d(TAG, "Tempo: ${System.currentTimeMillis() - startTime}ms")
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (ShortIcu)",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = shortIcuUrl ?: url
                        this.quality = quality
                    }
                )
                
                ErrorLogger.logPerformance("PlayerEmbedAPI ShortIcu", 
                    System.currentTimeMillis() - startTime)
                return
            }
            
            // Fallback se não encontrou vídeo
            Log.w(TAG, "⚠️ Não encontrou vídeo no short.icu, tentando legado...")
            tryLegacyExtractors(url, referer, subtitleCallback, callback)
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro: ${e.message}")
            e.printStackTrace()
            // Fallback em caso de erro
            tryLegacyExtractors(url, referer, subtitleCallback, callback)
        }
    }
    
    /**
     * Fallback para extractors legados quando ShortIcu falha
     */
    private suspend fun tryLegacyExtractors(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "Tentando extractors legados...")
        
        // 1. Tentar PlayerEmbedAPIExtractor (ExtractorApi padrão)
        try {
            Log.d(TAG, "Tentando: PlayerEmbedAPIExtractor")
            PlayerEmbedAPIExtractor().getUrl(url, referer, subtitleCallback, callback)
            Log.d(TAG, "PlayerEmbedAPIExtractor: sucesso")
            return
        } catch (e: Exception) {
            Log.w(TAG, "PlayerEmbedAPIExtractor falhou: ${e.message}")
        }
        
        // 2. Tentar PlayerEmbedAPIWebViewExtractor (classe diferente)
        try {
            Log.d(TAG, "Tentando: PlayerEmbedAPIWebViewExtractor")
            val links = PlayerEmbedAPIWebViewExtractor().extractFromUrl(url, referer ?: url)
            if (links.isNotEmpty()) {
                links.forEach { callback(it) }
                Log.d(TAG, "PlayerEmbedAPIWebViewExtractor: ${links.size} links")
                return
            }
        } catch (e: Exception) {
            Log.w(TAG, "PlayerEmbedAPIWebViewExtractor falhou: ${e.message}")
        }
        
        Log.e(TAG, "Todos os extractors legados falharam")
    }
}
