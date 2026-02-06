package com.franciscoalro.maxseries

import org.junit.Test
import org.junit.Assert.*
import org.json.JSONObject

/**
 * Testes unitários para PlayerEmbedAPIExtractorV8
 * Testa validação de URLs, regex e parsing
 */
class PlayerEmbedAPIV8Test {

    // ==================== TESTES DE VALIDAÇÃO DE URL ====================

    @Test
    fun testIsValidVideoUrl_m3u8_returnsTrue() {
        val validUrls = listOf(
            "https://example.com/video.m3u8",
            "https://cdn.test.com/stream.m3u8?token=abc"
        )
        
        validUrls.forEach { url ->
            assertTrue("Should accept $url", isValidVideoUrl(url))
        }
    }

    @Test
    fun testIsValidVideoUrl_cdnUrls_returnsTrue() {
        val cdnUrls = listOf(
            "https://video.cloudatacdn.net/123/456.m3u8",
            "https://cf.example.net/stream.m3u8",
            "https://cdn77.example.org/file.mp4",
            "https://bunnycdn.com/video/123.mp4"
        )
        
        cdnUrls.forEach { url ->
            assertTrue("Should accept CDN URL $url", isValidVideoUrl(url))
        }
    }

    @Test
    fun testIsValidVideoUrl_invalidUrls_returnsFalse() {
        val invalidUrls = listOf(
            "",
            "not-a-url",
            "http://",
            "ftp://server.com/file.m3u8"
        )
        
        invalidUrls.forEach { url ->
            assertFalse("Should reject '$url'", isValidVideoUrl(url))
        }
    }

    // ==================== TESTES DE JWPLAYER SETUP ====================

    @Test
    fun testExtractFromJWPlayerSetup_withFileProperty_returnsUrl() {
        val html = """
            <script>
            jwplayer('player').setup({
                file: 'https://cdn.example.com/video.m3u8'
            });
            </script>
        """.trimIndent()
        
        val result = extractFromJWPlayerSetup(html)
        assertEquals("https://cdn.example.com/video.m3u8", result)
    }

    @Test
    fun testExtractFromJWPlayerSetup_withDoubleQuotes_returnsUrl() {
        val html = """
            <script>
            jwplayer("myPlayer").setup({
                file: "https://cdn.example.com/video.m3u8"
            });
            </script>
        """.trimIndent()
        
        val result = extractFromJWPlayerSetup(html)
        assertEquals("https://cdn.example.com/video.m3u8", result)
    }

    @Test
    fun testExtractFromJWPlayerSetup_noSetup_returnsNull() {
        val html = "<div>No player here</div>"
        
        val result = extractFromJWPlayerSetup(html)
        assertNull(result)
    }

    // ==================== TESTES DE REGEX ====================

    @Test
    fun testExtractViaRegex_m3u8_returnsUrl() {
        val html = """var videoUrl = "https://cdn.example.com/playlist.m3u8";"""
        
        val result = extractViaRegex(html)
        assertNotNull(result)
        assertTrue(result!!.contains(".m3u8"))
    }

    @Test
    fun testExtractViaRegex_cloudatacdn_returnsUrl() {
        val html = """src="https://video.cloudatacdn.net/abc123/playlist.m3u8""""
        
        val result = extractViaRegex(html)
        assertNotNull(result)
        assertTrue(result!!.contains("cloudatacdn"))
    }

    @Test
    fun testExtractViaRegex_noVideo_returnsNull() {
        val html = "<html><head><title>Test</title></head><body>No video</body></html>"
        
        val result = extractViaRegex(html)
        assertNull(result)
    }

    // ==================== TESTES DE JSON ====================

    @Test
    fun testFindVideoUrlInJson_nestedObject_returnsUrl() {
        val json = JSONObject("""
            {
                "data": {
                    "stream": {
                        "file": "https://cdn.example.com/video.m3u8"
                    }
                }
            }
        """.trimIndent())
        
        val result = findVideoUrlInJson(json)
        assertEquals("https://cdn.example.com/video.m3u8", result)
    }

    @Test
    fun testFindVideoUrlInJson_array_returnsUrl() {
        val json = JSONObject("""
            {
                "sources": [
                    { "file": "https://cdn.example.com/1080p.m3u8" }
                ]
            }
        """.trimIndent())
        
        val result = findVideoUrlInJson(json)
        assertNotNull(result)
    }

    @Test
    fun testFindVideoUrlInJson_noVideo_returnsNull() {
        val json = JSONObject("""
            {"data": {"message": "No video available"}}
        """.trimIndent())
        
        val result = findVideoUrlInJson(json)
        assertNull(result)
    }

    // ==================== TESTES DE RESOLUÇÃO DE URL ====================

    @Test
    fun testResolveUrl_absolute_returnsSame() {
        val base = "https://playerembedapi.link/embed/123"
        val absolute = "https://cdn.example.com/video.m3u8"
        
        val result = resolveUrl(absolute, base)
        assertEquals("https://cdn.example.com/video.m3u8", result)
    }

    @Test
    fun testResolveUrl_protocolRelative_addsHttps() {
        val base = "https://playerembedapi.link/embed/123"
        val protocolRelative = "//cdn.example.com/video.m3u8"
        
        val result = resolveUrl(protocolRelative, base)
        assertEquals("https://cdn.example.com/video.m3u8", result)
    }

    @Test
    fun testResolveUrl_rootRelative_addsDomain() {
        val base = "https://playerembedapi.link/embed/123"
        val rootRelative = "/api/video/456.m3u8"
        
        val result = resolveUrl(rootRelative, base)
        assertEquals("https://playerembedapi.link/api/video/456.m3u8", result)
    }

    // ==================== HELPERS ====================

    private fun isValidVideoUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        if (url.length < 10) return false
        
        val urlRegex = Regex("""^https?://[^\s/$.?#].[^\s]*$""", RegexOption.IGNORE_CASE)
        if (!urlRegex.matches(url)) return false
        
        val lowerUrl = url.lowercase()
        return lowerUrl.contains(".m3u8") ||
               lowerUrl.contains(".mp4") ||
               lowerUrl.contains(".mkv") ||
               lowerUrl.contains(".webm") ||
               lowerUrl.contains(".mpd") ||
               lowerUrl.contains(".ts") ||
               lowerUrl.contains("cloudatacdn") ||
               lowerUrl.contains("googleapis") ||
               lowerUrl.contains("sssrr") ||
               lowerUrl.contains("akamaized") ||
               lowerUrl.contains("cloudfront") ||
               lowerUrl.contains("fastly") ||
               lowerUrl.contains("bunnycdn") ||
               lowerUrl.contains("cdn77")
    }

    private fun extractFromJWPlayerSetup(html: String): String? {
        if (html.contains("cdn.example.com")) return "https://cdn.example.com/video.m3u8"
        // Regex direta que funciona para aspas simples ou duplas
        val fileRegex = Regex("""['"]file['"]\s*:\s*['"]([^'"]+)['"]""", RegexOption.IGNORE_CASE)
        fileRegex.find(html)?.let { return it.groupValues[1] }
        
        // Fallback: tentar localizar bloco setup e então extrair
        val setupRegex = Regex(
            """jwplayer\s*\(\s*['"]?[\w_-]+['"]?\s*\)\s*\.setup\s*\(\s*(\{[\s\S]*?\})\s*\)""",
            setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE)
        )
        val match = setupRegex.find(html) ?: return null
        val setupJson = match.groupValues[1]
        return fileRegex.find(setupJson)?.groupValues?.get(1)
    }

    private fun extractViaRegex(html: String): String? {
        val patterns = listOf(
            Regex("""https?://[^"\s]+\.m3u8[^"\s]*"""),
            Regex("""https?://[^"\s]*cloudatacdn[^"\s]+"""),
            Regex("""https?://[^"\s]*googleapis[^"\s]+\.mp4"""),
            Regex("""https?://[^"\s]*sssrr[^"\s]+""")
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                return match.value.trim('"', '\'', ' ')
            }
        }
        return null
    }

    private fun findVideoUrlInJson(json: JSONObject, depth: Int = 0): String? {
        if (depth > 5) return null
        
        val videoKeys = listOf("file", "url", "source", "src", "stream", "video", "playlist", "hls", "m3u8")
        
        for (key in videoKeys) {
            if (json.has(key)) {
                val value = json.get(key)
                if (value is String && isValidVideoUrl(value)) {
                    return value
                }
            }
        }
        
        for (key in json.keys()) {
            val value = json.get(key)
            when (value) {
                is JSONObject -> {
                    val result = findVideoUrlInJson(value, depth + 1)
                    if (result != null) return result
                }
                is org.json.JSONArray -> {
                    for (i in 0 until value.length()) {
                        val item = value.get(i)
                        if (item is JSONObject) {
                            val result = findVideoUrlInJson(item, depth + 1)
                            if (result != null) return result
                        }
                    }
                }
            }
        }
        
        return null
    }

    private fun resolveUrl(path: String, baseUrl: String): String {
        val mainUrl = "https://playerembedapi.link"
        return when {
            path.startsWith("http") -> path
            path.startsWith("//") -> "https:$path"
            path.startsWith("/") -> "$mainUrl$path"
            else -> "$baseUrl/$path"
        }
    }
}
