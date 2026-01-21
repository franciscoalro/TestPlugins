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
        Log.d(TAG, "=== MEGAEMBED V7 v154 WEBVIEW PASSIVO ===")
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
        
        // FASE 2 — WEBVIEW PASSIVO (v154): Deixa JavaScript nativo executar
        Log.d(TAG, "🌐 Iniciando WebView PASSIVO (sem scripts custom)...")
        
        runCatching {
            // Regex para interceptar arquivos de vídeo
            val interceptRegex = Regex("""/v4/[^"'\s]+\.(txt|m3u8|woff2)""", RegexOption.IGNORE_CASE)
            
            // WebView SEM script customizado - deixa JavaScript do MegaEmbed executar
            val resolver = WebViewResolver(
                interceptUrl = interceptRegex,
                script = null, // SEM scripts! Deixa JS nativo executar
                timeout = 35_000L // 35s para JavaScript carregar
            )
            
            Log.d(TAG, "📱 Carregando página e aguardando JavaScript executar...")
            val response = app.get(url, headers = cdnHeaders, interceptor = resolver)
            val capturedUrl = response.url
            
            Log.d(TAG, "✅ WebView capturou: $capturedUrl")
            
            // Verificar se capturou URL com /v4/
            if (capturedUrl.contains("/v4/") && interceptRegex.containsMatchIn(capturedUrl)) {
                Log.d(TAG, "🎯 URL de vídeo interceptada com sucesso!")
                
                // Tentar usar URL diretamente
                if (tryUrl(capturedUrl)) {
                    val quality = QualityDetector.detectFromUrl(capturedUrl)
                    VideoUrlCache.put(url, capturedUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = capturedUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    return
                }
                
                // Se URL capturada não funcionar, extrair dados e tentar variações
                extractUrlData(capturedUrl)?.let { urlData ->
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
            } else {
                Log.d(TAG, "⚠️ WebView não capturou URL com /v4/, tentando buscar no HTML carregado...")
                
                // Fallback: Buscar no HTML que foi carregado pelo WebView
                val html = response.text
                Log.d(TAG, "📄 HTML carregado pelo WebView (${html.length} chars)")
                
                val v4Regex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/[^"'\s]+\.(txt|m3u8)""", RegexOption.IGNORE_CASE)
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
            }
            
            Log.e(TAG, "❌ WebView não conseguiu capturar URLs de vídeo")
            
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
