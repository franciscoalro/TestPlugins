# MaxSeries v254 - Production Release

## Release Notes - 31 de Janeiro de 2026

### ✅ PlayerEmbedAPI v5.0 - Validado para Produção

Esta release marca a versão **v254** do MaxSeries com o **PlayerEmbedAPI v5.0** completamente testado e validado.

---

## 🧪 Testes Automatizados

| Categoria | Testes | Status |
|-----------|--------|--------|
| Unit Tests | 52/52 | ✅ 100% |
| HTTP Tests | 5/5 | ✅ 100% |
| Structure Validation | 10/10 | ✅ 100% |

### Detalhes dos Testes
- **Base64 Extraction**: 8/8 passando
- **AES-CTR Decryption**: 6/6 passando
- **URL Validation**: 17/17 passando
- **Quality Detection**: 11/11 passando
- **JSON Escape Processing**: 10/10 passando

---

## 🔒 Melhorias de Segurança

- ✅ SSL Error Handling: `handler?.cancel()` implementado
- ✅ Removido logging de dados sensíveis
- ✅ Validação de URLs antes de retornar
- ✅ Sanitização de inputs

---

## ⚡ Melhorias de Performance

- ✅ Regex compilados em `companion object`
- ✅ Sistema de cache para URLs de vídeo
- ✅ CoroutineScope estruturado (não GlobalScope)
- ✅ 4 estratégias de fallback otimizadas

---

## 🎯 Estratégias de Extração (v5.0)

1. **API Strategy** (mais rápida): Base64 + AES-CTR decryption
2. **ShortIcu Strategy**: Redirecionamento + parsing
3. **Regex Strategy**: Parsing HTML direto
4. **WebView Strategy** (mais confiável): Interceptação de rede

---

## 📦 Informações do Build

```
Version: 254
File: MaxSeries.cs3
Size: 579,063 bytes (565 KB)
SHA256: 5c02206aec9125c0449019e9bc21c5e84dabd6dc3e5506fba7acbe157d6d2c2c
Build Date: 31/01/2026 15:30
```

---

## 🔗 Links

- **Download**: https://github.com/franciscoalro/TestPlugins/releases/download/v254/MaxSeries.cs3
- **Repository**: https://github.com/franciscoalro/TestPlugins
- **GitHub Pages**: https://franciscoalro.github.io/CloudstreamRepo/

---

## 📝 Changelog Completo

### v254 (31/01/2026)
- ✅ Production Release - PlayerEmbedAPI v5.0 Validated
- 🧪 52 unit tests passando (100% coverage de extração)
- 🔒 Security audit: SSL fix, no sensitive logging
- ⚡ Performance: Regex compilados, cache implementado
- 🎯 4 estratégias de fallback testadas automaticamente

### v253 (31/01/2026)
- 🚀 PlayerEmbedAPI v5.0: Enhanced Detection & Security
- 🔒 Removido logging de dados sensíveis
- 🎯 Múltiplas estratégias de extração (API, ShortIcu, Regex, WebView)
- 🛡️ Validação de URLs antes de retornar
- ⚡ Performance: Regex compilados em companion object

---

**Status**: ✅ Aprovado para Produção
