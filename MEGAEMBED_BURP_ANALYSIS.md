# MegaEmbed - Análise Completa via Burp Suite

## 📋 Resumo Executivo

O MegaEmbed usa um sistema de proteção em **3 camadas**:

1. **Token Generation**: Gera token hex de ~512 caracteres no frontend
2. **API Request**: Envia token para `/api/v1/player?t={token}`
3. **Response Decryption**: Descriptografa resposta AES-CBC para obter URL do m3u8

## 🔍 Fluxo Capturado no Burp Suite

### Passo 1: Seleção do Episódio
```
GET https://playerthree.online/episodio/255703
```

### Passo 2: Carregamento do Player
```
GET https://megaembed.link/
```

### Passo 3: APIs Chamadas

#### 3.1 Info API
```
GET https://megaembed.link/api/v1/info?id=3wnuij
```

#### 3.2 Video API
```
GET https://megaembed.link/api/v1/video?id=3wnuij&w=2144&h=1206&r=playerthree.online
```

#### 3.3 Player API (CRÍTICO)
```
GET https://megaembed.link/api/v1/player?t=3772aacff2bd31142eec3d5b0f291f4e5c614f33e76d4baae42f4465e6b385d1ea14418e657c5d7beacd41f1f7e414eca8c394117736628d0f21694daff4796288f05473f4fba70a83086743f2ffbe2d587f2ba405121c77225e307eed04af4e5eaf92cf853d5e7e37a448bd8c08d931b1e59ed2a0aada05a95c56d6dfbd1fe6415081ea0383b7eff8fcfb4acbe138b27e0050f801c8dfed275b533e4f9e85c3338d0446949b7ee8f27e8aa1076f5c59ff5c0cfc0f3bb4e38135658b8c94fbd28e524bd703753d6261fe830e1c64d5872d6b6d75dd16df586f3e57e6618acab9b6801b7925f0bb44cf1d21e746c9904e

Headers:
  sec-ch-ua-platform: "Windows"
  user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  accept: */*
  sec-fetch-site: same-origin
  sec-fetch-mode: cors
  sec-fetch-dest: empty
  referer: https://megaembed.link/
  cookie: _ym_uid=1768054560916313740; _ym_d=1768054560; _ym_isad=2

Response:
  Status: 200 OK
  Content-Type: application/octet-stream
  Body: 933a30ecdabc15152bfbe068bc27d5342f59759c823e7e206be7a128ff897fc4... (5000 chars hex)
```

## 🔐 Análise da Criptografia

### Token (Request)
- **Formato**: Hex string
- **Tamanho**: ~512 caracteres (256 bytes)
- **Exemplo**: `3772aacff2bd31142eec3d5b0f291f4e5c614f33e76d4baae42f4465e6b385d1...`
- **Geração**: Desconhecida (JavaScript ofuscado)

### Resposta Criptografada
- **Formato**: Hex string
- **Tamanho**: 5000 caracteres (2500 bytes)
- **Algoritmo**: AES-CBC (confirmado no código JS)
- **Entropia**: 7.92 bits/byte (alta = criptografado)
- **Primeiros bytes**: `933a30ecdabc15152bfbe068bc27d5342f59759c...`

### Análise de Entropia
```python
import collections
import math

byte_freq = collections.Counter(encrypted_bytes)
entropy = -sum((count/len(encrypted_bytes)) * math.log2(count/len(encrypted_bytes)) 
               for count in byte_freq.values())

# Resultado: 7.92 bits/byte
# Interpretação: ALTA entropia = dados CRIPTOGRAFADOS
```

## 🧪 Testes Realizados

### ❌ Teste 1: Chaves DRM
Testamos as chaves encontradas no JavaScript (DRM keys):
```
1077efecc0b24d02ace33c1e52e2fb4b  # CENC
e2719d58a985b3c9781ab030af78d30e  # CLEARKEY
9a04f07998404286ab92e65be0885f95  # PLAYREADY
edef8ba979d64acea3c827dcd51d21ed  # WIDEVINE
```
**Resultado**: Todas falharam. Essas são chaves de HLS encryption, não do MegaEmbed.

### ❌ Teste 2: IVs Comuns
Testamos IVs padrão:
```
- Zero IV (16 bytes de 0x00)
- Padrão (0123456789abcdef)
- Primeiros 16 bytes da resposta
```
**Resultado**: Nenhum funcionou.

### ❌ Teste 3: Decompressão
Tentamos descomprimir como gzip/zlib:
```python
import gzip, zlib
gzip.decompress(encrypted_bytes)  # Falhou: Not a gzipped file
zlib.decompress(encrypted_bytes)  # Falhou: incorrect header check
```
**Resultado**: Não é compressão, é criptografia.

## 📝 Código JavaScript Relevante

### Geração do Token
```javascript
// Ofuscado no código
location.hash[g(600)](g(800))[1]

// Tradução:
// g(600) = "split"
// g(800) = "#"
// Resultado: location.hash.split('#')[1]
```

### Descriptografia AES-CBC
```javascript
class ch {
  constructor(e, {removePKCS7Padding: t = !0} = {}) {
    this.subtle = self.crypto.subtle || self.crypto.webkitSubtle;
    this.removePKCS7Padding = t;
  }
  
  async decrypt(e, t, s, i) {
    // e = encrypted data
    // t = key
    // s = IV
    // i = mode (En.cbc or En.ctr)
    
    if (this.useSoftware) {
      return this.softwareDecrypt(e, t, s, i);
    }
    return this.webCryptoDecrypt(e, t, s, i);
  }
  
  webCryptoDecrypt(e, t, s, i) {
    const cipher = new xv(this.subtle, new Uint8Array(s), i);
    return cipher.decrypt(e.buffer, fastAesKey);
  }
}

function vv(n) {
  switch(n) {
    case En.cbc: return "AES-CBC";
    case En.ctr: return "AES-CTR";
    default: throw new Error(`invalid aes mode ${n}`);
  }
}
```

### Import Key
```javascript
crypto.subtle.importKey(
  "raw",
  this.key,
  {name: "AES-CBC"},
  false,
  ["encrypt", "decrypt"]
)
```

## 🎯 Próximos Passos

### Opção 1: Capturar Chave no Browser (RECOMENDADO)
Use DevTools para interceptar a chave:

```javascript
// No Console do Chrome/Firefox
const originalImportKey = crypto.subtle.importKey;
crypto.subtle.importKey = function(...args) {
  console.log('🔑 CHAVE CAPTURADA:', args[1]);
  console.log('   Hex:', Array.from(new Uint8Array(args[1]))
    .map(b => b.toString(16).padStart(2, '0')).join(''));
  return originalImportKey.apply(this, args);
};

// Depois recarregue a página do MegaEmbed
```

### Opção 2: Reverse Engineering do Token
Analise o JavaScript minificado para descobrir o algoritmo:

```bash
# Beautify o JS
npx js-beautify megaembed_index.js > megaembed_readable.js

# Procurar função de geração de token
grep -A 50 "player.*token" megaembed_readable.js
grep -A 50 "location.hash" megaembed_readable.js
```

### Opção 3: Usar WebView no CloudStream (MAIS FÁCIL)
Implemente um extractor que usa WebView:

```kotlin
// MegaEmbedExtractor.kt
suspend fun extract(url: String): List<ExtractorLink> {
    return suspendCoroutine { continuation ->
        val webView = WebView(context)
        webView.settings.javaScriptEnabled = true
        
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val url = request.url.toString()
                
                // Interceptar resposta da API player
                if (url.contains("/api/v1/player")) {
                    // Deixar o JavaScript descriptografar
                    // Depois interceptar a URL do m3u8
                }
                
                // Interceptar URL do m3u8
                if (url.endsWith(".txt") || url.contains("cf-master")) {
                    val m3u8Url = url
                    continuation.resume(listOf(
                        ExtractorLink(
                            "MegaEmbed",
                            "MegaEmbed",
                            m3u8Url,
                            "",
                            Qualities.Unknown.value,
                            INFER_TYPE
                        )
                    ))
                }
                
                return super.shouldInterceptRequest(view, request)
            }
        }
        
        webView.loadUrl(url)
    }
}
```

## 💡 Recomendação Final

**NÃO VALE A PENA** fazer reverse engineering completo do MegaEmbed porque:

1. ✅ **Outros 9 players funcionam** perfeitamente no MaxSeries
2. ⚠️ **WebView é pesado** e lento
3. ⚠️ **Token muda frequentemente** (manutenção constante)
4. ⚠️ **Pode quebrar** a qualquer momento
5. ✅ **MegaEmbed já é prioridade 10** (última opção)

**Mantenha MegaEmbed como fallback** e priorize os players que retornam MP4/HLS direto:
- PlayerEmbedAPI (prioridade 1)
- MyVidPlay (prioridade 2)
- StreamTape (prioridade 3)
- Doodstream (prioridade 4)
- etc.

## 📚 Arquivos Criados

### Scripts de Análise
- `analyze-megaembed-response.py` - Analisa a resposta criptografada
- `find-decrypt-key.py` - Procura a chave no JavaScript
- `extract-megaembed-key.py` - Extrai chaves hardcoded
- `decrypt-megaembed-response.py` - Tenta descriptografar

### Dados Capturados
- `sniffer_results.json` - Captura completa do Burp Suite
- `megaembed_index.js` - JavaScript completo (880KB)

### Documentação
- `MEGAEMBED_SOLUTION.md` - Solução completa
- `MEGAEMBED_BURP_ANALYSIS.md` - Este documento

## 🔗 Referências

- Burp Suite: `logsburpsuit/megaembed_burp_export.xml`
- JavaScript: `brcloudstream/megaembed_index.js`
- Provider: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`
