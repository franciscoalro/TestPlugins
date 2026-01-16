package com.franciscoalro.maxseries.utils

/**
 * Construtor de headers HTTP customizados por contexto
 * Inspirado nos padrões dos providers brasileiros
 */
object HeadersBuilder {
    private const val DEFAULT_USER_AGENT = 
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    
    /**
     * Headers para requisições AJAX (padrão FilmesOn/OverFlix)
     * @param referer URL de referência
     * @param origin Domínio de origem (opcional)
     * @return Map de headers configurados para AJAX
     */
    fun ajax(referer: String, origin: String? = null): Map<String, String> {
        return buildMap {
            put("X-Requested-With", "XMLHttpRequest")
            put("Accept", "application/json")
            put("Content-Type", "application/x-www-form-urlencoded")
            put("Referer", referer)
            origin?.let { put("Origin", it) }
            put("User-Agent", DEFAULT_USER_AGENT)
        }
    }
    
    /**
     * Headers padrão para requisições HTTP normais
     * @param referer URL de referência (opcional)
     * @return Map de headers básicos
     */
    fun standard(referer: String? = null): Map<String, String> {
        return buildMap {
            put("User-Agent", DEFAULT_USER_AGENT)
            put("Accept", "*/*")
            put("Accept-Language", "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
            referer?.let { put("Referer", it) }
        }
    }
    
    /**
     * Headers específicos para MediaFire (padrão FilmesOn)
     * @param mediafireUrl URL do MediaFire
     * @return Map de headers para MediaFire
     */
    fun mediaFire(mediafireUrl: String): Map<String, String> {
        return mapOf(
            "User-Agent" to DEFAULT_USER_AGENT,
            "Referer" to mediafireUrl
        )
    }
    
    /**
     * Headers para bypass de proteção anti-bot
     * @param referer URL de referência
     * @param origin Domínio de origem
     * @return Map de headers com proteções extras
     */
    fun bypass(referer: String, origin: String): Map<String, String> {
        return mapOf(
            "User-Agent" to DEFAULT_USER_AGENT,
            "Referer" to referer,
            "Origin" to origin,
            "Accept" to "*/*",
            "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding" to "gzip, deflate, br",
            "Connection" to "keep-alive",
            "Sec-Fetch-Dest" to "empty",
            "Sec-Fetch-Mode" to "cors",
            "Sec-Fetch-Site" to "same-origin"
        )
    }
    
    /**
     * Headers para WebView
     * @param referer URL de referência
     * @return Map de headers para WebView
     */
    fun webView(referer: String): Map<String, String> {
        return mapOf(
            "User-Agent" to DEFAULT_USER_AGENT,
            "Referer" to referer,
            "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        )
    }
}
