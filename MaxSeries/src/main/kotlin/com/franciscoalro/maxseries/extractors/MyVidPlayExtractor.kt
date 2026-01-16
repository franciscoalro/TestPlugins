package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import kotlin.random.Random

/**
 * MyVidPlay Extractor v2 - OPTIMIZED (FASE 4)
 * 
 * MyVidPlay é um wrapper do DoodStream que usa:
 * 1. Endpoint /pass_md5/ para obter URL base
 * 2. Token aleatório + timestamp para URL final
 * 3. Retorna MP4 direto do cloudatacdn.com
 * 
 * Melhorias v2:
 * - ✅ Cache de URLs extraídas (5min)
 * - ✅ Retry logic (3 tentativas)
 * - ✅ Quality detection automática
 * - ✅ Logs estruturados com ErrorLogger
 * - ✅ Performance tracking
 * 
 * PRIORIDADE 2 - Boa opção:
 * - MP4 direto sem JavaScript
 * - Compatível com ExoPlayer
 * - Não causa erro 3003
 */
class MyVidPlayExtractor : ExtractorApi() {
    override var name = "MyVidPlay"
    override var mainUrl = "https://myvidplay.com"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MyVidPlayExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        private const val CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
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
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)}",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = url
                    this.quality = cached.quality
                    this.headers = mapOf(
                        "User-Agent" to USER_AGENT,
                        "Referer" to url
                    )
                }
            )
            
            ErrorLogger.logPerformance("MyVidPlay Extraction (Cached)", 
                System.currentTimeMillis() - startTime)
            return
        }
        
        ErrorLogger.logCache(url, hit = false, VideoUrlCache.getStats())
        
        // 2. EXTRAIR COM RETRY LOGIC
        RetryHelper.withRetry(maxAttempts = 3) { attempt ->
            runCatching {
                ErrorLogger.d(TAG, "Iniciando extração MyVidPlay", mapOf(
                    "URL" to url,
                    "Attempt" to "$attempt/3"
                ))
                
                // Passo 1: Obter página do player
                val response = RetryHelper.httpRequest(url, maxAttempts = 3) {
                    app.get(
                        url,
                        referer = referer,
                        headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                        )
                    )
                }
                
                val html = response.text
                ErrorLogger.d(TAG, "Página obtida", mapOf("Size" to "${html.length} chars"))
                
                // Passo 2: Extrair URL do pass_md5
                val passMd5Pattern = Regex("""(/pass_md5/[^'"]+)""")
                val passMd5Match = passMd5Pattern.find(html)
                
                if (passMd5Match == null) {
                    val error = Exception("pass_md5 não encontrado no HTML")
                    ErrorLogger.logExtraction(name, url, success = false, error = error)
                    throw error
                }
                
                val passMd5Path = passMd5Match.groupValues[1]
                ErrorLogger.d(TAG, "pass_md5 encontrado", mapOf("Path" to passMd5Path))
                
                // Passo 3: Fazer request para pass_md5
                val passMd5Url = "$mainUrl$passMd5Path"
                val md5Response = RetryHelper.httpRequest(passMd5Url, maxAttempts = 3) {
                    app.get(
                        passMd5Url,
                        referer = url,
                        headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Accept" to "*/*"
                        )
                    )
                }
                
                val md5Text = md5Response.text.trim()
                
                if (md5Text.isEmpty() || !md5Text.startsWith("http")) {
                    val error = Exception("Resposta inválida do pass_md5: $md5Text")
                    ErrorLogger.logExtraction(name, url, success = false, error = error)
                    throw error
                }
                
                // Passo 4: Gerar token aleatório (10 caracteres)
                val token = (1..10).map { CHARS[Random.nextInt(CHARS.length)] }.joinToString("")
                
                // Passo 5: Construir URL final
                val timestamp = System.currentTimeMillis()
                val finalUrl = "${md5Text}${token}?token=${token}&expiry=${timestamp}"
                
                // 3. DETECTAR QUALIDADE
                val quality = QualityDetector.detectFromUrl(finalUrl)
                ErrorLogger.logQualityDetection(finalUrl, quality, "URL")
                
                // 4. SALVAR NO CACHE
                VideoUrlCache.put(url, finalUrl, quality, name)
                
                // 5. INVOCAR CALLBACK
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)}",
                        url = finalUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = url
                        this.quality = quality
                        this.headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Referer" to url
                        )
                    }
                )
                
                // Log de sucesso
                ErrorLogger.logExtraction(
                    extractor = name,
                    url = url,
                    success = true,
                    videoUrl = finalUrl,
                    quality = quality
                )
                
                ErrorLogger.logPerformance("MyVidPlay Extraction", 
                    System.currentTimeMillis() - startTime,
                    mapOf("Quality" to QualityDetector.getQualityLabel(quality))
                )
                
            }.getOrElse { error ->
                if (attempt < 3) {
                    ErrorLogger.logRetry(
                        operation = "MyVidPlay Extraction",
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
