package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v7 - v147 API-BASED
 *
 * DESCOBERTAS DO FIREFOX CONSOLE (2026-01-20):
 * 1. MegaEmbed usa APIs: /api/v1/info, /api/v1/video, /api/v1/player
 * 2. cf-master tem timestamp dinâmico: cf-master.1767387529.txt
 * 3. Nova CDN descoberta: rivonaengineering.sbs
 * 4. WebView como fallback
 *
 * Baseado em: ANALISE_FIREFOX_CONSOLE_REAL.md
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
        val host: String,      // sxix.rivonaengineering.sbs
        val cluster: String,   // is9, ic, x6b, 5c, db
        val videoId: String    // 6pyw3v (6 chars)
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MEGAEMBED V7 v147 API-BASED ===")
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
        
        // FASE 2 — TENTAR BUSCAR cf-master COM TIMESTAMP NO HTML
        Log.d(TAG, "🔍 Buscando cf-master com timestamp no HTML...")
        
        runCatching {
            val htmlResponse = app.get(url, headers = cdnHeaders)
            val html = htmlResponse.text
            
            // Buscar cf-master.{timestamp}.txt no HTML
            val cfMasterRegex = Regex("""https?://[^"'\s]+/v4/[^"'\s]+/[^"'\s]+/cf-master\.\d+\.txt""")
            val cfMasterMatch = cfMasterRegex.find(html)
            
            if (cfMasterMatch != null) {
                val cfMasterUrl = cfMasterMatch.value
                Log.d(TAG, "✅ cf-master com timestamp encontrado: $cfMasterUrl")
                
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
            } else {
                Log.d(TAG, "⏭️ cf-master com timestamp não encontrado no HTML")
            }
        }.onFailure {
            Log.d(TAG, "⏭️ Erro ao buscar cf-master: ${it.message}")
        }
        
        // FASE 3 — WEBVIEW COM REGEX ÚNICO AMPLO
        Log.d(TAG, "🔍 Iniciando WebView com regex único amplo...")
        
        runCatching {
            // REGEX ÚNICO: Captura QUALQUER URL com /v4/
            // Baseado em PIPELINE_REGEX_V142_EXPLICACAO.md
            val universalRegex = Regex("""https?://[^/]+/v4/[^"'\s<>]+""", RegexOption.IGNORE_CASE)
            
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        var attempts = 0;
                        var maxAttempts = 80;
                        
                        var interval = setInterval(function() {
                            attempts++;
                            
                            var html = document.documentElement.innerHTML;
                            
                            // Procurar por URLs .txt (M3U8 camuflado)
                            var txtMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.txt/i);
                            if (txtMatch) {
                                clearInterval(interval);
                                resolve(txtMatch[0]);
                                return;
                            }
                            
                            // Procurar por .woff/.woff2 (segmentos camuflados)
                            var woffMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.woff2?/i);
                            if (woffMatch) {
                                clearInterval(interval);
                                resolve(woffMatch[0]);
                                return;
                            }
                            
                            if (attempts >= maxAttempts) {
                                clearInterval(interval);
                                resolve('');
                            }
                        }, 100);
                    });
                })()
            """.trimIndent()
            
            val resolver = WebViewResolver(
                interceptUrl = universalRegex,
                script = captureScript,
                scriptCallback = { result ->
                    Log.d(TAG, "📱 WebView capturou: $result")
                },
                timeout = 12_000L
            )
            
            val headers = mapOf(
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer" to mainUrl
            )
            
            val response = app.get(url, headers = headers, interceptor = resolver)
            val captured = response.url
            
            Log.d(TAG, "📄 WebView retornou: $captured")
            
            // FASE 3 — PROCESSAR URL CAPTURADA
            if (!captured.contains("/v4/")) {
                Log.e(TAG, "❌ URL capturada não contém /v4/")
                return
            }
            
            // Extrair componentes da URL
            val urlData = extractUrlData(captured)
            if (urlData == null) {
                Log.e(TAG, "❌ Não foi possível extrair dados da URL: $captured")
                return
            }
            
            Log.d(TAG, "📦 Dados extraídos: host=${urlData.host}, cluster=${urlData.cluster}, videoId=${urlData.videoId}")
            
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
