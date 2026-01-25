package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.lagradost.cloudstream3.network.WebViewResolver
import com.franciscoalro.maxseries.utils.*
import android.util.Log

/**
 * MegaEmbed Extractor v9 - UNIVERSAL & AUTOMATIC (Jan 2026)
 * 
 * NOVIDADES v9:
 * 1. TRIPLE CLICK: Automação via JS para bypass de 2 overlays de ads + ativação do player.
 *    Sem o clique, o servidor agora invalida o token (Token is invalid).
 * 2. DOMÍNIOS DINÂMICOS: Extrai o host (orion, brightcrest, mountainpeak, etc) direto do HTML.
 * 3. FALLBACK DE MONTAGEM: Se a interceptação de rede falhar, monta a URL manualmente usando
 *    o ID, Domínio e Timestamp extraídos do HTML.
 */
class MegaEmbedExtractorV9 : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true
    
    companion object {
        private const val TAG = "MegaEmbedV9"
    }

    // Headers exatos do script TS que funcionou
    private val cdnHeaders = mapOf(
        "Referer" to "https://playerthree.online/",
        "Origin" to "https://megaembed.link",
        "Accept-Language" to "en-US,en;q=0.9",
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val videoId = extractVideoId(url) ?: return
        Log.d(TAG, "🚀 Iniciando MegaEmbed V9 para ID: $videoId")

        val embedUrl = "https://megaembed.link/#$videoId"
        var capturedUrl: String? = null

        // Script JS: Replicando EXATAMENTE o megaembed_solver.ts
        // - Clique nas coordenadas 640,360 (centro relativo)
        // - Intervalo de 2.5s (2500ms)
        // - 3 repetições
        val tripleClickScript = """
            (function() {
                console.log('[MegaEmbedV9] Iniciando sequência exata do TS (cliques 640x360)...');
                
                let clickCount = 0;
                
                // Função para simular clique no centro
                function clickCenter() {
                    const x = 640; // Coordenada usada no Puppeteer
                    const y = 360; // Coordenada usada no Puppeteer
                    
                    // Tenta encontrar elemento no ponto ou usa body
                    const el = document.elementFromPoint(x, y) || document.body;
                    
                    const mouseEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: x,
                        clientY: y
                    });
                    el.dispatchEvent(mouseEvent);
                    console.log('[MegaEmbedV9] Clique ' + (clickCount + 1) + '/3 disparado em ' + x + ',' + y);
                }

                // Intervalo de 2500ms (igual ao sleep(2500) do TS)
                let clickInterval = setInterval(() => {
                    clickCount++;
                    clickCenter();
                    
                    if (clickCount >= 3) {
                        clearInterval(clickInterval);
                        console.log('[MegaEmbedV9] Sequência de 3 cliques finalizada.');
                    }
                }, 2500);
                
                // Tenta remover overlays de ad manualmente também
                setInterval(() => {
                    document.querySelectorAll('iframe[style*="z-index"], div[style*="z-index"]').forEach(el => {
                         if(el.style.zIndex > 100) el.remove();
                    });
                }, 1000);
            })();
        """.trimIndent()

        // Regex igual ao anterior, mas focado no que o TS captura (.txt, .m3u8)
        val interceptRegex = Regex(""".*(/v4/|cf-master|\.txt|\.m3u8).*""", RegexOption.IGNORE_CASE)

        val resolver = WebViewResolver(
            interceptUrl = interceptRegex,
            script = tripleClickScript,
            timeout = 30_000L // 3 * 2.5s = 7.5s + carregamento. 30s é seguro.
        )

        try {
            val response = app.get(embedUrl, headers = cdnHeaders, interceptor = resolver)
            capturedUrl = response.url

            // Se a rede capturou algo válido, usamos
            if (isValidVideoUrl(capturedUrl)) {
                Log.d(TAG, "✅ Capturado via Rede: $capturedUrl")
                processUrl(capturedUrl, url, callback)
                return
            }

            // FALLBACK: Montagem Manual via HTML
            Log.d(TAG, "⚠️ Captura de rede falhou, tentando montagem manual via HTML...")
            val html = response.text
            
            val domain = extractDomain(html)
            val timestamp = extractTimestamp(html)
            
            if (domain != null && timestamp != null) {
                val manualUrl = "https://$domain/v4/xy/$videoId/cf-master.$timestamp.txt"
                Log.d(TAG, "🛠️ URL Montada Manualmente: $manualUrl")
                
                if (tryUrl(manualUrl)) {
                    processUrl(manualUrl, url, callback)
                    return
                }
            }

            Log.e(TAG, "❌ Falha total na extração do ID: $videoId")

        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no Resolver: ${e.message}")
        }
    }

    private suspend fun processUrl(link: String, originalUrl: String, callback: (ExtractorLink) -> Unit) {
        val quality = QualityDetector.detectFromUrl(link)
        VideoUrlCache.put(originalUrl, link, quality, name)
        
        M3u8Helper.generateM3u8(
            source = name,
            streamUrl = link,
            referer = mainUrl,
            headers = cdnHeaders
        ).forEach(callback)
    }

    private fun extractDomain(html: String): String? {
        val domains = listOf(
            "oriontraveldynamics.sbs",
            "brightcrestinteractive.site",
            "mountainpeakstudio.space"
        )
        for (d in domains) {
            val regex = Regex("""[\w-]+\.$d""")
            val match = regex.find(html)
            if (match != null) return match.value
        }
        return null
    }

    private fun extractTimestamp(html: String): String? {
        // Busca um número de 10 dígitos (padrão Unix timestamp atual 17xxxxxxxx)
        return Regex("""\b17\d{8}\b""").find(html)?.value
    }

    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrEmpty()) return false
        return url.contains("/v4/") && (url.contains(".txt") || url.contains(".m3u8") || url.contains("cf-master"))
    }

    private suspend fun tryUrl(url: String): Boolean {
        return runCatching {
            val response = app.get(url, headers = cdnHeaders, timeout = 5)
            response.code in 200..299 && response.text.contains("#EXTM3U")
        }.getOrDefault(false)
    }

    private fun extractVideoId(url: String): String? {
        return Regex("""#([a-zA-Z0-9]+)""").find(url)?.groupValues?.get(1)
    }
}
