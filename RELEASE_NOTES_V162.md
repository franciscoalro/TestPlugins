# 🚀 MaxSeries v162 - Correção Crítica de Parser

## 📅 Data: 22/01/2026 23:40

---

## 🛠️ O QUE MUDOU?

### 1. 🐛 Fix: Parse de Episódios
O site MaxSeries mudou a estrutura HTML da lista de episódios.
- **Antes:** Usava atributos `data-episode-id` e `data-season-id`.
- **Agora:** Usa links diretos com Hash: `<a href="#SEASONID_EPISODEID">`.

A versão 161 falhava em detectar os IDs, causando links quebrados ou loop infinito.
A **v162 corrige isso**, lendo corretamente o formato `#123_456`.

### 2. ⚡ Todas as melhorias da v161 inclusas
- Regex Universal (captura qualquer vídeo /v4/ ou .woff2)
- Auto-Clicker embutido
- Navegação Inteligente por Hash

---

## ⚠️ Obrigatório Atualizar
Se você usa o MaxSeries, esta atualização é obrigatória para que as séries funcionem.
