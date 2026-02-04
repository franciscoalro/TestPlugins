# Análise de Logs ADB - MaxSeries v260

## 📱 Dispositivo
- **IP:** 192.168.0.103:40529
- **App:** CloudStream Prerelease
- **Data:** 2026-02-03 23:33

---

## ✅ O que está funcionando

### Carregamento de categorias
```
D MaxSeriesProvider: ✅ Família: 30 items (página 1)
D MaxSeriesProvider: ✅ Em Alta: 30 items (página 1)
D MaxSeriesProvider: ✅ Adicionados Recentemente: 36 items (página 1)
D MaxSeriesProvider: ✅ Documentário: 30 items (página 1)
D MaxSeriesProvider: ✅ Comédia: 30 items (página 1)
D MaxSeriesProvider: ✅ Animação: 30 items (página 1)
D MaxSeriesProvider: ✅ Fantasia: 30 items (página 1)
D MaxSeriesProvider: ✅ Crime: 30 items (página 1)
D MaxSeriesProvider: ✅ Drama: 30 items (página 1)
... (todas as 18 categorias carregando)
```

### Detalhes de séries
```
D MaxSeriesProvider: 📺 Temporadas encontradas: 6
D MaxSeriesProvider: ✅ Total de episódios: 123
```

---

## ❌ Problema identificado

### Extração de vídeo falhando
```
E MaxSeriesProvider: 🔥 LOADLINKS CHAMADO! DATA: 
  https://playerthree.online/embed/world-enduro-super-series-wess/|episodio|175297|8738

D MaxSeriesProvider: 🔍 Analisando HTML (5692 chars)
D MaxSeriesProvider: 📋 Total sources extraídas (v184): 0 - []
E MaxSeriesProvider: ❌ Nenhuma source encontrada!
```

---

## 🔍 Diagnóstico

| Componente | Status |
|------------|--------|
| Navegação/Categorias | ✅ OK |
| Detalhes de séries | ✅ OK |
| Lista de episódios | ✅ OK |
| Extração de links | ❌ FALHANDO |

### Possíveis causas
1. **Regex desatualizado** - Site mudou estrutura HTML
2. **Proteção anti-bot** - Cloudflare ou similar bloqueando
3. **URL de embed mudou** - playerthree.online alterou endpoint
4. **Falta de headers** - Referer ou User-Agent necessários

---

## 📁 Arquivos de log

- **Log completo:** `cloudstream_logs_20260203_233309.txt` (67 MB)
- **Log filtrado:** `cloudstream_filtered_logs.txt`
- **Este relatório:** `ADB_ANALYSIS_V260.md`

---

## 🛠️ Próximos passos recomendados

1. Verificar se o site maxseries.pics está acessível
2. Atualizar regex de extração de links
3. Adicionar headers necessários (Referer)
4. Implementar retry com delay

---

*Análise gerada automaticamente via ADB*
