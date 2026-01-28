# 🔍 Diagnóstico - ERROR_CODE_IO_BAD_HTTP_STATUS (2004)

## 📸 Erro Observado

```
Erro no servidor
ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
Source error
```

## 🎯 O Que Significa

Este erro indica que:
- ✅ PlayerEmbedAPI foi **detectado** (aparece na lista)
- ✅ Extração foi **iniciada**
- ❌ URL retornada dá **erro HTTP** ao tentar reproduzir

## 🤔 Possíveis Causas

### 1. URL Expirou

PlayerEmbedAPI pode gerar URLs com timestamp que expiram rapidamente.

**Sintoma**: Funciona no browser mas não no app

**Solução**: Reduzir timeout de extração

### 2. Headers Incorretos

URL precisa de headers específicos (Referer, User-Agent, etc)

**Sintoma**: URL funciona no browser mas não no player

**Solução**: Adicionar headers corretos ao ExtractorLink

### 3. WebView Não Capturou URL Correta

WebView pode ter capturado URL intermediária em vez da final

**Sintoma**: URL capturada não é a do vídeo

**Solução**: Aguardar mais tempo ou capturar URL diferente

### 4. Detecção de Automação

Site detectou que é automação e retornou URL inválida

**Sintoma**: Sempre falha, nunca funciona

**Solução**: Melhorar stealth do WebView

## 🔧 Diagnóstico Passo a Passo

### Passo 1: Capturar Logs

```powershell
.\capture-playerembedapi-error.ps1
```

Siga as instruções e capture os logs quando o erro aparecer.

### Passo 2: Analisar Logs

Procurar por:

```
✅ Deve ter:
- "🚀🚀🚀 EXTRACT CHAMADO! IMDB: ttXXXXXX"
- "✅ Context obtido"
- "🌐 Loading: https://viewplayer.online/filme/..."
- "🎯 Captured: https://..."

❌ Não deve ter:
- "❌ Erro ao obter Context"
- "❌ IMDB ID não encontrado"
- "⏱️ Timeout"
```

### Passo 3: Verificar URL Capturada

Se logs mostram URL capturada, verificar:

1. **Formato da URL**:
   ```
   ✅ Correto: https://storage.googleapis.com/.../video.mp4
   ✅ Correto: https://subdomain.sssrr.org/?timestamp=...&id=...
   ❌ Errado: https://playerembedapi.link/?v=...
   ❌ Errado: https://viewplayer.online/...
   ```

2. **Timestamp**:
   ```
   Se URL tem timestamp, verificar se não expirou
   ```

3. **Headers**:
   ```
   Verificar se ExtractorLink tem referer correto
   ```

## 🛠️ Soluções Possíveis

### Solução 1: Adicionar Headers ao ExtractorLink

O código atual cria ExtractorLink assim:

```kotlin
newExtractorLink(
    source = "PlayerEmbedAPI",
    name = "PlayerEmbedAPI ${getQualityLabel(detectQuality(url))}",
    url = url,
    type = ExtractorLinkType.VIDEO
) {
    this.referer = "https://viewplayer.online/"
}
```

**Pode precisar adicionar**:

```kotlin
newExtractorLink(
    source = "PlayerEmbedAPI",
    name = "PlayerEmbedAPI ${getQualityLabel(detectQuality(url))}",
    url = url,
    type = ExtractorLinkType.VIDEO
) {
    this.referer = "https://viewplayer.online/"
    this.headers = mapOf(
        "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin" to "https://viewplayer.online",
        "Accept" to "*/*"
    )
}
```

### Solução 2: Aguardar Mais Tempo

Aumentar timeout de 30s para 45s:

```kotlin
// Timeout de 30 segundos
withTimeoutOrNull(30000) {
    extractionJob?.await()
}

// Mudar para 45 segundos
withTimeoutOrNull(45000) {
    extractionJob?.await()
}
```

### Solução 3: Capturar URL do Elemento Video

Em vez de interceptar requisições, pegar URL diretamente do elemento `<video>`:

```kotlin
// Adicionar no JavaScript
const video = document.querySelector('video');
if (video && video.src) {
    Android.onVideoFound(video.src);
}
```

### Solução 4: Seguir Redirects

Se URL capturada é intermediária, seguir redirect:

```kotlin
// Antes de retornar, fazer request para seguir redirect
val finalUrl = app.get(url, allowRedirects = true).url
```

## 📊 Análise do Erro 2004

### O Que É

`ERROR_CODE_IO_BAD_HTTP_STATUS` = Resposta HTTP inválida (não 200 OK)

Possíveis códigos:
- **403 Forbidden**: Headers incorretos ou detecção
- **404 Not Found**: URL expirou ou inválida
- **410 Gone**: Recurso removido
- **500 Server Error**: Problema no servidor

### Como Descobrir Qual Código

Nos logs, procurar por:
```
Response code: XXX
HTTP error: XXX
Status: XXX
```

## 🎯 Próximos Passos

### 1. Capturar Logs Detalhados

```powershell
.\capture-playerembedapi-error.ps1
```

### 2. Compartilhar Logs

Enviar arquivo `playerembedapi_error_XXXXXXXX_XXXXXX.txt` para análise

### 3. Testar Manualmente

Abrir URL capturada no browser e verificar:
- URL funciona?
- Precisa de headers específicos?
- Expira rapidamente?

### 4. Ajustar Código

Baseado na análise, aplicar uma das soluções acima.

## 💡 Dicas

### Se URL Funciona no Browser

Problema é headers. Adicionar headers ao ExtractorLink.

### Se URL Não Funciona no Browser

Problema é URL capturada. Aguardar mais tempo ou capturar URL diferente.

### Se Sempre Falha

Problema é detecção. Melhorar stealth do WebView.

### Se Funciona Às Vezes

Problema é timing. Ajustar timeout ou aguardar elemento específico.

## 🔍 Checklist de Diagnóstico

- [ ] Logs capturados
- [ ] "EXTRACT CHAMADO" aparece nos logs
- [ ] IMDB ID foi extraído
- [ ] Context foi obtido
- [ ] WebView carregou URL
- [ ] URLs foram capturadas
- [ ] URL capturada tem formato correto
- [ ] Código HTTP identificado
- [ ] URL testada manualmente no browser

## 📝 Template de Relatório

```
ERRO: ERROR_CODE_IO_BAD_HTTP_STATUS (2004)

LOGS:
- Extract chamado: [SIM/NÃO]
- IMDB ID: [ttXXXXXX ou NÃO ENCONTRADO]
- Context obtido: [SIM/NÃO]
- WebView carregou: [SIM/NÃO]
- URLs capturadas: [X URLs ou NENHUMA]
- URL capturada: [URL ou N/A]
- Formato da URL: [CORRETO/INCORRETO]
- URL funciona no browser: [SIM/NÃO]
- Código HTTP: [XXX ou DESCONHECIDO]

CONCLUSÃO:
[Descrever o que foi descoberto]

SOLUÇÃO PROPOSTA:
[Qual solução aplicar]
```

---

**Próxima ação**: Executar `.\capture-playerembedapi-error.ps1` e compartilhar logs para análise detalhada.
