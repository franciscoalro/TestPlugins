package com.franciscoalro.maxseries.utils

/**
 * Biblioteca centralizada de regex patterns reutilizáveis
 * Inspirado nos padrões dos providers brasileiros (PobreFlix, FilmesOn, OverFlix, Vizer)
 */
object RegexPatterns {
    // ==================== IFRAME EXTRACTION ====================
    
    /** Extrai parâmetros de GetIframe JavaScript (padrão PobreFlix) */
    val IFRAME_GETFRAME = Regex("""GetIframe\('(\d+)','(.*?)'\)""")
    
    /** Extrai src de tag iframe */
    val IFRAME_SRC = Regex("""<iframe[^>]+src=["']([^"']+)["']""", RegexOption.IGNORE_CASE)
    
    // ==================== JSON EXTRACTION ====================
    
    /** Extrai embed_url de resposta JSON (padrão FilmesOn) */
    val EMBED_URL_JSON = Regex("""(?i)"embed_url"\s*:\s*"([^"]+)"""")
    
    /** Extrai video_url de resposta JSON (padrão OverFlix) */
    val VIDEO_URL_JSON = Regex("""["']video_url["']\s*:\s*["'](.*?)["']""")
    
    /** Extrai ID de resposta JSON */
    val ID_JSON = Regex("""["']ID["']\s*:\s*(\d+)""")
    
    // ==================== JAVASCRIPT EXTRACTION ====================
    
    /** Extrai apiUrl de código JavaScript */
    val API_URL_JS = Regex("""const apiUrl = `([^`]+)`""")
    
    /** Extrai videoUrl de código JavaScript */
    val VIDEO_URL_JS = Regex("""videoUrl\s*[:=]\s*["'](.*?)["']""")
    
    /** Extrai player_base_url de código JavaScript */
    val PLAYER_BASE_URL_JS = Regex("""var player_base_url\s*=\s*"([^"]+)"""")
    
    /** Detecta código JavaScript packed/ofuscado (padrão OverFlix) */
    val PACKED_JS = Regex(
        """eval\s*\((function\(p,a,c,k,e,d\).+?)\)\s*;?\s*</script>""",
        RegexOption.DOT_MATCHES_ALL
    )
    
    // ==================== M3U8/HLS EXTRACTION ====================
    
    /** Extrai URLs de M3U8/HLS/TXT playlists */
    val M3U8_URL = Regex("""["']([^"']+\.(?:m3u8|hls|txt)[^"']*)["']""")
    
    /** Extrai M3U8 de qualquer formato */
    val M3U8_GENERIC = Regex("""(https?://[^\s"'<>]+\.m3u8[^\s"'<>]*)""")
    
    // ==================== REDIRECT EXTRACTION ====================
    
    /** Extrai URL de window.location.href */
    val WINDOW_LOCATION = Regex("""window\.location\.href\s*=\s*"([^"]+)"""")
    
    /** Extrai URL de meta refresh */
    val META_REFRESH = Regex("""<meta[^>]+http-equiv=["']refresh["'][^>]+content=["']\d+;\s*url=([^"']+)""", RegexOption.IGNORE_CASE)
    
    // ==================== SERVER DETECTION ====================
    
    /** Detecta nome do servidor em onclick */
    val SERVER_NAME = Regex("""'([^']*)'\)""")
    
    /** Detecta tipo de servidor em URL */
    val SERVER_TYPE = Regex("""(streamtape|filemoon|doodstream|mixdrop|mediafire)""", RegexOption.IGNORE_CASE)
    
    // ==================== URL PARAMETERS ====================
    
    /**
     * Cria regex para extrair parâmetro específico de URL
     * @param paramName Nome do parâmetro (ex: "url", "id", "video")
     * @return Regex para capturar o valor do parâmetro
     */
    fun urlParam(paramName: String) = Regex("""[?&]$paramName=([^&]+)""")
    
    // ==================== CONTENT INFO ====================
    
    /** Extrai CONTENT_INFO de JavaScript */
    val CONTENT_INFO_JS = Regex("""var CONTENT_INFO = '(\d+)';""")
    
    /** Extrai números de texto */
    val EXTRACT_NUMBER = Regex("""(\d+)""")
    
    // ==================== VALIDATION ====================
    
    /** Valida se string é uma URL válida */
    val IS_URL = Regex("""^(http(s)?://)[^\s]+?\.[^\s]+/?""")
    
    /** Valida se URL é de vídeo */
    val IS_VIDEO_URL = Regex("""\.(mp4|m3u8|mkv|avi|webm|ts)(\?.*)?$""", RegexOption.IGNORE_CASE)
}
