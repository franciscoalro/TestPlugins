package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*

/**
 * MediaFire Extractor v2 - OPTIMIZED (FASE 4)
 * Inspirado no padrão FilmesOn
 * 
 * Melhorias v2:
 * - ✅ Cache de URLs extraídas (5min)
 * - ✅ Retry logic (3 tentativas)
 * - ✅ Quality detection automática
 * - ✅ Logs estruturados com ErrorLogger
 * - ✅ Performance tracking
 * 
 * Extrai links diretos de download do MediaFire
 */
class MediaFireExtractor : ExtractorApi() {
    override val name = "MediaFire"
    override val mainUrl = "https://www.mediafire.com"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MediaFireExtractor"
        
        fun canHandle(url: String): Boolean {
            return url.contains("mediafire.com", ignoreCase = true)
        }
    }
    
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        // 1. VERIFICAR CACHE
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            ErrorLogger.logCache(url, hit = true, VideoUrlCache.getStats())
            
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name - ${QualityDetector.getQualityLabel(cached.quality)}",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = mainUrl
                    this.quality = cached.quality
                    this.headers = HeadersBuilder.mediaFire(url)
                }
            )
            
            ErrorLogger.logPerformance("MediaFire Extraction (Cached)", 
                System.currentTimeMillis() - startTime)
            return
        }
        
        ErrorLogger.logCache(url, hit = false, VideoUrlCache.getStats())
        
        // 2. EXTRAIR COM RETRY LOGIC
        RetryHelper.withRetry(maxAttempts = 3) { attempt ->
            runCatching {
                ErrorLogger.d(TAG, "Iniciando extração", mapOf(
                    "URL" to url,
                    "Attempt" to "$attempt/3"
                ))
                
                // Requisição HTTP com headers
                val headers = HeadersBuilder.standard(referer)
                val document = RetryHelper.httpRequest(url) {
                    app.get(url, headers = headers).document
                }
                
                // Extrair botão de download
                val downloadButton = document.select("a#downloadButton").attr("href")
                
                if (downloadButton.isNotEmpty() && LinkDecryptor.isUrl(downloadButton)) {
                    // 3. DETECTAR QUALIDADE
                    val quality = QualityDetector.detectFromUrl(downloadButton)
                    
                    ErrorLogger.logQualityDetection(downloadButton, quality, "URL")
                    
                    // 4. SALVAR NO CACHE
                    VideoUrlCache.put(url, downloadButton, quality, name)
                    
                    // 5. INVOCAR CALLBACK
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name - ${QualityDetector.getQualityLabel(quality)}",
                            url = downloadButton,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = mainUrl
                            this.quality = quality
                            this.headers = HeadersBuilder.mediaFire(url)
                        }
                    )
                    
                    // Log de sucesso
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = true,
                        videoUrl = downloadButton,
                        quality = quality
                    )
                    
                    ErrorLogger.logPerformance("MediaFire Extraction", 
                        System.currentTimeMillis() - startTime,
                        mapOf("Quality" to QualityDetector.getQualityLabel(quality))
                    )
                } else {
                    val error = Exception("Botão de download não encontrado")
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = false,
                        error = error
                    )
                    throw error
                }
            }.getOrElse { error ->
                // Log de retry se não for última tentativa
                if (attempt < 3) {
                    ErrorLogger.logRetry(
                        operation = "MediaFire Extraction",
                        attempt = attempt,
                        maxAttempts = 3,
                        nextDelayMs = RetryHelper.calculateDelay(attempt),
                        error = error
                    )
                } else {
                    ErrorLogger.logExtraction(
                        extractor = name,
                        url = url,
                        success = false,
                        error = error
                    )
                }
                throw error
            }
        }
    }
}
