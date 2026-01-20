# Guia de Teste com Postman - v127

## 📅 Data: 18/01/2026 - 21:20

## 🎯 Objetivo

Usar Postman para:
1. Testar APIs diretamente (sem WebView)
2. Capturar headers e cookies necessários
3. Entender fluxo de descriptografia
4. Validar solução antes de implementar

---

## 🧪 TESTE 1: PlayerEmbedAPI (Já Funcionou)

### Request 1: Get Episode Page
```
GET https://playerthree.online/episodio/255703
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

**Resultado Esperado**:
- Status: 200 OK
- Body contém: `https://playerembedapi.link/?v=kBJLtxCD3`

---

### Request 2: Get Player Embed API
```
GET https://playerembedapi.link/?v=kBJLtxCD3
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://playerthree.online/
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

**Resultado Esperado**:
- Status: 200 OK
- Body contém HTML com JavaScript
- Procurar por: `sssrr.org`, `htm4jbxon18`, ou URLs de vídeo

**O que procurar no HTML**:
```html
<!-- Procurar por: -->
<script>
  // Variáveis globais
  var videoUrl = "...";
  var playerConfig = {...};
  
  // Ou chamadas fetch/XMLHttpRequest
  fetch("https://htm4jbxon18.sssrr.org/...")
</script>
```

---

### Request 3: Get Video Metadata (SE encontrar no HTML)
```
GET https://htm4jbxon18.sssrr.org/?timestamp=&id=qx5haz5c0wg
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://playerembedapi.link/
Origin: https://playerembedapi.link
Accept: */*
```

**Resultado Esperado**:
- Status: 200 OK
- Body: URL do vídeo ou JSON com metadata

---

### Request 4: Get Video Stream
```
GET https://htm4jbxon18.sssrr.org/sora/651198119/{token}
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://playerembedapi.link/
Origin: https://playerembedapi.link
Accept: */*
```

**Resultado Esperado**:
- Status: 200 OK
- Body: Vídeo ou playlist M3U8

---

## 🧪 TESTE 2: MegaEmbed (API Criptografada)

### Request 1: Get MegaEmbed Page
```
GET https://megaembed.link/#3wnuij
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://playerthree.online/
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

**Resultado Esperado**:
- Status: 200 OK
- Body: HTML com JavaScript
- Procurar por: `/api/v1/info?id=`

---

### Request 2: Get Video Info API (CRIPTOGRAFADA)
```
GET https://megaembed.link/api/v1/info?id=3wnuij
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Referer: https://megaembed.link/
Origin: https://megaembed.link
Accept: application/json, text/plain, */*
```

**Resultado Esperado**:
- Status: 200 OK
- Body: **HEX STRING CRIPTOGRAFADA**
```
3553d5e3eaa72fcf2ad4c568effbb8c345554ba6c5f94ff72cf4676611b9615ab0c1484c699efafb4e75248fc92abc386e3a312b1b0fec002fcbee3f3559a7c9f2f21b962e815f65d268b0e0aca7afaddffbb9bc06cf04f5533b35c43825616e0e5459e9...
```

**⚠️ PROBLEMA**: Resposta está criptografada!

---

## 🔍 TESTE 3: Analisar JavaScript no Postman

### Passo 1: Capturar HTML do MegaEmbed
```
GET https://megaembed.link/#3wnuij
```

Salvar resposta como `megaembed_page.html`

---

### Passo 2: Procurar por Scripts
No HTML, procurar por:
```html
<script src="/assets/index-CZ_ja_1t.js"></script>
<script src="/assets/prod-cvEtvBo1.js"></script>
```

---

### Passo 3: Baixar Scripts
```
GET https://megaembed.link/assets/index-CZ_ja_1t.js
GET https://megaembed.link/assets/prod-cvEtvBo1.js
```

Salvar e analisar:
- Procurar por: `decrypt`, `crypto.subtle`, `AES`, `CryptoJS`
- Procurar por: chaves, IVs, algoritmos

---

## 🧪 TESTE 4: Usar Browser DevTools (Alternativa)

Se Postman não conseguir descriptografar, usar DevTools:

### Passo 1: Abrir MegaEmbed no Chrome
```
https://megaembed.link/#3wnuij
```

---

### Passo 2: Abrir DevTools (F12)
- Ir em **Console**
- Colar script de interceptação:

```javascript
// Interceptar crypto.subtle.decrypt
const originalDecrypt = crypto.subtle.decrypt;
crypto.subtle.decrypt = function(...args) {
    console.log('🔓 decrypt() chamado');
    console.log('   Algorithm:', args[0]);
    console.log('   Key:', args[1]);
    console.log('   Data:', args[2]);
    
    return originalDecrypt.apply(this, args).then(result => {
        const text = new TextDecoder().decode(result);
        console.log('✅ Descriptografado:', text);
        
        try {
            const json = JSON.parse(text);
            console.log('📦 JSON:', json);
            
            if (json.url || json.file || json.source) {
                console.log('🎯 URL DO VÍDEO:', json.url || json.file || json.source);
            }
        } catch(e) {}
        
        return result;
    });
};

console.log('✅ Interceptação ativada! Recarregue a página.');
```

---

### Passo 3: Recarregar Página
- Pressionar **F5**
- Observar console
- Copiar URL do vídeo quando aparecer

---

### Passo 4: Testar URL no VLC
```
vlc "https://.../.txt"
```

Se reproduzir, a URL está correta!

---

## 📊 RESULTADOS ESPERADOS

### PlayerEmbedAPI
| Request | Status | Body | Próximo Passo |
|---------|--------|------|---------------|
| Episode Page | 200 | HTML com `playerembedapi.link` | ✅ Extrair URL |
| Player Embed | 200 | HTML com JavaScript | 🔍 Procurar sssrr.org |
| Video Metadata | 200 | URL ou JSON | ✅ Usar URL |
| Video Stream | 200 | Vídeo/M3U8 | ✅ Funciona! |

### MegaEmbed
| Request | Status | Body | Próximo Passo |
|---------|--------|------|---------------|
| MegaEmbed Page | 200 | HTML | ✅ OK |
| Video Info API | 200 | **HEX CRIPTOGRAFADA** | ❌ Precisa descriptografar |

---

## 🎯 CONCLUSÕES DO TESTE

### Se PlayerEmbedAPI funcionar no Postman:
1. ✅ Problema é no WebView
2. ✅ Solução: Melhorar interceptação no WebView
3. ✅ Ou usar requests HTTP diretos (sem WebView)

### Se MegaEmbed retornar HEX:
1. ❌ API está criptografada
2. ✅ Usar DevTools para interceptar descriptografia
3. ✅ Copiar URL descriptografada
4. ✅ Implementar interceptação no WebView

---

## 🚀 PRÓXIMOS PASSOS

### Opção A: PlayerEmbedAPI Funciona no Postman
```kotlin
// v127: Usar requests HTTP diretos
// Sem WebView, mais rápido e confiável
suspend fun extractPlayerEmbedAPI(url: String): String? {
    val html = app.get(url).text
    // Extrair sssrr.org do HTML
    val cdnUrl = Regex("""https://[^"'\s]+\.sssrr\.org[^"'\s]+""").find(html)?.value
    return cdnUrl
}
```

### Opção B: MegaEmbed Precisa Interceptação
```kotlin
// v127: Interceptar crypto.subtle.decrypt no WebView
// Capturar resultado descriptografado
// Extrair URL do vídeo
```

---

## 📝 TEMPLATE POSTMAN COLLECTION

```json
{
  "info": {
    "name": "MaxSeries v127 - Test Collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "PlayerEmbedAPI Flow",
      "item": [
        {
          "name": "1. Get Episode Page",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "User-Agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              }
            ],
            "url": {
              "raw": "https://playerthree.online/episodio/255703",
              "protocol": "https",
              "host": ["playerthree", "online"],
              "path": ["episodio", "255703"]
            }
          }
        },
        {
          "name": "2. Get Player Embed API",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "User-Agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              },
              {
                "key": "Referer",
                "value": "https://playerthree.online/"
              }
            ],
            "url": {
              "raw": "https://playerembedapi.link/?v=kBJLtxCD3",
              "protocol": "https",
              "host": ["playerembedapi", "link"],
              "query": [
                {
                  "key": "v",
                  "value": "kBJLtxCD3"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "name": "MegaEmbed Flow",
      "item": [
        {
          "name": "1. Get MegaEmbed Page",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "User-Agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              }
            ],
            "url": {
              "raw": "https://megaembed.link/#3wnuij",
              "protocol": "https",
              "host": ["megaembed", "link"],
              "hash": "3wnuij"
            }
          }
        },
        {
          "name": "2. Get Video Info API (Encrypted)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "User-Agent",
                "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              },
              {
                "key": "Referer",
                "value": "https://megaembed.link/"
              },
              {
                "key": "Origin",
                "value": "https://megaembed.link"
              }
            ],
            "url": {
              "raw": "https://megaembed.link/api/v1/info?id=3wnuij",
              "protocol": "https",
              "host": ["megaembed", "link"],
              "path": ["api", "v1", "info"],
              "query": [
                {
                  "key": "id",
                  "value": "3wnuij"
                }
              ]
            }
          }
        }
      ]
    }
  ]
}
```

---

## 🎯 AÇÃO IMEDIATA

1. **Testar PlayerEmbedAPI no Postman**:
   - Se funcionar → Implementar sem WebView
   - Se falhar → Usar interceptação

2. **Testar MegaEmbed no DevTools**:
   - Interceptar `crypto.subtle.decrypt()`
   - Copiar URL descriptografada
   - Validar no VLC

3. **Implementar v127** baseado nos resultados

---

**Quer que eu crie a collection do Postman para você importar?**  
Ou prefere que eu implemente direto a v127 com interceptação?
