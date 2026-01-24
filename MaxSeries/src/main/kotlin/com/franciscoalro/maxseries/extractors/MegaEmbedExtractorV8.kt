package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v8 - v156 CORRIGIDO COM FETCH/XHR HOOKS
 *
 * PROBLEMA v155: WebView não intercepta requisições fetch/XHR
 * - Requisições assíncronas não passam por shouldInterceptRequest
 * - Regex muito restritivo (só /v4/ com .txt/.m3u8 no final)
 * - Timeout de 60s sem capturar URLs de vídeo
 *
 * SOLUÇÃO v156: FETCH/XHR HOOKS + REGEX ULTRA FLEXÍVEL
 * 1. Hooks JavaScript: Intercepta fetch() e XMLHttpRequest ANTES de enviar
 * 2. Regex ultra flexível: /v4/[a-z0-9]{1,3}/[a-z0-9]{6}/[^"'<>\s]*
 * 3. Timeout aumentado: 120s (para sites muito lentos)
 * 4. Logs detalhados: Debug completo de interceptação
 * 5. Fallback múltiplo: Script > Rede > HTML > Variações
 */
class MegaEmbedExtractorV8 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MegaEmbedV8"
        
        fun canHandle(url: String): Boolean {
            return url.contains("megaembed", true)
        }
    }

    private val cdnHeaders = mapOf(
        "Referer" to "https://megaembed.link/",
        "Origin" to "https://megaembed.link",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    // Estrutura de dados da URL
    data class UrlData(
        val host: String,
        val cluster: String,
        val videoId: String
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MEGAEMBED V8 v156 FETCH/XHR INTERCEPTION ===")
        Log.d(TAG, "Input: $url")
        
        val videoId = extractVideoId(url) ?: run {
            Log.e(TAG, "❌ VideoID não encontrado")
            return
        }
        
        // FASE 1 — CACHE
        VideoUrlCache.get(url)?.let { cached ->
            Log.d(TAG, "✅ CACHE HIT: ${cached.url}")
            M3u8Helper.generateM3u8(
                source = name,
                streamUrl = cached.url,
                referer = mainUrl,
                headers = cdnHeaders
            ).forEach(callback)
            return
        }
        
        // FASE 2 — WEBVIEW COM FETCH/XHR HOOKS (v156)
        Log.d(TAG, "🌐 Iniciando WebView com FETCH/XHR INTERCEPTION...")
        
        runCatching {
            var capturedUrl: String? = null
            
            // Script v163: SEM Auto-Clicker (MegaEmbed carrega automaticamente)
            val fetchXhrScript = """
                (function() {
                    console.log('[MegaEmbed v163] Interceptação ativa - aguardando requisições de vídeo');
                    
                    let captured = false;
                    
                    function trap(url) {
                        if (captured) return; // Evita múltiplas capturas
                        
                        console.log('[MegaEmbed] URL capturada: ' + url);
                        captured = true;
                        window.location.href = url; // Redireciona para CloudStream capturar
                    }

                    // Interceptor XHR
                    const originalXhrOpen = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function(method, url) {
                        if (typeof url === 'string') {
                            if (url.includes('/v4/') || url.includes('.woff2') || url.includes('.m3u8') || url.includes('.txt')) {
                                console.log('[MegaEmbed] XHR detectado: ' + url);
                                trap(url);
                            }
                        }
                        return originalXhrOpen.apply(this, arguments);
                    };

                    // Interceptor Fetch
                    const originalFetch = window.fetch;
                    window.fetch = function(input) {
                        const url = (typeof input === 'string') ? input : (input && input.url);
                        if (url) {
                            if (url.includes('/v4/') || url.includes('.woff2') || url.includes('.m3u8') || url.includes('.txt')) {
                                console.log('[MegaEmbed] Fetch detectado: ' + url);
                                trap(url);
                            }
                        }
                        return originalFetch.apply(this, arguments);
                    };
                    
                    // Polling HTML (fallback)
                    setInterval(function() {
                        if (captured) return;
                        
                        const html = document.documentElement.innerHTML;
                        const match = html.match(/https?:\/\/[^\s"'<>]+\/v4\/[a-z0-9]{1,3}\/[a-z0-9]{6}\/[^\s"'<>]+/i);
                        if (match) {
                            console.log('[MegaEmbed] URL encontrada no HTML: ' + match[0]);
                            trap(match[0]);
                        }
                    }, 1000);
                    
                    console.log('[MegaEmbed] Interceptação configurada com sucesso');
                })();
            """.trimIndent()
            
            // Regex ULTRA SIMPLES + Extensões
            val interceptRegex = Regex(""".*(/v4/|\.woff2|\.m3u8|\.txt).*""", RegexOption.IGNORE_CASE)
            
            val resolver = WebViewResolver(
                interceptUrl = interceptRegex,
                script = fetchXhrScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedUrl = result.trim('\"')
                        Log.d(TAG, "📜 Script capturou: $capturedUrl")
                    }
                },
                timeout = 120_000L // 120s (aumentado de 60s para evitar cancelamento prematuro)
            )
            
            Log.d(TAG, "📱 Carregando página com fetch/XHR interception...")
            val response = app.get(url, headers = cdnHeaders, interceptor = resolver)
            
            // Prioridade: URL do script > URL interceptada via rede
            val finalUrl = capturedUrl ?: response.url.takeIf { 
                it.contains("/v4/") && interceptRegex.containsMatchIn(it) 
            }
            
            Log.d(TAG, "🔍 URL do script: $capturedUrl")
            Log.d(TAG, "🔍 URL da rede: ${response.url}")
            Log.d(TAG, "🔍 URL final: $finalUrl")
            
            if (finalUrl != null && isValidVideoUrl(finalUrl)) {
                Log.d(TAG, "🎯 URL de vídeo capturada com sucesso!")
                
                if (tryUrl(finalUrl)) {
                    val quality = QualityDetector.detectFromUrl(finalUrl)
                    VideoUrlCache.put(url, finalUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = finalUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    return
                }
                
                // Fallback: extrair dados e testar variações
                extractUrlData(finalUrl)?.let { urlData ->
                    Log.d(TAG, "📦 Dados extraídos: host=${urlData.host}, cluster=${urlData.cluster}, videoId=${urlData.videoId}")
                    
                    val fileVariations = listOf(
                        "cf-master.txt",
                        "index-f1-v1-a1.txt",
                        "index-f2-v1-a1.txt",
                        "index.txt",
                        "seg-1-f1-v1-a1.woff2",
                        "seg-1-f1-v1-a1.txt"
                    )
                    
                    for ((index, fileName) in fileVariations.withIndex()) {
                        val testUrl = "https://${urlData.host}/v4/${urlData.cluster}/${urlData.videoId}/$fileName"
                        Log.d(TAG, "🧪 Testando ${index + 1}/${fileVariations.size}: $fileName")
                        
                        if (tryUrl(testUrl)) {
                            Log.d(TAG, "✅ SUCESSO! URL válida: $testUrl")
                            
                            val quality = QualityDetector.detectFromUrl(testUrl)
                            VideoUrlCache.put(url, testUrl, quality, name)
                            
                            M3u8Helper.generateM3u8(
                                source = name,
                                streamUrl = testUrl,
                                referer = mainUrl,
                                headers = cdnHeaders
                            ).forEach(callback)
                            return
                        }
                    }
                }
            }
            
            // Fallback final: buscar no HTML
            Log.d(TAG, "⚠️ Tentando fallback via HTML...")
            val html = response.text
            Log.d(TAG, "📄 HTML (${html.length} chars)")
            
            val v4Regex = Regex(
                """https?://[^\s"'<>]+/v4/[a-z0-9]{1,3}/[a-z0-9]{6}/[^\s"'<>]*(?:\.(txt|m3u8|woff2))?""",
                RegexOption.IGNORE_CASE
            )
            v4Regex.find(html)?.let { match ->
                val foundUrl = match.value
                Log.d(TAG, "✅ Encontrado no HTML: $foundUrl")
                
                if (tryUrl(foundUrl)) {
                    val quality = QualityDetector.detectFromUrl(foundUrl)
                    VideoUrlCache.put(url, foundUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = foundUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    return
                }
            }
            
            Log.e(TAG, "❌ Todas as estratégias falharam")
            
        }.onFailure {
            Log.e(TAG, "❌ Erro: ${it.message}")
            it.printStackTrace()
        }
    }
    
    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty() || !url.startsWith("http")) return false
        return url.contains(".txt") || url.contains(".m3u8") || 
               url.contains("cf-master") || url.contains("index-f") ||
               url.contains("/v4/")
    }
    
    /**
     * Extrai host, cluster e videoId de uma URL capturada
     * 
     * Exemplos:
     * - https://soq6.valenium.shop/v4/is9/xez5rx/seg-1-f1-v1-a1.woff2
     *   → host=soq6.valenium.shop, cluster=is9, videoId=xez5rx
     * 
     * - https://srcf.veritasholdings.cyou/v4/ic/6pyw8t/index-f1-v1-a1.txt
     *   → host=srcf.veritasholdings.cyou, cluster=ic, videoId=6pyw8t
     */
    private fun extractUrlData(url: String): UrlData? {
        // Regex: https://{host}/v4/{cluster}/{videoId}/{qualquer-arquivo}
        val regex = Regex("""https?://([^/]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})""", RegexOption.IGNORE_CASE)
        val match = regex.find(url) ?: return null
        
        return UrlData(
            host = match.groupValues[1],
            cluster = match.groupValues[2],
            videoId = match.groupValues[3]
        )
    }
    
    /**
     * Testa se uma URL é válida (retorna 200 OK)
     */
    private suspend fun tryUrl(url: String): Boolean {
        return runCatching {
            val response = app.get(url, headers = cdnHeaders, timeout = 5)
            val isValid = response.code in 200..299 && response.text.isNotBlank()
            
            if (isValid) {
                Log.d(TAG, "✅ URL válida (${response.code}): $url")
            } else {
                Log.d(TAG, "❌ URL inválida (${response.code}): $url")
            }
            
            isValid
        }.getOrElse { 
            Log.d(TAG, "❌ Erro ao testar URL: ${it.message}")
            false 
        }
    }
    
    private fun extractVideoId(url: String): String? {
        return Regex("""#([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
    }
}
