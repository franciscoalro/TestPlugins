# 🎬 Guia de Extração de Vídeos - MaxSeries

## 📋 Scripts Disponíveis

### 1. **extract_video_easy.py** (Básico - Rápido)
Extração simples via HTTP, sem navegador.

**Uso:**
```bash
python extract_video_easy.py https://maxseries.one/episodio/12345
```

**Vantagens:**
- ✅ Rápido (2-5 segundos)
- ✅ Não requer dependências pesadas
- ✅ Funciona para players simples

**Limitações:**
- ❌ Não captura vídeos que requerem JavaScript
- ❌ Não funciona com players protegidos

---

### 2. **extract_video_advanced.py** (Avançado - Completo)
Extração com Selenium + captura de tráfego de rede.

**Instalação:**
```bash
pip install selenium webdriver-manager
```

**Uso:**
```bash
python extract_video_advanced.py https://maxseries.one/episodio/12345
```

**Vantagens:**
- ✅ Captura vídeos de players complexos (MegaEmbed, PlayerEmbedAPI)
- ✅ Intercepta requisições de rede
- ✅ Detecta M3U8, MP4, e segmentos disfarçados (.woff2, .txt)

**Limitações:**
- ⚠️  Mais lento (10-20 segundos)
- ⚠️  Requer Chrome instalado

---

## 🎯 Fluxo Recomendado

```
1. Tente primeiro: extract_video_easy.py
   ↓
2. Se falhar: extract_video_advanced.py
   ↓
3. Se ainda falhar: Use o plugin CloudStream (MaxSeries v162)
```

---

## 🔧 Solução de Problemas

### ❌ "Nenhum player encontrado"
- Verifique se a URL está correta
- Confirme que é uma página de episódio (não série/filme)

### ❌ "M3U8 não encontrado"
- Use o script avançado (`extract_video_advanced.py`)
- Alguns players requerem interação manual

### ❌ "Erro ao acessar URL"
- Verifique sua conexão com a internet
- O site pode estar bloqueando requisições automatizadas

---

## 📊 Tipos de Players Suportados

| Player | Script Básico | Script Avançado | Plugin CloudStream |
|--------|---------------|-----------------|-------------------|
| **MegaEmbed** | ⚠️ Parcial | ✅ Sim | ✅ Sim |
| **PlayerEmbedAPI** | ❌ Não | ✅ Sim | ✅ Sim |
| **DoodStream** | ⚠️ Parcial | ✅ Sim | ✅ Sim |

---

## 🚀 Exemplos Práticos

### Exemplo 1: Extração Rápida
```bash
# Tentar extração básica
python extract_video_easy.py https://maxseries.one/episodio/258444

# Saída esperada:
# 🎥 Player 1 - MegaEmbed
#    URL: https://megaembed.cc/embed/abc123
#    ✅ M3U8: https://cdn.megaembed.cc/video.m3u8
```

### Exemplo 2: Extração Avançada
```bash
# Extração com captura de rede
python extract_video_advanced.py https://maxseries.one/episodio/258444

# Saída esperada:
# 📡 Capturado: https://cdn.megaembed.cc/playlist.m3u8
# 📡 Capturado: https://cdn.megaembed.cc/segment001.ts
```

---

## 🔗 Links Úteis

- **Plugin CloudStream:** [MaxSeries.cs3](./MaxSeries.cs3)
- **Documentação Completa:** [README.md](./README.md)
- **Changelog:** [RELEASE_NOTES_V162.md](./RELEASE_NOTES_V162.md)

---

## ⚙️ Configuração Avançada

### Modificar Timeout (Script Avançado)
Edite `extract_video_advanced.py`, linha 95:
```python
time.sleep(8)  # Altere para 15 se o vídeo demorar a carregar
```

### Desabilitar Modo Headless (Ver navegador)
Edite `extract_video_advanced.py`, linha 25:
```python
# chrome_options.add_argument('--headless')  # Comente esta linha
```

---

## 📝 Notas Importantes

1. **Respeite os Termos de Uso** do site MaxSeries
2. **Não redistribua** vídeos protegidos por direitos autorais
3. **Use apenas para fins educacionais** e testes

---

**Versão:** 1.0  
**Última Atualização:** 23/01/2026  
**Compatibilidade:** MaxSeries v162+
