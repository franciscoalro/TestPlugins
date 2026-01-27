# 🔍 Network Logs Analysis

**Data:** 27 Janeiro 2026  
**Source:** Firefox DevTools / Burp Suite  
**URL Testada:** `https://viewplayer.online/filme/tt39376546`

---

## 📊 REQUISIÇÕES IDENTIFICADAS

### 1. ViewPlayer (Principal)
```
GET https://viewplayer.online/filme/tt39376546
Status: 200
Size: 7740 bytes
Type: HTML
Title: "Caju, Meu Amigo"
```

**Análise:**
- Página principal do player
- Contém título do filme
- HTML com ~7.7KB

---

### 2. PlayerEmbedAPI
```
GET https://playerembedapi.link/sw.import.js
Status: 304 (Not Modified)
Type: script/js
```

**Análise:**
- Service Worker do PlayerEmbedAPI
- Carregado 3 vezes (cache)
- Usado para interceptar requests

**Outros arquivos:**
- `https://iamcdn.net/player-v2/core.bundle.js`
- `https://iamcdn.net/player-v2/sw.bundle.js`

---

### 3. sssrr.org (CDN de Vídeo)

#### Request 1:
```
GET https://cqndlnxcq36.sssrr.org/sora/1484112938/Yk00Qzk4Um5ySStjMXZVQ2pUcUFCdk8vaHNYNTZOSG5aV05SekZZUFhHclhkaDErRjIw
Status: 302 (Redirect)
Size: 712 bytes
Type: text
```

#### Request 2:
```
GET https://m0iidt1rp0.sssrr.org/sora/1285590959/aWpUTndHaVlTZmpDMDIwWHpLcXZjdklFc0dWKy85dEpndko2NXd5eElaWm5GaG91T21r
Status: 302 (Redirect)
Size: 678 bytes
Type: text
```

**Análise:**
- Subdomínios aleatórios: `cqndlnxcq36`, `m0iidt1rp0`
- Path: `/sora/{id}/{base64_token}`
- Retorna 302 redirect
- Provavelmente redireciona para CloudFlare tunnel

---

### 4. CloudFlare Tunnels

#### Tunnel 1:
```
GET https://elementary-recipients-numerical-transactions.trycloudflare.com/sora/1484112938/Yk00Qzk4Um5ySStjMXZVQ2pUcUFCdk8vaHNYNTZOSG5aV05SekZZUFhHclhkaDErRjIw
Status: 0 (Timeout/Failed)
```

#### Tunnel 2:
```
GET https://calvin-convert-guidelines-confidentiality.trycloudflare.com/sora/1484112938/Yk00Qzk4Um5ySStjMXZVQ2pUcUFCdk8vaHNYNTZOSG5aV05SekZZUFhHclhkaDErRjIw
Status: 0 (Timeout/Failed)
```

**Análise:**
- Nomes aleatórios de tunnel
- Mesmo path que sssrr.org
- Requests falharam (timeout)
- Provavelmente bloqueados ou expirados

---

### 5. JWPlayer
```
GET https://ssl.p.jwpcdn.com/player/v/8.34.3/jwplayer.stats.js
Status: 200
Size: 503708 bytes
Type: script/js
```

**Análise:**
- JWPlayer versão 8.34.3
- Player de vídeo usado
- Stats module para analytics

---

### 6. WebSocket
```
GET https://wss.morphify.net/
Status: 101 (Switching Protocols)
Type: WebSocket
```

**Análise:**
- WebSocket connection
- Provavelmente para analytics ou ads

---

### 7. Imagens Bloqueadas
```
GET https://img.freeimagecdn.net/image/NUHegbGwJ.jpg
Status: 403 (Forbidden)
Size: 5257 bytes
Type: HTML
Title: "Attention Required! | Cloudflare"
```

**Análise:**
- Imagens bloqueadas por CloudFlare
- Provavelmente overlays de propaganda

---

## 🎯 FLUXO DE EXTRAÇÃO

### Passo 1: Carregar ViewPlayer
```
GET https://viewplayer.online/filme/tt39376546
→ HTML com player embeddado
```

### Passo 2: Carregar PlayerEmbedAPI
```
GET https://playerembedapi.link/sw.import.js
GET https://iamcdn.net/player-v2/core.bundle.js
→ Service Worker + Core bundle
```

### Passo 3: Buscar URL de Vídeo
```
GET https://cqndlnxcq36.sssrr.org/sora/1484112938/{token}
→ 302 Redirect
→ https://elementary-recipients-numerical-transactions.trycloudflare.com/sora/...
→ Timeout/Failed
```

### Passo 4: Retry com Outro Tunnel
```
GET https://cqndlnxcq36.sssrr.org/sora/1484112938/{token}
→ 302 Redirect
→ https://calvin-convert-guidelines-confidentiality.trycloudflare.com/sora/...
→ Timeout/Failed
```

---

## 🔑 PADRÕES IDENTIFICADOS

### 1. sssrr.org URL Pattern
```
https://{random_subdomain}.sssrr.org/sora/{id}/{base64_token}
```

**Exemplos:**
- `cqndlnxcq36.sssrr.org`
- `m0iidt1rp0.sssrr.org`

**Token Base64:**
- `Yk00Qzk4Um5ySStjMXZVQ2pUcUFCdk8vaHNYNTZOSG5aV05SekZZUFhHclhkaDErRjIw`
- `aWpUTndHaVlTZmpDMDIwWHpLcXZjdklFc0dWKy85dEpndko2NXd5eElaWm5GaG91T21r`

### 2. CloudFlare Tunnel Pattern
```
https://{random-words-separated-by-dashes}.trycloudflare.com/sora/{id}/{base64_token}
```

**Exemplos:**
- `elementary-recipients-numerical-transactions.trycloudflare.com`
- `calvin-convert-guidelines-confidentiality.trycloudflare.com`

### 3. PlayerEmbedAPI Pattern
```
https://playerembedapi.link/sw.import.js
https://iamcdn.net/player-v2/core.bundle.js
https://iamcdn.net/player-v2/sw.bundle.js
```

---

## 💡 ESTRATÉGIA DE EXTRAÇÃO

### Método 1: Extrair do HTML
1. Buscar `data-source` attributes
2. Buscar URLs sssrr.org no HTML
3. Buscar URLs CloudFlare no HTML
4. Buscar iframes

### Método 2: Seguir Redirects
1. Fazer request para sssrr.org URL
2. Capturar Location header (302)
3. Seguir para CloudFlare tunnel
4. Capturar URL final de vídeo

### Método 3: Interceptar Network (Browser)
1. Usar Playwright/Puppeteer
2. Interceptar requests de rede
3. Capturar M3U8 ou MP4 URLs
4. Filtrar por `.m3u8`, `.mp4`, etc.

---

## 🚨 PROBLEMAS IDENTIFICADOS

### 1. CloudFlare Tunnels Timeout
- Tunnels expiram rapidamente
- Requests falham com timeout
- Precisa gerar novo tunnel

### 2. Tokens Base64
- Tokens parecem ter TTL curto
- Precisam ser regenerados
- Provavelmente vinculados a sessão

### 3. Subdomínios Aleatórios
- sssrr.org usa subdomínios aleatórios
- Dificulta whitelist/pattern matching
- Precisa regex flexível

---

## ✅ IMPLEMENTAÇÃO TYPESCRIPT

### ViewPlayerExtractor
```typescript
// 1. Buscar sssrr.org URLs
const sssrrPattern = /https?:\/\/[a-z0-9]+\.sssrr\.org\/[^"'\s]+/g;
const matches = html.match(sssrrPattern);

// 2. Buscar CloudFlare tunnels
const cfPattern = /https?:\/\/[a-z0-9-]+\.trycloudflare\.com\/[^"'\s]+/g;
const cfMatches = html.match(cfPattern);

// 3. Seguir redirects
const response = await axios.get(sssrrUrl, { maxRedirects: 0 });
const redirectUrl = response.headers.location;
```

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Implementar ViewPlayerExtractor
2. ⏳ Testar com URL real: `https://viewplayer.online/filme/tt39376546`
3. ⏳ Capturar sssrr.org URLs
4. ⏳ Seguir redirects para CloudFlare
5. ⏳ Capturar URL final de vídeo (M3U8/MP4)
6. ⏳ Portar lógica para Kotlin

---

## 📝 COMANDOS PARA TESTAR

```bash
cd video-extractor-test
npm install

# Testar ViewPlayer
npm run test:viewplayer

# Ou testar URL direta
npm run dev "https://viewplayer.online/filme/tt39376546" "https://maxseries.pics"
```

---

**Status:** ✅ ANÁLISE COMPLETA  
**Próximo:** Testar extractor com URL real
