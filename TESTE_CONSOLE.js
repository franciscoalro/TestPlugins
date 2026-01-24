// ==========================================
// 🧪 SCRIPT DE TESTE PARA CONSOLE (F12)
// Copie e cole na aba Console do navegador
// ==========================================

(function () {
    console.clear();
    console.log('%c🧪 INICIANDO TESTE DO SCRIPT V159...', 'color: yellow; font-size: 14px; font-weight: bold;');

    // 1. Simular o ambiente do Plugin
    window.__TEST_MODE__ = true;

    // Função que simula o "Trap" (no celular, isso força o download)
    function trapUrl(url) {
        console.log('%c✅ SUCESSO! URL ENCONTRADA:', 'color: green; font-size: 16px; font-weight: bold;');
        console.log(url);
        console.log('%c(No celular, o WebView teria capturado este link e iniciado o vídeo)', 'color: gray;');

        // Alerta visual para você ver que funcionou
        alert('✅ LINK CAPTURADO!\n\n' + url);
    }

    // 2. Interceptores (Exatamente como no plugin)

    // FETCH
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        const url = args[0];
        if (typeof url === 'string' && url.includes('/v4/')) {
            console.log('⚡ Fetch interceptado:', url);
            trapUrl(url);
        }
        return originalFetch.apply(this, args);
    };

    // XHR
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url, ...rest) {
        if (typeof url === 'string' && url.includes('/v4/')) {
            console.log('⚡ XHR interceptado:', url);
            trapUrl(url);
        }
        return originalOpen.apply(this, [method, url, ...rest]);
    };

    // 3. Scanner de DOM (Procura se o link já carregou)
    console.log('🔍 Escaneando página por links existentes...');
    var html = document.documentElement.innerHTML;
    var v4Match = html.match(/https?:\/\/[^\s"'<>]+\/v4\/[a-z0-9]{1,3}\/[a-z0-9]{6}\/[^\s"'<>]*(?:\.(txt|m3u8|woff2))?/i);

    if (v4Match) {
        console.log('🔎 Link encontrado no HTML!');
        trapUrl(v4Match[0]);
    } else {
        console.log('⏳ Nenhum link no HTML ainda. Monitorando rede...');
        console.log('▶️ Dê play no vídeo se ainda não deu.');
    }

})();
