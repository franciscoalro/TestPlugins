# 🌐 Guia: Script TypeScript/JavaScript no Navegador

## 🎯 Por Que Usar Script no Navegador?

### ✅ Vantagens do Script Browser vs Python:

| Recurso | Script Browser | Script Python |
|---------|----------------|---------------|
| **Acesso ao DOM** | ✅ Direto | ❌ Limitado |
| **Interceptação de Rede** | ✅ Nativo | ⚠️ Requer Selenium |
| **CORS/Same-Origin** | ✅ Sem bloqueio | ❌ Bloqueado |
| **JavaScript do Site** | ✅ Executa junto | ❌ Não acessa |
| **Velocidade** | ✅ Instantâneo | ⚠️ Mais lento |
| **Facilidade** | ✅ Cola e roda | ⚠️ Requer setup |

---

## 📋 Como Usar

### Passo 1: Abrir a Página
```
1. Navegue até: https://maxseries.one/episodio/[ID]
2. Aguarde a página carregar completamente
```

### Passo 2: Abrir DevTools
```
Windows/Linux: F12 ou Ctrl+Shift+I
Mac: Cmd+Option+I
```

### Passo 3: Ir para Console
```
Clique na aba "Console" no DevTools
```

### Passo 4: Colar o Script
```javascript
// Cole TODO o conteúdo de browser-video-extractor.js
// Pressione Enter
```

### Passo 5: Aguardar Análise
```
O script irá:
✅ Interceptar requisições de rede
✅ Analisar todos os iframes
✅ Extrair URLs de vídeo
✅ Mostrar resultados no console
```

---

## 🎬 Exemplo de Saída

```
🎬 MaxSeries Video Extractor v1.0
================================

🔍 Iniciando interceptação de requisições...

✅ Interceptação ativada!

📊 Encontrados 3 iframes na página

🎥 Iframe 1:
   URL: https://megaembed.cc/embed/abc123
   Tipo: MegaEmbed
   ❌ Acesso bloqueado (CORS)
   💡 Abra https://megaembed.cc/embed/abc123 em nova aba e execute lá

🎥 Iframe 2:
   URL: https://playerembedapi.com/player/xyz789
   Tipo: PlayerEmbedAPI
   ✅ Acesso ao conteúdo do iframe permitido
   🎯 Encontrados 2 URLs de vídeo:
      - https://cdn.playerembed.com/playlist.m3u8
      - https://cdn.playerembed.com/segment001.ts

📡 Requisição capturada: https://megaembed.cc/video/master.m3u8
📡 Requisição capturada: https://megaembed.cc/video/segment001.ts

============================================================
📊 RESUMO DA ANÁLISE
============================================================

🎥 Player 1 - MegaEmbed
   URL: https://megaembed.cc/embed/abc123
   ⚠️  Nenhum vídeo encontrado diretamente

🎥 Player 2 - PlayerEmbedAPI
   URL: https://playerembedapi.com/player/xyz789
   ✅ Vídeos encontrados:
      https://cdn.playerembed.com/playlist.m3u8
      https://cdn.playerembed.com/segment001.ts

📡 TODAS AS URLs CAPTURADAS (4):
   https://cdn.playerembed.com/playlist.m3u8
   https://cdn.playerembed.com/segment001.ts
   https://megaembed.cc/video/master.m3u8
   https://megaembed.cc/video/segment001.ts

============================================================
✅ Análise concluída!

💡 COMANDOS DISPONÍVEIS:
   extractor.copyToClipboard()        - Copiar URLs
   extractor.analyzeIframes()         - Reanalizar
   extractor.openIframeInNewTab(1)    - Abrir iframe 1 em nova aba
```

---

## 🔧 Comandos Úteis

### Copiar URLs para Área de Transferência
```javascript
extractor.copyToClipboard()
```

### Reanalizar Iframes
```javascript
extractor.analyzeIframes()
```

### Abrir Iframe em Nova Aba
```javascript
// Abrir iframe 1 em nova aba
extractor.openIframeInNewTab(1)

// Depois execute o script novamente na nova aba
```

### Ver Todas as URLs Capturadas
```javascript
Array.from(extractor.capturedUrls)
```

---

## 🚨 Solução de Problemas

### ❌ "Acesso bloqueado (CORS)"

**Problema:** O iframe está em domínio diferente e bloqueia acesso direto.

**Solução:**
```javascript
// 1. Use o comando para abrir em nova aba
extractor.openIframeInNewTab(1)

// 2. Na nova aba, cole o script novamente
// 3. Agora você terá acesso direto ao player
```

### ⚠️ "Nenhuma URL capturada"

**Possíveis causas:**
1. Vídeo ainda não começou a carregar
2. Player requer clique manual no "Play"
3. Player usa criptografia avançada

**Solução:**
```javascript
// 1. Clique no botão Play do vídeo
// 2. Aguarde 5-10 segundos
// 3. Verifique o console - novas URLs aparecerão automaticamente
```

### 🔄 "Quero reanalizar após clicar Play"

```javascript
// Aguarde o vídeo carregar, depois:
extractor.analyzeIframes()
```

---

## 🎓 Como Funciona Tecnicamente

### 1. **Interceptação de Fetch API**
```javascript
// O script substitui window.fetch para capturar requisições
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  const response = await originalFetch(...args);
  const url = args[0];
  
  // Captura URLs de vídeo
  if (url.includes('.m3u8') || url.includes('.mp4')) {
    console.log('Capturado:', url);
  }
  
  return response;
};
```

### 2. **Análise de Iframes**
```javascript
// Acessa o conteúdo interno do iframe (se permitido)
const iframeDoc = iframe.contentDocument;
const html = iframeDoc.documentElement.innerHTML;

// Busca por URLs de vídeo usando regex
const m3u8Regex = /https?:\/\/[^\s"'<>]+\.m3u8/gi;
const urls = html.match(m3u8Regex);
```

### 3. **Extração via Regex**
```javascript
// Padrões suportados:
- .m3u8   (HLS playlists)
- .mp4    (MP4 direto)
- .ts     (Segmentos HLS)
- .woff2  (Segmentos disfarçados)
```

---

## 📊 Comparação: Browser Script vs CloudStream Plugin

| Aspecto | Browser Script | CloudStream Plugin |
|---------|----------------|-------------------|
| **Setup** | ✅ Cola e roda | ⚠️ Requer build |
| **Debugging** | ✅ Console visual | ⚠️ ADB logs |
| **Velocidade** | ✅ Instantâneo | ⚠️ Mais lento |
| **Automação** | ❌ Manual | ✅ Automático |
| **Uso Final** | 🔧 Desenvolvimento | 📱 Produção |

**Conclusão:** Use o **Browser Script** para **descobrir como funciona**, depois implemente no **CloudStream Plugin** para **uso automático**.

---

## 🔗 Próximos Passos

1. ✅ Use o script browser para **descobrir URLs**
2. ✅ Analise os **padrões de URL** encontrados
3. ✅ Implemente a **lógica no plugin CloudStream**
4. ✅ Teste no **dispositivo Android**

---

## 📝 Arquivos Relacionados

- **Script TypeScript:** `browser-video-extractor.ts`
- **Script JavaScript:** `browser-video-extractor.js` ← **Use este!**
- **Plugin CloudStream:** `MaxSeries/src/main/kotlin/com/maxseries/`

---

**Versão:** 1.0  
**Última Atualização:** 23/01/2026  
**Compatibilidade:** Chrome, Firefox, Edge (DevTools)
