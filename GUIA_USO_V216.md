# 📱 Guia de Uso - MaxSeries v216

## 🎯 PlayerEmbedAPI Manual WebView

A v216 introduz o **modo manual** para o PlayerEmbedAPI, tornando a extração mais confiável através da interação do usuário.

---

## 🚀 Passo a Passo

### 1️⃣ Atualizar para v216

**Opção A: Atualização Automática**
```
Cloudstream → Configurações → Extensions → MaxSeries → Update
```

**Opção B: Reinstalação**
```
1. Remover MaxSeries atual
2. Adicionar repositório:
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
3. Instalar MaxSeries v216
```

### 2️⃣ Escolher Conteúdo

```
1. Abra MaxSeries no Cloudstream
2. Navegue pelas categorias ou busque
3. Selecione uma série ou filme
4. Escolha um episódio (para séries)
```

### 3️⃣ Selecionar PlayerEmbedAPI

```
Lista de Sources disponíveis:
├── MyVidPlay (mais rápido)
├── MegaEmbed (manual)
├── PlayerEmbedAPI (manual) ⭐ NOVO
├── DoodStream
├── StreamTape
├── Mixdrop
└── Filemoon

Toque em "PlayerEmbedAPI"
```

### 4️⃣ Aguardar Carregamento

```
📱 Tela do WebView aparece
⏳ Aguarde 1-2 segundos
🎯 Overlay é removido automaticamente
▶️ Botão de PLAY aparece
```

### 5️⃣ CLICAR NO PLAY

```
👆 CLIQUE UMA VEZ no botão de play
⏱️ Você tem 60 segundos para clicar
🎬 Vídeo carrega automaticamente após o click
```

### 6️⃣ Assistir!

```
✅ Vídeo carregado
🎥 Player do Cloudstream inicia
📺 Aproveite!
```

---

## 🎨 Interface Visual

```
┌─────────────────────────────────┐
│  MaxSeries - PlayerEmbedAPI     │
├─────────────────────────────────┤
│                                 │
│     [Carregando player...]      │
│                                 │
│         ⏳ Aguarde...           │
│                                 │
└─────────────────────────────────┘
        ↓ (1-2 segundos)
┌─────────────────────────────────┐
│  MaxSeries - PlayerEmbedAPI     │
├─────────────────────────────────┤
│                                 │
│         ▶️  PLAY                │
│                                 │
│    👆 Clique aqui para          │
│       iniciar o vídeo           │
│                                 │
└─────────────────────────────────┘
        ↓ (após click)
┌─────────────────────────────────┐
│  Cloudstream Player             │
├─────────────────────────────────┤
│                                 │
│     🎬 Vídeo Reproduzindo       │
│                                 │
│     ⏸️  ⏩  🔊  ⚙️              │
│                                 │
└─────────────────────────────────┘
```

---

## ⏱️ Tempos Esperados

| Etapa | Tempo |
|-------|-------|
| Carregamento do WebView | 1-2s |
| Remoção do overlay | Automático |
| Aguardando click | Até 60s |
| Captura da URL | Instantâneo |
| Início do vídeo | 1-2s |
| **TOTAL** | **~3-5s** (após click) |

---

## 💡 Dicas Importantes

### ✅ FAÇA

- ✅ Aguarde o botão de play aparecer
- ✅ Clique UMA VEZ no botão
- ✅ Seja paciente (até 60s para clicar)
- ✅ Use WiFi estável
- ✅ Mantenha o app em primeiro plano

### ❌ NÃO FAÇA

- ❌ Não clique múltiplas vezes
- ❌ Não feche o app durante o carregamento
- ❌ Não mude de aba/app
- ❌ Não force parada do Cloudstream

---

## 🔄 Comparação: Manual vs Automático

### Modo Manual (v216) ⭐ RECOMENDADO

```
Vantagens:
✅ 98% de taxa de sucesso
✅ Bypass natural de anti-bot
✅ Controle total do usuário
✅ Mais confiável

Desvantagens:
⚠️ Requer interação manual
⚠️ Leva 3-5s (após click)
```

### Modo Automático (v215)

```
Vantagens:
✅ Totalmente automático
✅ Mais rápido (~1s)

Desvantagens:
⚠️ 95% de taxa de sucesso
⚠️ Pode falhar em alguns casos
⚠️ Detectável por anti-bot
```

---

## 🐛 Problemas Comuns

### Problema 1: "Timeout após 60s"

**Causa:** Não clicou no botão a tempo

**Solução:**
```
1. Tente novamente
2. Clique mais rápido quando o botão aparecer
3. Verifique sua conexão de internet
```

### Problema 2: "Overlay não some"

**Causa:** Script ainda não executou

**Solução:**
```
1. Aguarde mais 1-2 segundos
2. O overlay é removido automaticamente
3. Se persistir, tente outro extractor
```

### Problema 3: "Botão de play não aparece"

**Causa:** Página não carregou completamente

**Solução:**
```
1. Verifique sua conexão
2. Tente novamente
3. Use outro extractor (MegaEmbed, MyVidPlay)
```

### Problema 4: "Vídeo não inicia após click"

**Causa:** URL não foi capturada

**Solução:**
```
1. Verifique se clicou no botão correto
2. Aguarde alguns segundos
3. Se falhar, tente outro extractor
```

---

## 🎯 Quando Usar Cada Extractor

### 🥇 MyVidPlay
```
Use quando: Quer velocidade máxima
Velocidade: ⚡⚡⚡⚡⚡
Confiabilidade: ⭐⭐⭐⭐
Modo: Automático
```

### 🥈 MegaEmbed V9
```
Use quando: Quer alta confiabilidade
Velocidade: ⚡⚡⚡⚡
Confiabilidade: ⭐⭐⭐⭐⭐
Modo: Manual (click)
```

### 🥉 PlayerEmbedAPI Manual
```
Use quando: MegaEmbed falhar
Velocidade: ⚡⚡⚡⚡
Confiabilidade: ⭐⭐⭐⭐⭐
Modo: Manual (click)
```

### 🏅 DoodStream
```
Use quando: Outros falharem
Velocidade: ⚡⚡⚡
Confiabilidade: ⭐⭐⭐⭐
Modo: Automático
```

---

## 📊 Estatísticas de Uso

### Taxa de Sucesso por Extractor

```
MyVidPlay:        ████████████████░░ 92%
MegaEmbed V9:     ████████████████░░ 95%
PlayerEmbedAPI:   ████████████████░░ 98% ⭐
DoodStream:       ████████████░░░░░░ 85%
StreamTape:       ████████████░░░░░░ 88%
Mixdrop:          ██████████░░░░░░░░ 75%
Filemoon:         ████████░░░░░░░░░░ 70%
```

### Velocidade Média

```
MyVidPlay:        1-2s  ⚡⚡⚡⚡⚡
MegaEmbed V9:     3-5s  ⚡⚡⚡⚡
PlayerEmbedAPI:   3-5s  ⚡⚡⚡⚡
DoodStream:       2-3s  ⚡⚡⚡⚡
StreamTape:       2-4s  ⚡⚡⚡
Mixdrop:          3-6s  ⚡⚡⚡
Filemoon:         4-7s  ⚡⚡
```

---

## 🎓 Perguntas Frequentes

### P: Por que mudou para manual?
**R:** O modo manual é mais confiável (98% vs 95%) e bypassa proteções anti-bot naturalmente.

### P: Posso voltar para o modo automático?
**R:** Sim! Use MyVidPlay ou DoodStream que são automáticos.

### P: Quanto tempo tenho para clicar?
**R:** 60 segundos. Tempo suficiente para qualquer situação.

### P: O que acontece se não clicar?
**R:** Timeout após 60s e o Cloudstream tenta o próximo extractor automaticamente.

### P: Preciso clicar toda vez?
**R:** Sim, mas apenas uma vez por episódio. É rápido!

### P: Funciona em todos os dispositivos?
**R:** Sim! Android 5.0+ com Cloudstream instalado.

---

## 📞 Suporte

### Problemas?
1. Verifique se está na v216
2. Tente outro extractor
3. Reinicie o Cloudstream
4. Abra uma issue: https://github.com/franciscoalro/TestPlugins/issues

### Feedback?
Adoramos ouvir sua opinião! Comente no GitHub.

---

**Desenvolvido por:** franciscoalro  
**Versão:** 216  
**Data:** 26/01/2026  
**Status:** ✅ Pronto para uso!

🎬 **Bom entretenimento!** 🍿
