# 🎯 Como pegar o link final AGORA (Método infalível)

Como vimos no Burp Suite, a API manda os dados "escondidos" (encriptados). Mas o seu navegador precisa "desenrolar" isso para mostrar o vídeo. 

**O que eu preciso:** O link que o seu navegador usa para tocar o vídeo.

### 🚀 Siga este passo a passo:

1. **Abra o vídeo** no site normalmente (não precisa de Burp Suite agora).
2. **Dê o PLAY** e espere o vídeo começar a rodar.
3. Pressione **F12** e clique na aba **Console**.
4. **Copie e cole** o código abaixo lá e dê **Enter**:

```javascript
(function() {
    console.clear();
    console.log("%c--- BUSCANDO LINKS DE VÍDEO ---", "color: cyan; font-weight: bold; font-size: 16px;");
    
    // Busca no tráfego de rede capturado pelo navegador
    const resources = performance.getEntriesByType("resource");
    const videoUrls = resources
        .filter(r => r.name.includes(".m3u8") || r.name.includes(".mp4") || r.name.includes("playlist"))
        .map(r => r.name);

    // Busca no elemento de vídeo da página
    const videoTags = Array.from(document.querySelectorAll("video"));
    videoTags.forEach(v => {
        if (v.src && !videoUrls.includes(v.src)) videoUrls.push(v.src);
    });

    if (videoUrls.length > 0) {
        console.log("%c✅ LINKS ENCONTRADOS:", "color: lime; font-weight: bold;");
        videoUrls.forEach((url, i) => {
            console.log(`\n📺 Link ${i+1}:`);
            console.log(`%c${url}`, "background: #222; color: #bada55; padding: 5px;");
            console.log(`%cComando VLC: vlc "${url}"`, "color: yellow;");
        });
    } else {
        console.log("%c❌ Nenhum link encontrado ainda. Clique no play e aguarde o vídeo começar!", "color: orange;");
    }
})();
```

### 📤 O que fazer depois:
O código vai imprimir o link do vídeo em **amarelo/verde**. 
- **Me envie esse link** aqui no chat.
- Ou simplesmente use o link que aparecer com o comando `vlc "link"` que ele sugerir.

---

### Por que o Burp Suite não leu direto?
A resposta que você mandou (`29e8fa77...`) é o link encriptado. O site usa um código JavaScript para transformar esse "monte de letras e números" no link real do vídeo. O script acima pega o link **DEPOIS** que esse processo terminou.
