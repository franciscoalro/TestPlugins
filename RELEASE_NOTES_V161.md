# 🚀 MaxSeries v161 - Smart Navigation

## 📅 Data: 22/01/2026 23:15

---

## 🧠 CORREÇÃO PARA SERIES MULTI-EPISÓDIO

### 🕵️‍♂️ O Problema
Em séries como "Sandokan", o site usa um iframe ÚNICO para temporaradas inteiras (Ex: `/embed/sandokan/`).
O CloudStream tentava extrair vídeo desse iframe, mas ele mostrava uma **lista de episódios**, e não o vídeo.
O Extrator falhava porque não sabia clicar na lista.

### ✅ A Solução (v161)
1.  **Smart Hash URL:** O Provider agora reconstrói a URL exata do episódio usando Hash Identifier (`#season_episode`), que força o site a carregar o episódio correto (Ex: `#12962_255703`).
2.  **Auto-Clicker:** O script do Extrator agora detecta botões "Player #1" ou "Dublado" e **clica automaticamente** neles se a reprodução não começar sozinha.

### 🧪 Resultado
Isso resolve o problema de "Tela Preta com Lista" ou "Fica carregando infinito" em séries.
Também mantém o **Regex Universal /v4/** da v160.

---

## ⚡ Atualização Crítica
Necessária para qualquer série hospedada no PlayerThree/MegaEmbed.
