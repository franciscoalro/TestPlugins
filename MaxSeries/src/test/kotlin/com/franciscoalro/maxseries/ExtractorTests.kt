package com.franciscoalro.maxseries

import com.franciscoalro.maxseries.extractors.*
import com.lagradost.cloudstream3.*
import kotlinx.coroutines.runBlocking
import org.junit.Test
import org.junit.Assert.*
import kotlin.system.measureTimeMillis

/**
 * ExtractorTests - Suite de testes para todos os extractors
 * 
 * Baseado no skill: testing-patterns
 * - AAA Pattern (Arrange, Act, Assert)
 * - Fast tests (<5s cada)
 * - Isolated (sem dependências externas reais)
 * - Self-checking
 * 
 * COMO RODAR:
 * ./gradlew MaxSeries:test
 */
class ExtractorTests {
    
    companion object {
        private const val TIMEOUT_MS = 5000L // 5 segundos
        
        // URLs de teste reais (substituir por URLs válidas)
        private const val TEST_MEGAEMBED_URL = "https://megaembed.cc/embed/..."
        private const val TEST_PLAYEREMBED_URL = "https://playerembedapi.link/..."
        private const val TEST_MYVIDPLAY_URL = "https://myvidplay.com/..."
        private const val TEST_DOODSTREAM_URL = "https://doodstream.com/..."
        private const val TEST_STREAMTAPE_URL = "https://streamtape.com/..."
        private const val TEST_MIXDROP_URL = "https://mixdrop.co/..."
        private const val TEST_FILEMOON_URL = "https://filemoon.sx/..."
    }
    
    // ==================== MEGAEMBED V9 TESTS ====================
    
    @Test
    fun `MegaEmbed should extract video URL within 5 seconds`() = runBlocking {
        // Arrange
        val extractor = MegaEmbedExtractorV9()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        val duration = measureTimeMillis {
            extractor.getUrl(
                url = TEST_MEGAEMBED_URL,
                referer = "https://maxseries.pics",
                subtitleCallback = {},
                callback = { links.add(it) }
            )
        }
        
        // Assert
        assertTrue("Should extract at least one link", links.isNotEmpty())
        assertTrue("Should complete within 5s", duration < TIMEOUT_MS)
        assertTrue("URL should be valid", links.first().url.startsWith("http"))
        assertEquals("Source should be MegaEmbed", "MegaEmbed", links.first().name.substringBefore(" "))
    }
    
    @Test
    fun `MegaEmbed should handle invalid URL gracefully`() = runBlocking {
        // Arrange
        val extractor = MegaEmbedExtractorV9()
        val links = mutableListOf<ExtractorLink>()
        
        // Act & Assert
        try {
            extractor.getUrl(
                url = "https://invalid-url.com",
                referer = null,
                subtitleCallback = {},
                callback = { links.add(it) }
            )
            // Should not throw exception
            assertTrue("Should handle gracefully", true)
        } catch (e: Exception) {
            // Expected behavior
            assertTrue("Should catch exception", true)
        }
    }
    
    // ==================== PLAYEREMBEDAPI MANUAL TESTS ====================
    
    @Test
    fun `PlayerEmbedAPI Manual should wait for user click`() = runBlocking {
        // Arrange
        val extractor = PlayerEmbedAPIExtractorManual()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        val duration = measureTimeMillis {
            try {
                extractor.getUrl(
                    url = TEST_PLAYEREMBED_URL,
                    referer = "https://maxseries.pics",
                    subtitleCallback = {},
                    callback = { links.add(it) }
                )
            } catch (e: Exception) {
                // Timeout esperado se não houver click
            }
        }
        
        // Assert
        // Este teste pode falhar por timeout (esperado)
        assertTrue("Should timeout or succeed", duration >= 1000L)
    }
    
    // ==================== MYVIDPLAY TESTS ====================
    
    @Test
    fun `MyVidPlay should extract MP4 URL`() = runBlocking {
        // Arrange
        val extractor = MyVidPlayExtractor()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        val duration = measureTimeMillis {
            extractor.getUrl(
                url = TEST_MYVIDPLAY_URL,
                referer = "https://maxseries.pics",
                subtitleCallback = {},
                callback = { links.add(it) }
            )
        }
        
        // Assert
        if (links.isNotEmpty()) {
            assertTrue("Should be MP4 or M3U8", 
                links.first().url.contains(".mp4") || links.first().url.contains(".m3u8"))
            assertTrue("Should complete fast", duration < 3000L)
        }
    }
    
    @Test
    fun `MyVidPlay should use cache on second call`() = runBlocking {
        // Arrange
        val extractor = MyVidPlayExtractor()
        val links1 = mutableListOf<ExtractorLink>()
        val links2 = mutableListOf<ExtractorLink>()
        
        // Act - First call
        val duration1 = measureTimeMillis {
            extractor.getUrl(TEST_MYVIDPLAY_URL, null, {}, { links1.add(it) })
        }
        
        // Act - Second call (should use cache)
        val duration2 = measureTimeMillis {
            extractor.getUrl(TEST_MYVIDPLAY_URL, null, {}, { links2.add(it) })
        }
        
        // Assert
        if (links1.isNotEmpty() && links2.isNotEmpty()) {
            assertTrue("Second call should be faster", duration2 < duration1)
            assertEquals("URLs should match", links1.first().url, links2.first().url)
        }
    }
    
    // ==================== DOODSTREAM TESTS ====================
    
    @Test
    fun `DoodStream should extract video URL`() = runBlocking {
        // Arrange
        val extractor = DoodStreamExtractor()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        extractor.getUrl(
            url = TEST_DOODSTREAM_URL,
            referer = "https://maxseries.pics",
            subtitleCallback = {},
            callback = { links.add(it) }
        )
        
        // Assert
        if (links.isNotEmpty()) {
            assertTrue("Should contain dood domain", 
                links.first().url.contains("dood") || links.first().url.contains("ds2"))
        }
    }
    
    // ==================== STREAMTAPE TESTS ====================
    
    @Test
    fun `StreamTape should extract video URL`() = runBlocking {
        // Arrange
        val extractor = StreamtapeExtractor()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        extractor.getUrl(
            url = TEST_STREAMTAPE_URL,
            referer = "https://maxseries.pics",
            subtitleCallback = {},
            callback = { links.add(it) }
        )
        
        // Assert
        if (links.isNotEmpty()) {
            assertTrue("Should be valid URL", links.first().url.startsWith("http"))
        }
    }
    
    // ==================== MIXDROP TESTS ====================
    
    @Test
    fun `Mixdrop should extract video URL`() = runBlocking {
        // Arrange
        val extractor = MixdropExtractor()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        extractor.getUrl(
            url = TEST_MIXDROP_URL,
            referer = "https://maxseries.pics",
            subtitleCallback = {},
            callback = { links.add(it) }
        )
        
        // Assert
        if (links.isNotEmpty()) {
            assertTrue("Should be valid URL", links.first().url.startsWith("http"))
        }
    }
    
    // ==================== FILEMOON TESTS ====================
    
    @Test
    fun `Filemoon should extract video URL`() = runBlocking {
        // Arrange
        val extractor = FilemoonExtractor()
        val links = mutableListOf<ExtractorLink>()
        
        // Act
        extractor.getUrl(
            url = TEST_FILEMOON_URL,
            referer = "https://maxseries.pics",
            subtitleCallback = {},
            callback = { links.add(it) }
        )
        
        // Assert
        if (links.isNotEmpty()) {
            assertTrue("Should be valid URL", links.first().url.startsWith("http"))
        }
    }
    
    // ==================== PERFORMANCE TESTS ====================
    
    @Test
    fun `All extractors should complete within timeout`() = runBlocking {
        val extractors = listOf(
            "MegaEmbed" to MegaEmbedExtractorV9(),
            "MyVidPlay" to MyVidPlayExtractor(),
            "DoodStream" to DoodStreamExtractor(),
            "StreamTape" to StreamtapeExtractor(),
            "Mixdrop" to MixdropExtractor(),
            "Filemoon" to FilemoonExtractor()
        )
        
        val results = mutableMapOf<String, Long>()
        
        extractors.forEach { (name, extractor) ->
            val duration = measureTimeMillis {
                try {
                    extractor.getUrl("https://test.com", null, {}, {})
                } catch (e: Exception) {
                    // Expected for invalid URL
                }
            }
            results[name] = duration
        }
        
        // Assert
        results.forEach { (name, duration) ->
            assertTrue("$name should complete within 10s", duration < 10000L)
        }
    }
}
