// Teste da função upgradeImageQuality

fun upgradeImageQuality(url: String?): String? {
    if (url.isNullOrBlank()) return null
    return url.replace("/w185/", "/original/")
              .replace("/w300/", "/original/")
              .replace("/w342/", "/original/")
              .replace("/w500/", "/original/")
              .replace("/w780/", "/original/")
              .replace("/w1280/", "/original/")
}

fun main() {
    val testUrls = listOf(
        "https://image.tmdb.org/t/p/w500/veFW7hi5eephPLgKHqWUq4ishkz.jpg",
        "https://image.tmdb.org/t/p/w1280/ueXO7FqIECtcPbpPSw87hiFlrSA.jpg",
        "https://image.tmdb.org/t/p/w300/abc123.jpg",
        null,
        ""
    )
    
    println("🧪 TESTE upgradeImageQuality()")
    println("="*60)
    
    testUrls.forEach { url ->
        val result = upgradeImageQuality(url)
        println("\nInput:  $url")
        println("Output: $result")
        
        if (url != null && url.contains("tmdb.org")) {
            val upgraded = result?.contains("/original/") == true
            println("Status: ${if (upgraded) "✅ UPGRADED" else "❌ FALHOU"}")
        }
    }
}
