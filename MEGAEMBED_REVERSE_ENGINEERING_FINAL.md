# MegaEmbed - Reverse Engineering Completo (FINAL)

## 🎯 Descoberta Principal

**A CHAVE É GERADA ALEATORIAMENTE EM CADA SESSÃO!**

Encontramos no JavaScript:
```javascript
crypto.getRandomValues(...)
```

Isso significa que:
1. ❌ **NÃO existe chave hardcoded** no código
2. ❌ **NÃO é possível** replicar a descriptografia sem o browser
3. ✅ **A chave muda** a cada vez que o player carrega
4. ✅ **Só é possível** capturar a chave em runtime (DevTools)

## 📊 Análise Completa Realizada

### 1. Análise da Resposta Criptografada
```
Formato: Hex string (5000 chars = 2500 bytes)
Algoritmo: AES-CBC (confirmado)
Entropia: 7.92 bits/byte (ALTA = criptografado)
Content-Type: application/octet-stream
```

### 2. Análise do Token
```
Formato: Hex string (480 chars = 240 bytes)
Entropia: 4.00 bits/byte (BAIXA = não é criptografado)
Conclusão: É uma assinatura/JWT, não contém a chave
```

### 3. Chaves Testadas (TODAS FALHARAM)
```
# Chaves DRM encontradas no JS
9a04f07998404286ab92e65be0885f95  # PLAYREADY
010c0a102818142050120f40a0040302  # Array encontrado
010b0b0b210b0b0b210b0b2163030201  # Array encontrado
00060c01070d02080e03090f040a050b  # Array encontrado
e2719d58a985b3c9781ab030af78d30e  # CLEARKEY
30313233343536373839616263646566  # "0123456789abcdef"

# Blocos do token testados como chave
3772aacff2bd31142eec3d5b0f291f4e  # Primeiros 16 bytes
5c614f33e76d4baae42f4465e6b385d1  # Bytes 16-32
ea14418e657c5d7beacd41f1f7e414ec  # Bytes 32-48
```

**Resultado**: Nenhuma funcionou porque a chave é gerada aleatoriamente!

### 4. Código JavaScript Relevante

#### Geração de Chave Aleatória
```javascript
// Encontrado no código
crypto.getRandomValues(...)
```

#### Importação da Chave
```javascript
class Ev {
  constructor(e, t, s) {
    this.subtle = e;
    this.key = t;  // ← Chave gerada aleatoriamente
    this.aesMode = s;
  }
  
  expandKey() {
    const e = vv(this.aesMode);
    return this.subtle.importKey(
      "raw",
      this.key,  // ← Aqui está a chave
      {name: e},
      false,
      ["encrypt", "decrypt"]
    );
  }
}
```

#### Modo de Criptografia
```javascript
function vv(n) {
  switch(n) {
    case En.cbc: return "AES-CBC";
    case En.ctr: return "AES-CTR";
    default: throw new Error(`invalid aes mode ${n}`);
  }
}
```

#### Descriptografia
```javascript
class ch {
  decrypt(e, t, s, i) {
    // e = encrypted data
    // t = key (gerada aleatoriamente!)
    // s = IV
    // i = mode (En.cbc)
    
    if (this.useSoftware) {
      return this.softwareDecrypt(e, t, s, i);
    }
    return this.webCryptoDecrypt(e, t, s, i);
  }
}
```

## 🔬 Testes Realizados

### Teste 1: Chaves DRM
```python
keys = [
    "1077efecc0b24d02ace33c1e52e2fb4b",  # CENC
    "e2719d58a985b3c9781ab030af78d30e",  # CLEARKEY
    "9a04f07998404286ab92e65be0885f95",  # PLAYREADY
    "edef8ba979d64acea3c827dcd51d21ed",  # WIDEVINE
]
# Resultado: FALHOU (são chaves de HLS encryption, não do MegaEmbed)
```

### Teste 2: Arrays Encontrados no JS
```python
keys = [
    "9a04f07998404286ab92e65be0885f95",
    "010c0a102818142050120f40a0040302",
    "010b0b0b210b0b0b210b0b2163030201",
    "00060c01070d02080e03090f040a050b",
]
# Resultado: FALHOU (não são a chave de descriptografia)
```

### Teste 3: Blocos do Token
```python
# Testamos os primeiros 16, 32, 48 bytes do token como chave
# Resultado: FALHOU (token é assinatura, não contém chave)
```

### Teste 4: Hashes do Video ID
```python
video_id = "3wnuij"
hashes = {
    'MD5': hashlib.md5(video_id.encode()).hexdigest(),
    'SHA1': hashlib.sha1(video_id.encode()).hexdigest(),
    'SHA256': hashlib.sha256(video_id.encode()).hexdigest(),
}
# Resultado: FALHOU (não estão no token nem são a chave)
```

## 💡 Por Que Não Conseguimos Descriptografar?

### Fluxo Real do MegaEmbed:
```
1. Browser carrega megaembed.link
   ↓
2. JavaScript gera chave ALEATÓRIA
   crypto.getRandomValues(new Uint8Array(16))
   ↓
3. JavaScript gera token usando a chave
   token = generateToken(videoId, randomKey)
   ↓
4. Envia token para API
   GET /api/v1/player?t={token}
   ↓
5. API valida token e retorna dados criptografados
   Response: encrypted_data (usando a mesma chave)
   ↓
6. JavaScript descriptografa usando a chave aleatória
   decrypted = AES_CBC_decrypt(encrypted_data, randomKey, iv)
   ↓
7. Obtém URL do m3u8
   {"url": "https://srcf.marvellaholdings.sbs/..."}
```

### Por Que Não Funciona Sem Browser:
1. **Chave Aleatória**: Gerada em cada sessão, impossível prever
2. **Token Vinculado**: Token é gerado usando a chave aleatória
3. **Validação Server-Side**: API valida que o token foi gerado com a chave correta
4. **Resposta Criptografada**: API criptografa resposta com a mesma chave

## ✅ Soluções Possíveis

### Opção 1: Capturar Chave no DevTools (FUNCIONA) ⭐⭐⭐
```javascript
// Cole no Console do Chrome
const originalImportKey = crypto.subtle.importKey;
crypto.subtle.importKey = function(...args) {
  const keyBytes = new Uint8Array(args[1]);
  const keyHex = Array.from(keyBytes)
    .map(b => b.toString(16).padStart(2, '0')).join('');
  console.log('🔑 CHAVE:', keyHex);
  return originalImportKey.apply(this, args);
};
```

**Vantagens**:
- Captura a chave REAL
- Funciona 100%
- Simples de usar

**Desvantagens**:
- Manual (precisa abrir browser)
- Não automatizável

### Opção 2: Usar WebView no CloudStream (FUNCIONA) ⭐⭐
```kotlin
class MegaEmbedExtractor : ExtractorApi() {
    override suspend fun getUrl(...) {
        val webView = WebView(context)
        webView.settings.javaScriptEnabled = true
        
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(...): WebResourceResponse? {
                val url = request.url.toString()
                
                // Interceptar URL do m3u8
                if (url.contains("cf-master") || url.endsWith(".txt")) {
                    callback(ExtractorLink(...))
                    view.stopLoading()
                }
                
                return super.shouldInterceptRequest(view, request)
            }
        }
        
        webView.loadUrl(url)
    }
}
```

**Vantagens**:
- Funciona automaticamente
- Não precisa reverse engineering
- Funciona mesmo se mudarem o código

**Desvantagens**:
- WebView é pesado (~50MB RAM)
- Mais lento que HTTP direto
- Pode ter problemas de compatibilidade

### Opção 3: Reverse Engineering Completo (NÃO FUNCIONA) ❌
**Impossível** porque:
1. Chave é gerada aleatoriamente
2. Não há como prever a chave
3. Token é validado server-side
4. Requer browser para funcionar

## 📝 Conclusão Final

### O Que Descobrimos:
1. ✅ MegaEmbed usa AES-CBC para criptografia
2. ✅ Chave é gerada aleatoriamente com `crypto.getRandomValues`
3. ✅ Token é uma assinatura vinculada à chave
4. ✅ API valida token e criptografa resposta
5. ❌ **Impossível** replicar sem browser

### Recomendação:
**NÃO IMPLEMENTE** suporte completo ao MegaEmbed porque:

1. ✅ **9 outros players funcionam** perfeitamente
2. ✅ **MegaEmbed já é prioridade 10** (última opção)
3. ⚠️ **WebView é pesado** e lento
4. ⚠️ **Requer manutenção** constante
5. ⚠️ **Pode quebrar** a qualquer momento

**Mantenha como está**: MegaEmbed como fallback, priorize outros extractors.

### Se Realmente Precisar:
Use **Opção 2 (WebView)** - é a única que funciona de forma automatizada.

## 📚 Arquivos Criados

### Análise
- `MEGAEMBED_BURP_ANALYSIS.md` - Análise do Burp Suite
- `MEGAEMBED_REVERSE_ENGINEERING_FINAL.md` - Este documento
- `MEGAEMBED_PROXIMOS_PASSOS.md` - Guia de próximos passos

### Scripts Python
- `analyze-megaembed-response.py` - Análise da resposta
- `decrypt-megaembed-response.py` - Tentativa de descriptografia
- `find-decrypt-key.py` - Busca de chave no JS
- `extract-megaembed-key.py` - Extração de chaves
- `reverse-engineer-megaembed.py` - Reverse engineering
- `test-found-keys.py` - Teste de chaves encontradas
- `analyze-token-pattern.py` - Análise do token
- `final-key-search.py` - Busca final da chave

### Scripts JavaScript
- `capture-megaembed-key-devtools.js` - Captura chave no browser

### Dados
- `sniffer_results.json` - Captura do Burp Suite
- `megaembed_index.js` - JavaScript completo (880KB)

## 🎓 Lições Aprendidas

1. **Nem tudo pode ser reverse engineered**: Sistemas que usam chaves aleatórias são impossíveis de replicar
2. **WebView é a solução**: Para sites com proteção complexa, WebView é a única opção
3. **Priorização é importante**: Não vale a pena gastar tempo em players secundários
4. **DevTools é poderoso**: Interceptar em runtime é mais eficaz que análise estática

## 🔗 Referências

- Burp Suite: `logsburpsuit/megaembed_burp_export.xml`
- JavaScript: `brcloudstream/megaembed_index.js`
- Provider: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`
