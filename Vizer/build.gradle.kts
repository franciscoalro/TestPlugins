version = 2

cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    description = "Vizer - Filmes, Séries, Animes"
    language = "pt-br"
    authors = listOf("saimuelbr", "franciscoalro")
    status = 1
    tvTypes = listOf("Movie", "TvSeries")
    iconUrl = "https://vizer.tv/favicon.ico"
    isCrossPlatform = true
} 