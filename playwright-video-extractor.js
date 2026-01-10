/**
 * Playwright Video Link Extractor
 * Captura links de vídeo, tokens e cookies de players embarcados
 * 
 * Uso: node playwright-video-extractor.js <URL>
 */

const { chromium } = require('playwright');

// Configurações
const CONFIG = {
    headless: false, // Mostra o navegador para debug
    timeout: 60000, // 60 segundos
    waitForVideo: 30000, // Espera até 30s pelo vídeo
};

// Padrões de URLs de vídeo conhecidos
const VIDEO_PATTERNS = [
    /\.m3u8/i,
    /\.mp4/i,
    /\.mkv/i,
    /\.avi/i,
    /\/playlist\.m3u8/i,
    /\/master\.m3u8/i,
    /abyss\.to/i,
    /filemoon/i,
    /streamtape/i,
    /doodstream/i,
    /mixdrop/i,
];

// Armazena requisições capturadas
const capturedRequests = [];
const capturedCookies = new Map();

/**
 * Verifica se a URL é um link de vídeo
 */
function isVideoUrl(url) {
    return VIDEO_PATTERNS.some(pattern => pattern.test(url));
}

/**
 * Extrai informações da requisição
 */
function extractRequestInfo(request) {
    const url = request.url();
    const headers = request.headers();
    const method = request.method();

    return {
        url,
        method,
        headers,
        timestamp: new Date().toISOString(),
    };
}

/**
 * Extrai cookies relevantes
 */
async function extractCookies(context, url) {
    const cookies = await context.cookies(url);
    return cookies.map(cookie => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        expires: cookie.expires,
        httpOnly: cookie.httpOnly,
        secure: cookie.secure,
        sameSite: cookie.sameSite,
    }));
}

/**
 * Extrai tokens da URL
 */
function extractTokens(url) {
    const tokens = {};

    try {
        const urlObj = new URL(url);
        const params = urlObj.searchParams;

        // Parâmetros comuns de token
        const tokenKeys = ['token', 'auth', 'key', 'signature', 'sig', 'hash', 'id', 'v'];

        tokenKeys.forEach(key => {
            if (params.has(key)) {
                tokens[key] = params.get(key);
            }
        });

        // Extrai todos os parâmetros
        params.forEach((value, key) => {
            if (!tokens[key]) {
                tokens[key] = value;
            }
        });
    } catch (error) {
        console.error('Erro ao extrair tokens:', error.message);
    }

    return tokens;
}

/**
 * Tenta clicar no botão de play
 */
async function tryClickPlay(page) {
    const playSelectors = [
        'button[aria-label*="play" i]',
        'button[title*="play" i]',
        'button.play-button',
        'button.vjs-big-play-button',
        'div.play-button',
        '[class*="play"]',
        '[id*="play"]',
        'video',
    ];

    for (const selector of playSelectors) {
        try {
            const element = await page.$(selector);
            if (element) {
                console.log(`🎬 Tentando clicar em: ${selector}`);
                await element.click({ timeout: 2000 });
                await page.waitForTimeout(2000);
                return true;
            }
        } catch (error) {
            // Continua tentando outros seletores
        }
    }

    return false;
}

/**
 * Aguarda e captura links de vídeo
 */
async function captureVideoLinks(page, context, targetUrl) {
    console.log(`\n🔍 Navegando para: ${targetUrl}\n`);

    // Função para interceptar requisições (usada em todos os frames)
    const handleRequest = (request) => {
        const url = request.url();

        if (isVideoUrl(url)) {
            const info = extractRequestInfo(request);
            capturedRequests.push(info);
            console.log(`\n✅ VÍDEO CAPTURADO!`);
            console.log(`📹 URL: ${url}`);
            console.log(`🔧 Method: ${info.method}`);
            console.log(`🖼️  Frame: ${request.frame().url()}`);
        }
    };

    // Função para interceptar respostas (usada em todos os frames)
    const handleResponse = async (response) => {
        const url = response.url();

        if (isVideoUrl(url)) {
            console.log(`\n📥 RESPOSTA DE VÍDEO:`);
            console.log(`📹 URL: ${url}`);
            console.log(`📊 Status: ${response.status()}`);
            console.log(`📦 Content-Type: ${response.headers()['content-type']}`);
        }
    };

    // Intercepta requisições da página principal
    page.on('request', handleRequest);
    page.on('response', handleResponse);

    // Intercepta requisições de TODOS os frames (incluindo iframes)
    page.on('frameattached', async (frame) => {
        console.log(`🖼️  Novo iframe detectado: ${frame.url()}`);
    });

    // Navega para a página
    try {
        await page.goto(targetUrl, {
            waitUntil: 'domcontentloaded',
            timeout: CONFIG.timeout
        });

        console.log('✅ Página carregada');

        // Aguarda um pouco para JavaScript carregar
        await page.waitForTimeout(5000);

        // Lista todos os iframes
        const frames = page.frames();
        console.log(`\n🖼️  Total de frames: ${frames.length}`);
        frames.forEach((frame, index) => {
            console.log(`   Frame ${index + 1}: ${frame.url()}`);
        });

        // Tenta clicar no play em todos os frames
        console.log('\n🎬 Procurando botão de play...');
        await tryClickPlay(page);

        // Tenta clicar em iframes também
        for (const frame of frames) {
            try {
                const playButton = await frame.$('button, div[class*="play"], video');
                if (playButton) {
                    console.log(`🎬 Tentando clicar no frame: ${frame.url()}`);
                    await playButton.click({ timeout: 2000 });
                    await page.waitForTimeout(2000);
                }
            } catch (e) {
                // Continua
            }
        }

        // Aguarda links de vídeo (aumentado para 60s)
        console.log(`\n⏳ Aguardando links de vídeo (60s)...`);
        await page.waitForTimeout(60000);

        // Captura cookies finais de todos os domínios
        const allCookies = await context.cookies();
        allCookies.forEach(cookie => {
            capturedCookies.set(`${cookie.domain}:${cookie.name}`, cookie);
        });

    } catch (error) {
        console.error(`❌ Erro ao navegar: ${error.message}`);
    }
}

/**
 * Formata e exibe resultados
 */
function displayResults() {
    console.log('\n\n' + '='.repeat(80));
    console.log('📊 RESULTADOS DA CAPTURA');
    console.log('='.repeat(80));

    if (capturedRequests.length === 0) {
        console.log('\n❌ Nenhum link de vídeo capturado');
        return;
    }

    console.log(`\n✅ ${capturedRequests.length} link(s) de vídeo capturado(s)\n`);

    capturedRequests.forEach((req, index) => {
        console.log(`\n${'─'.repeat(80)}`);
        console.log(`📹 VÍDEO #${index + 1}`);
        console.log(`${'─'.repeat(80)}`);

        console.log(`\n🔗 URL:`);
        console.log(req.url);

        const tokens = extractTokens(req.url);
        if (Object.keys(tokens).length > 0) {
            console.log(`\n🎫 TOKENS EXTRAÍDOS:`);
            Object.entries(tokens).forEach(([key, value]) => {
                console.log(`  ${key}: ${value}`);
            });
        }

        console.log(`\n📋 HEADERS:`);
        Object.entries(req.headers).forEach(([key, value]) => {
            console.log(`  ${key}: ${value}`);
        });
    });

    if (capturedCookies.size > 0) {
        console.log(`\n\n${'─'.repeat(80)}`);
        console.log(`🍪 COOKIES CAPTURADOS (${capturedCookies.size})`);
        console.log(`${'─'.repeat(80)}\n`);

        Array.from(capturedCookies.values()).forEach(cookie => {
            console.log(`📌 ${cookie.name}`);
            console.log(`   Domain: ${cookie.domain}`);
            console.log(`   Value: ${cookie.value}`);
            console.log(`   Path: ${cookie.path}`);
            console.log(`   Secure: ${cookie.secure}`);
            console.log(`   HttpOnly: ${cookie.httpOnly}`);
            console.log();
        });
    }

    // Salva em arquivo JSON
    const output = {
        timestamp: new Date().toISOString(),
        totalVideos: capturedRequests.length,
        videos: capturedRequests.map(req => ({
            url: req.url,
            tokens: extractTokens(req.url),
            headers: req.headers,
            method: req.method,
        })),
        cookies: Array.from(capturedCookies.values()),
    };

    const fs = require('fs');
    const filename = `video-capture-${Date.now()}.json`;
    fs.writeFileSync(filename, JSON.stringify(output, null, 2));

    console.log(`\n💾 Resultados salvos em: ${filename}`);
    console.log('='.repeat(80) + '\n');
}

/**
 * Função principal
 */
async function main() {
    const targetUrl = process.argv[2];

    if (!targetUrl) {
        console.error('❌ Uso: node playwright-video-extractor.js <URL>');
        console.error('📝 Exemplo: node playwright-video-extractor.js https://playerthree.online/...');
        process.exit(1);
    }

    console.log('🚀 Playwright Video Extractor');
    console.log('='.repeat(80));

    const browser = await chromium.launch({
        headless: CONFIG.headless,
        args: [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
        ],
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        ignoreHTTPSErrors: true,
    });

    const page = await context.newPage();

    try {
        await captureVideoLinks(page, context, targetUrl);
        displayResults();
    } catch (error) {
        console.error('❌ Erro fatal:', error);
    } finally {
        await browser.close();
    }
}

// Executa
main().catch(console.error);
