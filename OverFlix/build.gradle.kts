version = 1

cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    description = "OverFlix - Filmes em HD+ e Séries Séries em FHD"
    language = "pt-br"
    authors = listOf("saimuelbr", "franciscoalro")
    status = 1
    tvTypes = listOf("Movie", "TvSeries")
    iconUrl = "https://overflix.online/favicon.ico"
    isCrossPlatform = true
} 