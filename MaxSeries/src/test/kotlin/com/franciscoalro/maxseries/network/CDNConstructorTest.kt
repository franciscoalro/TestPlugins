package com.franciscoalro.maxseries.network

import org.junit.Test
import org.junit.Assert.*

/**
 * Testes unitários para o CDNConstructor
 * 
 * Estes testes verificam:
 * 1. Extração de dados de vídeo do HTML
 * 2. Construção de URLs CDN
 * 3. Detecção de CDNs
 * 4. Validação de URLs de vídeo
 */
class CDNConstructorTest {
    
    /**
     * HTML de exemplo com dados de vídeo
     */
    private val sampleHtml = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Video Player</title>
            <meta property="video:id" content="28930647">
        </head>
        <body>
            <div id="player" data-slug="kBJLtxCD3" data-md5-id="28930647"></div>
            <script>
                window.videoData = {
                    slug: "kBJLtxCD3",
                    md5_id: "28930647",
                    user_id: "482120"
                };
            </script>
        </body>
        </html>
    """.trimIndent()
    
    @Test
    fun `test extract video data from HTML`() {
        val videoData = CDNConstructor.extractVideoData(sampleHtml)
        
        assertNotNull("VideoData não deve ser null", videoData)
        assertEquals("Slug incorreto", "kBJLtxCD3", videoData?.slug)
        assertEquals("MD5 ID incorreto", "28930647", videoData?.md5Id)
        assertEquals("Source incorreto", 
            CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI, 
            videoData?.source)
    }
    
    @Test
    fun `test construct SSSRR URLs`() {
        val videoData = CDNConstructor.VideoData(
            slug = "kBJLtxCD3",
            md5Id = "28930647",
            source = CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI
        )
        
        val urls = CDNConstructor.constructCDNUrls(videoData)
        
        assertTrue("Deve construir múltiplas URLs", urls.size > 5)
        
        // Verificar padrões principais
        assertTrue("Deve conter URL com slug", 
            urls.any { it.contains("kBJLtxCD3.sssrr.org") })
        assertTrue("Deve conter URL CDN", 
            urls.any { it.contains("cdn.sssrr.org") })
        assertTrue("Deve conter URL statics", 
            urls.any { it.contains("statics.sssrr.org") })
        assertTrue("Deve conter playlist m3u8", 
            urls.any { it.contains(".m3u8") })
    }
    
    @Test
    fun `test construct Marvella URLs`() {
        val videoData = CDNConstructor.VideoData(
            slug = "",
            md5Id = "",
            videoId = "3wnuij",
            source = CDNConstructor.VideoData.VideoSource.MEGAEMBED
        )
        
        val urls = CDNConstructor.constructCDNUrls(videoData)
        
        assertTrue("Deve construir muitas URLs para Marvella", urls.size > 20)
        
        // Verificar padrões
        assertTrue("Deve conter domínio Marvella", 
            urls.any { it.contains("marvellaholdings.sbs") })
        assertTrue("Deve conter cf-master", 
            urls.any { it.contains("cf-master") })
        assertTrue("Deve conter shards", 
            urls.any { it.contains("/v4/x6b/") })
    }
    
    @Test
    fun `test detect CDN from URL`() {
        assertEquals("SSSRR", 
            CDNConstructor.detectCDN("https://kBJLtxCD3.sssrr.org/sora/123/"))
        assertEquals("Marvella", 
            CDNConstructor.detectCDN("https://stzm.marvellaholdings.sbs/v4/x6b/123/"))
        assertEquals("GCS", 
            CDNConstructor.detectCDN("https://storage.googleapis.com/mediastorage/123/video.mp4"))
        assertEquals("Unknown", 
            CDNConstructor.detectCDN("https://unknown-cdn.com/video.mp4"))
    }
    
    @Test
    fun `test is video URL`() {
        assertTrue("M3U8 deve ser vídeo", 
            CDNConstructor.isVideoUrl("https://example.com/video.m3u8"))
        assertTrue("MP4 deve ser vídeo", 
            CDNConstructor.isVideoUrl("https://example.com/video.mp4"))
        assertTrue("SSSRR deve ser vídeo", 
            CDNConstructor.isVideoUrl("https://cdn.sssrr.org/sora/123/"))
        assertTrue("cf-master deve ser vídeo", 
            CDNConstructor.isVideoUrl("https://cdn.example.com/cf-master.txt"))
        assertFalse("HTML não deve ser vídeo", 
            CDNConstructor.isVideoUrl("https://example.com/page.html"))
    }
    
    @Test
    fun `test extract host from URL`() {
        assertEquals("cdn.sssrr.org", 
            CDNConstructor.extractHost("https://cdn.sssrr.org/sora/123/"))
        assertEquals("storage.googleapis.com", 
            CDNConstructor.extractHost("https://storage.googleapis.com/bucket/file.mp4"))
        assertNull("URL inválida deve retornar null", 
            CDNConstructor.extractHost("not-a-url"))
    }
    
    @Test
    fun `test construct quick`() {
        val videoData = CDNConstructor.VideoData(
            slug = "kBJLtxCD3",
            md5Id = "28930647",
            source = CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI
        )
        
        val url = CDNConstructor.constructQuick(videoData)
        
        assertNotNull("URL não deve ser null", url)
        assertTrue("Deve conter slug", url!!.contains("kBJLtxCD3"))
        assertTrue("Deve conter md5Id", url.contains("28930647"))
        assertTrue("Deve usar HTTPS", url.startsWith("https://"))
    }
    
    @Test
    fun `test known CDNs structure`() {
        // Verificar que os CDNs conhecidos estão definidos
        assertTrue("SSSRR domains não deve estar vazio", 
            CDNConstructor.KnownCDNs.SSSRR_DOMAINS.isNotEmpty())
        assertTrue("Marvella domains não deve estar vazio", 
            CDNConstructor.KnownCDNs.MARVELLA_DOMAINS.isNotEmpty())
        assertTrue("Marvella shards não deve estar vazio", 
            CDNConstructor.KnownCDNs.MARVELLA_SHARDS.isNotEmpty())
        
        // Verificar valores específicos
        assertTrue("Deve conter sssrr.org", 
            CDNConstructor.KnownCDNs.SSSRR_DOMAINS.contains("sssrr.org"))
        assertTrue("Deve conter marvellaholdings.sbs", 
            CDNConstructor.KnownCDNs.MARVELLA_DOMAINS.contains("marvellaholdings.sbs"))
    }
    
    @Test
    fun `test video data source enum`() {
        val sources = CDNConstructor.VideoData.VideoSource.values()
        
        assertEquals("Deve ter 5 fontes", 5, sources.size)
        assertTrue("Deve conter PLAYEREMBEDAPI", 
            sources.contains(CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI))
        assertTrue("Deve conter MEGAEMBED", 
            sources.contains(CDNConstructor.VideoData.VideoSource.MEGAEMBED))
        assertTrue("Deve conter GOOGLE_STORAGE", 
            sources.contains(CDNConstructor.VideoData.VideoSource.GOOGLE_STORAGE))
        assertTrue("Deve conter CLOUDATA", 
            sources.contains(CDNConstructor.VideoData.VideoSource.CLOUDATA))
        assertTrue("Deve conter UNKNOWN", 
            sources.contains(CDNConstructor.VideoData.VideoSource.UNKNOWN))
    }
    
    @Test
    fun `test CDN result structure`() {
        val urls = listOf(
            "https://cdn1.example.com/video.m3u8",
            "https://cdn2.example.com/video.m3u8"
        )
        
        val result = CDNConstructor.CDNResult(
            urls = urls,
            source = CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI,
            isValidated = true,
            validUrl = urls[0]
        )
        
        assertEquals(2, result.urls.size)
        assertTrue(result.isValidated)
        assertEquals(urls[0], result.validUrl)
        assertEquals(CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI, result.source)
    }
    
    @Test
    fun `test empty data returns empty URLs`() {
        val videoData = CDNConstructor.VideoData(
            slug = "",
            md5Id = "",
            source = CDNConstructor.VideoData.VideoSource.PLAYEREMBEDAPI
        )
        
        val urls = CDNConstructor.constructCDNUrls(videoData)
        
        assertTrue("Deve retornar lista vazia para dados vazios", urls.isEmpty())
    }
    
    @Test
    fun `test extension functions`() {
        // Testar extensão constructCDN
        val urls = sampleHtml.constructCDN()
        assertTrue("Extensão deve construir URLs", urls.isNotEmpty())
        
        // Testar que html sem dados retorna vazio
        val emptyHtml = "<html></html>"
        val emptyUrls = emptyHtml.constructCDN()
        assertTrue("HTML vazio deve retornar lista vazia", emptyUrls.isEmpty())
    }
}
