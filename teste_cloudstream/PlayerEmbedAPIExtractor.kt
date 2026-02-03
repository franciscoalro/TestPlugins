/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PLAYEREMBEDAPI EXTRACTOR - MaxSeries Provider
 * Advanced Video Extraction with Multiple Fallback Techniques
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Técnicas implementadas (em ordem de prioridade):
 * 1. Extração direta via HTTP (regex de URLs de vídeo)
 * 2. Parse de JSON inline no HTML
 * 3. Decodificação do campo 'datas' base64
 * 4. WebView com interceptação de sssrr.org
 * 5. JavaScript injection para extrair do JWPlayer
 * 
 * Padrões de URL detectados:
 * - https://*.sssrr.org/sora/{video_id}/{token}
 * - https://*.sssrr.org/{path}/{hash}.{video_id}.{quality}.fd
 * - https://*.sssrr.org/future
 * 
 * Headers críticos:
 * - Referer: https://playerembedapi.link/
 * - Origin: https://playerembedapi.link
 */

package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import org.jsoup.nodes.Document
import java.util.Base64

class PlayerEmbedAPIExtractor {
    
    companion object {
        const val TAG = "PlayerEmbedAPI"
        
        // Padrões de URL de vídeo do PlayerEmbedAPI
        private val VIDEO_URL_PATTERNS = listOf(
            // Padrão sssrr.org (CDN principal)
            Regex("""https?://[^\s"'<>]+\.sssrr\.org/[^\s"'<>]+"""),
            // Padrão googleapis (fallback)
            Regex("""https?://[^\s"'<>]*googleapis\.com/mediastorage/[^\s"'<>]*\.mp4[^\s"'<>]*"""),
            // M3U8 playlists
            Regex("""https?://[^\s"'<>]+\.m3u8[^\s"'<>]*"""),
            // MP4 direto
            Regex("""https?://[^\s"'<>]+\.mp4[^\s"'<>]*"""),
        )
        
        // Regex para interceptação no WebView
        private val WEBVIEW_INTERCEPT_PATTERN = Regex(
            """(?i)(?:sssrr\.org|googleapis\.com/mediastorage|\.m3u8|\.mp4|/hls/|/video/)"""
        )
    }
    
    /**
     * Extrai links de vídeo de uma URL do PlayerEmbedAPI
     * Implementa múltiplas técnicas em cascata
     */
    suspend fun extract(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        Log.d(TAG, "Iniciando extração: $url")
        
        var found = false
        
        // TÉCNICA 1: Extração HTTP direta (mais rápida)
        if (extractDirectHTTP(url, callback)) {
            Log.d(TAG, "✓ Extração HTTP direta bem-sucedida")
            found = true
        }
        
        // TÉCNICA 2: Parse do campo 'datas' base64
        if (!found && extractFromDatasField(url, callback)) {
            Log.d(TAG, "✓ Extração via campo datas bem-sucedida")
            found = true
        }
        
        // TÉCNICA 3: WebView com interceptação
        if (!found && extractWithWebView(url, callback)) {
            Log.d(TAG, "✓ Extração via WebView bem-sucedida")
            found = true
        }
        
        return found
    }
    
    /**
     * TÉCNICA 1: Extração direta via HTTP
     * Analisa o HTML em busca de URLs de vídeo
     */
    private suspend fun extractDirectHTTP(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val response = app.get(url, timeout = 30)
            val html = response.text
            
            Log.d(TAG, "HTML obtido: ${html.length} bytes")
            
            var found = false
            
            // 1.1: Procurar por URLs de vídeo com regex
            for (pattern in VIDEO_URL_PATTERNS) {
                pattern.findAll(html).forEach { match ->
                    val videoUrl = match.value
                    if (isValidVideoUrl(videoUrl)) {
                        Log.d(TAG, "URL encontrada (regex): ${videoUrl.take(80)}...")
                        
                        val quality = extractQualityFromUrl(videoUrl)
                        
                        if (videoUrl.contains(".m3u8")) {
                            M3u8Helper.generateM3u8(
                                "PlayerEmbedAPI",
                                videoUrl,
                                url
                            ).forEach { link ->
                                callback(link)
                                found = true
                            }
                        } else {
                            callback(
                                newExtractorLink(
                                    "PlayerEmbedAPI",
                                    "PlayerEmbedAPI - $quality",
                                    videoUrl
                                ) {
                                    this.referer = url
                                    this.quality = getQualityFromName(quality)
                                }
                            )
                            found = true
                        }
                    }
                }
            }
            
            // 1.2: Procurar por JSON com configuração
            if (!found) {
                found = extractFromJsonConfig(html, url, callback)
            }
            
            // 1.3: Procurar por atributos data-*
            if (!found) {
                found = extractFromDataAttributes(html, url, callback)
            }
            
            found
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro na extração HTTP direta: ${e.message}")
            false
        }
    }
    
    /**
     * TÉCNICA 2: Extração do campo 'datas' base64
     * Decodifica o campo que contém metadados do vídeo
     */
    private suspend fun extractFromDatasField(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val response = app.get(url, timeout = 30)
            val html = response.text
            
            // Extrair campo datas
            val datasPattern = Regex("""const\s+datas\s*=\s*"([^"]+)"""")
            val match = datasPattern.find(html)
            
            if (match == null) {
                Log.d(TAG, "Campo datas não encontrado")
                return false
            }
            
            val datasB64 = match.groupValues[1]
            Log.d(TAG, "Campo datas encontrado: ${datasB64.take(50)}...")
            
            // Decodificar base64
            val decoded = try {
                val padded = padBase64(datasB64)
                String(Base64.getDecoder().decode(padded), Charsets.UTF_8)
            } catch (e: Exception) {
                Log.e(TAG, "Erro ao decodificar base64: ${e.message}")
                return false
            }
            
            Log.d(TAG, "Datas decodificado: ${decoded.take(100)}...")
            
            // Parse JSON
            val json = org.json.JSONObject(decoded)
            val slug = json.optString("slug")
            val md5Id = json.optInt("md5_id")
            val userId = json.optInt("user_id")
            
            Log.d(TAG, "Dados: slug=$slug, md5_id=$md5Id, user_id=$userId")
            
            // Tentar construir URL do CDN
            // Padrão: https://{slug}.sssrr.org/sora/{md5_id}/
            if (slug.isNotEmpty() && md5Id > 0) {
                val potentialUrls = listOf(
                    "https://${slug}.sssrr.org/sora/$md5Id/",
                    "https://cdn.sssrr.org/sora/$md5Id/",
                )
                
                for (potentialUrl in potentialUrls) {
                    // Verificar se URL existe
                    try {
                        val headResponse = app.head(potentialUrl, timeout = 10)
                        if (headResponse.isSuccessful) {
                            Log.d(TAG, "URL CDN válida: $potentialUrl")
                            
                            callback(
                                newExtractorLink(
                                    "PlayerEmbedAPI",
                                    "PlayerEmbedAPI - CDN",
                                    potentialUrl
                                ) {
                                    this.referer = url
                                    this.quality = Qualities.Unknown.value
                                }
                            )
                            return true
                        }
                    } catch (e: Exception) {
                        // Continuar para próxima URL
                    }
                }
            }
            
            false
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro na extração do campo datas: ${e.message}")
            false
        }
    }
    
    /**
     * TÉCNICA 3: Extração via WebView
     * Usa WebViewResolver para interceptar requisições de vídeo
     */
    private suspend fun extractWithWebView(
        url: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            Log.d(TAG, "Iniciando WebView extraction...")
            
            // Script JS para extrair do JWPlayer
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        // Aguardar JWPlayer carregar
                        var attempts = 0;
                        var maxAttempts = 30;
                        
                        var checkInterval = setInterval(function() {
                            attempts++;
                            var result = null;
                            
                            // Tentar extrair do JWPlayer
                            if (window.jwplayer) {
                                try {
                                    var jw = jwplayer();
                                    if (jw && jw.getPlaylist) {
                                        var playlist = jw.getPlaylist();
                                        if (playlist && playlist[0]) {
                                            var item = playlist[0];
                                            if (item.file) {
                                                result = JSON.stringify({
                                                    type: 'jwplayer',
                                                    url: item.file,
                                                    quality: item.label || 'unknown'
                                                });
                                            }
                                            if (item.sources) {
                                                var sources = item.sources.filter(function(s) {
                                                    return s.file && s.file.length > 10;
                                                });
                                                if (sources.length > 0) {
                                                    result = JSON.stringify({
                                                        type: 'jwplayer-sources',
                                                        sources: sources
                                                    });
                                                }
                                            }
                                        }
                                    }
                                } catch(e) {}
                            }
                            
                            // Tentar video element
                            if (!result) {
                                var video = document.querySelector('video');
                                if (video && video.src && video.src.length > 10) {
                                    result = JSON.stringify({
                                        type: 'video-element',
                                        url: video.src
                                    });
                                }
                            }
                            
                            if (result || attempts >= maxAttempts) {
                                clearInterval(checkInterval);
                                resolve(result || '');
                            }
                        }, 1000);
                    });
                })()
            """.trimIndent()
            
            var capturedResult: String? = null
            
            val resolver = WebViewResolver(
                interceptUrl = WEBVIEW_INTERCEPT_PATTERN,
                additionalUrls = listOf(
                    Regex("""\.m3u8"""),
                    Regex("""\.mp4"""),
                    Regex("""sssrr\.org""")
                ),
                useOkhttp = false,  // IMPORTANTE: false para bypass
                script = captureScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null") {
                        Log.d(TAG, "WebView capturou: ${result.take(100)}...")
                        capturedResult = result
                    }
                },
                timeout = 35_000L
            )
            
            val response = app.get(url, interceptor = resolver)
            val interceptedUrl = response.url
            
            var found = false
            
            // Verificar URL interceptada
            if (isValidVideoUrl(interceptedUrl)) {
                Log.d(TAG, "URL interceptada: $interceptedUrl")
                
                if (interceptedUrl.contains(".m3u8")) {
                    M3u8Helper.generateM3u8(
                        "PlayerEmbedAPI",
                        interceptedUrl,
                        url
                    ).forEach { link ->
                        callback(link)
                        found = true
                    }
                } else {
                    callback(
                        newExtractorLink(
                            "PlayerEmbedAPI",
                            "PlayerEmbedAPI - WebView",
                            interceptedUrl
                        ) {
                            this.referer = url
                            this.quality = Qualities.Unknown.value
                        }
                    )
                    found = true
                }
            }
            
            // Verificar resultado do script
            if (!found && capturedResult != null) {
                found = parseWebViewResult(capturedResult!!, url, callback)
            }
            
            found
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro na extração WebView: ${e.message}")
            false
        }
    }
    
    /**
     * Extrai de JSON inline no HTML
     */
    private fun extractFromJsonConfig(
        html: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val patterns = listOf(
            Regex("""var\s+config\s*=\s*(\{[^;]+\});"""),
            Regex("""var\s+sources\s*=\s*(\[[^\\]]+\]);"""),
            Regex(""""sources"\s*:\s*(\[[^\\]]+\])"""),
        )
        
        for (pattern in patterns) {
            pattern.findAll(html).forEach { match ->
                try {
                    val jsonStr = match.groupValues[1]
                    val json = org.json.JSONObject("""{"data": $jsonStr}""")
                    val data = json.optJSONArray("data")
                    
                    if (data != null) {
                        for (i in 0 until data.length()) {
                            val item = data.optJSONObject(i)
                            val file = item?.optString("file")
                            val label = item?.optString("label", "Unknown")
                            
                            if (!file.isNullOrEmpty()) {
                                if (file.contains(".m3u8")) {
                                    M3u8Helper.generateM3u8(
                                        "PlayerEmbedAPI",
                                        file,
                                        referer
                                    ).forEach { callback(it) }
                                } else {
                                    callback(
                                        newExtractorLink(
                                            "PlayerEmbedAPI",
                                            "PlayerEmbedAPI - $label",
                                            file
                                        ) {
                                            this.referer = referer
                                            this.quality = getQualityFromName(label)
                                        }
                                    )
                                }
                                return true
                            }
                        }
                    }
                } catch (e: Exception) {
                    // Ignorar erros de parse
                }
            }
        }
        
        return false
    }
    
    /**
     * Extrai de atributos data-*
     */
    private fun extractFromDataAttributes(
        html: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // Procurar por data-source, data-video, etc.
        val patterns = listOf(
            Regex("""data-source\s*=\s*"([^"]+)"""),
            Regex("""data-video\s*=\s*"([^"]+)"""),
            Regex("""data-url\s*=\s*"([^"]+)"""),
        )
        
        for (pattern in patterns) {
            pattern.findAll(html).forEach { match ->
                val videoUrl = match.groupValues[1]
                if (isValidVideoUrl(videoUrl)) {
                    callback(
                        newExtractorLink(
                            "PlayerEmbedAPI",
                            "PlayerEmbedAPI",
                            videoUrl
                        ) {
                            this.referer = referer
                            this.quality = Qualities.Unknown.value
                        }
                    )
                    return true
                }
            }
        }
        
        return false
    }
    
    /**
     * Parse do resultado do WebView
     */
    private fun parseWebViewResult(
        result: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        return try {
            val json = org.json.JSONObject(result)
            val type = json.optString("type")
            
            when (type) {
                "jwplayer", "video-element" -> {
                    val videoUrl = json.optString("url")
                    if (videoUrl.isNotEmpty()) {
                        if (videoUrl.contains(".m3u8")) {
                            M3u8Helper.generateM3u8(
                                "PlayerEmbedAPI",
                                videoUrl,
                                referer
                            ).forEach { callback(it) }
                        } else {
                            callback(
                                newExtractorLink(
                                    "PlayerEmbedAPI",
                                    "PlayerEmbedAPI",
                                    videoUrl
                                ) {
                                    this.referer = referer
                                    this.quality = Qualities.Unknown.value
                                }
                            )
                        }
                        true
                    } else false
                }
                "jwplayer-sources" -> {
                    val sources = json.optJSONArray("sources")
                    if (sources != null) {
                        for (i in 0 until sources.length()) {
                            val source = sources.optJSONObject(i)
                            val file = source?.optString("file")
                            val label = source?.optString("label", "Unknown")
                            
                            if (!file.isNullOrEmpty()) {
                                callback(
                                    newExtractorLink(
                                        "PlayerEmbedAPI",
                                        "PlayerEmbedAPI - $label",
                                        file
                                    ) {
                                        this.referer = referer
                                        this.quality = getQualityFromName(label)
                                    }
                                )
                            }
                        }
                        true
                    } else false
                }
                else -> false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao parse resultado WebView: ${e.message}")
            false
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // HELPERS
    // ═══════════════════════════════════════════════════════════════════════════
    
    private fun isValidVideoUrl(url: String): Boolean {
        return url.startsWith("http") && (
            url.contains(".m3u8") ||
            url.contains(".mp4") ||
            url.contains("sssrr.org") ||
            url.contains("googleapis.com/mediastorage")
        )
    }
    
    private fun extractQualityFromUrl(url: String): String {
        val patterns = listOf(
            Regex("""(\d{3,4})p"""),
            Regex("""\.(\d{3,4})\."""),
        )
        
        for (pattern in patterns) {
            pattern.find(url)?.let { return it.groupValues[1] + "p" }
        }
        
        return "HD"
    }
    
    private fun padBase64(input: String): String {
        val padding = 4 - input.length % 4
        return if (padding != 4) input + "=".repeat(padding) else input
    }
    
    private fun getQualityFromName(name: String?): Int {
        return when {
            name.isNullOrEmpty() -> Qualities.Unknown.value
            name.contains("1080", true) -> Qualities.P1080.value
            name.contains("720", true) -> Qualities.P720.value
            name.contains("480", true) -> Qualities.P480.value
            name.contains("360", true) -> Qualities.P360.value
            else -> Qualities.Unknown.value
        }
    }
}
