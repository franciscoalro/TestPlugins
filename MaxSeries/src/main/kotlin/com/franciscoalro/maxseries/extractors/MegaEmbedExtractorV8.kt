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
            
            // Script MELHORADO: Intercepta fetch() e XMLHttpRequest ANTES de enviar
            val fetchXhrScript = """
                (function() {
                    console.log('[MegaEmbed v156] Iniciando captura com fetch/XHR hooks...');
                    
                    // ===== INTERCEPTAR FETCH =====
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        const url = args[0];
                        console.log('[MegaEmbed v156] FETCH:', url);
                        
                        // Se a URL contém /v4/, capturar imediatamente
                        if (typeof url === 'string' && url.includes('/v4/')) {
                            window.__MEGAEMBED_VIDEO_URL__ = url;
                            console.log('[MegaEmbed v156] ✅ URL capturada via FETCH:', url);
                        }
                        
                        return originalFetch.apply(this, args).then(response => {
                            const cloned = response.clone();
                            
                            // Tentar ler o corpo da resposta
                            cloned.text().then(text => {
                                try {
                                    // Procurar URL no texto da resposta
                                    const urlMatch = text.match(/https?:\/\/[^\s"'<>]+\/v4\/[a-z0-9]{1,3}\/[a-z0-9]{6}\/[^\s"'<>]*(?:\.(txt|m3u8|woff2))?/i);
                                    if (urlMatch) {
                                        window.__MEGAEMBED_VIDEO_URL__ = urlMatch[0];
                                        console.log('[MegaEmbed v156] ✅ URL capturada na resposta FETCH:', urlMatch[0]);
                                    }
                                    
                                    // Tentar parsear como JSON
                                    try {
                                        const json = JSON.parse(text);
                                        const u = json.url || json.file || json.source || json.playlist || json.data?.url;
                                        if (u && (u.includes('/v4/') || u.includes('.txt') || u.includes('.m3u8'))) {
                                            window.__MEGAEMBED_VIDEO_URL__ = u;
                                            console.log('[MegaEmbed v156] ✅ URL do JSON:', u);
                                        }
                                    } catch(e) {}
                                } catch(e) {
                                    console.log('[MegaEmbed v156] Erro ao processar resposta:', e);
                                }
                            }).catch(e => console.log('[MegaEmbed v156] Erro ao ler resposta:', e));
                            
                            return response;
                        }).catch(e => {
                            console.log('[MegaEmbed v156] Erro no fetch:', e);
                            return originalFetch.apply(this, args);
                        });
                    };
                    
                    // ===== INTERCEPTAR XMLHttpRequest =====
                    const originalOpen = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                        console.log('[MegaEmbed v156] XHR:', method, url);
                        
                        // Se a URL contém /v4/, capturar imediatamente
                        if (typeof url === 'string' && url.includes('/v4/')) {
                            window.__MEGAEMBED_VIDEO_URL__ = url;
                            console.log('[MegaEmbed v156] ✅ URL capturada via XHR:', url);
                        }
                        
                        return originalOpen.apply(this, [method, url, ...rest]);
                    };
                    
                    // Interceptar onreadystatechange para capturar resposta
                    const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
                    XMLHttpRequest.prototype.setRequestHeader = function(...args) {
                        return originalSetRequestHeader.apply(this, args);
                    };
                    
                    // ===== POLLING PARA CAPTURAR VARIÁVEIS GLOBAIS =====
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 1200; // 120s (100ms × 1200)
                        
                        var interval = setInterval(function() {
                            attempts++;
                            
                            // 1. Verificar variável global da interceptação
                            if (window.__MEGAEMBED_VIDEO_URL__) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v156] ✅ SUCESSO! URL capturada:', window.__MEGAEMBED_VIDEO_URL__);
                                resolve(window.__MEGAEMBED_VIDEO_URL__);
                                return;
                            }
                            
                            // 2. Buscar no DOM (procurar em scripts, iframes, etc)
                            var html = document.documentElement.innerHTML;
                            
                            // Padrão: URLs com /v4/ (ULTRA FLEXÍVEL)
                            var v4Match = html.match(/https?:\/\/[^\s"'<>]+\/v4\/[a-z0-9]{1,3}\/[a-z0-9]{6}\/[^\s"'<>]*(?:\.(txt|m3u8|woff2))?/i);
                            if (v4Match) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v156] ✅ URL no DOM:', v4Match[0]);
                                resolve(v4Match[0]);
                                return;
                            }
                            
                            // 3. Procurar em atributos de data
                            var dataMatch = html.match(/data-url\s*=\s*["\']([^"\']+\/v4\/[^"\']+)["\']/i);
                            if (dataMatch) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v156] ✅ URL em data-url:', dataMatch[1]);
                                resolve(dataMatch[1]);
                                return;
                            }
                            
                            // 4. Procurar em variáveis JavaScript
                            var varMatch = html.match(/(?:var|let|const)\s+\w*url\w*\s*=\s*["\']([^"\']+\/v4\/[^"\']+)["\']/i);
                            if (varMatch) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v156] ✅ URL em variável:', varMatch[1]);
                                resolve(varMatch[1]);
                                return;
                            }
                            
                            // Timeout
                            if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v156] ⏱️ Timeout após 120s');
                                resolve('');
                            }
                        }, 100);
                    });
                })();
            """.trimIndent()
            
            // Regex ULTRA FLEXÍVEL para interceptar arquivos de vídeo via rede
            val interceptRegex = Regex(
                """https?://[^/\s"'<>]+/v4/[a-z0-9]{1,3}/[a-z0-9]{6}/[^"'<>\s]*(?:\.(txt|m3u8|woff2))?(?:\?[^"'<>\s]*)?""",
                RegexOption.IGNORE_CASE
            )
            
            val resolver = WebViewResolver(
                interceptUrl = interceptRegex,
                script = fetchXhrScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedUrl = result.trim('\"')
                        Log.d(TAG, "📜 Script capturou: $capturedUrl")
                    }
                },
                timeout = 120_000L // 120s (2 minutos)
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
