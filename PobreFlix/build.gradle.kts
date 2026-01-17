version = 1

cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "franciscoalro/TestPlugins")
    authors = listOf("saimuelbr", "franciscoalro")

    status = 1

    tvTypes = listOf("Movie","TvSeries")
    iconUrl = "https://pobreflix.biz/favicon.ico"

    isCrossPlatform = true
}
