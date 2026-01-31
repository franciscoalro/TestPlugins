# Guia de Debug - Análise de Logs do CloudStream

## 📱 Como Capturar Logs

### Método 1: Android Studio (Logcat) - RECOMENDADO

1. **Conecte o dispositivo** via USB com debug ativado
2. **Abra o Android Studio**
3. **Clique em "Logcat"** (aba inferior)
4. **Filtre por tag:** `PlayerEmbedAPI`
5. **Reproduza o erro** no CloudStream

**Filtros úteis:**
```
tag:PlayerEmbedAPI-v5
package:com.lagradost.cloudstream3
```

### Método 2: ADB (Linha de Comando)

```bash
# Conectar ao dispositivo
adb devices

# Capturar logs em tempo real
adb logcat -s PlayerEmbedAPI-v5:D

# Salvar logs em arquivo
adb logcat -d > cloudstream_logs.txt

# Filtrar apenas CloudStream
adb logcat | findstr "cloudstream"
```

### Método 3: Apps de Terceiros (Sem PC)

- **Logcat Reader** (Google Play)
- **MatLog** (F-Droid)
- Requer root em alguns dispositivos

---

## 🔍 O que Procurar nos Logs

### ✅ Sinais de Sucesso

```
🌐 PRIORIDADE 1 - PlayerEmbedAPI v5.0: https://playerembedapi.link/...
✅✅✅ PlayerEmbedAPI v5.0: SUCESSO
📺 Encontradas X fontes
📺 URL: https://storage.googleapis.com/...
```

### ⚠️ Avisos (Fallback ativado)

```
⚠️  Não encontrou base64 'datas'
⚠️  Extração via API falhou: ...
🔄 Tentando ShortIcu...
```

### ❌ Erros

```
❌ Erro no request: ...
❌ Falha na decriptação AES-CTR
❌ Nenhuma URL encontrada
```

---

## 📊 Fluxo Esperado nos Logs

```
[1] 🌐 PRIORIDADE 1 - PlayerEmbedAPI v5.0
[2] ℹ️  Cache MISS (primeira vez)
[3] ℹ️  [1/4] Tentando extração via API...
[4] ℹ️  Obtendo HTML...
[5] ℹ️  Pattern X funcionou!
[6] ℹ️  Key MD5: a3f5... (truncado)
[7] 🔓 Decrypting media: 1234 bytes
[8] 📺 Encontradas 3 fontes:
[9]    [0] 1080p - https://...
[10]   [1] 720p - https://...
[11]   [2] 360p - https://...
[12] ✅✅✅ PlayerEmbedAPI v5.0: SUCESSO
[13] ℹ️  Cache HIT (segunda vez)
```

---

## 🎯 Interpretação de Resultados

### Cenário 1: Tudo Funciona ✅
```
Estratégia 1 (API) funciona → Links retornados → Vídeo reproduz
```

### Cenário 2: Fallback para ShortIcu ⚠️
```
Estratégia 1 falha → 🔄 Tentando ShortIcu → Links retornados
```
**Status:** Funcional, mas não ideal (mais lento)

### Cenário 3: Fallback para Regex ⚠️
```
Estratégia 1 e 2 falham → 🔄 Regex direto → Links retornados
```
**Status:** Funcional, menos confiável

### Cenário 4: Fallback para WebView ⚠️
```
Estratégias 1-3 falham → 🔄 WebView → Links retornados
```
**Status:** Funcional, mas muito lento

### Cenário 5: Todas Falham ❌
```
Todas as estratégias falham → ❌ Nenhuma URL encontrada
```
**Ação:** Reportar bug com logs

---

## 🐛 Problemas Comuns

### "SSL Error"
**Significado:** Certificado inválido
**Solução:** Verificar se handler?.cancel() está funcionando

### "Timeout"
**Significado:** Servidor demorou para responder
**Solução:** Aumentar timeout ou verificar conexão

### "Cache HIT" mas não reproduz
**Significado:** URL expirou no cache
**Solução:** Limpar cache do app

### "Pattern X não funcionou"
**Significado:** Site mudou estrutura HTML
**Solução:** Atualizar regex no código

---

## 📤 Como Exportar Logs

### Para Análise (Me enviar)

```bash
# Método completo
adb logcat -d -v time > cloudstream_complete.log

# Método filtrado (recomendado)
adb logcat -d -s PlayerEmbedAPI-v5:D > playerembedapi.log
```

Ou use o script:
```powershell
.\capture_logs.ps1
```

---

## 🎨 Cores nos Logs

| Emoji | Significado | Ação |
|-------|-------------|------|
| 🌐 | Início da extração | Normal |
| ℹ️  | Informação | Normal |
| ✅ | Sucesso | Normal |
| ⚠️  | Aviso/Alerta | Monitorar |
| ❌ | Erro | Investigar |
| 🔄 | Fallback ativado | Melhorar estratégia |
| 📺 | Vídeo encontrado | Sucesso |
| 🔓 | Decriptação | Normal |

---

## 📊 Métricas de Performance

**Tempos esperados:**
- Estratégia 1 (API): 2-5s
- Estratégia 2 (ShortIcu): 3-8s
- Estratégia 3 (Regex): 1-3s
- Estratégia 4 (WebView): 10-20s

**Se consistentemente > 15s:** Revisar código

---

## 🆘 Precisa de Ajuda?

1. Capture os logs
2. Salve em arquivo .txt
3. Anexe ao relatório de bug

**Template de report:**
```
Versão: v253
URL testada: https://...
Estratégia que funcionou: API/ShortIcu/Regex/WebView
Erro encontrado: [colar log]
```
