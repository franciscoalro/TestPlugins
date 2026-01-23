# 🔥 HOTFIX: MaxSeries v157 - Correção de Timeout

## ❌ PROBLEMA IDENTIFICADO

**Player não iniciava** devido a:
```
MegaEmbedV8: ❌ Erro: Job was cancelled
kotlinx.coroutines.JobCancellationException: Job was cancelled
```

### **Causa Raiz:**
- CloudStream tem timeout padrão de ~60 segundos
- MegaEmbed V8 tinha timeout de 120 segundos
-  CloudStream cancelava o job ANTES do MegaEmbed completar

---

## ✅ CORREÇÃO APLICADA

### **Timeout Reduzido: 120s → 60s**

**Arquivo**: `MegaEmbedExtractorV8.kt` linha 225

**Antes:**
```kotlin
timeout = 120_000L // 120s (2 minutos)
```

**Depois:**
```kotlin
timeout = 60_000L // 60s (evita cancelamento do CloudStream)
```

---

## 📊 IMPACTO

### **Antes (v156):**
```
1. CloudStream chama MegaEmbed
2. WebView inicia
3. CloudStream aguarda 60s
4. CloudStream CANCELA (timeout)
5. MegaEmbed ainda processando (até 120s)
6. Job cancelled
7. Player NÃO inicia ❌
```

### **Agora (v157):**
```
1. CloudStream chama MegaEmbed
2. WebView inicia
3. Fetch/XHR hooks capturam URL (2-5s esperado)
4. MegaEmbed retorna URL dentro de 60s
5. CloudStream recebe URL
6. Player INICIA ✅
```

---

## 🎯 CHANGELOG

### **v157 (22/01/2026 20:57)**
```
[HOTFIX] Timeout Fix
- Reduzido timeout: 120s → 60s
- Fix: Job was cancelled
- Previne CloudStream cancelar antes de completar
```

### **v156 (22/01/2026 20:10)** 
```
[FEATURE] MegaEmbed V8
- Fetch/XHR Hooks
- Regex ultra flexível
- 7+ fallbacks
- Taxa esperada: 95%+
```

---

## 🚀 COMO ATUALIZAR

### **Método 1: CloudStream (Recomendado)**
```
1. Settings → Extensions → Repositories
2. Atualizar repositório (pull down)
3. MaxSeries → Update to v157
4. Testar reprodução
```

### **Método 2: Manual**
```
1. Download: https://github.com/franciscoalro/TestPlugins/releases/download/v157/MaxSeries.cs3
2. CloudStream → Settings → Extensions
3. Install → Selecionar arquivo .cs3
```

---

## 🧪 TESTE APÓS ATUALIZAÇÃO

1. Abrir CloudStream
2. Escolher episódio do MaxSeries
3. Clicar em reproduzir
4. Aguardar (deve iniciar em 2-5s)
5. Verificar se player inicia

---

## 📝 LOGS ESPERADOS (v157)

**Sucesso:**
```
MegaEmbedV8: === MEGAEMBED V8 v157 FETCH/XHR INTERCEPTION ===
MegaEmbedV8: Input: https://megaembed.link/#...
MegaEmbedV8: 🌐 Iniciando WebView com FETCH/XHR INTERCEPTION...
MegaEmbedV8: 📜 Script capturou: https://...
MegaEmbedV8: ✅ URL válida (200): https://...
```

**Sem mais "Job was cancelled"!**

---

## ⚠️ SE AINDA NÃO FUNCIONAR

Se player ainda não iniciar após atualizar para v157:

1. **Verificar versão instalada**:
   ```
   Settings → Extensions → MaxSeries → Version: 157
   ```

2. **Capturar logs**:
   ```powershell
   C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -d > logs_v157.txt
   ```

3. **Reportar** com:
   - Logs
   - URL do episódio
   - Tempo que aguardou

---

## 📊 ARQUIVOS MODIFICADOS

```
MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/MegaEmbedExtractorV8.kt
  - Linha 225: timeout = 60_000L (antes: 120_000L)

MaxSeries/build.gradle.kts
  - version = 157 (antes: 156)
  - description atualizada
```

---

## ✅ BUILD INFO

```
Data: 22/01/2026 20:57
Versão: 157
Arquivo: MaxSeries.cs3 (182 KB)
Git: [commit hash]
```

---

**Status**: ✅ Correção aplicada  
**Teste**: Pendente  
**Disponibilidade**: Após release v157
