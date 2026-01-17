package com.franciscoalro.maxseries.utils

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.lagradost.cloudstream3.app

/**
 * Utilitário para manipulação avançada de JSON (Jackson/Gson)
 * Sincronizado com os padrões do saimuelrepo-main
 */
object JsonHelper {
    val mapper = jacksonObjectMapper().apply {
        configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
    }

    /**
     * Converte uma resposta JSON que vem como Map (ex: {"0": {...}, "1": {...}}) 
     * em uma lista de objetos, padrão comum em APIs brasileiras (Vizer, MegaFlix)
     */
    inline fun <reified T> mapToList(json: String): List<T> {
        return try {
            val map = mapper.readValue<Map<String, T>>(json)
            map.values.toList()
        } catch (e: Exception) {
            try {
                // Tenta como lista direta se falhar o map
                mapper.readValue<List<T>>(json)
            } catch (e2: Exception) {
                emptyList()
            }
        }
    }

    /**
     * Faz um request e parseia o JSON de forma segura
     */
    suspend inline fun <reified T> safeFetch(url: String, headers: Map<String, String> = emptyMap()): T? {
        return try {
            val res = app.get(url, headers = headers).text
            mapper.readValue<T>(res)
        } catch (e: Exception) {
            null
        }
    }
}
