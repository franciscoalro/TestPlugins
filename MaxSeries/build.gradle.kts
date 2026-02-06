// use an integer for version numbers
version = 267

cloudstream {
    // All of these properties are optional, you can safely remove them
    description = "MaxSeries - Filmes e Series em FHD e HD."
    language    = "pt-br"
    authors = listOf("franciscoalro")

    /**
    * Status int as the following:
    * 0: Down
    * 1: Ok
    * 2: Slow
    * 3: Beta only
    * */
    status = 1 // will be 3 if unspecified

    // List of video source types. Users are able to filter for extensions in a given category.
    // You can find a list of available types here:
    // https://recloudstream.github.io/cloudstream/html/app/com.lagradost.cloudstream3/-tv-type/index.html
    tvTypes = listOf("Movie", "TvSeries")
    iconUrl = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"

    isCrossPlatform = true
}

android {
    namespace = "com.franciscoalro.maxseries"
}
