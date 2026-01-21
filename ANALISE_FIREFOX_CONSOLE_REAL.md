# 🔍 Análise do Firefox Console - Fluxo Real do MegaEmbed

## 📊 Dados Capturados (2026-01-20 21:24)

### Video ID: `6pyw3v`

---

## 🎯 FLUXO COMPLETO DESCOBERTO

### 1. Carregamento Inicial
```
21:24:51.662 GET https://megaembed.link/#6pyw3v [HTTP/3 200  23ms]
21:24:51.787 GET https://megaembed.link/assets/index-CZ_ja_1t.js [HTTP/3 200  435ms]
21:24:51.810 GET https://megaembed.link/assets/index-DsSvO8OB.css [HTTP/3 200  152ms]
```

### 2. APIs do MegaEmbed (CRÍTICO!)
```
21:24:52.367 XHR GET
https://megaembed.link/api/v1/info?id=6pyw3v
[HTTP/3 200  165ms]

21:24:52.890 XHR GET
https://megaembed.link/api/v1/video?id=6pyw3v&w=1920&h=1080&r=playerthree.online
[HTTP/3 200  169ms]

21:24:53.130 XHR GET
https://megaembed.link/api/v1/player?t=3772aacff2bd31142eec3d5b0f291f4e5c614f33e76d4baae42f4465e6b385d1...
[HTTP/3 200  187ms]
```

**DESCOBERTA CHAVE:**
- `/api/v1/info?id=6pyw3v` - Retorna metadados do vídeo
- `/api/v1/video?id=6pyw3v&w=1920&h=1080&r=playerthree.online` - Retorna configuração do player
- `/api/v1/player?t={token}` - Retorna URL do CDN **COM TOKEN DE AUTENTICAÇÃO**

---

### 3. CDN URLs - O Link REAL do Vídeo! 🎯

#### Estrutura Descoberta:
```
Host: sxix.rivonaengineering.sbs
Cluster: db  ← NOVO! Não estava nos padrões conhecidos
VideoID: 6pyw3v
```

#### URLs Capturadas (em ordem cronológica):

```
21:24:53.211 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/cf-master.1767387529.txt
[HTTP/2 200  510ms]

21:24:53.787 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f1-v1-a1.txt
[HTTP/2 200  447ms]

21:24:54.469 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/init-f1-v1-a1.woff
[HTTP/3 200  270ms]

21:24:54.812 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/seg-1-f1-v1-a1.woff2
[HTTP/3 200  997ms]

21:24:54.829 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/seg-2-f1-v1-a1.woff2
[HTTP/3 200  1028ms]

21:24:55.842 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/seg-3-f1-v1-a1.woff2
[HTTP/3 200  846ms]

21:24:56.012 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/seg-4-f1-v1-a1.woff2
[HTTP/3 200  1078ms]

21:24:55.911 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f2-v1-a1.txt
[HTTP/3 200  2106ms]

21:24:58.285 XHR GET
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/init-f2-v1-a1.woff
[HTTP/3 200  454ms]
```

---

## ⚠️ PROBLEMAS IDENTIFICADOS NO v146

### 1. CLUSTER "db" NÃO ESTÁ COBERTO
```kotlin
// v146 espera clusters de 2-3 chars alfanuméricos
val regex = Regex("""https?://([^/]+)/v4/([a-z0-9]{1,3})/([a-z0-9]{6})""")

// MAS "db" tem apenas 2 chars ✅
// DEVERIA funcionar!
```

**Status:** ✅ Regex do v146 DEVERIA capturar "db"

---

### 2. NOVA CDN DESCOBERTA: rivonaengineering.sbs

**CDNs conhecidos (documentação):**
- valenium.shop
- veritasholdings.cyou
- marvellaholdings.sbs
- travianastudios.space

**NOVO:**
- ✅ rivonaengineering.sbs ← NÃO ESTAVA NA LISTA!

---

### 3. cf-master TEM TIMESTAMP DINÂMICO

```
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/cf-master.1767387529.txt
                                                             ↑
                                                    Timestamp Unix
```

**Problema:** v146 testa `cf-master.txt`, mas o arquivo real é `cf-master.1767387529.txt`

**Status:** ❌ v146 NÃO vai encontrar cf-master com timestamp

**Solução:** Adicionar `cf-master.*.txt` nas variações

---

## 🔍 ANÁLISE DETALHADA

### Ordem de Requisições (Player Real):

```
1. cf-master.1767387529.txt     ← Playlist master com timestamp
2. index-f1-v1-a1.txt           ← Playlist qualidade 1
3. init-f1-v1-a1.woff           ← Inicialização qualidade 1
4. seg-1-f1-v1-a1.woff2         ← Segmento 1 qualidade 1
5. seg-2-f1-v1-a1.woff2         ← Segmento 2 qualidade 1
6. seg-3-f1-v1-a1.woff2         ← Segmento 3 qualidade 1
7. seg-4-f1-v1-a1.woff2         ← Segmento 4 qualidade 1
8. index-f2-v1-a1.txt           ← Playlist qualidade 2
9. init-f2-v1-a1.woff           ← Inicialização qualidade 2
10. seg-*-f2-v1-a1.woff2        ← Segmentos qualidade 2
```

**INSIGHT:**
- Player tenta `index-f1-v1-a1.txt` ANTES de `index-f2-v1-a1.txt`
- v146 está CORRETO na ordem de prioridade! ✅

---

## 🎯 URLS QUE FUNCIONAM (COMPROVADO)

### Para VideoID: 6pyw3v

```
✅ https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/cf-master.1767387529.txt
✅ https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f1-v1-a1.txt
✅ https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f2-v1-a1.txt
✅ https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/init-f1-v1-a1.woff
✅ https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/seg-1-f1-v1-a1.woff2
```

---

## 🚨 CORREÇÕES NECESSÁRIAS NO v146

### 1. Adicionar suporte a cf-master com timestamp

**Problema:**
```kotlin
// v146 atual:
val fileVariations = listOf(
    "index-f1-v1-a1.txt",
    "index-f2-v1-a1.txt",
    "index.txt",
    "cf-master.txt"  // ← Não funciona! Precisa do timestamp
)
```

**Solução:**
```kotlin
// v147: Buscar cf-master.*.txt no HTML capturado
val capturedHtml = response.text
val cfMasterRegex = Regex("""cf-master\.\d+\.txt""")
val cfMasterMatch = cfMasterRegex.find(capturedHtml)

if (cfMasterMatch != null) {
    val cfMasterFile = cfMasterMatch.value
    // Testar cf-master.1767387529.txt
}
```

---

### 2. Extrair URL do CDN da API /player

**API descoberta:**
```
https://megaembed.link/api/v1/player?t={token_longo}
```

**Resposta provável (JSON):**
```json
{
  "cdn": "https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f1-v1-a1.txt",
  "qualities": ["f1", "f2"],
  "timestamp": 1767387529
}
```

**Solução v147:**
```kotlin
// 1. Chamar API /player
val apiUrl = "https://megaembed.link/api/v1/player?t=${extractToken(html)}"
val apiResponse = app.get(apiUrl, headers = cdnHeaders).parsed<PlayerApiResponse>()

// 2. Usar URL direta do CDN
val cdnUrl = apiResponse.cdn
if (cdnUrl != null && tryUrl(cdnUrl)) {
    return cdnUrl
}
```

---

### 3. Buscar Token no HTML

**Token descoberto (truncado):**
```
t=3772aacff2bd31142eec3d5b0f291f4e5c614f33e76d4baae42f4465e6b385d1ea14418e657c5d7beacd41f1f7e414ecc1c867295fc9bba2f9320351473d6f077...
```

**Tamanho:** ~500+ caracteres hexadecimais

**Regex para capturar:**
```kotlin
val tokenRegex = Regex("""t=([a-f0-9]{200,})""")
val token = tokenRegex.find(html)?.groupValues?.get(1)
```

---

## 📋 RESUMO DAS DESCOBERTAS

### ✅ O que v146 JÁ FAZ CERTO:

1. ✅ Regex único amplo captura `/v4/`
2. ✅ Ordem de prioridade correta: `index-f1` antes de `index-f2`
3. ✅ Valida URLs com `tryUrl()`
4. ✅ Extrai componentes: host, cluster, videoId

### ❌ O que v146 PRECISA CORRIGIR:

1. ❌ cf-master tem timestamp dinâmico (não é só `cf-master.txt`)
2. ❌ Não usa APIs do MegaEmbed (`/api/v1/player`)
3. ❌ Não extrai token de autenticação do HTML
4. ❌ CDN `rivonaengineering.sbs` não estava documentado (mas regex deve capturar)

---

## 🎯 PROPOSTA v147 (MELHORIAS)

### Abordagem Híbrida:

```
1. FASE 1: Cache (atual v146) ✅

2. FASE 2: Tentar APIs do MegaEmbed (NOVO!)
   └─ GET /api/v1/info?id={videoId}
   └─ GET /api/v1/video?id={videoId}&w=1920&h=1080&r=megaembed.link
   └─ Extrair token do HTML
   └─ GET /api/v1/player?t={token}
   └─ Parsear JSON e obter URL do CDN
   └─ Se funcionar → retornar ✅

3. FASE 3: WebView (fallback v146)
   └─ Se API falhar, usa WebView como v146
   └─ MAS: Procurar cf-master.*.txt com regex no HTML
   └─ Tentar variações incluindo cf-master com timestamp
```

---

## 📊 Estrutura da URL Confirmada

```
https://{subdominio}.{dominio}.{tld}/v4/{cluster}/{videoId}/{arquivo}

Exemplo Real:
https://sxix.rivonaengineering.sbs/v4/db/6pyw3v/index-f1-v1-a1.txt
       ↑                         ↑     ↑  ↑      ↑
   subdominio                   tld  cluster videoId  arquivo

Componentes:
- subdominio: sxix (s[a-z0-9]{2,4})
- dominio: rivonaengineering
- tld: sbs
- cluster: db (2 chars) ✅ v146 suporta
- videoId: 6pyw3v (6 chars) ✅
- arquivo: index-f1-v1-a1.txt ✅
```

---

## 🔍 Outros Dados Importantes

### Thumbnail
```
https://megaembed.link/MVwK9ANeKEFMfmW44RnRnA/db/r8c1nmni/q15weq/thumbnail.vtt
https://megaembed.link/MVwK9ANeKEFMfmW44RnRnA/db/r8c1nmni/q15weq/thumbnail.jpg
```

### Poster
```
https://megaembed.link/6Un2hu2WKKKd8HyUkIZzOw/db/r8c1nmni/q15weq/poster.png
```

### WebSocket (P2P)
```
wss://5.180.24.81:8080/
wss://185.237.107.13:8080/
wss://45.12.138.169:8080/
wss://45.156.158.199:8080/
wss://tracker.webtorrent.dev/
```

**INSIGHT:** MegaEmbed usa P2P (WebTorrent) além de CDN direto!

---

## 🎯 CONCLUSÃO

### v146 DEVE FUNCIONAR?

**Parcialmente:**
- ✅ Regex captura `/v4/db/6pyw3v/*`
- ✅ Tenta `index-f1-v1-a1.txt` (que FUNCIONA!)
- ❌ Não vai encontrar `cf-master.1767387529.txt` (tem timestamp)
- ❌ Não usa APIs que dão URL direta

### v147 PROPOSTA:

1. **Adicionar chamadas às APIs** (`/api/v1/player`)
2. **Buscar cf-master com timestamp** no HTML
3. **Extrair token de autenticação**
4. **Usar URL direta da API quando disponível**
5. **Fallback para WebView** (como v146)

---

**Análise por:** Verdent AI  
**Data:** 2026-01-20  
**Fonte:** Firefox Console (dados reais)  
**Status:** ✅ DADOS VALIDADOS
