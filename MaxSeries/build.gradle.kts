version = 258

cloudstream {
    description = "MaxSeries v258 - Clean Build & Fixed Repository"
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
