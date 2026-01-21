# MaxSeries v144 - Fix: Regex Simplificado

## 🔧 Correções Críticas

### Problema v143
- Pipeline WebVideoCast-like estava muito complexo
- Regex não estava encontrando nenhum link
- Tentativa de usar `resolver.interceptedUrls` (não existe na API)

### Solução v144
- **Voltou ao regex simples que funcionava**: `https?://[^/]+/v4/[^"'<>\s]+`
- Removida classificação de pipeline complexa
- Verificação direta em `response.url`
- Mantida conversão de arquivos .woff para index.txt

## 📋 Mudanças Técnicas

### MegaEmbedExtractorV7.kt
```kotlin
// Regex ultra-simplificado
val resolver = WebViewResolver(
    interceptUrl = Regex("""https?://[^/]+/v4/[^"'<>\s]+""", RegexOption.IGNORE_CASE),
    script = captureScript,
    timeout = 10_000L
)

// Verificação direta
val captured = response.url
if (!captured.contains("/v4/")) {
    return
}
```

### Lógica de Detecção
1. Captura URL via WebView
2. Verifica se contém `/v4/`
3. Converte .woff → index.txt se necessário
4. Valida formato (index.txt ou cf-master)
5. Adiciona ao cache

## 🎯 Objetivo
Restaurar funcionalidade básica de captura de links que estava funcionando na v141, sem complexidade desnecessária.

## 📦 Instalação
```
https://github.com/franciscoalro/TestPlugins/releases/download/v144/MaxSeries.cs3
```

## 🧪 Como Testar
1. Abrir qualquer série/filme no MaxSeries
2. Verificar logs: `adb logcat | findstr "MegaEmbedV7"`
3. Procurar por: `✅ index.txt encontrado` ou `✅ cf-master encontrado`
4. Confirmar que links estão sendo capturados

---
**Data**: 2026-01-20
**Build**: SUCCESSFUL
