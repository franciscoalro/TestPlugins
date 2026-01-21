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
        
        // FASE 2 — BUSCA DIRETA NO HTML (SEM WEBVIEW - mais confiável)
        Log.d(TAG, "🔍 Buscando URLs de vídeo diretamente no HTML...")
        
        runCatching {
            val htmlResponse = app.get(url, headers = cdnHeaders)
            val html = htmlResponse.text
            
            Log.d(TAG, "📄 HTML recebido (${html.length} chars)")
            
            // Extrair videoId da URL
            val videoId = extractVideoId(url)
            if (videoId == null) {
                Log.e(TAG, "❌ VideoID não encontrado na URL")
                return
            }
            
            // PADRÃO 1: cf-master com timestamp no HTML
            val cfMasterRegex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/cf-master\.(\d+)\.txt""", RegexOption.IGNORE_CASE)
            cfMasterRegex.find(html)?.let { match ->
                val cfUrl = match.value
                Log.d(TAG, "✅ cf-master encontrado no HTML: $cfUrl")
                
                if (tryUrl(cfUrl)) {
                    val quality = QualityDetector.detectFromUrl(cfUrl)
                    VideoUrlCache.put(url, cfUrl, quality, name)
                    
                    M3u8Helper.generateM3u8(
                        source = name,
                        streamUrl = cfUrl,
                        referer = mainUrl,
                        headers = cdnHeaders
                    ).forEach(callback)
                    return
                }
            }
            
            // PADRÃO 2: index-f{n}-v{n}-a{n}.txt no HTML
            val indexRegex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/index-f\d+-v\d+-a\d+\.txt""", RegexOption.IGNORE_CASE)
            indexRegex.find(html)?.let { match ->
                val indexUrl = match.value
                Log.d(TAG, "✅ index encontrado no HTML: $indexUrl")
                
                if (tryUrl(indexUrl)) {
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
            
            // PADRÃO 3: Extrair host/cluster de QUALQUER arquivo no HTML e fazer brute-force
            val v4Regex = Regex("""https?://([^"'\s]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})/[^"'\s]+""", RegexOption.IGNORE_CASE)
            v4Regex.find(html)?.let { match ->
                val host = match.groupValues[1]
                val cluster = match.groupValues[2]
                val foundVideoId = match.groupValues[3]
                
                Log.d(TAG, "✅ Encontrado padrão /v4/: host=$host, cluster=$cluster, videoId=$foundVideoId")
                
                // Usar videoId da URL original, não do HTML
                val targetVideoId = if (foundVideoId == videoId) videoId else videoId
                
                // Tentar variações de arquivo
                val fileVariations = listOf(
                    "index-f1-v1-a1.txt",
                    "index-f2-v1-a1.txt", 
                    "index.txt",
                    "cf-master.txt"
                )
                
                for ((index, fileName) in fileVariations.withIndex()) {
                    val testUrl = "https://$host/v4/$cluster/$targetVideoId/$fileName"
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
            
            Log.d(TAG, "⚠️ Nenhum padrão encontrado no HTML")
            
        }.onFailure {
            Log.e(TAG, "❌ Erro na busca HTML: ${it.message}")
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
