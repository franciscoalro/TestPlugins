const { chromium } = require('playwright');
const { exec } = require('child_process');

/* CONFIGURAÇÃO */
const EMBED_URL = 'https://playerthree.online/embed/synden/';
const OUTPUT_FILE = 'video_downloaded.mp4';

(async () => {
    console.log('🚀 Iniciando Auto-FFmpeg Downloader (Versão Camuflada)...');

    // Inicia navegador CAMUFLADO (parece usuário real)
    const browser = await chromium.launch({
        headless: false, // IMPORTANTE: Visível para burlar detecção simples
        args: [
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--autoplay-policy=no-user-gesture-required', // Força autoplay
            '--disable-blink-features=AutomationControlled' // ESCONDE que é robô
        ]
    });

    // Contexto com User-Agent real
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1366, height: 768 },
        deviceScaleFactor: 1,
        isMobile: false,
        hasTouch: false
    });

    // Injeta scripts para esconder webdriver
    const page = await context.newPage();
    await page.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    });

    let videoUrl = null;
    let referer = 'https://megaembed.link/';

    // Monitora requisições
    page.on('request', request => {
        const url = request.url();
        // Filtra o padrão exato .txt do Cloudflare ou .m3u8
        if ((url.includes('/v4/db/') && url.endsWith('.txt')) ||
            (url.includes('.m3u8') && !url.includes('google'))) {
            console.log('🎯 LINK DETECTADO:', url);
            videoUrl = url;

            // Já manda baixar assim que achar!
            startDownload(videoUrl);
        }
    });

    console.log(`🌐 Navegando para: ${EMBED_URL}`);

    try {
        await page.goto(EMBED_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    } catch (e) { console.log('⚠️ Navegação lenta, mas continuando...'); }

    console.log('🖱️ Página carregada. TENTANDO CLICAR...');

    // Tenta clicar por 1 minuto
    const startTime = Date.now();
    let downloaded = false;

    while (!videoUrl && (Date.now() - startTime < 60000)) {
        try {
            // Clica em iframes
            for (const frame of page.frames()) {
                const btn = await frame.$('button, [role="button"], video');
                if (btn) await btn.click({ timeout: 500 }).catch(() => { { } });
            }
            // Clique no centro
            await page.mouse.click(683, 384).catch(() => { { } });
        } catch (e) { }

        await page.waitForTimeout(2000);
        if (downloaded) break;
    }

    function startDownload(url) {
        if (downloaded) return;
        downloaded = true;

        console.log('\n✅ SUCESSO! Iniciando FFmpeg...');
        const ffmpegCmd = `ffmpeg -headers "Referer: ${referer}" -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" -i "${url}" -c copy -bsf:a aac_adtstoasc "${OUTPUT_FILE}" -y`;

        console.log(ffmpegCmd);

        exec(ffmpegCmd, (error, stdout, stderr) => {
            if (error && !stderr.includes('frame=')) {
                console.error(`❌ Erro FFmpeg: ${error.message}`);
            }
            console.log(`\n✅ Download em andamento... salvando em ${OUTPUT_FILE}`);
        });
    }

    if (!downloaded) {
        console.log('\n❌ Tempo esgotado. Tente clicar manualmente!');
    }

    // Mantém aberto para garantir o download
    await page.waitForTimeout(10000);
})();
