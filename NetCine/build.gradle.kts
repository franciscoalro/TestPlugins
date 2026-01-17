version = 1

cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    description = "Filmes, Séries e Animes em Português"
    language = "pt-br"
    authors = listOf("Phisher98", "saimuelbr", "franciscoalro")
    status = 1
    tvTypes = listOf("Movie","TvSeries")
    iconUrl = "https://netcine.tv/favicon.ico"
    isCrossPlatform = true
}
