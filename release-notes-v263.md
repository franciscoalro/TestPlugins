# MaxSeries v263 - PlayerEmbedAPI Otimizado (Timeout Fix + Prioridade V8)

**Data:** 04/02/2026  
**Versão:** v263  
**Tamanho:** ~730 KB

---

## 🚀 Novidades

### 1. PlayerEmbedAPI V8 como Prioridade #1
- **Fluxo otimizado**: V8 (Pure HTTP) é tentado **primeiro** (~50-100ms)
- **V7 (WebView)** só é usado como **fallback** se V8 falhar
- **Resultado**: Carregamento muito mais rápido dos vídeos

### 2. Timeout do V7 Aumentado
- **Anterior**: 15 segundos (causava timeouts frequentes)
- **Novo**: 25 segundos (mais tempo para WebView carregar)

### 3. Melhorias na Extração
- Removida tentativa dupla desnecessária quando V8 funciona
- Logs mais claros sobre qual método foi usado
- Código mais limpo e eficiente

---

## 🔧 Mudanças Técnicas

| Componente | Alteração |
|------------|-----------|
| `PlayerEmbedAPIExtractorV7.kt` | `TIMEOUT_SECONDS`: 15L → 25L |
| `MaxSeriesProvider.kt` | Ordem de extração invertida: V8 primeiro, V7 fallback |

---

## 📊 Comparativo de Performance

| Método | Tempo Médio | Status |
|--------|-------------|--------|
| V8 (Pure HTTP) | ~50-100ms | ✅ **Principal** |
| V7 (WebView) | Até 25s | 🔄 **Fallback** |

---

## 🐛 Correções

- **Fix**: Timeout do PlayerEmbedAPI v7 causando exception null
- **Fix**: Carregamento lento quando V7 era tentado primeiro
- **Fix**: Melhor tratamento de erro quando ambos métodos falham

---

## 📝 Fluxo de Extração Atual

```
PlayerEmbedAPI
├── 🚀 FASE 1: V8 (Pure HTTP) - ~50-100ms
│   ├── ✅ Sucesso: Retorna links imediatamente
│   └── ❌ Falha: Vai para FASE 2
│
└── 🔄 FASE 2: V7 (WebView - 25s timeout)
    └── Fallback mais lento mas confiável
```

---

## 📦 Arquivos

- `MaxSeries.cs3` - Plugin compilado
- `plugins.json` - Manifesto atualizado

---

**Instalação:** Baixe o arquivo `MaxSeries.cs3` e instale no Cloudstream3.
