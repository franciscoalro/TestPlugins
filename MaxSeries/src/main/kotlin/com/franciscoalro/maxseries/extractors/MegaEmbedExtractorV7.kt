package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v7 - v150 HÍBRIDO COM HOOKS
 *
 * PROBLEMA v149: WebView não intercepta requisições fetch/XHR
 * - Requisições assíncronas não passam por shouldInterceptRequest
 * - Regex muito restritivo (só \.txt no final)
 * - Timeout de 20s sem capturar URLs de vídeo
 *
 * SOLUÇÃO v150: HOOKS FETCH/XHR + REGEX MELHORADO
 * 1. Hooks JavaScript: Intercepta fetch() e XMLHttpRequest
 * 2. Regex amplo: /v4/.*\.(txt|m3u8|woff2)
 * 3. Timeout aumentado: 30s (para sites lentos)
 * 4. Logs detalhados: Debug completo de interceptação
 * 5. Array de captura: Múltiplas URLs detectadas
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
        Log.d(TAG, "=== MEGAEMBED V7 v155 CRYPTO INTERCEPTION ===")
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
        
        // FASE 2 — WEBVIEW COM SCRIPT ATIVO (v155): Intercepta crypto.subtle.decrypt()
        Log.d(TAG, "🌐 Iniciando WebView com CRYPTO INTERCEPTION...")
        
        runCatching {
            var capturedUrl: String? = null
            
            // Script de crypto interception - intercepta descriptografia AES
            val cryptoScript = """
                (function() {
                    console.log('[MegaEmbed v155] Iniciando captura...');
                    
                    // Interceptar crypto.subtle.decrypt se disponível
                    if (window.crypto && window.crypto.subtle) {
                        const originalDecrypt = window.crypto.subtle.decrypt;
                        window.crypto.subtle.decrypt = function(...args) {
                            return originalDecrypt.apply(this, args).then(result => {
                                try {
                                    const text = new TextDecoder().decode(result);
                                    console.log('[MegaEmbed v155] Descriptografado:', text.substring(0, 200));
                                    
                                    // Procurar URL no texto descriptografado
                                    const urlMatch = text.match(/https?:\/\/[^\s"'<>]+\.(txt|m3u8)/i);
                                    if (urlMatch) {
                                        window.__MEGAEMBED_VIDEO_URL__ = urlMatch[0];
                                        console.log('[MegaEmbed v155] ✅ URL capturada:', urlMatch[0]);
                                    }
                                    
                                    // Tentar parsear como JSON
                                    try {
                                        const json = JSON.parse(text);
                                        const u = json.url || json.file || json.source || json.playlist;
                                        if (u && (u.includes('.txt') || u.includes('.m3u8'))) {
                                            window.__MEGAEMBED_VIDEO_URL__ = u;
                                            console.log('[MegaEmbed v155] ✅ URL do JSON:', u);
                                        }
                                    } catch(e) {}
                                } catch(e) {}
                                return result;
                            });
                        };
                    }
                    
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 600; // 60s
                        
                        var interval = setInterval(function() {
                            attempts++;
                            
                            // 1. Verificar variável global da interceptação
                            if (window.__MEGAEMBED_VIDEO_URL__) {
                                clearInterval(interval);
                                resolve(window.__MEGAEMBED_VIDEO_URL__);
                                return;
                            }
                            
                            // 2. Buscar no DOM
                            var html = document.documentElement.innerHTML;
                            
                            // Padrão: URLs com /v4/ e .txt ou .m3u8
                            var v4Match = html.match(/https?:\/\/[^\s"'<>]+\/v4\/[a-z0-9]+\/[a-z0-9]+\/[^\s"'<>]+\.(txt|m3u8)/i);
                            if (v4Match) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v155] ✅ URL no DOM:', v4Match[0]);
                                resolve(v4Match[0]);
                                return;
                            }
                            
                            // Padrão: cf-master ou index-f
                            var cfMatch = html.match(/https?:\/\/[^\s"'<>]+(?:cf-master|index-f)[^\s"'<>]+\.txt/i);
                            if (cfMatch) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v155] ✅ cf-master/index:', cfMatch[0]);
                                resolve(cfMatch[0]);
                                return;
                            }
                            
                            // Timeout
                            if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                console.log('[MegaEmbed v155] ⏱️ Timeout após 60s');
                                resolve('');
                            }
                        }, 100);
                    });
                })();
            """.trimIndent()
            
            // Regex para interceptar arquivos de vídeo via rede
            val interceptRegex = Regex("""/v4/[^"'\s]+\.(txt|m3u8|woff2)""", RegexOption.IGNORE_CASE)
            
            val resolver = WebViewResolver(
                interceptUrl = interceptRegex,
                script = cryptoScript,
                scriptCallback = { result ->
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedUrl = result.trim('"')
                        Log.d(TAG, "📜 Script capturou: $capturedUrl")
                    }
                },
                timeout = 60_000L // 60s
            )
            
            Log.d(TAG, "📱 Carregando página com crypto interception...")
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
                        "index.txt"
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
            
            val v4Regex = Regex("""https?://[^\s"'<>]+/v4/[a-z0-9]+/[a-z0-9]+/[^\s"'<>]+\.(txt|m3u8)""", RegexOption.IGNORE_CASE)
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
