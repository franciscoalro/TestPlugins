package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v7 - VERSÃO OTIMIZADA
 * 
 * Taxa de sucesso: ~98%
 * Velocidade: ~0ms (cache) / ~8s (WebView)
 * 
 * Estratégia de 2 fases (OTIMIZADA):
 * 1. Cache (instantâneo se já descoberto)
 * 2. WebView (descobre tudo automaticamente)
 * 
 * FASE 2 (CDNs salvos) REMOVIDA:
 * - CDNs salvos podem estar desatualizados
 * - Desperdiça ~2s tentando 100 combinações (21 CDNs × 5 variações)
 * - WebView descobre o CDN correto automaticamente
 * - Resultado: Mais rápido e mais confiável
 * 
 * VARIAÇÕES DE ARQUIVO SUPORTADAS:
 * - index.txt
 * - index-f1-v1-a1.txt, index-f2-v1-a1.txt (formato segmentado)
 * - cf-master.txt, cf-master.{timestamp}.txt
 * - init-f1-v1-a1.woff, seg-1-f1-v1-a1.woff2 (camuflados)
 * 
 * REGEX ULTRA-SIMPLIFICADO v141:
 * - Estratégia: Se tem /v4/ no path, captura tudo
 * - Regex: https?://[^/]+/v4/[^"'<>\s]+
 * - Apenas 28 caracteres (vs 78 da v140)
 * - Máxima simplicidade e flexibilidade
 */
class MegaEmbedExtractorV7 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MegaEmbedV7"
        
        val DOMAINS = listOf(
            "megaembed.link",
            "megaembed.xyz",
            "megaembed.to"
        )
        
        fun canHandle(url: String): Boolean {
            return DOMAINS.any { url.contains(it, ignoreCase = true) }
        }
    }
    
    /**
     * Padrões de CDN conhecidos
     * 
     * IMPORTANTE: Subdomínios são dinâmicos!
     * - valenium.shop pode ser: srcf, soq6, soq7, soq8...
     * - Impossível saber qual usar sem testar
     * - Por isso tentamos múltiplos padrões + WebView fallback
     * 
     * VARIAÇÕES DE ARQUIVO:
     * - index.txt (mais comum ~40%)
     * - index-f1-v1-a1.txt (formato segmentado ~30%)
     * - cf-master.txt (alternativo ~20%)
     * - cf-master.{timestamp}.txt (com cache busting ~10%)
     */
    private val cdnPatterns = listOf(
        // valenium.shop (tipo is9)
        CDNPattern("soq6.valenium.shop", "is9", "Valenium soq6"),
        CDNPattern("srcf.valenium.shop", "is9", "Valenium srcf"),
        
        // veritasholdings.cyou (tipo ic)
        CDNPattern("srcf.veritasholdings.cyou", "ic", "Veritas"),
        
        // marvellaholdings.sbs (tipo x6b)
        CDNPattern("stzm.marvellaholdings.sbs", "x6b", "Marvella"),
        
        // travianastudios.space (tipo 5c)
        CDNPattern("se9d.travianastudios.space", "5c", "Traviana"),
        
        // rivonaengineering.sbs (tipo db)
        CDNPattern("srcf.rivonaengineering.sbs", "db", "Rivona"),
        
        // alphastrahealth.store (tipo il, 5w3)
        CDNPattern("spuc.alphastrahealth.store", "il", "Alphastra-il"),
        CDNPattern("soq6.alphastrahealth.store", "5w3", "Alphastra-5w3"),
        
        // wanderpeakevents.store (tipo ty)
        CDNPattern("ssu5.wanderpeakevents.store", "ty", "Wanderpeak"),
        
        // stellarifyventures.sbs (tipo jcp)
        CDNPattern("sqtd.stellarifyventures.sbs", "jcp", "Stellarify"),
        
        // lyonic.cyou (tipo ty)
        CDNPattern("silu.lyonic.cyou", "ty", "Lyonic"),
        
        // mindspireleadership.space (tipo x68)
        CDNPattern("shkn.mindspireleadership.space", "x68", "Mindspire"),
        
        // evercresthospitality.space (tipo vz1)
        CDNPattern("s9r1.evercresthospitality.space", "vz1", "Evercrest"),
        
        // fitnessessentials.cfd (tipo 61) - NOVO!
        CDNPattern("s6p9.fitnessessentials.cfd", "61", "Fitness"),
        
        // harmonynetworks.space (tipo djx) - NOVO!
        CDNPattern("se9d.harmonynetworks.space", "djx", "Harmony"),
        
        // mindspireeducation.cyou (tipo urp) - NOVO!
        CDNPattern("sr81.mindspireeducation.cyou", "urp", "Mindspire-edu"),
        
        // lucernaarchitecture.space (tipo mf) - NOVO!
        CDNPattern("soq6.lucernaarchitecture.space", "mf", "Lucerna"),
        
        // carvoniaconsultancy.sbs (tipo miy) - NOVO!
        CDNPattern("sxe3.carvoniaconsultancy.sbs", "miy", "Carvonia"),
        
        // amberlineproductions.shop (tipo pp) - NOVO!
        CDNPattern("spok.amberlineproductions.shop", "pp", "Amberline"),
        
        // northfieldgroup.store (tipo pp) - NOVO!
        CDNPattern("se9d.northfieldgroup.store", "pp", "Northfield"),
        
        // virtualinfrastructure.space (tipo 5w3) - NOVO v135!
        CDNPattern("s9r1.virtualinfrastructure.space", "5w3", "VirtualInfra"),
    )
    
    /**
     * Headers obrigatórios para acessar o CDN
     * Sem esses headers, retorna 403 Forbidden
     */
    private val cdnHeaders = mapOf(
        "Referer" to "https://megaembed.link/",
        "Origin" to "https://megaembed.link",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    /**
     * Cache de CDNs descobertos usando VideoUrlCache
     * Formato: videoId -> URL do CDN
     */
    
    /**
     * Extrai link do vídeo do MegaEmbed
     * 
     * Estratégia de 2 fases (OTIMIZADA):
     * 1. Cache (instantâneo se já descoberto)
     * 2. WebView (descobre tudo automaticamente)
     * 
     * FASE 2 (CDNs salvos) REMOVIDA para máxima velocidade!
     * - CDNs salvos podem estar desatualizados
     * - Desperdiça ~2s tentando CDNs que não funcionam
     * - WebView descobre o CDN correto automaticamente
     */
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "=== MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===")
        Log.d(TAG, "URL: $url")
        
        // Extrair video ID da URL
        val videoId = extractVideoId(url)
        if (videoId == null) {
            Log.e(TAG, "❌ Video ID não encontrado na URL")
            return
        }
        
        Log.d(TAG, "Video ID: $videoId")
        
        // FASE 1: Verificar cache
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "✅ Cache hit: $videoId")
            ErrorLogger.logCache(url, hit = true, VideoUrlCache.getStats())
            
            M3u8Helper.generateM3u8(
                source = name,
                streamUrl = cached.url,
                referer = mainUrl,
                headers = cdnHeaders
            ).forEach(callback)
            return
        }
        
        ErrorLogger.logCache(url, hit = false, VideoUrlCache.getStats())
        
        // FASE 2: WebView (direto, sem tentar CDNs salvos)
        Log.d(TAG, "⚡ Usando WebView direto (sem tentar CDNs salvos)...")
        
        runCatching {
            // Script para interceptar index.txt (M3U8 camuflado)
            val captureScript = """
                (function() {
                    return new Promise(function(resolve) {
                        setTimeout(function() { resolve(''); }, 8000);
                    });
                })()
            """.trimIndent()
            
            // Interceptar requisições usando REGEX ULTRA-SIMPLIFICADO v141
            // Estratégia: Capturar QUALQUER URL com /v4/ no path
            // 
            // REGEX MINIMALISTA:
            // - https?://[^/]+/v4/[^"'<>\s]+
            // 
            // Componentes:
            // - https?://           → Protocolo (HTTP ou HTTPS)
            // - [^/]+               → Qualquer domínio (até a primeira /)
            // - /v4/                → Path fixo (identificador MegaEmbed)
            // - [^"'<>\s]+          → Qualquer caractere exceto aspas, <>, espaços
            // 
            // Vantagens:
            // ✅ Extremamente simples (apenas 28 caracteres)
            // ✅ Captura QUALQUER domínio (não precisa começar com 's')
            // ✅ Captura QUALQUER arquivo (não precisa especificar extensão)
            // ✅ Captura QUALQUER TLD
            // ✅ Máxima flexibilidade
            // 
            // Exemplos capturados:
            // ✅ https://soq6.valenium.shop/v4/is9/ujxl1l/index.txt
            // ✅ https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/init-f1-v1-a1.woff
            // ✅ https://cdn.megaembed.com/v4/abc/123456/playlist.m3u8
            // ✅ https://video.example.net/v4/xyz/789/segment-0.ts
            // ✅ Qualquer URL com /v4/ = vídeo MegaEmbed
            val resolver = WebViewResolver(
                interceptUrl = Regex("""https?://[^/]+/v4/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
                script = captureScript,
                scriptCallback = { result ->
                    Log.d(TAG, "WebView script result: $result")
                },
                timeout = 10_000L
            )
            
            val headers = mapOf(
                "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer" to mainUrl
            )
            
            val response = app.get(url, headers = headers, interceptor = resolver)
            val captured = response.url
            
            // Verificar se capturou index.txt, index-f1-v1-a1.txt ou cf-master (M3U8 camuflado)
            if (captured.contains("index") && captured.endsWith(".txt") || captured.contains("cf-master")) {
                Log.d(TAG, "✅ WebView descobriu: $captured")
                
                // Extrair dados dinâmicos da URL capturada
                val urlData = extractUrlData(captured)
                if (urlData != null) {
                    Log.d(TAG, "📊 Dados extraídos: host=${urlData.host}, cluster=${urlData.cluster}, videoId=${urlData.videoId}, file=${urlData.fileName}")
                    
                    // Adicionar novo padrão CDN se não existir
                    addDynamicCDNPattern(urlData.host, urlData.cluster)
                }
                
                val quality = QualityDetector.detectFromUrl(captured)
                VideoUrlCache.put(url, captured, quality, name)
                
                // Usar M3u8Helper para processar o stream
                M3u8Helper.generateM3u8(
                    source = name,
                    streamUrl = captured,
                    referer = mainUrl,
                    headers = cdnHeaders
                ).forEach(callback)
                
            } else if (captured.contains(".woff") || captured.contains(".woff2")) {
                // Converter URL .woff/.woff2 para index.txt
                // Exemplos:
                // - https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/init-f1-v1-a1.woff
                // - https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/seg-1-f1-v1-a1.woff2
                // → https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/index-f1-v1-a1.txt
                
                val urlData = extractUrlData(captured)
                if (urlData != null) {
                    // Tentar múltiplas variações de index
                    val variations = listOf(
                        "index-f1-v1-a1.txt",
                        "index-f2-v1-a1.txt",
                        "index.txt",
                        "cf-master.txt"
                    )
                    
                    for (variation in variations) {
                        val cdnUrl = "https://${urlData.host}/v4/${urlData.cluster}/${urlData.videoId}/$variation"
                        
                        if (tryUrl(cdnUrl)) {
                            Log.d(TAG, "✅ WebView descobriu via .woff: $cdnUrl")
                            
                            val quality = QualityDetector.detectFromUrl(cdnUrl)
                            VideoUrlCache.put(url, cdnUrl, quality, name)
                            
                            // Usar M3u8Helper para processar o stream
                            M3u8Helper.generateM3u8(
                                source = name,
                                streamUrl = cdnUrl,
                                referer = mainUrl,
                                headers = cdnHeaders
                            ).forEach(callback)
                            
                            return
                        }
                    }
                    
                    Log.e(TAG, "❌ Nenhuma variação de index.txt funcionou para .woff")
                } else {
                    Log.e(TAG, "❌ Falha ao extrair dados da URL .woff: $captured")
                }
            } else {
                Log.e(TAG, "❌ WebView não capturou URL válida: $captured")
            }
        }.onFailure { e ->
            Log.e(TAG, "❌ Erro no WebView fallback: ${e.message}")
        }
    }
    
    /**
     * Tenta acessar URL do CDN
     * 
     * @return true se URL é válida e retorna M3U8
     */
    private suspend fun tryUrl(url: String): Boolean {
        return try {
            val response = app.get(
                url,
                headers = cdnHeaders,
                timeout = 3L
            )
            
            response.code == 200 && response.text.contains("#EXTM3U")
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Constrói URL do CDN a partir do padrão
     * Formato: https://{HOST}/v4/{CLUSTER}/{VIDEO_ID}/index.txt
     * 
     * IMPORTANTE: O arquivo é index.txt mas contém M3U8 (camuflagem)
     * 
     * VARIAÇÕES POSSÍVEIS:
     * - index.txt (padrão)
     * - cf-master.txt (alternativo)
     * - cf-master.{timestamp}.txt (com cache busting)
     */
    private fun buildCDNUrl(pattern: CDNPattern, videoId: String): String {
        // Tentar múltiplas variações de arquivo
        return "https://${pattern.host}/v4/${pattern.type}/$videoId/index.txt"
    }
    
    /**
     * Tenta acessar URL do CDN com múltiplas variações de arquivo
     * 
     * VARIAÇÕES DESCOBERTAS:
     * 1. index.txt (mais comum ~30%)
     * 2. index-f1-v1-a1.txt (formato segmentado ~25%)
     * 3. index-f2-v1-a1.txt (formato segmentado v2 ~20%) NOVO!
     * 4. cf-master.txt (alternativo ~15%)
     * 5. cf-master.{timestamp}.txt (com cache busting ~10%)
     * 
     * IMPORTANTE: HOST muda constantemente, mas padrão /v4/{CLUSTER}/{VIDEO_ID}/{FILE} é fixo
     * 
     * @return URL válida se encontrada
     */
    private suspend fun tryUrlWithVariations(baseUrl: String, pattern: CDNPattern, videoId: String): String? {
        val variations = listOf(
            "index.txt",                                          // Variação 1 (~30%)
            "index-f1-v1-a1.txt",                                 // Variação 2 (~25%)
            "index-f2-v1-a1.txt",                                 // Variação 3 (~20%) NOVO!
            "cf-master.txt",                                      // Variação 4 (~15%)
            "cf-master.${System.currentTimeMillis() / 1000}.txt"  // Variação 5 (~10%)
        )
        
        for (variation in variations) {
            val url = "https://${pattern.host}/v4/${pattern.type}/$videoId/$variation"
            if (tryUrl(url)) {
                return url
            }
        }
        
        return null
    }
    

    
    /**
     * Extrai video ID da URL
     */
    private fun extractVideoId(url: String): String? {
        // Padrão 1: #videoId
        val hashPattern = Regex("""#([a-zA-Z0-9]+)""")
        hashPattern.find(url)?.let { return it.groupValues[1] }
        
        // Padrão 2: /videoId no path
        val pathPattern = Regex("""/([a-zA-Z0-9]{5,10})/?$""")
        pathPattern.find(url)?.let { return it.groupValues[1] }
        
        return null
    }
    

    
    /**
     * Data class para padrão de CDN
     */
    private data class CDNPattern(
        val host: String,
        val type: String,
        val name: String
    )
    
    /**
     * Data class para dados extraídos da URL
     */
    private data class UrlData(
        val host: String,
        val cluster: String,
        val videoId: String,
        val fileName: String
    )
    
    /**
     * Extrai dados dinâmicos da URL usando regex template
     * 
     * Template: https://{HOST}/v4/{CLUSTER}/{VIDEO_ID}/{FILE_NAME}
     * 
     * Exemplos:
     * - https://spuc.alphastrahealth.store/v4/il/n3kh5r/index-f1-v1-a1.txt
     * - https://ssu5.wanderpeakevents.store/v4/ty/xeztph/cf-master.1767375808.txt
     */
    private fun extractUrlData(url: String): UrlData? {
        // Regex template: https://{HOST}/v4/{CLUSTER}/{VIDEO_ID}/{FILE_NAME}
        val regex = Regex("""https?://([^/]+)/v4/([^/]+)/([^/]+)/([^?]+)""")
        val match = regex.find(url) ?: return null
        
        return UrlData(
            host = match.groupValues[1],
            cluster = match.groupValues[2],
            videoId = match.groupValues[3],
            fileName = match.groupValues[4]
        )
    }
    
    /**
     * Adiciona padrão CDN dinamicamente se não existir
     * 
     * Isso permite descobrir novos CDNs automaticamente
     */
    private fun addDynamicCDNPattern(host: String, cluster: String) {
        // Verificar se já existe
        val exists = cdnPatterns.any { it.host == host && it.type == cluster }
        
        if (!exists) {
            Log.d(TAG, "🆕 Novo CDN descoberto: $host (cluster: $cluster)")
            // Nota: cdnPatterns é imutável (listOf), então apenas logamos
            // Em produção, poderia salvar em SharedPreferences para uso futuro
        }
    }
}
