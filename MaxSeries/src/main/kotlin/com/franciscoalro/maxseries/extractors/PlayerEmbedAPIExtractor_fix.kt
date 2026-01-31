// Trecho de código para substituir na função getUrl
            val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
            // Usar ISO-8859-1 para preservar bytes 1:1 (não interpreta como UTF-8)
            val decodedString = String(decodedBytes, Charsets.ISO_8859_1)
            Log.d(TAG, "✅ JSON decodificado (ISO-8859-1): ${decodedString.take(200)}...")
            
            // Extrair campos simples (ASCII seguro)
            val userIdRegex = """"user_id"\s*:\s*(\d+)""".toRegex()
            val slugRegex = """"slug"\s*:\s*"([^"]+)"""".toRegex()
            val md5IdRegex = """"md5_id"\s*:\s*(\d+)""".toRegex()
            
            val userId = userIdRegex.find(decodedString)?.groupValues?.get(1)
            val slug = slugRegex.find(decodedString)?.groupValues?.get(1)
            val md5Id = md5IdRegex.find(decodedString)?.groupValues?.get(1)
            
            // Extrair media usando bytes raw (crítico para preservar dados binários)
            val mediaKey = "\"media\":\"".toByteArray(Charsets.ISO_8859_1)
            val mediaStartIdx = decodedBytes.indexOf(mediaKey)
            val mediaEncrypted = if (mediaStartIdx >= 0) {
                val start = mediaStartIdx + mediaKey.size
                var pos = start
                val result = java.io.ByteArrayOutputStream()
                while (pos < decodedBytes.size) {
                    val b = decodedBytes[pos]
                    if (b == 0x22) { // aspas "
                        break
                    } else if (b == 0x5C && pos + 1 < decodedBytes.size) { // backslash \
                        val next = decodedBytes[pos + 1].toInt()
                        when (next) {
                            0x22, 0x5C, 0x2F -> { result.write(next); pos += 2 } // ", \, /
                            0x62 -> { result.write(0x08); pos += 2 } // \b
                            0x66 -> { result.write(0x0C); pos += 2 } // \f
                            0x6E -> { result.write(0x0A); pos += 2 } // \n
                            0x72 -> { result.write(0x0D); pos += 2 } // \r
                            0x74 -> { result.write(0x09); pos += 2 } // \t
                            0x75 -> { // \uXXXX
                                if (pos + 5 < decodedBytes.size) {
                                    val hex = String(decodedBytes, pos + 2, 4, Charsets.ISO_8859_1)
                                    try {
                                        val code = hex.toInt(16)
                                        result.write(code and 0xFF)
                                    } catch (e: Exception) {
                                        result.write(0x5C); result.write(0x75)
                                    }
                                    pos += 6
                                } else {
                                    result.write(b.toInt()); pos++
                                }
                            }
                            else -> { result.write(next); pos += 2 }
                        }
                    } else {
                        result.write(b.toInt())
                        pos++
                    }
                }
                String(result.toByteArray(), Charsets.ISO_8859_1)
            } else null
            
            Log.d(TAG, "📋 Campos extraídos:")
            Log.d(TAG, "   - userId: $userId")
            Log.d(TAG, "   - slug: $slug")
            Log.d(TAG, "   - md5Id: $md5Id")
            Log.d(TAG, "   - media: ${mediaEncrypted?.length} chars")
            Log.d(TAG, "   - media first 20 bytes (hex): ${mediaEncrypted?.take(20)?.toByteArray(Charsets.ISO_8859_1)?.joinToString(" ") { "%02x".format(it) }}")
