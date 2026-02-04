package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.BRExtractorUtils
import com.franciscoalro.maxseries.utils.RetryHelper
import android.util.Log
import kotlin.random.Random

/**
 * DoodStream Extractor - PRIORITY 3
 * Baseado no MyVidPlayExtractor existente + padrões do saimuelrepo
 * 
 * DoodStream (e seus clones: myvidplay, bysebuho, g9r6) usam:
 * 1. Endpoint /pass_md5/ para obter URL base
 * 2. Token aleatório + timestamp para URL final
 */
class DoodStreamExtractor : ExtractorApi() {
    override var name = "DoodStream"
    override var mainUrl = "https://doodstream.com"
    override val requiresReferer = true

    companion object {
        private const val TAG = "DoodStreamExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        private const val CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        
        fun canHandle(url: String): Boolean = BRExtractorUtils.isDoodStream(url)
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 Iniciando extração DoodStream: $url")
        
        try {
            // Detectar o domínio correto
            val domain = Regex("""https?://([^/]+)""").find(url)?.groupValues?.get(1)
                ?: "doodstream.com"
            val baseUrl = "https://$domain"
            
            // Primeira requisição com timeout e retry
            val response = RetryHelper.withRetry(maxAttempts = 2) {
                app.get(
                    url,
                    referer = referer ?: baseUrl,
                    headers = mapOf("User-Agent" to USER_AGENT),
                    timeout = 8_000L  // 8 segundos máximo
                )
            }
            
            // Early exit para erros HTTP
            if (response.code == 404) {
                Log.w(TAG, "Vídeo não encontrado (404)")
                return
            }
            if (response.code >= 500) {
                Log.w(TAG, "Erro servidor (${response.code})")
                return
            }
            
            val html = response.text
            
            // Extrair path do pass_md5
            val passMd5Pattern = Regex("""(/pass_md5/[^'"\s]+)""")
            val passMd5Match = passMd5Pattern.find(html)
            
            if (passMd5Match != null) {
                val passMd5Path = passMd5Match.groupValues[1]
                val passMd5Url = "$baseUrl$passMd5Path"
                
                Log.d(TAG, "🔑 pass_md5 encontrado: $passMd5Url")
                
                // Segunda requisição com timeout menor e retry
                val md5Response = RetryHelper.withRetry(maxAttempts = 2) {
                    app.get(
                        passMd5Url,
                        referer = url,
                        headers = mapOf(
                            "User-Agent" to USER_AGENT,
                            "Accept" to "*/*"
                        ),
                        timeout = 5_000L  // 5s apenas
                    )
                }
                
                val md5Text = md5Response.text.trim()
                
                if (md5Text.isNotEmpty() && md5Text.startsWith("http")) {
                    // Gerar token aleatório (10 caracteres)
                    val token = (1..10).map { CHARS[Random.nextInt(CHARS.length)] }.joinToString("")
                    
                    // Construir URL final
                    val timestamp = System.currentTimeMillis()
                    val videoUrl = "${md5Text}${token}?token=${token}&expiry=${timestamp}"
                    
                    Log.d(TAG, "✅ URL capturada: $videoUrl")
                    
                    callback.invoke(
                        newExtractorLink(
                            source = "${name}_${System.currentTimeMillis() % 10000}",
                            name = "$name HD",
                            url = videoUrl,
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
                    Log.e(TAG, "❌ Resposta inválida do pass_md5: $md5Text")
                }
            } else {
                Log.e(TAG, "❌ pass_md5 não encontrado no HTML")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro DoodStream: ${e.message}")
        }
    }
}
