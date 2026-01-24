const puppeteer = require('puppeteer');

// TESTE DIRETO NO IFRAME (TENTANDO ADIVINHAR URL CORRETA)
const TARGET_URL = 'https://playerthree.online/embed/sandokan/1/1'; // S1 E1?
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

(async () => {
    console.log('🤖 INICIANDO ROBÔ DE TESTE (MEGAEMBED v160 SIMULATOR)');
    console.log('=====================================================');

    // Launch browser
    const browser = await puppeteer.launch({
        headless: "new", // "new" para headless, false para visível
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setUserAgent(UA);

    // Enable Request Interception
    await page.setRequestInterception(true);

    page.on('request', request => {
        const url = request.url();

        // A LÓGICA V160 (Regex Universal)
        if (url.includes('/v4/')) {
            console.log('\n🔥 [SUCESSO] VIDEO ENCONTRADO!');
            console.log('🔗 URL:', url);
            console.log('📄 Tipo:', request.resourceType());
            console.log('=====================================================');
        }

        request.continue();
    });

    console.log(`🌐 Navegando para: ${TARGET_URL}`);
    try {
        await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: 60000 });
        console.log('✅ Página carregada.');

        console.log('🔍 Procurando iframe...');
        // Espera iframes carregarem
        await new Promise(r => setTimeout(r, 2000));

        const frames = page.frames();
        let playerFrame = null;

        for (const frame of frames) {
            const url = frame.url();
            console.log('   Frame: ' + url);
            if (url.includes('playerthree') || url.includes('megaembed')) {
                playerFrame = frame;
                console.log('   🎯 Iframe Alvo detectado!');
            }
        }

        if (playerFrame) {
            console.log('▶️ Tentando dar PLAY no vídeo...');
            try {
                // Injeta script no frame para clicar
                await playerFrame.evaluate(() => {
                    const btn = document.querySelector('button, .play, .vjs-big-play-button, .jw-display-icon-container');
                    if (btn) btn.click();
                });
                console.log('   🖱️ Clique simulado via JS.');
            } catch (e) {
                console.log('   ⚠️ Erro ao clicar: ' + e.message);
            }
        } else {
            console.log('⚠️ Aviso: Player não encontrado nos frames.');
        }

        console.log('⏳ Aguardando requisições de vídeo (20s)...');
        await new Promise(r => setTimeout(r, 20000));

    } catch (e) {
        console.error('❌ Erro:', e.message);
    }

    console.log('🏁 Teste finalizado.');
    await browser.close();
})();
