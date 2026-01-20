package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v7 — Pipeline WebVideoCast-like
 *
 * PRINCÍPIO FUNDAMENTAL:
 * → O ÚNICO PADRÃO CONFIÁVEL É: /v4/{cluster}/{video}/
 * → TODO o resto muda (domínio, extensão, nome do arquivo)
 *
 * Estratégia:
 * 1. Cache (instantâneo)
 * 2. WebView com interceptação total
 * 3. Pipeline de classificação
 * 4. Normalização para M3U8
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
    }

    private val cdnHeaders = mapOf(
        "Referer" to "https://megaembed.link/",
        "Origin" to "https://megaembed.link",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    /**
     * Pipeline de detecção — ordem de prioridade
     */
    private val patterns = listOf(
        // Regra principal: /v4/{cluster}/{video}/
        Regex("""https?://[^/]+/v4/[^/]+/[^/]+/[^"'\s>]+"""),
        // Específicos comuns
        Regex("""https?://[^/]+/v4/[^/]+/[^/]+/.*\.(txt|m3u8)"""),
        Regex("""https?://[^/]+/v4/[^/]+/[^/]+/.*\.(woff2?|ts)"""),
        // Fallback
        Regex("""/v4/[^"'\s>]+""", RegexOption.IGNORE_CASE)
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MEGAEMBED V7 START ===")
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
        
        // FASE 2 — WEBVIEW
        runCatching {
            val jsInterceptor = """
                (function(){
                    try {
                        const origOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function() {
                            this.addEventListener('load', function() {
                                if (this.responseURL)
                                    console.log("XHR>>" + this.responseURL);
                            });
                            origOpen.apply(this, arguments);
                        };
                        
                        const origFetch = window.fetch;
                        window.fetch = function() {
                            const p = origFetch.apply(this, arguments);
                            p.then(r => {
                                console.log("FETCH>>" + r.url);
                            });
                            return p;
                        };
                    } catch(e) {}
                    return "ok";
                })();
            """.trimIndent()
            
            val resolver = WebViewResolver(
                interceptUrl = Regex(".*"),
                script = jsInterceptor,
                scriptCallback = {
                    Log.d(TAG, "JS callback: $it")
                },
                timeout = 12_000L
            )
            
            val headers = mapOf(
                "User-Agent" to cdnHeaders["User-Agent"]!!,
                "Referer" to mainUrl
            )
            
            val response = app.get(url, headers = headers, interceptor = resolver)
            
            // CLASSIFICAÇÃO - usar a URL da resposta
            val videoUrl = response.url
            
            if (!patterns.any { it.containsMatchIn(videoUrl) }) {
                Log.e(TAG, "❌ URL não corresponde aos padrões: $videoUrl")
                return
            }
            
            Log.d(TAG, "🎯 DETECTADO: $videoUrl")
            
            // NORMALIZAÇÃO
            val normalized = normalize(videoUrl)
            val quality = QualityDetector.detectFromUrl(normalized)
            
            VideoUrlCache.put(url, normalized, quality, name)
            
            M3u8Helper.generateM3u8(
                source = name,
                streamUrl = normalized,
                referer = mainUrl,
                headers = cdnHeaders
            ).forEach(callback)
            
        }.onFailure {
            Log.e(TAG, "❌ Falha WebView: ${it.message}")
        }
    }

    // UTILITÁRIOS
    private fun normalize(url: String): String {
        // .woff → index
        if (url.contains(".woff")) {
            return url.replace(Regex("""/[^/]+\.(woff2?|ts)$"""), "/index.txt")
        }
        return url
    }
    
    private fun extractVideoId(url: String): String? {
        return Regex("""#([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
    }
}