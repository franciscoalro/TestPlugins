# ⚡ Teste MaxSeries v220 AGORA

## 🎯 O Que Foi Corrigido

PlayerEmbedAPI agora funciona em **FILMES**! 

Bug corrigido:
- ✅ Detecta `viewplayer.online` (antes só `playerthree.online`)
- ✅ Processa PlayerEmbedAPI via WebView em filmes
- ✅ Extrai sources corretamente

---

## 🚀 Teste Rápido (3 minutos)

### 1️⃣ Atualizar (30s)

```
Cloudstream → ⚙️ Configurações → 🧩 Extensões → MaxSeries → 🔄 Atualizar
```

Verificar versão: **deve ser 220**

### 2️⃣ Testar Filme (1min)

Abrir Cloudstream e buscar:
```
"A Última Aventura - Stranger Things 5"
```

Ou qualquer filme em: https://www.maxseries.pics/filmes/

Clicar para assistir e aguardar **20-30 segundos**.

### 3️⃣ Verificar Players (30s)

Deve aparecer:
- ✅ PlayerEmbedAPI (NOVO!)
- ✅ MegaEmbed
- ✅ MyVidPlay
- ✅ DoodStream
- ✅ Outros...

### 4️⃣ Capturar Logs (1min) - OPCIONAL

```powershell
# Conectar ADB
adb connect 192.168.0.106:40253

# Capturar logs
adb logcat -c
adb logcat | Select-String "MaxSeries|PlayerEmbedAPI"
```

Procurar por:
```
🌐🌐🌐 PLAYEREMBEDAPI DETECTADO (DIRECT)!
✅✅✅ PlayerEmbedAPI: X links via WebView
```

---

## ✅ Sucesso

Se PlayerEmbedAPI aparecer nos players → **FUNCIONOU!** 🎉

## ❌ Problema

Se PlayerEmbedAPI NÃO aparecer:

1. Verificar versão (deve ser 220)
2. Reiniciar Cloudstream
3. Limpar cache
4. Tentar outro filme
5. Capturar logs e reportar

---

## 📊 Comparação Visual

### Antes (v219)

```
Players disponíveis:
├─ MegaEmbed ✅
├─ MyVidPlay ✅
├─ DoodStream ✅
└─ PlayerEmbedAPI ❌ (não aparecia em filmes)
```

### Depois (v220)

```
Players disponíveis:
├─ PlayerEmbedAPI ✅ (NOVO!)
├─ MegaEmbed ✅
├─ MyVidPlay ✅
└─ DoodStream ✅
```

---

## 🎯 Filme de Teste

**Recomendado**: A Última Aventura - Nos Bastidores de Stranger Things 5

**Por quê?**
- Foi o filme usado para identificar o bug
- Confirmado ter PlayerEmbedAPI
- URL: `https://viewplayer.online/filme/tt39307872`

**Alternativas**:
- Qualquer filme recente em maxseries.pics
- Filmes populares geralmente têm mais sources

---

## 💡 Dicas

### Se PlayerEmbedAPI demorar

- Normal! Extração via WebView leva 20-30s
- Aguarde pacientemente
- Outros players aparecem mais rápido

### Se quiser testar episódios também

- PlayerEmbedAPI já funcionava em episódios (v219)
- v220 apenas corrigiu filmes
- Mas pode testar para confirmar que não quebrou nada

### Se quiser ver logs detalhados

```powershell
# Logs completos
adb logcat | Select-String "MaxSeries|PlayerEmbedAPI|WebView" | Tee-Object -FilePath "teste_v220.txt"
```

---

## 📝 Checklist

- [ ] Atualizado para v220
- [ ] Versão confirmada (220)
- [ ] Testado com filme
- [ ] PlayerEmbedAPI apareceu
- [ ] Vídeo reproduziu
- [ ] Logs capturados (opcional)

---

## 🎉 Resultado Esperado

```
🎬 Filme: A Última Aventura - Stranger Things 5
⏱️ Aguardando players... (5s)
✅ MegaEmbed carregado
✅ MyVidPlay carregado
⏱️ Aguardando PlayerEmbedAPI... (20s)
✅ PlayerEmbedAPI carregado (2 links)
🎥 Reproduzindo vídeo...
```

---

**Tempo total**: ~3 minutos  
**Dificuldade**: Fácil  
**Resultado**: PlayerEmbedAPI funcionando em filmes! 🚀
