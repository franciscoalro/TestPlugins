version = 257

cloudstream {
    description = "MaxSeries v257 - PlayerEmbedAPI V8+V7 Fixes"
    authors = listOf("franciscoalro")
    status = 1
    tvTypes = listOf("TvSeries", "Movie")
    language = "pt-BR"
    iconUrl = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
}

android {
    namespace = "com.franciscoalro.maxseries"
    
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
}
