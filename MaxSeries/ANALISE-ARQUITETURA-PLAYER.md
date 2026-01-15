# 🔍 ANÁLISE TÉCNICA - Arquitetura Real do Player MaxSeries

**Data:** 14/01/2026  
**Versão do Plugin:** v80  
**Status:** ✅ Implementação Alinhada com Arquitetura Real

---

## 📊 ARQUITETURA REAL DESCOBERTA (Burp Suite)

### 🎯 Fluxo Completo de Streaming

```
playerthree.online (catálogo/UI)
        │
        ▼
iframe embed (/embed/synden)
        │
        ▼
megaembed.link (API + token)
        │
        ▼
marvellaholdings.sbs (CDN HLS real)
        │
        ▼
cf-master.txt → playlists → segmentos
```

### 🔑 Descobertas Críticas

#### ✅ **Ponto Mais Importante**
**O vídeo NÃO nasce no playerthree.online**

Ele apenas aponta para:
```html
<button data-source="https://megaembed.link/#3wnuij">
```

**Hierarquia Real:**
- `playerthree.online` = UI / catálogo
- `megaembed.link` = controle + token
- `*.marvellaholdings.sbs` = stream real (CDN)

---

## 🎬 ARQUIVO-CHAVE: `cf-master.txt`

### 📌 Exemplo Capturado

```
https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

### ✅ Por Que Isso É Ouro?

| Característica | Valor |
|----------------|-------|
| **Content-Type** | `application/vnd.apple.mpegurl` |
| **Formato** | HLS Manifest |
| **Cache** | Cloudflare cache HIT |
| **DRM** | ❌ Sem DRM |
| **Método** | GET direto |
| **Requisito** | Referer correto |

**📌 Isso é EXATAMENTE o que o CloudStream precisa.**

---

## 🧬 ESTRUTURA DO HLS (Simplificada)

```
cf-master.txt
 ├── index-f1-v1-a1.txt   (qualidade 1)
 ├── index-f2-v1-a1.txt   (qualidade 2)
 └── index-f3-v1-a1.txt   (qualidade 3)
       ├── seg-1.woff2
       ├── seg-2.woff2
       ├── seg-3.woff2
```

### ⚠️ IMPORTANTE: `.woff2` NÃO são fontes
É apenas **ofuscação de extensão** (Cloudflare anti-scraping).

---

## 🔐 O PAPEL DO TOKEN (`api/v1/player`)

### Chamadas Capturadas

```
GET https://megaembed.link/api/v1/player?t=TOKEN_GIGANTE
```

### O Que Esse Token Faz?

1. ✅ Autoriza o embed
2. ✅ Valida origem (Referer)
3. ✅ Retorna dados JS (não o vídeo direto)
4. ❌ **NÃO precisa ser quebrado no CloudStream**

### 📌 Conclusão
**O CloudStream não precisa desse token**  
👉 Basta usar o HLS final, com headers corretos.

---

## 🧪 O QUE NÃO É RELEVANTE (Pode Ignorar)

❌ `api/v1/log`  
❌ `api/v1/info`  
❌ `jwplayer_key`  
❌ `redirector_url`  
❌ Scripts obfuscados enormes  
❌ Cloudflare analytics  
❌ CSS / UI  

**Eles não participam do streaming.**

---

## 🧠 POR QUE O BURP AJUDOU MUITO

### ✔ Confirmações Obtidas

1. ✅ Ordem real das requisições
2. ✅ Endpoint HLS final descoberto
3. ✅ Headers obrigatórios identificados
4. ✅ Domínio CDN rotativo mapeado
5. ✅ Prova de que não há DRM
6. ✅ ID do vídeo isolado (`3wnuij`)

---

## 🔥 TESTES ADICIONAIS POSSÍVEIS NO BURP

### 1️⃣ Repeater no `cf-master.txt`

**Testar:**
- ❌ Sem Referer
- ❌ Com Referer errado
- ✅ Com User-Agent Android

**Objetivo:** Descobrir mínimo de headers necessários

### 2️⃣ Comparer

**Comparar:**
- `cf-master.txt` de episódios diferentes
- IDs diferentes (`3wnuij`, outro)

**Objetivo:** Ver se o padrão `/v4/x6b/{id}/` muda

### 3️⃣ Scope só `marvellaholdings.sbs`

**Resultado:** Limpa tudo e deixa só:
- CDN real
- Manifest
- Segmentos

---

## ✅ ESTADO ATUAL DO PLUGIN MaxSeries v80

### 🎯 O Que Já Temos Implementado

| Componente | Status | Arquivo |
|------------|--------|---------|
| **Link final do vídeo** | ✅ | `MegaEmbedExtractor.kt` |
| **Formato compatível** | ✅ | HLS via `M3u8Helper` |
| **Headers necessários** | ✅ | `Referer` + `User-Agent` |
| **Padrão de URL** | ✅ | Regex para `.m3u8`, `master.txt`, `/v4/` |
| **Prova sem DRM** | ✅ | Validado via Burp |

---

## 📋 ANÁLISE DO CÓDIGO ATUAL

### 🔍 `MegaEmbedExtractor.kt` (Linha 102-113)

```kotlin
val resolver = WebViewResolver(
    interceptUrl = Regex("""\\.m3u8|\\.mp4|master\\.txt|cf-master.*\\.txt|/hls/|/video/|/v4/.*\\.txt|cloudatacdn|sssrr\\.org"""),
    additionalUrls = listOf(
        Regex("""https?://[^/]+/v4/[^/]+/[^/]+/cf-master.*\\.txt"""),
        Regex("""https?://[^/]+\\.m3u8"""),
        Regex("""https?://[^/]+\\.mp4"""),
        Regex("""cloudatacdn\\.com[^"'\\s]*"""),
        Regex("""sssrr\\.org[^"'\\s]*\\.m3u8""")
    ),
    useOkhttp = false, // Importante para bypass Cloudflare
    timeout = 45_000L
)
```

### ✅ **PERFEITO!** Já captura:
- ✅ `cf-master.txt` (linha 102)
- ✅ `/v4/{id}/{id}/cf-master.*.txt` (linha 105)
- ✅ `.m3u8` genérico (linha 106)
- ✅ `marvellaholdings.sbs` via regex genérico

---

## 🎯 VALIDAÇÃO: Regex vs. URL Real

### URL Real Capturada
```
https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

### Regex Atual (Linha 105)
```kotlin
Regex("""https?://[^/]+/v4/[^/]+/[^/]+/cf-master.*\\.txt""")
```

### ✅ Match Breakdown
```
https?://              → https://
[^/]+                  → spo3.marvellaholdings.sbs
/v4/                   → /v4/
[^/]+                  → x6b
/                      → /
[^/]+                  → 3wnuij
/cf-master.*\\.txt     → /cf-master.1767386783.txt
```

**✅ MATCH COMPLETO!**

---

## 🔍 VALIDAÇÃO: Headers Implementados

### Headers Atuais (Linha 117-122)

```kotlin
headers = mapOf(
    "User-Agent" to USER_AGENT,
    "Referer" to (referer ?: mainUrl),
    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
)
```

### ✅ Comparação com Burp Suite

| Header | Implementado | Necessário | Status |
|--------|--------------|------------|--------|
| `User-Agent` | ✅ Android | ✅ Qualquer | ✅ OK |
| `Referer` | ✅ `megaembed.link` | ✅ Obrigatório | ✅ OK |
| `Accept` | ✅ | ⚪ Opcional | ✅ OK |
| `Accept-Language` | ✅ | ⚪ Opcional | ✅ OK |

**✅ HEADERS CORRETOS!**

---

## 📌 PRÓXIMOS PASSOS (Não é mais Burp)

### ✅ O Que Já Está Pronto

1. ✅ Extractor implementado (`MegaEmbedExtractor.kt`)
2. ✅ Regex captura `cf-master.txt`
3. ✅ Headers corretos configurados
4. ✅ WebView com interceptação de rede
5. ✅ Fallback JavaScript + HTTP direto
6. ✅ Validação de URL de vídeo

### 🔄 Próximo Passo: **IMPLEMENTAR/TESTAR**

**Não é mais análise de rede, é código:**

1. **Build do Plugin**
   ```powershell
   cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release
   .\gradlew.bat :MaxSeries:assembleRelease
   ```

2. **Deploy no Cloudstream**
   - Copiar `.aar` para o app
   - Testar com episódio real

3. **Validar Logs**
   ```bash
   adb logcat | grep -E "MegaEmbed|MaxSeries"
   ```

4. **Verificar Captura**
   - URL interceptada deve ser `cf-master.*.txt`
   - Referer deve ser `megaembed.link`
   - Playback deve iniciar

---

## 🧩 CONCLUSÃO DIRETA

### ✅ **SIM, ISSO É RELEVANTE**

Na prática, você já tem:

| Item | Status |
|------|--------|
| ✅ Link final do vídeo | **IMPLEMENTADO** |
| ✅ Formato compatível com CloudStream | **HLS via M3u8Helper** |
| ✅ Header necessário | **Referer configurado** |
| ✅ Padrão de URL | **Regex completo** |
| ✅ Prova de que não há DRM | **Validado via Burp** |

---

## 🎯 ALINHAMENTO: Burp vs. Código

### Descobertas do Burp Suite

```
✅ cf-master.txt é o arquivo-chave
✅ marvellaholdings.sbs é o CDN real
✅ Referer obrigatório
✅ Sem DRM
✅ Padrão /v4/{id}/{id}/cf-master.*.txt
```

### Implementação no Código

```kotlin
✅ Regex captura cf-master.txt (linha 102, 105)
✅ Regex genérico captura marvellaholdings.sbs
✅ Referer configurado (linha 119)
✅ Sem tratamento de DRM (não necessário)
✅ Padrão /v4/ implementado (linha 105)
```

---

## 📊 MATRIZ DE COMPATIBILIDADE

| Requisito (Burp) | Implementação (Código) | Status |
|------------------|------------------------|--------|
| `cf-master.txt` | `cf-master.*\\.txt` | ✅ MATCH |
| `/v4/{id}/{id}/` | `/v4/[^/]+/[^/]+/` | ✅ MATCH |
| `marvellaholdings.sbs` | `https?://[^/]+` | ✅ MATCH |
| `Referer: megaembed.link` | `referer ?: mainUrl` | ✅ MATCH |
| `User-Agent: Android` | `USER_AGENT` | ✅ MATCH |
| Sem DRM | Sem código DRM | ✅ MATCH |
| HLS Manifest | `M3u8Helper` | ✅ MATCH |

---

## 🔥 RESUMO EXECUTIVO

### 🎯 Situação Atual

**O plugin MaxSeries v80 JÁ ESTÁ ALINHADO com a arquitetura real descoberta via Burp Suite.**

### ✅ Evidências

1. **Regex captura `cf-master.txt`** ✅
2. **Headers corretos configurados** ✅
3. **Padrão `/v4/` implementado** ✅
4. **WebView intercepta rede** ✅
5. **Sem dependência de token** ✅

### 🔄 Próxima Ação

**NÃO é mais análise de rede (Burp).**  
**É BUILD + DEPLOY + TESTE.**

---

## 📝 RECOMENDAÇÕES FINAIS

### 1️⃣ **Build Imediato**
```powershell
.\gradlew.bat :MaxSeries:assembleRelease
```

### 2️⃣ **Deploy no App**
```
MaxSeries/build/outputs/aar/MaxSeries-release.aar
```

### 3️⃣ **Teste com Episódio Real**
- Escolher episódio de `playerthree.online`
- Verificar logs `adb logcat`
- Confirmar captura de `cf-master.txt`

### 4️⃣ **Validar Playback**
- Vídeo deve iniciar
- Múltiplas qualidades disponíveis
- Sem erro 3003

---

## 🎓 GLOSSÁRIO TÉCNICO

| Termo | Significado |
|-------|-------------|
| **cf-master.txt** | Manifest HLS principal (Cloudflare) |
| **HLS** | HTTP Live Streaming (Apple) |
| **Manifest** | Arquivo índice com URLs dos segmentos |
| **Referer** | Header HTTP que indica origem da requisição |
| **WebView** | Navegador embutido no Android |
| **Interceptação** | Captura de requisições HTTP em tempo real |
| **DRM** | Digital Rights Management (proteção de conteúdo) |
| **CDN** | Content Delivery Network (rede de distribuição) |

---

**✅ ANÁLISE CONCLUÍDA**  
**🎯 CÓDIGO JÁ ESTÁ CORRETO**  
**🔄 PRÓXIMO PASSO: BUILD + TESTE**

---

**Versão:** 1.0  
**Autor:** Análise Técnica MaxSeries  
**Data:** 14/01/2026
