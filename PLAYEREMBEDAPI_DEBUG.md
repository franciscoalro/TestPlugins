# 🔍 PlayerEmbedAPI - Problema de Extração

**Data:** 2026-02-01 23:26  
**Tipo:** Debugging de Plugin (não repositório)

---

## 📊 Análise dos Logs

**O que funciona:**
- ✅ Plugin MaxSeries baixa e instala
- ✅ Acessa `playerembedapi.link/?v=rTxfmoIhd` (200 OK)
- ✅ Recebe HTML da página

**O que falha:**
- ❌ URL do vídeo `ixx272l.cloudatacdn.com` retorna 0 bytes
- ❌ Player não mostra vídeo

---

## 🚨 Problema Identificado

**Tipo:** Código do extrator PlayerEmbedAPI

**Causa possível:**
1. Extrator não está capturando URL correta do HTML
2. URL do vídeo expira muito rápido
3. Token de autenticação inválido
4. Site mudou estrutura HTML

---

## 🔧 Solução

**Isto NÃO é problema de repositório!**

Você precisa:
1. **Debugar o código** do extrator em `MaxSeries/src/main/kotlin/.../extractors/`
2. **Testar qual versão funciona** (V5, V6, V7, V8)
3. **Atualizar regex/parsing** se site mudou
4. **Recompilar plugin** com fix

---

## 📁 Arquivos Relevantes

```
MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/
├── PlayerEmbedAPIExtractor.kt
├── PlayerEmbedAPIExtractorV5.kt
├── PlayerEmbedAPIExtractorV6.kt
├── PlayerEmbedAPIExtractorV7.kt
├── PlayerEmbedAPIExtractorV8.kt
├── PlayerEmbedAPIWebViewExtractor.kt
└── PlayerEmbedAPIWebViewExtractorV5.kt
```

---

## ✅ Repositório Está Correto

**9/11 plugins funcionam = repositório OK!**

Este é um problema de **código do plugin MaxSeries**, não de configuração.

---

**Quer ajuda para debugar o código do extrator?**
