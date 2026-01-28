# 📋 Capturar Logs Manualmente - PlayerEmbedAPI Error 2004

## ⚠️ Problema de Conexão ADB WiFi

A conexão ADB WiFi não está funcionando. Vamos capturar logs manualmente.

## 🔌 Opção 1: Usar Cabo USB (RECOMENDADO)

### Passo 1: Conectar USB

1. Conectar cabo USB entre PC e Android
2. No Android: Configurações → Opções do desenvolvedor
3. Habilitar "Depuração USB"
4. Aceitar prompt de autorização no Android

### Passo 2: Verificar Conexão

```powershell
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
```

Deve mostrar:
```
List of devices attached
XXXXXXXXXX      device
```

### Passo 3: Capturar Logs

```powershell
# Limpar logs antigos
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -c

# Aguardar você clicar em PlayerEmbedAPI no app
Write-Host "Clique em PlayerEmbedAPI no app e aguarde o erro aparecer..."
Write-Host "Pressione ENTER quando o erro aparecer"
Read-Host

# Capturar logs
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -d | Select-String -Pattern "PlayerEmbedAPI|WebView|ERROR|Captured|IMDB|Extract|Context|Loading" > playerembedapi_error_manual.txt

Write-Host "Logs salvos em: playerembedapi_error_manual.txt"
```

## 📱 Opção 2: Usar App de Logs no Android

Se USB também não funcionar:

### Apps Recomendados

- **Logcat Reader**: Captura logs no próprio Android
- **MatLog**: Visualizador de logs
- **aLogcat**: Simples e eficaz

### Como Usar

1. Instalar app de logs
2. Abrir app e iniciar captura
3. Voltar para Cloudstream
4. Clicar em PlayerEmbedAPI
5. Aguardar erro
6. Voltar para app de logs
7. Filtrar por "PlayerEmbedAPI"
8. Exportar logs

## 🎯 O Que Procurar nos Logs

### ✅ Logs de Sucesso (devem aparecer)

```
PlayerEmbedAPI: 🚀🚀🚀 EXTRACT CHAMADO! IMDB: ttXXXXXXX
PlayerEmbedAPI: 📱 Iniciando extração na Main thread
PlayerEmbedAPI: ✅ Context obtido: Application
PlayerEmbedAPI: 🌐 Loading: https://viewplayer.online/filme/ttXXXXXXX
```

### 🎯 Logs de Captura (o mais importante)

```
PlayerEmbedAPI: 🎯 Captured: https://...sssrr.org/?timestamp=...
PlayerEmbedAPI: 📹 Captured: https://storage.googleapis.com/.../video.mp4
```

### ❌ Logs de Erro (não devem aparecer)

```
PlayerEmbedAPI: ❌ Erro ao obter Context
PlayerEmbedAPI: ❌ IMDB ID não encontrado
PlayerEmbedAPI: ⏱️ Timeout
```

## 📊 Análise Rápida

### Se Aparecer "Captured"

✅ **BOM**: WebView capturou URL  
❓ **Verificar**: Qual URL foi capturada?

**URLs corretas**:
- `https://storage.googleapis.com/.../video.mp4`
- `https://subdomain.sssrr.org/?timestamp=...&id=...`

**URLs incorretas**:
- `https://playerembedapi.link/?v=...` (não é do vídeo)
- `https://viewplayer.online/...` (página, não vídeo)

### Se NÃO Aparecer "Captured"

❌ **RUIM**: WebView não capturou nada  
❓ **Verificar**: Por que não capturou?

**Possíveis causas**:
- Timeout (30s não foi suficiente)
- Elemento não encontrado
- JavaScript não executou
- Detecção de automação

## 🛠️ Próximos Passos Baseados nos Logs

### Cenário A: URL Capturada Correta

**Problema**: Headers incorretos

**Solução**: Adicionar headers ao ExtractorLink
```kotlin
this.headers = mapOf(
    "User-Agent" to "Mozilla/5.0...",
    "Origin" to "https://viewplayer.online",
    "Referer" to "https://viewplayer.online/"
)
```

### Cenário B: URL Capturada Intermediária

**Problema**: URL precisa seguir redirect

**Solução**: Seguir redirect antes de retornar
```kotlin
val finalUrl = app.get(url, allowRedirects = true).url
```

### Cenário C: Nenhuma URL Capturada

**Problema**: Timeout ou elemento não encontrado

**Solução**: Aumentar timeout ou melhorar seletor
```kotlin
withTimeoutOrNull(45000) { // 45s em vez de 30s
    extractionJob?.await()
}
```

### Cenário D: Erro de Context

**Problema**: Não conseguiu obter Context do Android

**Solução**: Método alternativo de obter Context
```kotlin
val context = AndroidContextHolder.getContext()
```

## 📝 Template de Relatório

Depois de capturar logs, preencha:

```
ERRO: ERROR_CODE_IO_BAD_HTTP_STATUS (2004)

LOGS ENCONTRADOS:
[ ] "EXTRACT CHAMADO" - SIM/NÃO
[ ] "Context obtido" - SIM/NÃO
[ ] "Loading: https://..." - SIM/NÃO
[ ] "Captured: https://..." - SIM/NÃO

SE CAPTURED = SIM:
URL capturada: _________________________________
Formato: [ ] googleapis.com [ ] sssrr.org [ ] outro

SE CAPTURED = NÃO:
Último log antes do erro: _____________________
Tempo decorrido: _______ segundos

ERROS VISTOS:
_____________________________________________
_____________________________________________

CONCLUSÃO:
[ ] Cenário A - Headers incorretos
[ ] Cenário B - URL intermediária
[ ] Cenário C - Timeout
[ ] Cenário D - Context error
[ ] Outro: ___________________________________
```

## 💡 Dica Final

Se não conseguir capturar logs de jeito nenhum, podemos tentar uma abordagem diferente:

1. Testar PlayerEmbedAPI no browser manualmente
2. Capturar URL do vídeo no DevTools
3. Comparar com URL que código está gerando
4. Ajustar código baseado na diferença

---

**Próxima ação**: Conectar USB e executar comandos acima, OU usar app de logs no Android
