# 🔧 Guia Prático de Implementação - BRCloudstream Plugin

**Data**: 2026-02-09  
**Status**: Pronto para implementação após validação

---

## 🎯 Objetivo

Implementar a decriptação do PlayerEmbedAPI no plugin BRCloudstream usando a fórmula descoberta.

---

## ✅ Pré-requisitos

1. **Validar a fórmula** usando `SOLUCAO_FINAL.md` (5 minutos)
2. **Capturar o algoritmo exato** dos logs do DevTools
3. **Documentar os parâmetros** de decriptação

---

## 📊 Fórmula Descoberta

```kotlin
// Fórmula da chave AES
val key = "$userId:$slug:$md5Id"

// Exemplo
val key = "482120:kBJLtxCD3:28930647"
```

---

## 🔧 Implementação em Kotlin (Android)

### 1. Estrutura de Dados

```kotlin
data class PlayerEmbedData(
    val userId: String,
    val slug: String,
    val md5Id: String,
    val media: String  // Dados criptografados em base64
)

data class VideoSource(
    val url: String,
    val quality: String,
    val type: String = "hls"
)

data class DecryptedMedia(
    val title: String,
    val sources: List<VideoSource>,
    val subtitles: List<Subtitle>? = null,
    val thumbnail: String? = null
)
```

### 2. Função de Extração de Dados

```kotlin
suspend fun extractPlayerEmbedData(slug: String): PlayerEmbedData? {
    return try {
        // URL do player
        val url = "https://playerembedapi.link/?v=$slug"
        
        // Fazer requisição
        val response = app.get(url).text
        
        // Extrair dados base64 do HTML
        val dataRegex = """const datas = "([^"]+)";""".toRegex()
        val match = dataRegex.find(response) ?: return null
        val base64Data = match.groupValues[1]
        
        // Decodificar base64
        val jsonData = String(Base64.decode(base64Data, Base64.DEFAULT))
        val data = parseJson<PlayerEmbedData>(jsonData)
        
        data
    } catch (e: Exception) {
        Log.e("PlayerEmbed", "Erro ao extrair dados", e)
        null
    }
}
```

### 3. Função de Decriptação

```kotlin
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import javax.crypto.spec.IvParameterSpec
import java.security.MessageDigest

suspend fun decryptPlayerEmbedMedia(data: PlayerEmbedData): DecryptedMedia? {
    return try {
        // Gerar chave
        val key = "${data.userId}:${data.slug}:${data.md5Id}"
        
        // TODO: Implementar baseado no algoritmo capturado
        // Você verá o algoritmo exato nos logs do DevTools
        
        // Exemplo (ajustar conforme necessário):
        val decrypted = decryptAES(data.media, key)
        
        // Parsear JSON decriptado
        parseJson<DecryptedMedia>(decrypted)
    } catch (e: Exception) {
        Log.e("PlayerEmbed", "Erro ao decriptar", e)
        null
    }
}

private fun decryptAES(encryptedData: String, key: String): String {
    // TODO: Implementar baseado no algoritmo capturado
    // Algoritmo provável: AES-CTR ou AES-CBC
    
    // Exemplo genérico (AJUSTAR CONFORME NECESSÁRIO):
    val keyBytes = key.toByteArray()
    val md5Key = MessageDigest.getInstance("MD5").digest(keyBytes)
    
    val cipher = Cipher.getInstance("AES/CTR/NoPadding")
    val secretKey = SecretKeySpec(md5Key, "AES")
    
    // IV pode ser derivado da chave ou ser fixo
    val iv = IvParameterSpec(md5Key.copyOf(16))
    
    cipher.init(Cipher.DECRYPT_MODE, secretKey, iv)
    
    val encryptedBytes = Base64.decode(encryptedData, Base64.DEFAULT)
    val decryptedBytes = cipher.doFinal(encryptedBytes)
    
    return String(decryptedBytes, Charsets.UTF_8)
}
```

### 4. Integração no Provider

```kotlin
class PlayerEmbedProvider : MainAPI() {
    override var name = "PlayerEmbed"
    override var mainUrl = "https://playerembedapi.link"
    override val hasQuickSearch = false
    override val hasMainPage = false
    
    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // data contém o slug do vídeo
        val slug = data
        
        // Extrair dados
        val embedData = extractPlayerEmbedData(slug) ?: return false
        
        // Decriptar
        val decryptedMedia = decryptPlayerEmbedMedia(embedData) ?: return false
        
        // Adicionar sources
        decryptedMedia.sources.forEach { source ->
            callback.invoke(
                ExtractorLink(
                    name = name,
                    source = name,
                    url = source.url,
                    referer = mainUrl,
                    quality = getQualityFromString(source.quality),
                    isM3u8 = source.type == "hls"
                )
            )
        }
        
        // Adicionar legendas se houver
        decryptedMedia.subtitles?.forEach { subtitle ->
            subtitleCallback.invoke(
                SubtitleFile(
                    lang = subtitle.lang,
                    url = subtitle.url
                )
            )
        }
        
        return true
    }
}
```

---

## 🔧 Implementação em JavaScript (Node.js)

### 1. Extração de Dados

```javascript
const axios = require('axios');
const crypto = require('crypto');

async function extractPlayerEmbedData(slug) {
    try {
        const url = `https://playerembedapi.link/?v=${slug}`;
        const response = await axios.get(url);
        
        // Extrair dados base64
        const match = response.data.match(/const datas = "([^"]+)";/);
        if (!match) return null;
        
        const base64Data = match[1];
        const jsonData = Buffer.from(base64Data, 'base64').toString('utf-8');
        const data = JSON.parse(jsonData);
        
        return data;
    } catch (error) {
        console.error('Erro ao extrair dados:', error);
        return null;
    }
}
```

### 2. Decriptação

```javascript
const CryptoJS = require('crypto-js');

function decryptPlayerEmbedMedia(data) {
    try {
        // Gerar chave
        const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
        
        // TODO: Implementar baseado no algoritmo capturado
        // Exemplo (ajustar conforme necessário):
        const decrypted = CryptoJS.AES.decrypt(data.media, key);
        const decryptedText = decrypted.toString(CryptoJS.enc.Utf8);
        
        return JSON.parse(decryptedText);
    } catch (error) {
        console.error('Erro ao decriptar:', error);
        return null;
    }
}
```

### 3. Uso Completo

```javascript
async function getVideoSources(slug) {
    // Extrair dados
    const embedData = await extractPlayerEmbedData(slug);
    if (!embedData) {
        console.error('Falha ao extrair dados');
        return null;
    }
    
    console.log('Dados extraídos:', {
        user_id: embedData.user_id,
        slug: embedData.slug,
        md5_id: embedData.md5_id
    });
    
    // Decriptar
    const decryptedMedia = decryptPlayerEmbedMedia(embedData);
    if (!decryptedMedia) {
        console.error('Falha ao decriptar');
        return null;
    }
    
    console.log('Dados decriptados:', decryptedMedia);
    return decryptedMedia;
}

// Uso
getVideoSources('kBJLtxCD3').then(sources => {
    if (sources) {
        console.log('Sources:', sources.sources);
    }
});
```

---

## 🧪 Testes

### 1. Teste Unitário (Kotlin)

```kotlin
@Test
fun testKeyGeneration() {
    val userId = "482120"
    val slug = "kBJLtxCD3"
    val md5Id = "28930647"
    
    val key = "$userId:$slug:$md5Id"
    
    assertEquals("482120:kBJLtxCD3:28930647", key)
}

@Test
suspend fun testExtraction() {
    val data = extractPlayerEmbedData("kBJLtxCD3")
    
    assertNotNull(data)
    assertEquals("482120", data?.userId)
    assertEquals("kBJLtxCD3", data?.slug)
    assertEquals("28930647", data?.md5Id)
}
```

### 2. Teste de Integração

```kotlin
@Test
suspend fun testFullFlow() {
    val slug = "kBJLtxCD3"
    
    // Extrair
    val embedData = extractPlayerEmbedData(slug)
    assertNotNull(embedData)
    
    // Decriptar
    val decryptedMedia = decryptPlayerEmbedMedia(embedData!!)
    assertNotNull(decryptedMedia)
    
    // Verificar sources
    assertTrue(decryptedMedia!!.sources.isNotEmpty())
    
    // Verificar URL
    val firstSource = decryptedMedia.sources.first()
    assertTrue(firstSource.url.startsWith("http"))
}
```

---

## 📝 Checklist de Implementação

- [ ] Validar fórmula com `SOLUCAO_FINAL.md`
- [ ] Capturar algoritmo exato dos logs
- [ ] Documentar parâmetros de decriptação
- [ ] Implementar extração de dados
- [ ] Implementar função de decriptação
- [ ] Testar com vídeo de exemplo
- [ ] Testar com múltiplos vídeos
- [ ] Adicionar tratamento de erros
- [ ] Adicionar logs de debug
- [ ] Criar testes unitários
- [ ] Integrar no provider principal
- [ ] Testar no app completo
- [ ] Documentar código
- [ ] Fazer commit

---

## 🐛 Troubleshooting

### Problema: Extração falha

**Solução**:
- Verificar se a URL está correta
- Verificar se o regex está capturando o base64
- Adicionar logs para debug

### Problema: Decriptação falha

**Solução**:
- Verificar se a chave está sendo gerada corretamente
- Confirmar o algoritmo usado (AES-CTR, AES-CBC, etc.)
- Verificar se o IV está correto
- Usar os logs do DevTools como referência

### Problema: JSON inválido após decriptação

**Solução**:
- Verificar se a decriptação está completa
- Verificar encoding (UTF-8)
- Verificar se há padding incorreto

---

## 💡 Dicas

1. **Use os logs do DevTools** como referência para o algoritmo exato
2. **Teste com múltiplos vídeos** para garantir que funciona em todos os casos
3. **Adicione cache** para evitar requisições desnecessárias
4. **Implemente retry** para requisições que falham
5. **Adicione timeout** para evitar travamentos

---

## 📚 Recursos

### Bibliotecas Úteis

**Kotlin/Android**:
- `javax.crypto` - Criptografia nativa
- `org.bouncycastle` - Biblioteca de criptografia avançada

**JavaScript/Node.js**:
- `crypto-js` - Criptografia JavaScript
- `node-forge` - Biblioteca de criptografia completa

### Documentação

- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [Java Cryptography](https://docs.oracle.com/javase/8/docs/technotes/guides/security/crypto/CryptoSpec.html)
- [CryptoJS Documentation](https://cryptojs.gitbook.io/docs/)

---

## 🎯 Próximos Passos

1. **Validar** a fórmula usando `SOLUCAO_FINAL.md`
2. **Capturar** o algoritmo exato dos logs
3. **Implementar** a função de decriptação
4. **Testar** com vídeos reais
5. **Integrar** no plugin BRCloudstream
6. **Publicar** atualização

---

**Última atualização**: 2026-02-09  
**Status**: Pronto para implementação  
**Pré-requisito**: Validar com `SOLUCAO_FINAL.md`

---

**🚀 Boa sorte com a implementação!**
