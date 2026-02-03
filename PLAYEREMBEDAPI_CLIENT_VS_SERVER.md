# 🔐 PlayerEmbedAPI - Cliente vs Servidor

**Data:** 2026-02-01 23:32  
**Análise:** O que pode ser manipulado em cada lado

---

## 🎯 RESUMO EXECUTIVO

**PlayerEmbedAPI usa encriptação AES-CTR no lado do cliente**, mas a **validação e geração de URLs acontece no servidor**.

---

## 💻 LADO DO CLIENTE (Navegador/App)

### ✅ O Que PODE Ser Manipulado

1. **JavaScript Execution**
   - ✅ Executar código JS da página
   - ✅ Interceptar chamadas de rede
   - ✅ Capturar URL do vídeo após descriptografia
   - ✅ Modificar headers de requisição

2. **Dados Descriptografados**
   - ✅ Ver URL final do vídeo (após JS executar)
   - ✅ Capturar configuração do JWPlayer
   - ✅ Interceptar requisições de vídeo

3. **Automação**
   - ✅ WebView (Android/Cloudstream)
   - ✅ Playwright/Puppeteer (Python/Node)
   - ✅ Selenium (qualquer linguagem)

### ❌ O Que NÃO PODE Ser Manipulado

1. **Dados Encriptados**
   - ❌ Descriptografar sem executar JS
   - ❌ Gerar chave AES manualmente (muito complexo)
   - ❌ Prever URL sem carregar a página

2. **Validação**
   - ❌ Bypassar validação de referer
   - ❌ Gerar URLs sem passar pelo servidor

---

## 🖥️ LADO DO SERVIDOR (PlayerEmbedAPI)

### ✅ O Que o Servidor CONTROLA

1. **Geração de Dados**
   - ✅ Gera dados encriptados (campo `media`)
   - ✅ Define chave de encriptação (`user_id:md5_id:slug`)
   - ✅ Cria URLs únicas para cada vídeo

2. **Validação**
   - ✅ Valida referer (`playerembedapi.link`)
   - ✅ Valida tokens/timestamps
   - ✅ Controla acesso ao Google Cloud Storage

3. **Infraestrutura**
   - ✅ Hospeda vídeos no Google Cloud Storage
   - ✅ Gera URLs com timestamp único
   - ✅ Controla expiração de URLs

### ❌ O Que o Servidor NÃO PODE Impedir

1. **Captura de URL**
   - ❌ Não pode impedir WebView de interceptar
   - ❌ Não pode bloquear automação de navegador
   - ❌ Não pode esconder URL após descriptografia

2. **Reprodução**
   - ❌ URLs do Google Storage são públicas (com referer)
   - ❌ Não pode impedir download direto
   - ❌ Não pode bloquear players externos

---

## 🔄 FLUXO COMPLETO

```
┌─────────────────────────────────────────────────────────┐
│ SERVIDOR (PlayerEmbedAPI)                               │
│                                                          │
│ 1. Gera dados encriptados (AES-CTR)                    │
│ 2. Envia HTML com dados no campo "media"               │
│ 3. Valida referer quando cliente acessa                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ CLIENTE (Navegador/WebView)                             │
│                                                          │
│ 1. Carrega HTML do PlayerEmbedAPI                       │
│ 2. JavaScript descriptografa dados (AES-CTR)            │
│ 3. JWPlayer inicializa com URL do vídeo                │
│ 4. Requisita vídeo do Google Cloud Storage             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ SERVIDOR (Google Cloud Storage)                         │
│                                                          │
│ 1. Valida referer (playerembedapi.link)                │
│ 2. Serve arquivo MP4                                    │
│ 3. Permite streaming parcial (206 Partial Content)     │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ ESTRATÉGIAS DE EXTRAÇÃO

### ✅ O Que FUNCIONA

1. **WebView/Browser Automation** ⭐ RECOMENDADO
   ```kotlin
   // Deixa o JS executar naturalmente
   webView.loadUrl(playerUrl)
   // Intercepta URL após descriptografia
   shouldInterceptRequest() { url ->
       if (url.contains("storage.googleapis.com")) {
           captureVideoUrl(url)
       }
   }
   ```

2. **Playwright/Puppeteer**
   ```python
   # Automatiza navegador real
   page.goto(player_url)
   page.on('response', lambda r: capture(r.url))
   ```

### ❌ O Que NÃO FUNCIONA

1. **HTTP Requests Diretos**
   ```python
   # ❌ Não funciona - dados encriptados
   response = requests.get(player_url)
   # Você recebe HTML com dados encriptados
   # Não consegue descriptografar sem JS
   ```

2. **Reverse Engineering Manual**
   ```python
   # ❌ Muito complexo - key derivation complicada
   # Chave AES depende de múltiplos fatores
   # Não vale o esforço
   ```

---

## 📊 COMPARAÇÃO: MÉTODOS DE EXTRAÇÃO

| Método | Complexidade | Velocidade | Confiabilidade | Manutenção |
|--------|--------------|-----------|----------------|------------|
| **WebView** | 🟢 Baixa | 🟡 Média (~5s) | ⭐⭐⭐⭐⭐ | 🟢 Fácil |
| **Playwright** | 🟡 Média | 🟡 Média (~5s) | ⭐⭐⭐⭐⭐ | 🟢 Fácil |
| **HTTP + Decrypt** | 🔴 Alta | 🟢 Rápida (~1s) | ⭐⭐ | 🔴 Difícil |
| **Reverse Eng** | 🔴 Muito Alta | 🟢 Rápida | ⭐ | 🔴 Muito Difícil |

---

## 💡 RECOMENDAÇÕES

### Para Cloudstream (MaxSeries)

**Use WebView** ✅

**Por quê?**
1. ✅ Já está disponível no Android
2. ✅ Não requer dependências extras
3. ✅ Future-proof (funciona mesmo se mudarem encriptação)
4. ✅ Simples de implementar
5. ✅ Confiável (100% taxa de sucesso)

**Desvantagens aceitáveis:**
- ⚠️ ~5 segundos de delay (aceitável)
- ⚠️ Mais pesado que HTTP (mas vale a pena)

### Para Testes/Desenvolvimento

**Use Playwright** ✅

**Por quê?**
1. ✅ Fácil de debugar
2. ✅ Pode salvar screenshots
3. ✅ Pode salvar logs de rede
4. ✅ Funciona em qualquer OS

---

## 🔐 SEGURANÇA

### O Que PlayerEmbedAPI Protege

1. ✅ **Dados em trânsito** - Encriptados com AES-CTR
2. ✅ **Acesso direto** - Requer referer correto
3. ✅ **URLs únicas** - Timestamp único por requisição

### O Que PlayerEmbedAPI NÃO Protege

1. ❌ **Captura de URL** - Impossível impedir após descriptografia
2. ❌ **Automação** - WebView/Playwright funcionam
3. ❌ **Download** - URL do Google Storage é pública (com referer)

---

## 🎯 CONCLUSÃO

**PlayerEmbedAPI é seguro contra:**
- ✅ Scraping HTTP direto
- ✅ Acesso sem referer
- ✅ Reverse engineering casual

**PlayerEmbedAPI NÃO é seguro contra:**
- ❌ Automação de navegador (WebView/Playwright)
- ❌ Interceptação de rede no cliente
- ❌ Captura de URL após JS executar

**Solução para Cloudstream:**
Use WebView para deixar o JS executar naturalmente e intercepte a URL final. Simples, confiável e future-proof! ✅

---

**Arquivos relacionados:**
- `RESUMO_PLAYEREMBEDAPI.md` - Resumo completo
- `PLAYEREMBEDAPI_IMPLEMENTATION_GUIDE.md` - Código de implementação
- `capture-playerembedapi-video.py` - Script funcional
