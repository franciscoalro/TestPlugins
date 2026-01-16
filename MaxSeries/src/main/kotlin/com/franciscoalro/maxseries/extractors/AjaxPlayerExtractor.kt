package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.SubtitleFile
import com.lagradost.cloudstream3.app
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import org.jsoup.nodes.Element

/**
 * AJAX Player Extractor Helper v2 - OPTIMIZED (FASE 4)
 * Inspirado nos padrões FilmesOn e OverFlix
 * 
 * Melhorias v2:
 * - ✅ Logs estruturados com ErrorLogger
 * - ✅ Já usa ServerPriority, RateLimiter, HeadersBuilder
 * 
 * Classe auxiliar para extrair links de players que usam requisições AJAX
 * Não é um ExtractorApi, mas sim um helper usado por outros extractors
 */
class AjaxPlayerExtractor(private val mainUrl: String) {
    
    companion object {
        private const val TAG = "AjaxPlayerExtractor"
    }
    
    /**
     * Processa opções de player e extrai links via AJAX
     * 
     * @param playerOptions Lista de elementos HTML com opções de player
     * @param referer URL de referência
     * @param subtitleCallback Callback para legendas
     * @param callback Callback para links extraídos
     * @return true se encontrou pelo menos um link
     */
    suspend fun processPlayerOptions(
        playerOptions: List<Element>,
        referer: String,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        var foundLink = false
        
        // Ordenar opções por prioridade de servidor
        val sortedOptions = ServerPriority.sortByPriority(playerOptions) { option ->
            val serverName = option.select("span.server").text().trim()
            ServerPriority.detectServer(serverName)
        }
        
        // Processar com rate limiting
        RateLimiter.processWithRateLimit(sortedOptions) { option ->
            val embedUrl = requestEmbedUrl(option, referer)
            if (embedUrl != null) {
                processEmbedPage(embedUrl, referer, callback)
                foundLink = true
            }
        }
        
        return foundLink
    }
    
    /**
     * Requisita embed URL via AJAX (padrão FilmesOn)
     */
    private suspend fun requestEmbedUrl(
        option: Element,
        referer: String
    ): String? {
        return runCatching {
            val domain = try {
                val url = java.net.URL(referer)
                "${url.protocol}://${url.host}"
            } catch (e: Exception) { mainUrl }
            
            // Headers AJAX customizados
            val headers = HeadersBuilder.ajax(referer, domain)
            
            // Payload do formulário
            val payload = mapOf(
                "action" to "doo_player_ajax",
                "post" to option.attr("data-post"),
                "nume" to option.attr("data-nume"),
                "type" to option.attr("data-type")
            )
            
            // Fazer requisição AJAX
            val response = app.post(
                "$domain/wp-admin/admin-ajax.php",
                headers = headers,
                data = payload
            ).text
            
            if (response == "0" || response.isBlank()) {
                ErrorLogger.w(TAG, "Resposta AJAX vazia")
                return null
            }
            
            // Extrair embed_url usando regex pattern
            val embedUrl = RegexPatterns.EMBED_URL_JSON
                .find(response)?.groupValues?.get(1)
                ?.let { LinkDecryptor.cleanUrl(it) }
            
            if (embedUrl != null) {
                ErrorLogger.d(TAG, "Embed URL extraída", mapOf("URL" to embedUrl))
            }
            
            embedUrl
        }.getOrElse { error ->
            ErrorLogger.e(TAG, "Erro ao requisitar embed URL", error = error)
            null
        }
    }
    
    /**
     * Processa página embed para extrair link final
     */
    private suspend fun processEmbedPage(
        embedUrl: String,
        referer: String,
        callback: (ExtractorLink) -> Unit
    ) {
        runCatching {
            val headers = HeadersBuilder.standard(embedUrl)
            val document = app.get(embedUrl, headers = headers).document
            
            // Buscar opções de player na página embed
            document.select("div.player_select_item").forEach { option ->
                val embedData = option.attr("data-embed")
                val prefix = option.select(".player_select_name").text().trim()
                
                if (embedData.isNotEmpty() && LinkDecryptor.isUrl(embedData)) {
                    processPlayerData(embedData, embedUrl, prefix, callback)
                }
            }
        }.getOrElse { error ->
            ErrorLogger.e(TAG, "Erro ao processar embed page", error = error)
        }
    }
    
    /**
     * Processa dados do player para extrair link final
     */
    private suspend fun processPlayerData(
        playerUrl: String,
        referer: String,
        prefix: String,
        callback: (ExtractorLink) -> Unit
    ) {
        runCatching {
            val headers = HeadersBuilder.standard(referer)
            val html = app.get(playerUrl, headers = headers).text
            
            // Buscar iframe com player_2.php
            val iframeSrc = RegexPatterns.IFRAME_SRC.find(html)?.groupValues?.get(1)
            if (iframeSrc == null) {
                ErrorLogger.w(TAG, "Iframe não encontrado")
                return
            }
            
            val fullIframeSrc = if (iframeSrc.startsWith("//")) {
                "https:$iframeSrc"
            } else {
                iframeSrc
            }
            
            // Processar iframe final
            handleFinalStep(fullIframeSrc, playerUrl, prefix, callback)
            
        }.getOrElse { error ->
            ErrorLogger.e(TAG, "Erro ao processar player data", error = error)
        }
    }
    
    /**
     * Passo final: extrair link de vídeo
     */
    private suspend fun handleFinalStep(
        playerUrl: String,
        referer: String,
        prefix: String,
        callback: (ExtractorLink) -> Unit
    ) {
        runCatching {
            val headers = HeadersBuilder.standard(referer)
            val html = app.get(playerUrl, headers = headers).text
            
            // Extrair apiUrl do JavaScript
            val apiUrl = RegexPatterns.API_URL_JS.find(html)?.groupValues?.get(1)
            if (apiUrl == null) {
                ErrorLogger.w(TAG, "apiUrl não encontrada")
                return
            }
            
            // Extrair URL do MediaFire
            val mediafireUrl = LinkDecryptor.decryptMediaFireUrl(apiUrl)
            if (mediafireUrl == null) {
                ErrorLogger.w(TAG, "MediaFire URL não encontrada")
                return
            }
            
            // Buscar link direto do MediaFire
            val direct = app.get(mediafireUrl).document
                .select("a#downloadButton").attr("href")
            
            if (direct.isNotEmpty() && LinkDecryptor.isVideoUrl(direct)) {
                val quality = QualityDetector.detectFromUrl(direct)
                ErrorLogger.d(TAG, "Link final extraído", mapOf(
                    "URL" to direct,
                    "Quality" to QualityDetector.getQualityLabel(quality)
                ))
                
                callback.invoke(
                    newExtractorLink(
                        source = "AjaxPlayer",
                        name = "$prefix - AjaxPlayer",
                        url = direct,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = mainUrl
                        this.quality = quality
                        this.headers = HeadersBuilder.mediaFire(mediafireUrl)
                    }
                )
            }
            
        }.getOrElse { error ->
            ErrorLogger.e(TAG, "Erro no passo final", error = error)
        }
    }
}
