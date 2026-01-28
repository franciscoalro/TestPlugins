# ⚡ Quick Start - MaxSeries v219

## 🎯 TL;DR

**Status**: ✅ Código funcionando, aguardando conteúdo com PlayerEmbedAPI para teste

**Problema**: Conteúdo testado não tinha PlayerEmbedAPI disponível

**Solução**: Encontrar conteúdo válido e testar novamente

---

## 🚀 Teste Rápido (3 passos)

### 1️⃣ Encontrar Conteúdo

```powershell
.\find-playerembedapi-content.ps1
```

### 2️⃣ Testar no App

1. Abrir Cloudstream
2. Buscar conteúdo identificado
3. Selecionar episódio
4. Aguardar 20-30s

### 3️⃣ Verificar Logs

```powershell
.\test-v219-manual.ps1
```

Procurar por:
```
🌐🌐🌐 PLAYEREMBEDAPI DETECTADO!
🚀🚀🚀 EXTRACT CHAMADO!
🎯 Captured: ...
✅✅✅ PlayerEmbedAPI: X links via WebView
```

---

## ❓ FAQ Rápido

### PlayerEmbedAPI não aparece?

**R**: Conteúdo provavelmente não tem essa source. Use o script para encontrar conteúdo válido.

### Como saber se conteúdo tem PlayerEmbedAPI?

**R**: Abrir no browser, inspecionar (F12), buscar "playerembedapi" no HTML.

### MegaEmbed funciona mas PlayerEmbedAPI não?

**R**: Sistema está OK! Só precisa de conteúdo que tenha PlayerEmbedAPI.

### Quanto tempo demora?

**R**: 20-30 segundos para extrair URLs.

### Como capturar logs?

**R**: `.\test-v219-manual.ps1` ou `adb logcat | Select-String "MaxSeries|PlayerEmbedAPI"`

---

## 📊 Diagnóstico Rápido

```
✅ MegaEmbed funciona?
   └─ SIM → Sistema OK
      └─ PlayerEmbedAPI não aparece?
         └─ Conteúdo não tem essa source
            └─ Usar find-playerembedapi-content.ps1

❌ MegaEmbed não funciona?
   └─ Problema no sistema
      └─ Ver TROUBLESHOOTING_V219.md
```

---

## 🔗 Links Úteis

- **Documentação completa**: [README_V219_PLAYEREMBEDAPI.md](README_V219_PLAYEREMBEDAPI.md)
- **Troubleshooting**: [TROUBLESHOOTING_V219.md](TROUBLESHOOTING_V219.md)
- **Status completo**: [V219_FINAL_STATUS.md](V219_FINAL_STATUS.md)
- **Resumo visual**: [V219_RESUMO_VISUAL.md](V219_RESUMO_VISUAL.md)
- **Análise de logs**: [adb_logs_v219_diagnosis.md](adb_logs_v219_diagnosis.md)

---

## 🎯 Checklist

Antes de reportar problema:

- [ ] Versão é v219?
- [ ] MegaEmbed funciona?
- [ ] Conteúdo TEM PlayerEmbedAPI? (verificado no browser)
- [ ] Logs capturados?
- [ ] Script `find-playerembedapi-content.ps1` executado?

Se TODOS marcados → reportar bug  
Se algum NÃO marcado → seguir troubleshooting

---

## 💡 Dica

**O código está correto!** Se PlayerEmbedAPI não aparece, é porque o conteúdo não tem essa source. Use MegaEmbed que está funcionando perfeitamente enquanto procura conteúdo com PlayerEmbedAPI.

---

**Versão**: 219 | **Data**: 28 Jan 2026 | **Status**: ✅ Pronto
