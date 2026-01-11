package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.utils.JsUnpacker
import com.lagradost.cloudstream3.network.WebViewResolver
import android.util.Log

/**
 * PlayerEmbedAPI Extractor v2 - Enhanced Chain Following
 * 
 * DESCOBERTA (Jan 2026):
 * O vídeo final é servido do Google Cloud Storage!
 * URL: storage.googleapis.com/mediastorage/{timestamp}/{hash}/{id}.mp4
 * 
 * Cadeia de redirecionamentos completa:
 * playerembedapi.link → short.icu → abyss.to → storage.googleapis.com
 * 
 * MELHORIAS v2:
 * - Seguimento inteligente de redirecionamentos
 * - Detecção aprimorada de padrões GCS
 * - Fallback robusto para múltiplos domínios
 * - Timeout otimizado para cada etapa
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override val name = "PlayerEmbedAPI"
    override val mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPIExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        // Todos os domínios da cadeia (expandido)
        val DOMAINS = listOf(
            "playerembedapi.link",
            "short.icu",
            "abysscdn.com",
            "abyss.to",
            "storage.googleapis.com",
            // Variantes descobertas
            "playerembed.link",
            "embed-player.com",
            "shortener.icu",
            "abyss.cc"
        )
        
        // Padrões de URL aprimorados
        val GCS_PATTERN = Regex("""https?://storage\.googleapis\.com/[^"'\s]+\.mp4[^"'\s]*""")
        val SHORT_ICU_PATTERN = Regex("""https?://(?:short|shortener)\.icu/[^"'\s]+""")
        val ABYSS_PATTERN = Regex("""https?://(?:abyss\.to|abyss\.cc|abysscdn\.com)/[^"'\s]+""")
        
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
        Log.d(TAG, "=== PlayerEmbedAPI Extractor v2 - Enhanced Chain Following ===")
        Log.d(TAG, "🎬 URL: $url")
        Log.d(TAG, "🔗 Referer: $referer")
        
        try {
            // Método 1: Seguimento inteligente de redirecionamentos (principal)
            Log.d(TAG, "🔄 Tentando seguimento de redirecionamentos...")
            if (tryEnhancedRedirectChain(url, referer, callback)) {
                Log.d(TAG, "✅ Redirect chain funcionou!")
                return
            }
            
            // Método 2: WebView para casos complexos (fallback)
            Log.d(TAG, "🔄 Tentando WebView extraction...")
            if (tryWebViewExtraction(url, referer, callback)) {
                Log.d(TAG, "✅ WebView funcionou!")
                return
            }
            
            // Método 3: Extração direta do HTML (último recurso)
            Log.d(TAG, "🔄 Tentando extração direta...")
            if (tryDirectExtraction(url, referer, callback)) {
                Log.d(TAG, "✅ Extração direta funcionou!")
                return
            }
            
            Log.e(TAG, "❌ Todos os métodos falharam para: $url")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro crítico na extração: ${e.message}")
            e.printStackTrace()
        }
    }

    /**
     * Método 1: Seguimento inteligente de redirecionamentos
     * Segue a cadeia completa: playerembedapi → short.icu → abyss.to → GCS
     */
    private suspend fun tryEnhancedRedirectChain(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "🌐 Iniciando seguimento de cadeia de redirecionamentos...")
            
            var currentUrl = url
            var currentReferer = referer ?: mainUrl
            val visitedUrls = mutableSetOf<String>()
            val maxRedirects = 10
            var redirectCount = 0
            
            while (redirectCount < maxRedirects && currentUrl !in visitedUrls) {
                visitedUrls.add(currentUrl)
                redirectCount++
                
                Log.d(TAG, "🔗 Etapa $redirectCount: $currentUrl")
                
                // Verificar se já chegamos no GCS
                if (currentUrl.contains("storage.googleapis.com")) {
                    Log.d(TAG, "🎯 GCS URL encontrada diretamente: $currentUrl")
                    emitExtractorLink(currentUrl, currentReferer, callback)
                    return true
                }
                
                val response = app.get(
                    currentUrl,
                    headers = mapOf(
                        "User-Agent" to USER_AGENT,
                        "Referer" to currentReferer,
                        "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                    ),
                    allowRedirects = false // Controlar redirecionamentos manualmente
                )
                
                val html = response.text
                val responseUrl = response.url
                
                Log.d(TAG, "📄 Response URL: $responseUrl")
                Log.d(TAG, "📊 Status: ${response.code}")
                
                // Verificar redirecionamento HTTP
                if (response.code in 300..399) {
                    val location = response.headers["Location"] ?: response.headers["location"]
                    if (!location.isNullOrEmpty()) {
                        currentUrl = if (location.startsWith("http")) {
                            location
                        } else if (location.startsWith("//")) {
                            "https:$location"
                        } else {
                            "${currentUrl.substringBeforeLast("/")}/$location"
                        }
                        currentReferer = responseUrl
                        Log.d(TAG, "↪️ Redirecionamento HTTP para: $currentUrl")
                        continue
                    }
                }
                
                // Procurar GCS no HTML atual
                val gcsMatch = GCS_PATTERN.find(html)
                if (gcsMatch != null) {
                    val gcsUrl = gcsMatch.value
                    Log.d(TAG, "🎯 GCS URL encontrada no HTML: $gcsUrl")
                    emitExtractorLink(gcsUrl, responseUrl, callback)
                    return true
                }
                
                // Procurar próximo link na cadeia
                val nextUrl = findNextUrlInChain(html, responseUrl)
                if (nextUrl != null) {
                    currentReferer = responseUrl
                    currentUrl = nextUrl
                    Log.d(TAG, "➡️ Próximo na cadeia: $currentUrl")
                    continue
                }
                
                // Procurar iframe
                val iframeUrl = findIframeUrl(html, responseUrl)
                if (iframeUrl != null) {
                    currentReferer = responseUrl
                    currentUrl = iframeUrl
                    Log.d(TAG, "🖼️ Iframe encontrado: $currentUrl")
                    continue
                }
                
                // Tentar extrair vídeo diretamente do HTML atual
                val videoUrl = extractVideoFromHtml(html)
                if (videoUrl != null && isValidVideoUrl(videoUrl)) {
                    Log.d(TAG, "🎬 Vídeo extraído do HTML: $videoUrl")
                    emitExtractorLink(videoUrl, responseUrl, callback)
                    return true
                }
                
                Log.w(TAG, "⚠️ Nenhum próximo passo encontrado na etapa $redirectCount")
                break
            }
            
            Log.w(TAG, "❌ Cadeia de redirecionamentos não levou ao vídeo")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no seguimento de redirecionamentos: ${e.message}")
            false
        }
    }
    
    /**
     * Encontra o próximo URL na cadeia de redirecionamentos
     */
    private fun findNextUrlInChain(html: String, baseUrl: String): String? {
        // Padrões específicos para cada etapa da cadeia
        val patterns = listOf(
            // Short.icu patterns
            SHORT_ICU_PATTERN,
            // Abyss patterns  
            ABYSS_PATTERN,
            // Generic redirect patterns
            Regex("""window\.location\.href\s*=\s*["']([^"']+)["']"""),
            Regex("""location\.href\s*=\s*["']([^"']+)["']"""),
            Regex("""window\.open\s*\(\s*["']([^"']+)["']"""),
            // Meta refresh
            Regex("""<meta[^>]+http-equiv=["']refresh["'][^>]+content=["'][^;]*;\s*url=([^"']+)["']""", RegexOption.IGNORE_CASE),
            // Button/link redirects
            Regex("""<a[^>]+href=["']([^"']+(?:short\.icu|abyss\.to|abysscdn)[^"']*)["']""", RegexOption.IGNORE_CASE)
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                val url = match.groupValues.getOrNull(1) ?: match.value
                return normalizeUrl(url, baseUrl)
            }
        }
        
        return null
    }
    
    /**
     * Encontra URL de iframe
     */
    private fun findIframeUrl(html: String, baseUrl: String): String? {
        val iframePattern = Regex("""<iframe[^>]+src=["']([^"']+)["']""", RegexOption.IGNORE_CASE)
        val match = iframePattern.find(html)
        
        if (match != null) {
            val url = match.groupValues[1]
            return normalizeUrl(url, baseUrl)
        }
        
        return null
    }
    
    /**
     * Normaliza URL relativa para absoluta
     */
    private fun normalizeUrl(url: String, baseUrl: String): String {
        return when {
            url.startsWith("http") -> url
            url.startsWith("//") -> "https:$url"
            url.startsWith("/") -> "${baseUrl.substringBefore("/", baseUrl.substringAfter("://"))}$url"
            else -> "${baseUrl.substringBeforeLast("/")}/$url"
        }
    }

    /**
     * Método 2: WebView para capturar URL do Google Cloud Storage
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
     * Método 3: Extração direta do HTML (último recurso)
     */
    private suspend fun tryDirectExtraction(
        url: String,
        referer: String?,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "📄 Tentando extração direta do HTML...")
            
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
            
            Log.d(TAG, "📄 URL final: $finalUrl")
            
            // Procurar URL do GCS no HTML
            val gcsMatch = GCS_PATTERN.find(html)
            if (gcsMatch != null) {
                val gcsUrl = gcsMatch.value
                Log.d(TAG, "🎯 GCS URL encontrada: $gcsUrl")
                emitExtractorLink(gcsUrl, finalUrl, callback)
                return true
            }
            
            // Procurar qualquer URL de vídeo válida
            val videoUrl = extractVideoFromHtml(html)
            if (videoUrl != null && isValidVideoUrl(videoUrl)) {
                Log.d(TAG, "🎬 URL de vídeo extraída: $videoUrl")
                emitExtractorLink(videoUrl, finalUrl, callback)
                return true
            }
            
            Log.w(TAG, "⚠️ Nenhuma URL de vídeo encontrada no HTML")
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na extração direta: ${e.message}")
            false
        }
    }

    /**
     * Extrai URL de vídeo do HTML/JavaScript (melhorado)
     */
    private fun extractVideoFromHtml(html: String): String? {
        val patterns = listOf(
            // GCS pattern (prioridade máxima)
            GCS_PATTERN,
            // Padrões específicos PlayerEmbedAPI
            Regex("""["'](https?://storage\.googleapis\.com/[^"']+\.mp4[^"']*)["']"""),
            Regex("""file:\s*["'](https?://storage\.googleapis\.com/[^"']+\.mp4[^"']*)["']"""),
            // HLS patterns
            Regex("""["'](https?://[^"']+\.m3u8[^"']*)["']"""),
            Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""source:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""playlist:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            // MP4 patterns
            Regex("""["'](https?://[^"']+\.mp4[^"']*)["']"""),
            Regex("""file:\s*["']([^"']+\.mp4[^"']*)["']"""),
            Regex("""src:\s*["']([^"']+\.mp4[^"']*)["']"""),
            // Generic video patterns
            Regex("""playUrl:\s*["']([^"']+)["']"""),
            Regex("""videoUrl:\s*["']([^"']+)["']"""),
            Regex("""video_url:\s*["']([^"']+)["']"""),
            Regex("""streamUrl:\s*["']([^"']+)["']"""),
            // Abyss/AbyssCDN specific
            Regex("""["'](https?://[^"']*abyss[^"']*\.(?:mp4|m3u8)[^"']*)["']"""),
            Regex("""["'](https?://[^"']*abysscdn[^"']*\.(?:mp4|m3u8)[^"']*)["']""")
        )
        
        // Primeiro, tentar padrões diretos
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                val url = match.groupValues.getOrNull(1) ?: match.value.trim('"', '\'')
                if (isValidVideoUrl(url)) {
                    Log.d(TAG, "🎯 Padrão encontrado: ${pattern.pattern}")
                    return url
                }
            }
        }
        
        // Tentar desempacotar JavaScript P.A.C.K.E.R.
        val packed = getPackedCode(html)
        if (!packed.isNullOrEmpty()) {
            try {
                Log.d(TAG, "📦 Tentando desempacotar JavaScript...")
                val unpacked = JsUnpacker(packed).unpack() ?: ""
                if (unpacked.isNotEmpty()) {
                    Log.d(TAG, "📦 JavaScript desempacotado com sucesso")
                    for (pattern in patterns) {
                        val match = pattern.find(unpacked)
                        if (match != null) {
                            val url = match.groupValues.getOrNull(1) ?: match.value.trim('"', '\'')
                            if (isValidVideoUrl(url)) {
                                Log.d(TAG, "🎯 Padrão encontrado no JS desempacotado: ${pattern.pattern}")
                                return url
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "❌ Erro ao desempacotar JS: ${e.message}")
            }
        }
        
        // Procurar em atributos data-*
        val dataPatterns = listOf(
            Regex("""data-src=["']([^"']+\.(?:mp4|m3u8)[^"']*)["']"""),
            Regex("""data-url=["']([^"']+\.(?:mp4|m3u8)[^"']*)["']"""),
            Regex("""data-file=["']([^"']+\.(?:mp4|m3u8)[^"']*)["']"""),
            Regex("""data-video=["']([^"']+\.(?:mp4|m3u8)[^"']*)["']""")
        )
        
        for (pattern in dataPatterns) {
            val match = pattern.find(html)
            if (match != null) {
                val url = match.groupValues[1]
                if (isValidVideoUrl(url)) {
                    Log.d(TAG, "🎯 Data attribute encontrado: ${pattern.pattern}")
                    return url
                }
            }
        }
        
        Log.w(TAG, "⚠️ Nenhum padrão de vídeo encontrado no HTML")
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
     * Emite ExtractorLink para o CloudStream (melhorado)
     */
    private suspend fun emitExtractorLink(
        videoUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        try {
            // Limpar URL (remover fragmentos desnecessários)
            val cleanUrl = videoUrl.substringBefore("#").substringBefore("?token=")
            
            // Determinar o referer correto baseado no domínio
            val effectiveReferer = when {
                videoUrl.contains("storage.googleapis.com") -> "https://abyss.to/"
                videoUrl.contains("abyss") -> "https://abyss.to/"
                videoUrl.contains("abysscdn") -> "https://abysscdn.com/"
                videoUrl.contains("short.icu") -> "https://short.icu/"
                else -> referer
            }
            
            // Extrair qualidade da URL se disponível
            val quality = when {
                videoUrl.contains("1080p") || videoUrl.contains("1080") -> Qualities.P1080.value
                videoUrl.contains("720p") || videoUrl.contains("720") -> Qualities.P720.value
                videoUrl.contains("480p") || videoUrl.contains("480") -> Qualities.P480.value
                videoUrl.contains("360p") || videoUrl.contains("360") -> Qualities.P360.value
                else -> Qualities.Unknown.value
            }
            
            // Determinar nome da fonte
            val sourceName = when {
                videoUrl.contains("storage.googleapis.com") -> "$name GCS"
                videoUrl.contains("abyss") -> "$name Abyss"
                videoUrl.contains("abysscdn") -> "$name AbyssCDN"
                else -> name
            }
            
            val qualityLabel = if (quality != Qualities.Unknown.value) "${quality}p" else "HD"
            
            if (videoUrl.contains(".m3u8")) {
                // HLS - usar M3u8Helper para múltiplas qualidades
                Log.d(TAG, "📺 Processando como HLS: $cleanUrl")
                M3u8Helper.generateM3u8(sourceName, cleanUrl, effectiveReferer).forEach(callback)
            } else {
                // MP4 direto (GCS ou outros)
                Log.d(TAG, "📺 Processando como MP4: $cleanUrl")
                callback(
                    newExtractorLink(
                        sourceName,
                        "$sourceName - $qualityLabel",
                        cleanUrl
                    ) {
                        this.referer = effectiveReferer
                        this.quality = quality
                    }
                )
            }
            
            Log.d(TAG, "✅ ExtractorLink emitido: $sourceName - $qualityLabel")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao emitir ExtractorLink: ${e.message}")
        }
    }

    /**
     * Valida se é uma URL de vídeo válida (melhorado)
     */
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        if (!url.startsWith("http")) return false
        if (url.length < 10) return false // URLs muito curtas são suspeitas
        
        // Priorizar GCS
        if (url.contains("storage.googleapis.com")) return true
        
        // Padrões de vídeo válidos
        return url.contains(".m3u8") || 
               url.contains(".mp4") || 
               url.contains("/hls/") || 
               url.contains("/video/") ||
               url.contains("/stream/") ||
               url.contains("abyss") ||
               url.contains("abysscdn")
    }
}
