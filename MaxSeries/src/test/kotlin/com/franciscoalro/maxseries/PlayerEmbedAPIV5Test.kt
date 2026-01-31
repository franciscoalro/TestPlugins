package com.franciscoalro.maxseries

import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractorV5
import com.franciscoalro.maxseries.utils.*
import org.junit.Test
import org.junit.Assert.*

/**
 * Testes unitários para PlayerEmbedAPI Extractor v5.0
 */
class PlayerEmbedAPIV5Test {

    private val extractor = PlayerEmbedAPIExtractorV5()

    @Test
    fun `test isValidVideoUrl with valid Google Storage URL`() {
        val url = "https://storage.googleapis.com/bucket/video.mp4"
        assertTrue(extractor.isValidVideoUrl(url))
    }

    @Test
    fun `test isValidVideoUrl with valid SSSRR URL`() {
        val url = "https://cdn.sssrr.org/video/123.mp4"
        assertTrue(extractor.isValidVideoUrl(url))
    }

    @Test
    fun `test isValidVideoUrl with valid M3U8 URL`() {
        val url = "https://stream.example.com/playlist.m3u8"
        assertTrue(extractor.isValidVideoUrl(url))
    }

    @Test
    fun `test isValidVideoUrl with invalid URL`() {
        val url = "https://google.com"
        assertFalse(extractor.isValidVideoUrl(url))
    }

    @Test
    fun `test isValidVideoUrl with non-http URL`() {
        val url = "ftp://example.com/video.mp4"
        assertFalse(extractor.isValidVideoUrl(url))
    }

    @Test
    fun `test detectQualityFromUrl with 4K`() {
        val url = "https://example.com/video_2160p.mp4"
        assertEquals("4K", extractor.detectQualityFromUrl(url))
    }

    @Test
    fun `test detectQualityFromUrl with 1080p`() {
        val url = "https://example.com/video_1080.mp4"
        assertEquals("1080p", extractor.detectQualityFromUrl(url))
    }

    @Test
    fun `test detectQualityFromUrl with 720p`() {
        val url = "https://example.com/video_720p.mp4"
        assertEquals("720p", extractor.detectQualityFromUrl(url))
    }

    @Test
    fun `test detectQualityFromUrl with unknown quality`() {
        val url = "https://example.com/video.mp4"
        assertEquals("HD", extractor.detectQualityFromUrl(url))
    }

    @Test
    fun `test findBase64Datas with valid base64`() {
        // Criar um HTML de teste com base64 válido
        val validBase64 = "eyJ0ZXN0IjogdHJ1ZX0=" // {"test": true} em base64
        val html = """
            <script>
                const datas = "$validBase64";
            </script>
        """.trimIndent()
        
        val result = extractor.findBase64Datas(html)
        assertNotNull(result)
        assertEquals(validBase64, result)
    }

    @Test
    fun `test findBase64Datas with no base64`() {
        val html = "<html><body>No base64 here</body></html>"
        val result = extractor.findBase64Datas(html)
        assertNull(result)
    }

    @Test
    fun `test extractShortIcuUrl with iframe`() {
        val html = """
            <iframe src="https://short.icu/abc123" width="100%"></iframe>
        """.trimIndent()
        
        val result = extractor.extractShortIcuUrl(html)
        assertEquals("https://short.icu/abc123", result)
    }

    @Test
    fun `test extractShortIcuUrl with direct link`() {
        val html = """
            <a href="https://short.icu/xyz789">Link</a>
        """.trimIndent()
        
        val result = extractor.extractShortIcuUrl(html)
        assertEquals("https://short.icu/xyz789", result)
    }

    @Test
    fun `test extractVideoUrlFromHtml with Google Storage`() {
        val html = """
            var videoUrl = "https://storage.googleapis.com/bucket/video.mp4?token=abc";
        """.trimIndent()
        
        val result = extractor.extractVideoUrlFromHtml(html)
        assertNotNull(result)
        assertTrue(result!!.contains("storage.googleapis.com"))
    }

    @Test
    fun `test extractVideoUrlFromHtml with SSSRR`() {
        val html = """
            sources: [{"file": "https://cdn.sssrr.org/123/video.mp4"}]
        """.trimIndent()
        
        val result = extractor.extractVideoUrlFromHtml(html)
        assertNotNull(result)
        assertTrue(result!!.contains("sssrr.org"))
    }

    @Test
    fun `test processJsonStringToBytes with simple string`() {
        val input = "hello"
        val result = extractor.processJsonStringToBytes(input)
        assertArrayEquals(byteArrayOf(0x68, 0x65, 0x6C, 0x6C, 0x6F), result)
    }

    @Test
    fun `test processJsonStringToBytes with escaped quotes`() {
        val input = "test\"quote"
        val result = extractor.processJsonStringToBytes(input)
        assertArrayEquals(byteArrayOf(0x74, 0x65, 0x73, 0x74, 0x22, 0x71, 0x75, 0x6F, 0x74, 0x65), result)
    }

    @Test
    fun `test processJsonStringToBytes with unicode escape`() {
        val input = "test\\u0041" // \u0041 = 'A'
        val result = extractor.processJsonStringToBytes(input)
        assertArrayEquals(byteArrayOf(0x74, 0x65, 0x73, 0x74, 0x41), result)
    }

    @Test
    fun `test canHandle returns true for playerembedapi URLs`() {
        val validUrls = listOf(
            "https://playerembedapi.link/?v=abc123",
            "https://playerembedapi.link/embed/xyz",
            "https://www.playerembedapi.link/video/123"
        )
        
        validUrls.forEach { url ->
            assertTrue("Should handle $url", extractor.canHandle(url))
        }
    }

    @Test
    fun `test canHandle returns false for other URLs`() {
        val invalidUrls = listOf(
            "https://youtube.com/watch?v=abc",
            "https://example.com/video.mp4",
            "https://streamtape.com/v/abc"
        )
        
        invalidUrls.forEach { url ->
            assertFalse("Should not handle $url", extractor.canHandle(url))
        }
    }

    // Testes de integração (requer rede)
    /*
    @Test
    fun `integration test - extract from real URL`() = runBlocking {
        val url = "https://playerembedapi.link/?v=TEST_ID"
        val links = mutableListOf<ExtractorLink>()
        
        extractor.getUrl(url, null, {}) { link ->
            links.add(link)
        }
        
        // Não garante sucesso (URL pode expirar), mas verifica se não crasha
        assertTrue(links.isEmpty() || links.all { it.url.isNotBlank() })
    }
    */
}
