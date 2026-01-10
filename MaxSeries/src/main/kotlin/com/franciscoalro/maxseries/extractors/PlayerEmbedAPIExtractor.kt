package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.JsUnpacker
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * PlayerEmbedAPI Extractor para CloudStream
 * 
 * DESCOBERTA (Jan 2026):
 * O vídeo final é servido do Google Cloud Storage!
 * URL: storage.googleapis.com/mediastorage/{timestamp}/{hash}/{id}.mp4
 * 
 * Cadeia de redirecionamentos:
 * playerembedapi.link → short.icu → abyss.to → storage.googleapis.com
 * 
 * Este extractor usa WebView para navegar pelos iframes e capturar
 * a URL final do GCS que é um MP4 direto.
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override val name = "PlayerEmbedAPI"
    override val mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPIExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        // Todos os domínios da cadeia
        val DOMAINS = listOf(
            "playerembedapi.link",
            "short.icu",
            "abysscdn.com",
            "abyss.to",
            "storage.googleapis.com"
        )
        
        // Padrão da URL do GCS
        val GCS_PATTERN = Regex("""https?://storage\.googleapis\.com/mediastorage/[^"'\s]+\.mp4[^"'\s]*""")
        
        fun canHandle(url: String): Boolean {
            return DOMAINS.any { url.contains(it, ignoreCase = true) }
        }
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "Extraindo: $url")
        
        // Método 1: WebView para capturar URL do GCS (mais confiável)
        if (tryWebViewExtraction(url, referer, callback)) {
            return
        }
        
        // Método 2: Tentar seguir redirecionamentos via HTTP
        tryRedirectExtraction(url, referer, callback)
    }

    /**
     * Método 1: WebView para capturar URL do Google Cloud Storage
     * O vídeo final é um MP4 direto do GCS
     */
    private suspend fun tryWebViewExtraction(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            Log.d(TAG, "Usando WebView para: $url")
            
            // Script para capturar URL do player - foco no GCS
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var interval = setInterval(function() {
                            attempts++;
                            var result = '';

                            // Tentar capturar de elemento video
                            var video = document.querySelector('video');
                            if (video) {
                                if (video.currentSrc && video.currentSrc.length > 0) result = video.currentSrc;
                                else if (video.src && video.src.length > 0) result = video.src;
                            }
                            
                            if (!result) {
                                var source = document.querySelector('video source');
                                if (source && source.src) result = source.src;
                            }
                            
                            // Procurar em iframes
                            if (!result) {
                                var iframes = document.querySelectorAll('iframe');
                                for (var i = 0; i < iframes.length; i++) {
                                    try {
                                        var iframeDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                                        var iframeVideo = iframeDoc.querySelector('video');
                                        if (iframeVideo) {
                                            if (iframeVideo.currentSrc) { result = iframeVideo.currentSrc; break; }
                                            if (iframeVideo.src) { result = iframeVideo.src; break; }
                                        }
                                    } catch(e) {}
                                }
                            }
                            
                            // Variáveis globais
                            if (!result) {
                                if (window.source) result = window.source;
                                else if (window.file) result = window.file;
                                else if (window.videoUrl) result = window.videoUrl;
                            }
                            
                            if (result && result.length > 0) {
                                clearInterval(interval);
                                resolve(result);
                            } else if (attempts > 50) { // 5s timeout
                                clearInterval(interval);
                                resolve('');
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            var capturedUrl: String? = null
            
            // Interceptar requisições para GCS e outros vídeos
            val resolver = WebViewResolver(
                interceptUrl = Regex("""storage\.googleapis\.com|\.m3u8|\.mp4|master\.txt|/hls/|/video/|/stream/"""),
                additionalUrls = listOf(Regex("""storage\.googleapis\.com.*\.mp4""")),
                useOkhttp = false,
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result != "\"\"") {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "WebView script capturou: $capturedUrl")
                    }
                },
                timeout = 60_000L // Timeout maior para carregar iframes aninhados
            )
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl)
                ),
                interceptor = resolver
            )
            
            val interceptedUrl = response.url
            
            // Priorizar URL do GCS
            val videoUrl = when {
                !capturedUrl.isNullOrEmpty() && capturedUrl!!.contains("storage.googleapis.com") -> capturedUrl!!
                interceptedUrl.contains("storage.googleapis.com") -> interceptedUrl
                !capturedUrl.isNullOrEmpty() && isValidVideoUrl(capturedUrl!!) -> capturedUrl!!
                isValidVideoUrl(interceptedUrl) -> interceptedUrl
                else -> null
            }
            
            if (videoUrl != null) {
                Log.d(TAG, "WebView extraiu com sucesso: $videoUrl")
                emitExtractorLink(videoUrl, url, callback)
                return true
            }
            
            Log.w(TAG, "WebView não conseguiu extrair URL de vídeo")
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no WebView: ${e.message}")
        }
        
        return false
    }

    /**
     * Método 2: Seguir redirecionamentos e tentar extrair do HTML
     */
    private suspend fun tryRedirectExtraction(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        try {
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to (referer ?: mainUrl)
                ),
                allowRedirects = true
            )
            
            val html = response.text
            val finalUrl = response.url
            
            Log.d(TAG, "URL final após redirect: $finalUrl")
            
            // Procurar URL do GCS no HTML
            val gcsMatch = GCS_PATTERN.find(html)
            if (gcsMatch != null) {
                val gcsUrl = gcsMatch.value
                Log.d(TAG, "URL GCS encontrada: $gcsUrl")
                emitExtractorLink(gcsUrl, url, callback)
                return true
            }
            
            // Procurar iframe de short.icu ou abyss.to
            val iframePattern = Regex("""<iframe[^>]+src=["']([^"']+(?:short\.icu|abyss\.to|abysscdn)[^"']*)["']""", RegexOption.IGNORE_CASE)
            val iframeMatch = iframePattern.find(html)
            
            if (iframeMatch != null) {
                val iframeSrc = iframeMatch.groupValues[1].let {
                    if (it.startsWith("//")) "https:$it"
                    else if (!it.startsWith("http")) "https://$it"
                    else it
                }
                
                Log.d(TAG, "Iframe encontrado: $iframeSrc")
                
                val iframeResponse = app.get(
                    iframeSrc,
                    headers = mapOf(
                        "User-Agent" to USER_AGENT,
                        "Referer" to finalUrl
                    ),
                    allowRedirects = true
                )
                
                val iframeHtml = iframeResponse.text
                
                // Procurar GCS no iframe
                val iframeGcsMatch = GCS_PATTERN.find(iframeHtml)
                if (iframeGcsMatch != null) {
                    val gcsUrl = iframeGcsMatch.value
                    Log.d(TAG, "URL GCS no iframe: $gcsUrl")
                    emitExtractorLink(gcsUrl, iframeSrc, callback)
                    return true
                }
                
                val videoUrl = extractVideoFromHtml(iframeHtml)
                if (videoUrl != null) {
                    Log.d(TAG, "URL extraída do iframe: $videoUrl")
                    emitExtractorLink(videoUrl, iframeSrc, callback)
                    return true
                }
            }
            
            val directUrl = extractVideoFromHtml(html)
            if (directUrl != null) {
                Log.d(TAG, "URL extraída diretamente: $directUrl")
                emitExtractorLink(directUrl, url, callback)
                return true
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no redirect extraction: ${e.message}")
        }
        
        return false
    }

    /**
     * Extrai URL de vídeo do HTML/JavaScript
     */
    private fun extractVideoFromHtml(html: String): String? {
        val patterns = listOf(
            // GCS pattern (prioridade)
            GCS_PATTERN,
            // HLS patterns
            Regex("""["'](https?://[^"']+\.m3u8[^"']*)["']"""),
            Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""source:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            // MP4 patterns
            Regex("""["'](https?://[^"']+\.mp4[^"']*)["']"""),
            Regex("""file:\s*["']([^"']+\.mp4[^"']*)["']"""),
            // Generic patterns
            Regex("""playUrl:\s*["']([^"']+)["']"""),
            Regex("""videoUrl:\s*["']([^"']+)["']""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                val url = match.groupValues.getOrNull(1) ?: match.value
                if (isValidVideoUrl(url)) {
                    return url
                }
            }
        }
        
        // Tentar desempacotar JavaScript P.A.C.K.E.R.
        val packed = getPackedCode(html)
        if (!packed.isNullOrEmpty()) {
            try {
                val unpacked = JsUnpacker(packed).unpack() ?: ""
                if (unpacked.isNotEmpty()) {
                    for (pattern in patterns) {
                        val match = pattern.find(unpacked)
                        if (match != null) {
                            val url = match.groupValues.getOrNull(1) ?: match.value
                            if (isValidVideoUrl(url)) {
                                return url
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Erro ao desempacotar JS: ${e.message}")
            }
        }
        
        return null
    }
    
    /**
     * Extrai código P.A.C.K.E.R. do HTML
     */
    private fun getPackedCode(html: String): String? {
        return Regex("""eval\(function\(p,a,c,k,e,[dr]\).*?\)\)""", RegexOption.DOT_MATCHES_ALL)
            .find(html)?.value
    }

    /**
     * Emite ExtractorLink para o CloudStream
     */
    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        // Limpar URL (remover fragmentos desnecessários)
        val cleanUrl = videoUrl.substringBefore("#")
        
        // Determinar o referer correto baseado no domínio
        val effectiveReferer = when {
            videoUrl.contains("storage.googleapis.com") -> "https://abyss.to/"
            videoUrl.contains("abyss") -> "https://abyss.to/"
            videoUrl.contains("abysscdn") -> "https://abysscdn.com/"
            else -> referer
        }
        
        val headers = mapOf(
            "User-Agent" to USER_AGENT,
            "Referer" to effectiveReferer,
            "Origin" to effectiveReferer.substringBeforeLast("/")
        )
        
        // Extrair qualidade da URL se disponível
        val quality = when {
            videoUrl.contains("1080p") -> Qualities.P1080.value
            videoUrl.contains("720p") -> Qualities.P720.value
            videoUrl.contains("480p") -> Qualities.P480.value
            videoUrl.contains("360p") -> Qualities.P360.value
            else -> Qualities.Unknown.value
        }
        
        if (videoUrl.contains(".m3u8")) {
            try {
                M3u8Helper.generateM3u8(name, cleanUrl, effectiveReferer).forEach(callback)
            } catch (e: Exception) {
                callback(
                    newExtractorLink(name, "$name HLS", cleanUrl, isM3u8 = true) {
                        this.referer = effectiveReferer
                        this.quality = quality
                    }
                )
            }
        } else {
            // MP4 direto (GCS)
            callback(
                newExtractorLink(
                    name, 
                    if (videoUrl.contains("storage.googleapis.com")) "$name GCS" else name, 
                    cleanUrl
                ) {
                    this.referer = effectiveReferer
                    this.quality = quality
                }
            )
        }
    }

    /**
     * Valida se é uma URL de vídeo válida
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        if (!url.startsWith("http")) return false
        
        return url.contains("storage.googleapis.com") ||
               url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("/hls/") || 
               url.contains("/video/") ||
               url.contains("/stream/")
    }
}
