version = 261

cloudstream {
    description = "MaxSeries v261 - Multi-Source: Captura TODAS as sources simultaneamente"
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
