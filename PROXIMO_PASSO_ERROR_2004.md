# ⚡ Próximo Passo - Corrigir Error 2004

## 🎯 Situação Atual

✅ **BOM**: PlayerEmbedAPI aparece na lista (detecção funcionando)  
❌ **RUIM**: Dá erro 2004 ao tentar reproduzir (URL com problema)

## 📋 O Que Fazer AGORA

### 1. Conectar ADB WiFi

```
Seu IP: 100.124.161.4:42685
```

No PowerShell:
```powershell
adb connect 100.124.161.4:42685
```

### 2. Executar Script de Captura

```powershell
.\capture-playerembedapi-error.ps1
```

O script vai:
1. Conectar no dispositivo
2. Limpar logs antigos
3. Pedir para você clicar em PlayerEmbedAPI
4. Capturar logs quando erro aparecer
5. Analisar automaticamente
6. Salvar em arquivo

### 3. Seguir Instruções do Script

Quando o script pedir:
1. Abrir filme no Cloudstream
2. Clicar em "Fontes"
3. Clicar em "PlayerEmbedAPI HD"
4. Aguardar erro aparecer
5. Pressionar ENTER no script

### 4. Analisar Resultado

O script vai mostrar:
- ✅ O que funcionou
- ❌ O que falhou
- 📄 Arquivo com logs completos

### 5. Compartilhar Logs

Enviar o arquivo `playerembedapi_error_XXXXXXXX_XXXXXX.txt` para análise.

## 🔍 O Que Vamos Descobrir

Com os logs, vamos saber:

1. **URL foi capturada?**
   - Se SIM: problema é na URL (headers, expiração, etc)
   - Se NÃO: problema é no WebView (timeout, elemento não encontrado, etc)

2. **Qual URL foi capturada?**
   - `https://storage.googleapis.com/...` = URL correta
   - `https://subdomain.sssrr.org/?timestamp=...` = URL intermediária (precisa seguir redirect)
   - `https://playerembedapi.link/?v=...` = URL errada (não é do vídeo)

3. **Quanto tempo demorou?**
   - < 30s = OK
   - = 30s = Timeout (precisa mais tempo)
   - > 30s = Não deveria acontecer

4. **Houve erros?**
   - Context não obtido
   - IMDB ID não extraído
   - WebView não carregou
   - Etc.

## 🛠️ Possíveis Correções

Baseado nos logs, vou aplicar uma destas correções:

### Correção A: Adicionar Headers

Se URL foi capturada mas dá erro 2004:

```kotlin
// Adicionar headers ao ExtractorLink
this.headers = mapOf(
    "User-Agent" to "Mozilla/5.0...",
    "Origin" to "https://viewplayer.online",
    "Referer" to "https://viewplayer.online/"
)
```

### Correção B: Aumentar Timeout

Se deu timeout antes de capturar:

```kotlin
// Aumentar de 30s para 45s
withTimeoutOrNull(45000) {
    extractionJob?.await()
}
```

### Correção C: Seguir Redirects

Se URL capturada é intermediária:

```kotlin
// Seguir redirect para URL final
val finalUrl = app.get(url, allowRedirects = true).url
```

### Correção D: Capturar do Elemento Video

Se interceptação não funciona:

```kotlin
// Pegar URL diretamente do <video>
const video = document.querySelector('video');
if (video && video.src) {
    Android.onVideoFound(video.src);
}
```

## 📊 Fluxo de Diagnóstico

```
1. Executar script
   ↓
2. Capturar logs
   ↓
3. Analisar logs
   ↓
4. Identificar problema
   ↓
5. Aplicar correção
   ↓
6. Build v221
   ↓
7. Testar novamente
```

## ⏱️ Tempo Estimado

- Capturar logs: **2 minutos**
- Analisar logs: **5 minutos**
- Aplicar correção: **10 minutos**
- Build e teste: **5 minutos**

**Total**: ~20 minutos para corrigir

## 💡 Dica Importante

**NÃO tente corrigir sem logs!**

Sem logs, é impossível saber qual é o problema real. Pode ser:
- Headers
- Timeout
- URL errada
- Detecção
- Etc.

Com logs, sabemos exatamente o que corrigir.

## 🎯 Resumo

```
AGORA:
1. adb connect 100.124.161.4:42685
2. .\capture-playerembedapi-error.ps1
3. Seguir instruções
4. Compartilhar logs

DEPOIS:
1. Analisar logs
2. Identificar problema
3. Aplicar correção
4. Build v221
5. Testar
```

---

**Status**: Aguardando logs para diagnóstico  
**Próxima ação**: Executar `.\capture-playerembedapi-error.ps1`  
**Tempo estimado**: 2 minutos para capturar logs
