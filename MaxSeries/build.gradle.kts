version = 264

cloudstream {
    description = "MaxSeries v264 - Build otimizado e estabilidade aprimorada"
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
