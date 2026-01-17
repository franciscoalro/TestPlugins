package com.franciscoalro.maxseries.utils

import com.lagradost.cloudstream3.base64Decode
import android.util.Log

/**
 * Brazilian Extractor Utilities
 * Padrões extraídos de saimuelrepo: PobreFlix, OverFlix, Vizer, AnimesCloud
 */
object BRExtractorUtils {
    
    private const val TAG = "BRExtractorUtils"

    /**
     * Prioridade de servidores (baseado no PobreFlixExtractor)
     * Menor número = maior prioridade
     */
    val SERVER_PRIORITY = mapOf(
        "streamtape" to 1,
        "strtape" to 1,
        "strtpe" to 1,
        "filemoon" to 2,
        "moonmov" to 2,
        "doodstream" to 3,
        "dood" to 3,
        "myvidplay" to 3,
        "bysebuho" to 3,
        "g9r6" to 3,
        "mixdrop" to 4,
        "mxtape" to 4,
        "uqload" to 5,
        "upstream" to 6,
        "vidcloud" to 7,
        "embedplay" to 8,
        "playerembedapi" to 9,
        "megaembed" to 10
    )

    /**
     * Ordena URLs por prioridade de servidor
     */
    fun <T> sortByPriority(items: List<T>, urlExtractor: (T) -> String): List<T> {
        return items.sortedBy { item ->
            val url = urlExtractor(item).lowercase()
            SERVER_PRIORITY.entries.firstOrNull { url.contains(it.key) }?.value ?: Int.MAX_VALUE
        }
    }

    /**
     * Detecta o tipo de servidor a partir da URL
     */
    fun detectServer(url: String): String? {
        val lowerUrl = url.lowercase()
        return SERVER_PRIORITY.keys.firstOrNull { lowerUrl.contains(it) }
    }

    /**
     * Descriptografia Base64 reversa (padrão Vizer)
     * Decodifica, reverte e ajusta os últimos 5 caracteres
     */
    fun decryptVizerKey(encoded: String): String {
        return try {
            var decoded = base64Decode(encoded.replace("redirect/", ""))
            decoded = decoded.trim().reversed()
            val last = decoded.takeLast(5).reversed()
            decoded.dropLast(5) + last
        } catch (e: Exception) {
            Log.e(TAG, "Erro decryptVizerKey: ${e.message}")
            ""
        }
    }

    /**
     * Constrói URL de endpoint dooplayer AJAX (padrão AnimesCloud/FilmesOn)
     */
    fun buildDooplayerUrl(mainUrl: String, dataPost: String, dataType: String, dataNume: String): String {
        return "$mainUrl/wp-json/dooplayer/v2/$dataPost/$dataType/$dataNume"
    }

    /**
     * Extrai embed_url de resposta JSON do dooplayer
     */
    fun extractEmbedUrl(jsonResponse: String): String? {
        val regex = Regex(""""embed_url"\s*:\s*"([^"]+)"""")
        return regex.find(jsonResponse)?.groupValues?.get(1)
            ?.replace("\\/", "/")
            ?.replace("\\", "")
    }

    /**
     * Headers AJAX padrão para requests WordPress
     */
    fun ajaxHeaders(referer: String): Map<String, String> {
        return mapOf(
            "X-Requested-With" to "XMLHttpRequest",
            "Accept" to "application/json, text/javascript, */*; q=0.01",
            "Referer" to referer,
            "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    /**
     * Extrai ID de conteúdo de script CONTENT_INFO (padrão OverFlix)
     */
    fun extractContentInfo(html: String): String? {
        val regex = Regex("""var CONTENT_INFO = '(\d+)';""")
        return regex.find(html)?.groupValues?.get(1)
    }

    /**
     * Resolve redirecionamento window.location.href
     */
    fun extractWindowLocation(html: String): String? {
        val regex = Regex("""window\.location\.href\s*=\s*"([^"]+)"""")
        return regex.find(html)?.groupValues?.get(1)
    }

    /**
     * Extrai player_base_url de script (padrão OverFlix internal player)
     */
    fun extractPlayerBaseUrl(html: String): String? {
        val regex = Regex("""var player_base_url\s*=\s*"([^"]+)"""")
        return regex.find(html)?.groupValues?.get(1)
    }

    /**
     * Lista de domínios DoodStream conhecidos
     */
    val DOOD_DOMAINS = listOf(
        "dood.to", "dood.watch", "dood.so", "dood.pm", "dood.wf",
        "dood.re", "dood.yt", "dood.sh", "dood.cx", "dood.la",
        "doodstream.com", "ds2play.com", "doods.pro",
        "myvidplay.com", "bysebuho.com", "g9r6.com"
    )

    /**
     * Lista de domínios Streamtape conhecidos
     */
    val STREAMTAPE_DOMAINS = listOf(
        "streamtape.com", "streamtape.to", "streamtape.net",
        "strtape.cloud", "strtpe.link", "strcloud.link",
        "tapecontent.net", "tapewithadblock.org"
    )

    /**
     * Lista de domínios Filemoon conhecidos
     */
    val FILEMOON_DOMAINS = listOf(
        "filemoon.sx", "filemoon.to", "filemoon.in",
        "moonmov.net", "moonmov.pro", "kerapoxy.cc"
    )

    /**
     * Lista de domínios Mixdrop conhecidos
     */
    val MIXDROP_DOMAINS = listOf(
        "mixdrop.co", "mixdrop.to", "mixdrop.sx",
        "mixdrop.bz", "mixdrop.ch", "mixdrp.co",
        "mxtape.co", "mdbekjwqa.pw", "mdfx9dc8n.net"
    )

    /**
     * Verifica se URL pertence a um domínio específico
     */
    fun isDoodStream(url: String): Boolean = DOOD_DOMAINS.any { url.contains(it, true) }
    fun isStreamtape(url: String): Boolean = STREAMTAPE_DOMAINS.any { url.contains(it, true) }
    fun isFilemoon(url: String): Boolean = FILEMOON_DOMAINS.any { url.contains(it, true) }
    fun isMixdrop(url: String): Boolean = MIXDROP_DOMAINS.any { url.contains(it, true) }
}
