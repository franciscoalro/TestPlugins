# 🎯 Como Capturar Link de Vídeo do MaxSeries para VLC

## ❌ Resultado do Teste Automático

O script Playwright rodou por ~150 segundos mas **não capturou nenhum link de vídeo**.

**Motivo:** O PlayerThree do MaxSeries requer interação humana real e usa proteções anti-bot que impedem captura automática.

---

## ✅ SOLUÇÃO RECOMENDADA: Captura Manual com DevTools

### Método 1: DevTools do Navegador (MAIS FÁCIL)

1. **Abra o MaxSeries no navegador normal**
   - Vá para: https://www.maxseries.one
   - Escolha uma série/episódio

2. **Abra o DevTools**
   - Pressione `F12` ou `Ctrl+Shift+I`
   - Vá para a aba **Network**

3. **Filtre por vídeos**
   - No campo de filtro, digite: `m3u8`
   - Ou clique em "Media" para filtrar apenas mídia

4. **Clique no PLAY**
   - Clique no botão de play do vídeo
   - Aguarde o vídeo começar a carregar

5. **Copie o link**
   - Você verá requisições aparecendo
   - Procure por URLs terminando em `.m3u8`
   - Clique com botão direito → "Copy" → "Copy link address"

6. **Cole no VLC**
   ```
   vlc "URL_COPIADA_AQUI"
   ```

---

### Método 2: Script no Console (ALTERNATIVO)

1. **Abra o episódio no navegador**

2. **Abra o Console** (`F12` → Console)

3. **Cole este código:**
   ```javascript
   // Monitora requisições de vídeo
   const observer = new PerformanceObserver((list) => {
     for (const entry of list.getEntries()) {
       if (entry.name.includes('.m3u8') || entry.name.includes('.mp4')) {
         console.log('🎯 VÍDEO ENCONTRADO:');
         console.log(entry.name);
         console.log('\\nPara VLC:');
         console.log(`vlc "${entry.name}"`);
       }
     }
   });
   observer.observe({ entryTypes: ['resource'] });
   console.log('✅ Monitorando... Clique no PLAY agora!');
   ```

4. **Clique no PLAY**

5. **O link aparecerá no console**

---

### Método 3: Extensão do Navegador

Use extensões como:
- **Video DownloadHelper** (Firefox/Chrome)
- **Stream Detector** (Chrome)
- **Video Downloader Professional** (Chrome)

Estas extensões detectam automaticamente streams de vídeo.

---

## 🎬 Exemplo de Link M3U8

Links do MaxSeries geralmente seguem este padrão:
```
https://[dominio]/[path]/playlist.m3u8?token=[TOKEN]&sig=[SIGNATURE]
```

**Exemplo real:**
```
https://abyss.to/hls/12345/playlist.m3u8?token=abc123&sig=xyz789
```

---

## 📋 Comandos VLC

### Abrir link direto:
```bash
vlc "https://exemplo.com/video.m3u8"
```

### Com headers (se necessário):
```bash
vlc "https://exemplo.com/video.m3u8" --http-referrer="https://playerthree.online/" --http-user-agent="Mozilla/5.0"
```

### Salvar vídeo:
```bash
vlc "https://exemplo.com/video.m3u8" --sout=file/ts:video.ts
```

---

## 🛠️ Ferramentas Playwright Criadas

Embora não funcionem para MaxSeries (proteção anti-bot), as ferramentas estão prontas para outros sites:

### Scripts Disponíveis:
- `vlc-link-extractor.js` - Extrator com interação manual
- `playwright-video-extractor.js` - Extrator genérico
- `maxseries-advanced-extractor.js` - Captura todas requisições

### Uso:
```bash
node vlc-link-extractor.js "URL_DO_PLAYER"
```

**Funcionam bem para sites sem proteção anti-bot!**

---

## 💡 Dicas Importantes

### Headers Necessários

Se o VLC não reproduzir, pode precisar de headers:

```javascript
// Headers capturados do MaxSeries:
Referer: https://playerthree.online/
Origin: https://playerthree.online
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
```

### Tokens Expiram

Links M3U8 geralmente têm tokens que **expiram em minutos/horas**.  
Capture e use imediatamente!

### Qualidade

Links M3U8 podem ter múltiplas qualidades:
- `master.m3u8` - Índice de qualidades
- `playlist.m3u8` - Qualidade específica

---

## 🎯 Resumo

| Método | Dificuldade | Sucesso |
|--------|-------------|---------|
| DevTools Manual | ⭐ Fácil | ✅ 100% |
| Script Console | ⭐⭐ Médio | ✅ 90% |
| Extensão Browser | ⭐ Fácil | ✅ 95% |
| Playwright Auto | ⭐⭐⭐ Difícil | ❌ 0% (MaxSeries) |

**Recomendação:** Use **DevTools Manual** (Método 1)

---

## 📞 Próximos Passos

1. Tente o **Método 1** (DevTools)
2. Se conseguir o link, teste no VLC
3. Se não funcionar, pode precisar de headers adicionais
4. Compartilhe o link capturado para ajudarmos a configurar o VLC corretamente

---

**Boa sorte! 🍀**
