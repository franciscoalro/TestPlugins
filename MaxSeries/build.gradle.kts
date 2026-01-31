version = 256

cloudstream {
    description = "MaxSeries v256 - PlayerEmbedAPI V8+V7 Fixes (Pure HTTP + WebView Optimized, Timeout 25s, 12 URL Patterns)"
    authors = listOf("franciscoalro")
    status = 1
    tvTypes = listOf("TvSeries", "Movie")
    language = "pt-BR"
    iconUrl = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
}

android {
    namespace = "com.franciscoalro.maxseries"
    
    sourceSets {
        getByName("main") {
            res.srcDirs("src/main/res")
        }
    }
    
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
}
