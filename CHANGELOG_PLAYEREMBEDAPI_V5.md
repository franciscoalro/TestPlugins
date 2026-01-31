# Changelog - PlayerEmbedAPI v5.0

**Data:** 31 de Janeiro de 2026  
**Versão:** v5.0  
**Status:** Pronto para Release

---

## 🚀 Novidades

### Sistema de Extração Multi-Estratégia
O novo extractor implementa 4 estratégias hierárquicas para máxima compatibilidade:

1. **API (base64 + AES-CTR)** - Extração criptográfica completa
2. **ShortIcu** - Redirecionamento via iframe
3. **Regex HTML** - Extração direta do HTML
4. **WebView** - Último recurso com navegador emulado

### 📺 Suporte a Mais Qualidades

```kotlin
// Antes (v4.4)
RES_ID_QUALITY = mapOf(
    2 to Qualities.P360,
    4 to Qualities.P720,
    5 to Qualities.P1080
)

// Depois (v5.0)
RES_ID_QUALITY = mapOf(
    1 to Qualities.P360,
    2 to Qualities.P480,   // NOVO
    3 to Qualities.P720,
    4 to Qualities.P1080,
    5 to Qualities.P2160   // 4K - NOVO
)
```

---

## 🔒 Correções de Segurança

### SSL/TLS
**Antes (INSEGURO):**
```kotlin
override fun onReceivedSslError(view, handler, error) {
    handler?.proceed() // ⚠️ IGNORA ERROS SSL!
}
```

**Depois (SEGURO):**
```kotlin
override fun onReceivedSslError(view, handler, error) {
    Log.e(TAG, "SSL Error: $error")
    handler?.cancel() // ✅ CANCELA REQUISIÇÃO INSEGURA
}
```

### Dados Sensíveis
**Antes:**
```kotlin
Log.d("LinkDecryptor", "preKey: $preKey")     // ❌ Chave exposta
Log.d("LinkDecryptor", "md5Hash: $md5Hash")   // ❌ Hash exposto
```

**Depois:**
```kotlin
Log.d("LinkDecryptor", "Decrypting: ${encryptedBytes.size} bytes") // ✅ Seguro
```

---

## ⚡ Melhorias de Performance

### Regex Compilados
```kotlin
// Antes: Compilado a cada chamada
val pattern = Regex("""...""") // ❌ Ineficiente

// Depois: Compilado uma vez
companion object {
    private val PATTERN = Regex("""...""") // ✅ Eficiente
}
```

### Gerenciamento de Coroutines
```kotlin
// Antes: Memory leak garantido
GlobalScope.launch { ... }

// Depois: Scope controlado
CoroutineScope(Dispatchers.IO).launch { ... }
```

---

## 🛡️ Validação de URLs

Novo sistema de validação para evitar URLs inválidas:

```kotlin
private fun isValidVideoUrl(url: String): Boolean {
    // Verifica protocolo HTTPS
    // Verifica domínios permitidos
    // Verifica extensões de vídeo
}
```

Domínios permitidos:
- `googleapis.com`
- `sssrr.org`
- CDNs conhecidos

---

## 📁 Arquivos Modificados/Criados

### Novos Arquivos
- `PlayerEmbedAPIExtractorV5.kt` - Extractor principal
- `PlayerEmbedAPIWebViewExtractorV5.kt` - WebView seguro
- `PlayerEmbedAPIV5Test.kt` - Testes unitários

### Modificados
- `MaxSeriesProvider.kt` - Atualizado para v5.0
- `LinkDecryptor.kt` - Removido logging sensível
- `build.gradle.kts` - Versão 253

### Scripts de Teste (Python)
- `test_playerembedapi_v5.py` - Teste individual
- `test_playerembedapi_batch.py` - Teste em batch
- `validate_implementation.py` - Validação Python vs Kotlin

---

## 🧪 Testes

### Testes Unitários Kotlin
```bash
.\gradlew.bat :MaxSeries:test --tests "*PlayerEmbedAPIV5Test*"
```

Cobertura:
- ✅ Validação de URLs
- ✅ Detecção de qualidade
- ✅ Extração de base64
- ✅ Processamento de JSON escapes

### Testes Python
```bash
# Teste individual
python test_playerembedapi_v5.py "<URL>"

# Teste em batch
python test_playerembedapi_batch.py urls.txt

# Validação
python validate_implementation.py
```

---

## 📊 Comparativo de Versões

| Aspecto | v4.4 | v5.0 | Melhoria |
|---------|------|------|----------|
| Estratégias | 1 | 4 | +300% |
| Qualidades | 3 | 5 | +67% |
| Segurança SSL | ❌ | ✅ | Crítica |
| Logs seguros | ❌ | ✅ | Crítica |
| Regex compilados | ❌ | ✅ | Performance |
| GlobalScope | ✅ | ❌ | Stability |
| Validação de URLs | ❌ | ✅ | Robustez |
| Testes unitários | ❌ | ✅ | Qualidade |

---

## 🔄 Fluxo de Fallback

```
URL do PlayerEmbedAPI
        │
        ▼
┌─────────────────┐
│  1. API         │ ──► Base64 → AES-CTR → JSON
│  (mais rápida)  │
└────────┬────────┘
         │ Falha
         ▼
┌─────────────────┐
│  2. ShortIcu    │ ──► Iframe → Google Storage
│  (sem WebView)  │
└────────┬────────┘
         │ Falha
         ▼
┌─────────────────┐
│  3. Regex       │ ──► HTML direto
│  (direto)       │
└────────┬────────┘
         │ Falha
         ▼
┌─────────────────┐
│  4. WebView     │ ──► Automação navegador
│  (último recurso)│
└─────────────────┘
```

---

## 📝 Como Usar

### Build Automático
```powershell
# Build completo com testes
.\build_with_tests.ps1

# Build rápido (sem testes)
.\build_with_tests.ps1 -SkipTests

# Build para release
.\build_with_tests.ps1 -Release
```

### Instalação Manual
1. Execute o build
2. Copie `MaxSeries/build/outputs/*.cs3` para o CloudStream
3. Ou use o script `auto-update-repo.ps1`

---

## ⚠️ Breaking Changes

- O novo extractor usa `PlayerEmbedAPIExtractorV5` ao invés de `PlayerEmbedAPIExtractor`
- A versão mínima do CloudStream permanece a mesma
- URLs de vídeo são validadas antes de retornar (pode rejeitar URLs que antes passavam)

---

## 🐛 Known Issues

Nenhum issue conhecido no momento.

---

## 🙏 Créditos

- Implementação baseada na análise do protocolo PlayerEmbedAPI
- Testes validados com Python para garantir consistência
- Correções de segurança revisadas

---

**Próxima Versão:** v5.1 (planejado)
- Cache distribuído
- Retry automático com backoff exponencial
- Métricas de performance
