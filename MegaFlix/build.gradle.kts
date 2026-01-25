version = 2

cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    description = "Filmes, Séries e Animes em Português"
    language = "pt-br"
    authors = listOf("saimuelbr", "franciscoalro")
    status = 1
    tvTypes = listOf("Movie","TvSeries")
    iconUrl = "https://megaflix.co/favicon.ico"
    isCrossPlatform = true
}
