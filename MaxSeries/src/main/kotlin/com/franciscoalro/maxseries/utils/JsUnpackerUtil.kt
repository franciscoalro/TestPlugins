package com.franciscoalro.maxseries.utils

import android.util.Log

/**
 * Utilitário para descompactar scripts JavaScript compactados com Dean Edwards Packer
 * (eval(function(p,a,c,k,e,d)...))
 */
object JsUnpackerUtil {
    private const val TAG = "JsUnpackerUtil"

    fun unpack(packedJs: String): String? {
        return try {
            val match = Regex("""eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*r\s*\)\s*\{.+?\}\s*\(\s*(.+)\s*\)\s*\)\s*;?""", RegexOption.DOT_MATCHES_ALL)
                .find(packedJs) ?: Regex("""eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{.+?\}\s*\(\s*(.+)\s*\)\s*\)\s*;?""", RegexOption.DOT_MATCHES_ALL)
                .find(packedJs) ?: return null

            val pRaw = match.groupValues[1]
            
            // Extrair os argumentos p, a, c, k, e, r/d
            val jsArgs = pRaw.split(",").map { it.trim() }
            if (jsArgs.size < 4) return null

            val p = jsArgs[0].trim('\'', '"')
            val a = jsArgs[1].toIntOrNull() ?: 62
            val c = jsArgs[2].toIntOrNull() ?: 0
            val k = jsArgs[3].split(".split")[0].trim('\'', '"').split("|")

            unPack(p, a, c, k)
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao descompactar script", e)
            null
        }
    }

    private fun unPack(p: String, a: Int, c: Int, k: List<String>): String {
        var result = p
        for (i in c - 1 downTo 0) {
            if (i < k.size && k[i].isNotEmpty()) {
                val regex = Regex("\\b${i.toString(a)}\\b")
                result = regex.replace(result, k[i])
            }
        }
        return result
    }
}
