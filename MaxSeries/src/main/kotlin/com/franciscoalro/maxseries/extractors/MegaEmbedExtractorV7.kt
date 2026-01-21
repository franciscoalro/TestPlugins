package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v7 - v145 MULTI-REGEX
 *
 * Múltiplos regex baseados em CDNs descobertos
 */
class MegaEmbedExtractorV7 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MegaEmbedV7"
        
        fun canHandle(url: String): Boolean {
            return url.contains("megaembed", true)
        }
        
        // Múltiplos regex baseados em CDNs conhecidos
        private val CDN_PATTERNS = listOf(
            // Padrão 1: Valenium (is9)
            Regex("""https?://[a-z0-9]+\.valenium\.shop/v4/is9/[a-z0-9]{6}/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 2: Veritasholdings (ic)
            Regex("""https?://[a-z0-9]+\.veritasholdings\.cyou/v4/ic/[a-z0-9]{6}/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 3: Marvellaholdings (x6b)
            Regex("""https?://[a-z0-9]+\.marvellaholdings\.sbs/v4/x6b/[a-z0-9]{6}/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 4: Travianastudios (5c)
            Regex("""https?://[a-z0-9]+\.travianastudios\.space/v4/5c/[a-z0-9]{6}/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 5: Genérico /v4/ com cluster de 2-3 chars
            Regex("""https?://[a-z0-9]+\.[a-z]+\.[a-z]{2,}/v4/[a-z0-9]{2,3}/[a-z0-9]{6}/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 6: Qualquer /v4/ (fallback)
            Regex("""https?://[^/]+/v4/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
            
            // Padrão 7: index.txt ou cf-master.txt
            Regex("""https?://[^/]+/.*/(index|cf-master)\.txt""", RegexOption.IGNORE_CASE),
            
            // Padrão 8: Arquivos .woff/.woff2 (segmentos camuflados)
            Regex("""https?://[^/]+/v4/.*/.*\.woff2?""", RegexOption.IGNORE_CASE)
        )
    }

    private val cdnHeaders = mapOf(
        "Referer" to "https://megaembed.link/",
        "Origin" to "https://megaembed.link",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MEGAEMBED V7 v145 MULTI-REGEX ===")
        Log.d(TAG, "Input: $url")
        
        val videoId = extractVideoId(url) ?: run {
            Log.e(TAG, "❌ VideoID não encontrado")
            return
        }
        
        // FASE 1 — CACHE
        VideoUrlCache.get(url)?.let { cached ->
            Log.d(TAG, "✅ CACHE HIT")
            M3u8Helper.generateM3u8(
                source = name,
                streamUrl = cached.url,
                referer = mainUrl,
                headers = cdnHeaders
            ).forEach(callback)
            return
        }
        
        // FASE 2 — TENTAR CADA REGEX
        for ((index, pattern) in CDN_PATTERNS.withIndex()) {
            Log.d(TAG, "🔍 Tentando regex ${index + 1}/${CDN_PATTERNS.size}")
            
            runCatching {
                val captureScript = """
                    (function() {
                        return new Promise(function(resolve) {
                            setTimeout(function() { resolve(''); }, 8000);
                        });
                    })()
                """.trimIndent()
                
                val resolver = WebViewResolver(
                    interceptUrl = pattern,
                    script = captureScript,
                    scriptCallback = { result ->
                        Log.d(TAG, "WebView script result: $result")
                    },
                    timeout = 10_000L
                )
                
                val headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer" to mainUrl
                )
                
                val response = app.get(url, headers = headers, interceptor = resolver)
                val captured = response.url
                
                Log.d(TAG, "📄 Response URL: $captured")
                
                // Verificar se capturou algo válido
                if (!captured.contains("/v4/") && !captured.contains("index.txt") && !captured.contains("cf-master")) {
                    Log.d(TAG, "⏭️ Regex ${index + 1} não capturou nada relevante")
                    continue
                }
                
                // Normalizar URL
                val videoUrl = normalizeVideoUrl(captured)
                if (videoUrl == null) {
                    Log.d(TAG, "⏭️ Regex ${index + 1} - URL não pôde ser normalizada")
                    continue
                }
                
                Log.d(TAG, "✅ SUCESSO com regex ${index + 1}: $videoUrl")
                
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                M3u8Helper.generateM3u8(
                    source = name,
                    streamUrl = videoUrl,
                    referer = mainUrl,
                    headers = cdnHeaders
                ).forEach(callback)
                
                return // Sucesso! Sair da função
                
            }.onFailure {
                Log.d(TAG, "⏭️ Regex ${index + 1} falhou: ${it.message}")
            }
        }
        
        Log.e(TAG, "❌ Nenhum regex conseguiu capturar link")
    }
    
    private fun normalizeVideoUrl(url: String): String? {
        return when {
            // Já é index.txt ou cf-master.txt
            url.contains("index.txt") || url.contains("cf-master.txt") -> {
                Log.d(TAG, "✅ URL já normalizada: $url")
                url
            }
            
            // Converter .woff para index.txt
            url.contains(".woff") -> {
                val normalized = url.replace(Regex("""/[^/]+\.(woff2?|ts)$"""), "/index.txt")
                Log.d(TAG, "🔄 Convertido .woff → $normalized")
                normalized
            }
            
            // Tem /v4/ mas não tem arquivo específico - adicionar index.txt
            url.contains("/v4/") && !url.contains(".txt") -> {
                val normalized = url.trimEnd('/') + "/index.txt"
                Log.d(TAG, "🔄 Adicionado index.txt → $normalized")
                normalized
            }
            
            else -> {
                Log.e(TAG, "❌ Formato não reconhecido: $url")
                null
            }
        }
    }
    
    private fun extractVideoId(url: String): String? {
        return Regex("""#([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
    }
}
