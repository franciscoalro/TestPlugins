package com.franciscoalro.maxseries.utils

/**
 * Sistema de priorização de servidores de vídeo
 * Inspirado no padrão PobreFlix
 * 
 * Prioridades (menor = melhor):
 * 1. Streamtape (alta qualidade, confiável)
 * 2. Filemoon (boa qualidade)
 * 3. Doodstream (média qualidade)
 * 4. Mixdrop (baixa qualidade)
 * Int.MAX_VALUE. Desconhecidos (última opção)
 */
object ServerPriority {
    
    private val priorities = mapOf(
        // Alta prioridade (qualidade melhor, mais confiável)
        "streamtape" to 1,
        "filemoon" to 2,
        
        // Média prioridade
        "doodstream" to 3,
        "mixdrop" to 4,
        
        // Servidores adicionais
        "mediafire" to 5,
        "mega" to 6,
        "fembed" to 7,
        "voe" to 8,
        
        // Fallback para servidores desconhecidos
        "default" to Int.MAX_VALUE
    )
    
    /**
     * Obtém prioridade de um servidor
     * 
     * @param serverName Nome do servidor (case-insensitive)
     * @return Valor de prioridade (menor = melhor)
     */
    fun getPriority(serverName: String): Int {
        return priorities[serverName.lowercase()] ?: priorities["default"]!!
    }
    
    /**
     * Ordena lista de itens por prioridade de servidor
     * 
     * @param T Tipo genérico do item
     * @param items Lista de itens para ordenar
     * @param serverExtractor Função que extrai nome do servidor do item
     * @return Lista ordenada por prioridade (melhor primeiro)
     */
    fun <T> sortByPriority(
        items: List<T>,
        serverExtractor: (T) -> String
    ): List<T> {
        return items.sortedBy { getPriority(serverExtractor(it)) }
    }
    
    /**
     * Detecta nome do servidor a partir de URL
     * 
     * @param url URL do servidor
     * @return Nome do servidor detectado ou "unknown"
     */
    fun detectServer(url: String): String {
        val match = RegexPatterns.SERVER_TYPE.find(url.lowercase())
        return match?.value ?: "unknown"
    }
    
    /**
     * Verifica se servidor é de alta prioridade
     * 
     * @param serverName Nome do servidor
     * @return true se prioridade <= 2
     */
    fun isHighPriority(serverName: String): Boolean {
        return getPriority(serverName) <= 2
    }
    
    /**
     * Obtém todos os servidores ordenados por prioridade
     * 
     * @return Lista de nomes de servidores ordenados
     */
    fun getAllServersSorted(): List<String> {
        return priorities.entries
            .filter { it.key != "default" }
            .sortedBy { it.value }
            .map { it.key }
    }
}
