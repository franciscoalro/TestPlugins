package com.franciscoalro.maxseries.utils

/**
 * JsUnpacker - Descompacta JavaScript ofuscado com eval(function(p,a,c,k,e,d)...)
 * Baseado no padrão do OverFlixExtractor do saimuelrepo
 */
object JsUnpacker {
    
    private val PACKED_REGEX = Regex(
        """eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\)""",
        RegexOption.IGNORE_CASE
    )
    
    private val UNPACK_REGEX = Regex(
        """}\s*\(\s*'(.+?)'\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'(.+?)'\.split\s*\(\s*'[|]'\s*\)""",
        RegexOption.DOT_MATCHES_ALL
    )

    /**
     * Verifica se o código é packed (ofuscado)
     */
    fun isPacked(js: String): Boolean {
        return PACKED_REGEX.containsMatchIn(js)
    }

    /**
     * Descompacta código JavaScript ofuscado
     * @return String descompactada ou null se falhar
     */
    fun unpack(packedJs: String): String? {
        return try {
            val match = UNPACK_REGEX.find(packedJs) ?: return null
            
            val payload = match.groupValues[1]
            val radix = match.groupValues[2].toIntOrNull() ?: 36
            val count = match.groupValues[3].toIntOrNull() ?: 0
            val keywords = match.groupValues[4].split("|")
            
            if (keywords.size != count) return null
            
            unbase(payload, radix, keywords)
        } catch (e: Exception) {
            null
        }
    }

    private fun unbase(payload: String, radix: Int, keywords: List<String>): String {
        val pattern = Regex("""\b(\w+)\b""")
        
        return pattern.replace(payload) { match ->
            val word = match.groupValues[1]
            val index = unbaser(word, radix)
            
            if (index < keywords.size && keywords[index].isNotEmpty()) {
                keywords[index]
            } else {
                word
            }
        }
    }

    private fun unbaser(value: String, radix: Int): Int {
        if (radix <= 36) {
            return value.toIntOrNull(radix) ?: 0
        }
        
        // Para radix > 36 (até 62)
        val digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        var result = 0
        
        for (char in value) {
            val index = digits.indexOf(char)
            if (index == -1) return 0
            result = result * radix + index
        }
        
        return result
    }

    /**
     * Extrai URLs de vídeo do código descompactado
     */
    fun extractVideoUrls(unpacked: String): List<String> {
        val patterns = listOf(
            Regex("""["']?(https?://[^"'\s]+\.(?:m3u8|mp4)[^"'\s]*)["']?"""),
            Regex("""file\s*:\s*["']([^"']+)["']"""),
            Regex("""source\s*:\s*["']([^"']+)["']"""),
            Regex("""src\s*:\s*["']([^"']+\.(?:m3u8|mp4)[^"']*)["']"""),
            Regex("""videoUrl\s*[:=]\s*["']([^"']+)["']""")
        )
        
        val urls = mutableSetOf<String>()
        
        for (pattern in patterns) {
            pattern.findAll(unpacked).forEach { match ->
                val url = match.groupValues.getOrNull(1) ?: match.value
                if (url.startsWith("http") && !url.contains("google-analytics")) {
                    urls.add(url.replace("\\/", "/"))
                }
            }
        }
        
        return urls.toList()
    }
}
