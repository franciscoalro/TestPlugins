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
        Log.d(TAG, "=== MEGAEMBED V7 v150 HÍBRIDO COM HOOKS ===")
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
        
        // FASE 2 — BUSCAR PADRÕES NO HTML (SEM WEBVIEW)
        Log.d(TAG, "🔍 Buscando padrões de vídeo no HTML...")
        
        runCatching {
            val htmlResponse = app.get(url, headers = cdnHeaders)
            val html = htmlResponse.text
            
            Log.d(TAG, "📄 HTML recebido (${html.length} chars)")
            
            // Padrão 1: cf-master com timestamp
            val cfMasterRegex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/cf-master\.(\d+)\.txt""", RegexOption.IGNORE_CASE)
            val cfMasterMatch = cfMasterRegex.find(html)
            
            if (cfMasterMatch != null) {
                val cfMasterUrl = cfMasterMatch.value
                val host = cfMasterMatch.groupValues[1]
                val cluster = cfMasterMatch.groupValues[2]
                val videoIdFound = cfMasterMatch.groupValues[3]
                val timestamp = cfMasterMatch.groupValues[4]
                
                Log.d(TAG, "✅ cf-master encontrado: host=$host, cluster=$cluster, videoId=$videoIdFound, timestamp=$timestamp")
                Log.d(TAG, "🔗 URL completa: $cfMasterUrl")
                
                if (tryUrl(cfMasterUrl)) {
                    Log.d(TAG, "✅ cf-master válido!")
                    
                    val quality = QualityDetector.detectFromUrl(cfMasterUrl)
                    VideoUrlCache.put(url, cfMasterUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = cfMasterUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    
                    return
                }
            }
            
            // Padrão 2: index-f{n}-v{n}-a{n}.txt
            val indexRegex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/index-f\d+-v\d+-a\d+\.txt""", RegexOption.IGNORE_CASE)
            val indexMatch = indexRegex.find(html)
            
            if (indexMatch != null) {
                val indexUrl = indexMatch.value
                val host = indexMatch.groupValues[1]
                val cluster = indexMatch.groupValues[2]
                val videoIdFound = indexMatch.groupValues[3]
                
                Log.d(TAG, "✅ index encontrado: host=$host, cluster=$cluster, videoId=$videoIdFound")
                Log.d(TAG, "🔗 URL completa: $indexUrl")
                
                if (tryUrl(indexUrl)) {
                    Log.d(TAG, "✅ index válido!")
                    
                    val quality = QualityDetector.detectFromUrl(indexUrl)
                    VideoUrlCache.put(url, indexUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = indexUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    
                    return
                }
            }
            
            // Padrão 3: Extrair host/cluster/videoId de qualquer arquivo /v4/
            val v4Regex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/[^"'\s]+""", RegexOption.IGNORE_CASE)
            val v4Match = v4Regex.find(html)
            
            if (v4Match != null) {
                val host = v4Match.groupValues[1]
                val cluster = v4Match.groupValues[2]
                val videoIdFound = v4Match.groupValues[3]
                
                Log.d(TAG, "✅ Padrão /v4/ encontrado: host=$host, cluster=$cluster, videoId=$videoIdFound")
                
                // Tentar variações de arquivo
                val fileVariations = listOf(
                    "index-f1-v1-a1.txt",
                    "index-f2-v1-a1.txt",
                    "index.txt",
                    "cf-master.txt"
                )
                
                for ((index, fileName) in fileVariations.withIndex()) {
                    val testUrl = "https://$host/v4/$cluster/$videoIdFound/$fileName"
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
            
            Log.d(TAG, "⏭️ Nenhum padrão encontrado no HTML, tentando WebView...")
            
        }.onFailure {
            Log.e(TAG, "❌ Erro ao buscar no HTML: ${it.message}")
        }
        
        // FASE 2 — WEBVIEW HÍBRIDO (v149)
        Log.d(TAG, "🔍 Iniciando WebView HÍBRIDO (interceptação + script + API)...")
        
        runCatching {
            var capturedApiUrl: String? = null
            
            // Script JavaScript SIMPLIFICADO - executa no WebView
            val hybridScript = """
                (function() {
                    var capturedUrls = [];
                    var found = false;
                    
                    // HOOK FETCH
                    if (typeof window.fetch !== 'undefined') {
                        var originalFetch = window.fetch;
                        window.fetch = function() {
                            var url = arguments[0];
                            if (typeof url === 'string' && (url.includes('/v4/') || url.match(/\.(txt|m3u8|woff2)/i))) {
                                capturedUrls.push(url);
                                found = true;
                            }
                            return originalFetch.apply(this, arguments);
                        };
                    }
                    
                    // HOOK XHR
                    if (typeof XMLHttpRequest !== 'undefined') {
                        var originalOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function(method, url) {
                            if (typeof url === 'string' && (url.includes('/v4/') || url.match(/\.(txt|m3u8|woff2)/i))) {
                                capturedUrls.push(url);
                                found = true;
                            }
                            return originalOpen.apply(this, arguments);
                        };
                    }
                    
                    // AGUARDAR CAPTURA
                    var attempts = 0;
                    var checkInterval = setInterval(function() {
                        attempts++;
                        
                        if (found && capturedUrls.length > 0) {
                            clearInterval(checkInterval);
                            var best = capturedUrls.find(function(u) { return u.includes('cf-master') || u.includes('index-f'); }) || capturedUrls[0];
                            window.__RESULT__ = best;
                            return;
                        }
                        
                        // FALLBACK: buscar no HTML
                        if (attempts === 30) {
                            var html = document.documentElement.innerHTML;
                            var match = html.match(/https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.(txt|m3u8)/i);
                            if (match) {
                                clearInterval(checkInterval);
                                window.__RESULT__ = match[0];
                                return;
                            }
                        }
                        
                        if (attempts >= 150) {
                            clearInterval(checkInterval);
                            window.__RESULT__ = capturedUrls[0] || '';
                        }
                    }, 100);
                    
                    // RETORNAR RESULTADO APÓS DELAY
                    setTimeout(function() {
                        return window.__RESULT__ || '';
                    }, 15000);
                })();
                
                // RETORNAR RESULTADO FINAL
                (function check() {
                    if (typeof window.__RESULT__ !== 'undefined') {
                        return window.__RESULT__;
                    }
                    return '';
                })();
            """.trimIndent()
            
            // REGEX MELHORADO: Intercepta /v4/ com arquivos de vídeo
            val interceptRegex = Regex("""/v4/[^"'\s]+\.(txt|m3u8|woff2)""", RegexOption.IGNORE_CASE)
            
            // additionalUrls: Captura requisições específicas
            val additionalUrls = listOf(
                Regex("""/api/v1/info"""),
                Regex("""/api/v1/video"""),
                Regex("""/api/v1/player"""),
                Regex("""cf-master\.\d+\.txt"""),
                Regex("""index-f\d+-v\d+-a\d+\.txt"""),
                Regex("""/v4/[^/]+/[^/]+/[^"'\s]+\.txt""")
            )
            
            val resolver = WebViewResolver(
                interceptUrl = interceptRegex,
                additionalUrls = additionalUrls,
                script = hybridScript,
                scriptCallback = { result ->
                    Log.d(TAG, "📜 scriptCallback recebeu: '$result' (tipo: ${result.javaClass.simpleName}, tamanho: ${result.length})")
                    if (result.isNotEmpty() && result != "null" && result.startsWith("http")) {
                        capturedApiUrl = result.trim('"')
                        Log.d(TAG, "✅ Script capturou URL VÁLIDA: $capturedApiUrl")
                    } else {
                        Log.d(TAG, "⚠️ Script retornou valor inválido ou vazio")
                    }
                },
                timeout = 30_000L // Aumentado para 30s (sites lentos)
            )
            
            Log.d(TAG, "🌐 Carregando WebView...")
            val response = app.get(url, headers = cdnHeaders, interceptor = resolver)
            val capturedUrl = response.url
            
            Log.d(TAG, "📄 WebView interceptou (response.url): $capturedUrl")
            Log.d(TAG, "📜 Script retornou: $capturedApiUrl")
            
            // PRIORIDADE: Script > Interceptação
            val finalUrl = capturedApiUrl ?: capturedUrl
            
            Log.d(TAG, "🔍 Analisando URL final: $finalUrl")
            
            // FASE 3 — PROCESSAR URL CAPTURADA
            // Se a URL contém /v4/, extrair dados dela
            val urlData = if (finalUrl.contains("/v4/")) {
                extractUrlData(finalUrl)?.also {
                    Log.d(TAG, "📦 Dados extraídos da URL: host=${it.host}, cluster=${it.cluster}, videoId=${it.videoId}")
                }
            } else {
                Log.d(TAG, "⚠️ URL não contém /v4/, tentando buscar no HTML da página...")
                
                // Buscar padrões no HTML da página capturada
                runCatching {
                    val pageHtml = app.get(url, headers = cdnHeaders).text
                    
                    // Buscar qualquer URL com /v4/
                    val v4Regex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/[^"'\s]+""", RegexOption.IGNORE_CASE)
                    val v4Match = v4Regex.find(pageHtml)
                    
                    if (v4Match != null) {
                        val host = v4Match.groupValues[1]
                        val cluster = v4Match.groupValues[2]
                        val videoIdFound = v4Match.groupValues[3]
                        
                        Log.d(TAG, "✅ Encontrado no HTML: host=$host, cluster=$cluster, videoId=$videoIdFound")
                        UrlData(host, cluster, videoIdFound)
                    } else {
                        Log.e(TAG, "❌ Nenhum padrão /v4/ encontrado no HTML")
                        null
                    }
                }.getOrNull()
            }
            
            if (urlData == null) {
                Log.e(TAG, "❌ Não foi possível extrair dados da URL ou do HTML")
                return
            }
            
            Log.d(TAG, "📦 Usando dados: host=${urlData.host}, cluster=${urlData.cluster}, videoId=${urlData.videoId}")
            
            // FASE 4 — BUSCAR cf-master COM TIMESTAMP NO HTML CAPTURADO
            runCatching {
                val htmlResponse = app.get(url, headers = cdnHeaders)
                val html = htmlResponse.text
                
                // Buscar cf-master.{timestamp}.txt
                val cfMasterRegex = Regex("""cf-master\.(\d+)\.txt""")
                val cfMasterMatch = cfMasterRegex.find(html)
                
                if (cfMasterMatch != null) {
                    val cfMasterFile = cfMasterMatch.value
                    val testUrl = "https://${urlData.host}/v4/${urlData.cluster}/${urlData.videoId}/$cfMasterFile"
                    
                    Log.d(TAG, "🧪 Testando cf-master com timestamp: $cfMasterFile")
                    
                    if (tryUrl(testUrl)) {
                        Log.d(TAG, "✅ SUCESSO! cf-master com timestamp válido: $testUrl")
                        
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
            }.onFailure {
                Log.d(TAG, "⏭️ Erro ao buscar cf-master com timestamp: ${it.message}")
            }
            
            // FASE 5 — TENTAR VARIAÇÕES DE ARQUIVO
            // Baseado em ANALISE_FIREFOX_CONSOLE_REAL.md
            val fileVariations = listOf(
                "index-f1-v1-a1.txt",      // Mais comum (95% dos casos - COMPROVADO!)
                "index-f2-v1-a1.txt",      // Segunda qualidade
                "index.txt",                // Genérico
                "cf-master.txt"             // Sem timestamp (raro)
            )
            
            for ((index, fileName) in fileVariations.withIndex()) {
                val testUrl = "https://${urlData.host}/v4/${urlData.cluster}/${urlData.videoId}/$fileName"
                Log.d(TAG, "🧪 Testando variação ${index + 1}/${fileVariations.size}: $fileName")
                
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
            
            Log.e(TAG, "❌ Nenhuma variação de arquivo funcionou")
            
        }.onFailure {
            Log.e(TAG, "❌ Erro no WebView: ${it.message}")
            it.printStackTrace()
        }
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
