// Test file to verify ExtractorLink syntax is correct
// This should compile without errors in CloudStream v4.6.0+

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*

fun testExtractorLinkSyntax() {
    val callback: (ExtractorLink) -> Unit = { }
    val videoUrl = "https://example.com/video.mp4"
    val referer = "https://example.com"
    val name = "TestExtractor"
    
    // ✅ CORRECT - New syntax (CloudStream v4.6.0+)
    callback(
        newExtractorLink(name, "$name HD", videoUrl) {
            this.referer = referer
            this.quality = Qualities.P720.value
            this.isM3u8 = false
        }
    )
    
    // ❌ DEPRECATED - Old syntax (will cause build errors)
    /*
    callback(
        newExtractorLink(
            source = name,
            name = "$name HD", 
            url = videoUrl,
            referer = referer,
            quality = Qualities.P720.value,
            isM3u8 = false
        )
    )
    */
}