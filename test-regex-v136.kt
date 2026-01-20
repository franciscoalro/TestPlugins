/**
 * Teste do Regex Ultra-Otimizado v136
 * 
 * Testa se o regex detecta URLs parciais ou completas
 */

fun main() {
    val regex = Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)""", RegexOption.IGNORE_CASE)
    
    println("=== TESTE REGEX v136 ===\n")
    
    // ========================================
    // TESTE 1: URLs COMPLETAS
    // ========================================
    println("📊 TESTE 1: URLs COMPLETAS")
    println("-".repeat(60))
    
    val urlsCompletas = listOf(
        "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt",
        "https://s6p9.fitnessessentials.cfd/v4/61/caojzl/index-f1-v1-a1.txt",
        "https://ssu5.wanderpeakevents.store/v4/ty/xeztph/cf-master.1767375808.txt",
        "https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/init-f1-v1-a1.woff",
        "https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/seg-1-f1-v1-a1.woff2"
    )
    
    urlsCompletas.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (match) "✅" else "❌"} $url")
    }
    
    println()
    
    // ========================================
    // TESTE 2: URLs PARCIAIS (Falta arquivo)
    // ========================================
    println("📊 TESTE 2: URLs PARCIAIS (Falta arquivo)")
    println("-".repeat(60))
    
    val urlsParciais1 = listOf(
        "https://spuc.alphastrahealth.store/v4/il/n3kh5r/",
        "https://s6p9.fitnessessentials.cfd/v4/61/caojzl/",
        "https://ssu5.wanderpeakevents.store/v4/ty/xeztph/"
    )
    
    urlsParciais1.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (match) "✅" else "❌"} $url")
    }
    
    println()
    
    // ========================================
    // TESTE 3: URLs PARCIAIS (Falta video ID)
    // ========================================
    println("📊 TESTE 3: URLs PARCIAIS (Falta video ID)")
    println("-".repeat(60))
    
    val urlsParciais2 = listOf(
        "https://spuc.alphastrahealth.store/v4/il/",
        "https://s6p9.fitnessessentials.cfd/v4/61/",
        "https://ssu5.wanderpeakevents.store/v4/ty/"
    )
    
    urlsParciais2.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (match) "✅" else "❌"} $url")
    }
    
    println()
    
    // ========================================
    // TESTE 4: URLs PARCIAIS (Só domínio)
    // ========================================
    println("📊 TESTE 4: URLs PARCIAIS (Só domínio)")
    println("-".repeat(60))
    
    val urlsParciais3 = listOf(
        "https://spuc.alphastrahealth.store/",
        "https://s6p9.fitnessessentials.cfd/",
        "https://ssu5.wanderpeakevents.store/"
    )
    
    urlsParciais3.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (match) "✅" else "❌"} $url")
    }
    
    println()
    
    // ========================================
    // TESTE 5: URL DENTRO DE TEXTO
    // ========================================
    println("📊 TESTE 5: URL DENTRO DE TEXTO")
    println("-".repeat(60))
    
    val textos = listOf(
        "Carregando vídeo: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt aguarde...",
        "URL encontrada: https://s6p9.fitnessessentials.cfd/v4/61/caojzl/index.txt",
        "Múltiplas URLs: https://ssu5.wanderpeakevents.store/v4/ty/xeztph/cf-master.txt e https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/init.woff"
    )
    
    textos.forEach { texto ->
        val match = regex.containsMatchIn(texto)
        println("${if (match) "✅" else "❌"} Texto contém URL válida")
        
        if (match) {
            val urls = regex.findAll(texto).map { it.value }.toList()
            urls.forEach { url ->
                println("   → $url")
            }
        }
    }
    
    println()
    
    // ========================================
    // TESTE 6: FORMATOS NOVOS (Hipotéticos)
    // ========================================
    println("📊 TESTE 6: FORMATOS NOVOS (Hipotéticos)")
    println("-".repeat(60))
    
    val urlsNovas = listOf(
        "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index-f3-v2-a1.txt",
        "https://s6p9.fitnessessentials.cfd/v4/61/caojzl/master-playlist.txt",
        "https://ssu5.wanderpeakevents.store/v4/ty/xeztph/video-data.woff2",
        "https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/novo-formato-2026.txt"
    )
    
    urlsNovas.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (match) "✅" else "❌"} $url")
    }
    
    println()
    
    // ========================================
    // TESTE 7: URLs INVÁLIDAS
    // ========================================
    println("📊 TESTE 7: URLs INVÁLIDAS (Não devem dar match)")
    println("-".repeat(60))
    
    val urlsInvalidas = listOf(
        "https://google.com/search",
        "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.mp4",
        "https://spuc.alphastrahealth.store/v3/il/n3kh5r/index.txt",
        "https://alphastrahealth.store/v4/il/n3kh5r/index.txt",
        "http://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"
    )
    
    urlsInvalidas.forEach { url ->
        val match = regex.containsMatchIn(url)
        println("${if (!match) "✅" else "❌"} $url (deve ser false)")
    }
    
    println()
    
    // ========================================
    // RESUMO
    // ========================================
    println("=".repeat(60))
    println("📊 RESUMO")
    println("=".repeat(60))
    println("✅ URLs completas: SIM, detecta")
    println("❌ URLs parciais: NÃO, não detecta")
    println("✅ URL em texto: SIM, detecta")
    println("✅ Formatos novos: SIM, detecta automaticamente")
    println("❌ URLs inválidas: NÃO, não detecta")
    println()
    println("🎯 CONCLUSÃO: Regex exige URL COMPLETA")
    println("   Mas WebView sempre captura URL completa, então OK!")
}
