/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PLAYEREMBEDAPI EXTRACTOR - Versão Final Ultra-Rápida
 * Tempo alvo: ~200-300ms por vídeo
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Uso no MaxSeriesProvider:
 * 
 * private val playerEmbedExtractor = PlayerEmbedAPIExtractor()
 * 
 * override suspend fun loadLinks(...) {
 *     if (playerUrl.contains("playerembedapi")) {
 *         playerEmbedExtractor.extract(playerUrl, callback)
 *     }
 * }
 */

package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.lagradost.cloudstream3.utils.*
import android.util.Base64
import android.util.Log
import java.util.regex.Pattern

class PlayerEmbedAPIExtractor {
    
    companion object {
        const val TAG = "PlayerEmbedAPI"
        
        // Regex pré-compiladas para máxima performance
        private val RE_DATAS = Pattern.compile("""const\s+datas\s*=\s*"([^"]+)""", Pattern.CASE_INSENSITIVE)
        private val RE_SLUG = Pattern.compile(""""slug":"([^"]+)""")
        private val RE_MD5 = Pattern.compile(""""md5_id":(\d+)""")
        
        // Headers otimizados
        val HEADERS = mapOf(
            "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding" to "gzip, deflate",
            "Connection" to "keep-alive",
            "DNT" to "1",
            "Upgrade-Insecure-Requests" to "1"
        )
        
        // Regex para interceptação WebView
        val INTERCEPT_PATTERN = Regex("""(?i)(sssrr\.org|googleapis\.com/mediastorage|\.m3u8|\.mp4|/hls/|/video/)""")
    }
    
    /**
     * Extrai link de vídeo de uma URL do PlayerEmbedAPI
     * Ordem de tentativas:
     * 1. HTTP Direto Otimizado (~200-300ms)
     * 2. Construção de URL CDN
     * 3. WebView Fallback (~10-15s)
     */
    suspend fun extract(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val startTime = System.currentTimeMillis()
        Log.d(TAG, "Iniciando extração: $url")
        
        // TÉCNICA 1: HTTP Direto Otimizado
        val result = extractFast(url)
        
        if (result != null) {
            callback(
                newExtractorLink(
                    "PlayerEmbedAPI",
                    "PlayerEmbedAPI - HD",
                    result
                ) {
                    this.referer = url
                    this.quality = Qualities.Unknown.value
                }
            )
            
            val elapsed = System.currentTimeMillis() - startTime
            Log.d(TAG, "✅ Extração rápida em ${elapsed}ms")
            return true
        }
        
        // TÉCNICA 2: WebView Fallback
        Log.d(TAG, "HTTP rápido falhou, usando WebView...")
        return extractWithWebView(url, callback)
    }
    
    /**
     * Extração rápida via HTTP direto
     * Target: ~200-300ms
     */
    private suspend fun extractFast(url: String): String? {
        return try {
            // 1. Download HTML (mais lento - ~200ms)
            val response = app.get(
                url,
                headers = HEADERS,
                timeout = 5  // 5 segundos apenas
            )
            
            val html = response.text
            
            // 2. Extrair campo datas com regex (rápido - <1ms)
            val datasMatcher = RE_DATAS.matcher(html)
            if (!datasMatcher.find()) {
                Log.w(TAG, "Campo datas não encontrado")
                return null
            }
            
            val datasB64 = datasMatcher.group(1)
            
            // 3. Decodificar base64 (rápido - <1ms)
            val decoded = try {
                val padded = if (datasB64.length % 4 != 0) {
                    datasB64 + "=".repeat(4 - datasB64.length % 4)
                } else datasB64
                Base64.decode(padded, Base64.DEFAULT)
            } catch (e: Exception) {
                Log.e(TAG, "Erro decode base64: ${e.message}")
                return null
            }
            
            val decodedStr = String(decoded, Charsets.UTF_8)
            
            // 4. Extrair slug e md5 (rápido - <1ms)
            val slugMatcher = RE_SLUG.matcher(decodedStr)
            val md5Matcher = RE_MD5.matcher(decodedStr)
            
            if (!slugMatcher.find() || !md5Matcher.find()) {
                Log.w(TAG, "Slug ou MD5 não encontrado")
                return null
            }
            
            val slug = slugMatcher.group(1)
            val md5Id = md5Matcher.group(1)
            
            Log.d(TAG, "Dados extraídos: slug=$slug, md5_id=$md5Id")
            
            // 5. Construir URL CDN
            "https://${slug}.sssrr.org/sora/${md5Id}/"
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro extração rápida: ${e.message}")
            null
        }
    }
    
    /**
     * WebView Fallback para quando HTTP falha
     * Timeout: 30 segundos
     */
    private suspend fun extractWithWebView(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "Iniciando WebView...")
            
            // Script para extrair do JWPlayer
            val script = """
                (function() {
                    return new Promise(function(resolve) {
                        // Esperar player carregar
                        setTimeout(function() {
                            var result = '';
                            
                            // 1. Tentar JWPlayer
                            if (window.jwplayer) {
                                try {
                                    var jw = jwplayer();
                                    if (jw && jw.getPlaylist) {
                                        var playlist = jw.getPlaylist();
                                        if (playlist && playlist[0]) {
                                            result = playlist[0].file || '';
                                        }
                                    }
                                } catch(e) {}
                            }
                            
                            // 2. Tentar video element
                            if (!result) {
                                var video = document.querySelector('video');
                                if (video && video.src) {
                                    result = video.src;
                                }
                            }
                            
                            // 3. Tentar sources
                            if (!result) {
                                var sources = document.querySelectorAll('source[src*=".m3u8"], source[src*=".mp4"]');
                                if (sources.length > 0) {
                                    result = sources[0].src;
                                }
                            }
                            
                            resolve(result);
                        }, 4000);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = INTERCEPT_PATTERN,
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4"""),
                    Regex("""sssrr\.org""")
                ),
                useOkhttp = false,  // IMPORTANTE: false para bypass
                script = script,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result.startsWith("http")) {
                        capturedUrl = result
                        Log.d(TAG, "URL capturada via script: $result")
                    }
                },
                timeout = 30000L  // 30 segundos
            )
            
            val response = app.get(url, interceptor = resolver)
            
            // Verificar URL interceptada
            val videoUrl = when {
                response.url.contains(".m3u8") || response.url.contains(".mp4") -> response.url
                !capturedUrl.isNullOrEmpty() -> capturedUrl!!
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d(TAG, "✅ WebView sucesso: $videoUrl")
                
                if (videoUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8("PlayerEmbedAPI", videoUrl, url).forEach(callback)
                } else {
                    callback(
                        newExtractorLink(
                            "PlayerEmbedAPI",
                            "PlayerEmbedAPI",
                            videoUrl
                        ) {
                            this.referer = url
                            this.quality = Qualities.Unknown.value
                        }
                    )
                }
                true
            } else {
                Log.e(TAG, "❌ WebView não encontrou vídeo")
                false
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro WebView: ${e.message}")
            false
        }
    }
    
    /**
     * Extrai múltiplas qualidades se disponíveis
     */
    suspend fun extractMultiple(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // Por enquanto, mesma implementação
        // Futuro: suportar múltiplas qualidades (360p, 480p, 720p, 1080p)
        return extract(url, callback)
    }
}
