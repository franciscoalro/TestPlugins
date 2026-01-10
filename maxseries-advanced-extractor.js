/**
 * MaxSeries Video URL Extractor - Advanced Version
 * Captura TODAS as requisições e analisa respostas para encontrar links de vídeo
 */

const { chromium } = require('playwright');
const fs = require('fs');

// Configurações
const CONFIG = {
    headless: false,
    timeout: 60000,
    waitTime: 90000, // 90 segundos
};

// Armazena TODAS as requisições
const allRequests = [];
const videoUrls = new Set();

/**
 * Analisa corpo da resposta em busca de URLs de vídeo
 */
function analyzeResponseBody(body, url) {
    if (!body) return [];

    const found = [];

    // Padrões de URLs de vídeo
    const patterns = [
        /https?:\/\/[^\s"'<>]+\.m3u8[^\s"'<>]*/gi,
        /https?:\/\/[^\s"'<>]+\.mp4[^\s"'<>]*/gi,
        /https?:\/\/[^\s"'<>]+\/playlist\.m3u8[^\s"'<>]*/gi,
        /https?:\/\/[^\s"'<>]+\/master\.m3u8[^\s"'<>]*/gi,
        /"file":\s*"([^"]+)"/gi,
        /"sources":\s*\[([^\]]+)\]/gi,
        /"url":\s*"([^"]+\.m3u8[^"]*)"/gi,
    ];

    patterns.forEach(pattern => {
        const matches = body.matchAll(pattern);
        for (const match of matches) {
            const videoUrl = match[1] || match[0];
            if (videoUrl && (videoUrl.includes('.m3u8') || videoUrl.includes('.mp4'))) {
                found.push(videoUrl);
            }
        }
    });

    return found;
}

/**
 * Captura e analisa todas as requisições
 */
async function captureAllRequests(page, context, targetUrl) {
    console.log(`\n🚀 MaxSeries Advanced Video Extractor`);
    console.log('='.repeat(80));
    console.log(`\n🔍 URL: ${targetUrl}\n`);

    // Intercepta TODAS as requisições e respostas
    page.on('request', request => {
        const url = request.url();
        const method = request.method();

        console.log(`📤 ${method} ${url}`);
    });

    page.on('response', async response => {
        const url = response.url();
        const status = response.status();
        const contentType = response.headers()['content-type'] || '';

        console.log(`📥 ${status} ${url}`);

        try {
            // Captura corpo da resposta
            let body = null;

            // Só captura texto/json/html
            if (contentType.includes('text') ||
                contentType.includes('json') ||
                contentType.includes('javascript') ||
                contentType.includes('html')) {
                try {
                    body = await response.text();
                } catch (e) {
                    // Ignora erros de leitura
                }
            }

            // Salva requisição
            allRequests.push({
                method: response.request().method(),
                url,
                headers: response.request().headers(),
                status,
                contentType,
                bodyLength: body ? body.length : 0,
            });

            // Analisa corpo em busca de vídeos
            if (body) {
                const foundVideos = analyzeResponseBody(body, url);
                if (foundVideos.length > 0) {
                    console.log(`\n🎯 VÍDEOS ENCONTRADOS NA RESPOSTA!`);
                    foundVideos.forEach(videoUrl => {
                        console.log(`   📹 ${videoUrl}`);
                        videoUrls.add(videoUrl);
                    });
                    console.log('');
                }

                // Salva respostas importantes
                if (url.includes('/episodio/') ||
                    url.includes('/player/') ||
                    url.includes('/embed/') ||
                    body.includes('m3u8') ||
                    body.includes('sources')) {
                    const filename = `response_${Date.now()}_${url.split('/').pop().replace(/[^a-z0-9]/gi, '_')}.txt`;
                    fs.writeFileSync(filename, body);
                    console.log(`💾 Resposta salva: ${filename}\n`);
                }
            }

            // Detecta vídeos diretamente na URL
            if (url.includes('.m3u8') || url.includes('.mp4')) {
                console.log(`\n✅ VÍDEO CAPTURADO DIRETAMENTE!`);
                console.log(`📹 ${url}\n`);
                videoUrls.add(url);
            }

        } catch (error) {
            // Ignora erros
        }
    });

    // Navega
    try {
        await page.goto(targetUrl, {
            waitUntil: 'networkidle',
            timeout: CONFIG.timeout
        });

        console.log('\n✅ Página carregada\n');
        await page.waitForTimeout(5000);

        // Lista frames
        const frames = page.frames();
        console.log(`🖼️  Frames: ${frames.length}`);
        frames.forEach((frame, i) => {
            console.log(`   ${i + 1}. ${frame.url()}`);
        });
        console.log('');

        // Tenta clicar em botões de play
        const playSelectors = [
            'button[class*="play"]',
            'button[id*="play"]',
            'div[class*="play"]',
            '.play-button',
            'button',
            'video',
        ];

        for (const selector of playSelectors) {
            try {
                const elements = await page.$$(selector);
                for (const element of elements) {
                    try {
                        const text = await element.textContent();
                        if (text && (text.toLowerCase().includes('play') || text.toLowerCase().includes('assistir'))) {
                            console.log(`🎬 Clicando: "${text}"`);
                            await element.click({ timeout: 2000 });
                            await page.waitForTimeout(3000);
                            break;
                        }
                    } catch (e) {
                        // Continua
                    }
                }
            } catch (e) {
                // Continua
            }
        }

        // Aguarda
        console.log(`\n⏳ Aguardando ${CONFIG.waitTime / 1000}s para capturar requisições...\n`);
        await page.waitForTimeout(CONFIG.waitTime);

    } catch (error) {
        console.error(`\n❌ Erro: ${error.message}\n`);
    }
}

/**
 * Exibe resultados
 */
function displayResults() {
    console.log('\n\n' + '='.repeat(80));
    console.log('📊 RESULTADOS');
    console.log('='.repeat(80));

    console.log(`\n📋 Total de requisições: ${allRequests.length}`);
    console.log(`📹 URLs de vídeo encontradas: ${videoUrls.size}\n`);

    if (videoUrls.size > 0) {
        console.log('🎯 VÍDEOS CAPTURADOS:\n');
        Array.from(videoUrls).forEach((url, i) => {
            console.log(`${i + 1}. ${url}\n`);
        });
    } else {
        console.log('❌ Nenhum vídeo encontrado\n');
    }

    // Salva tudo em JSON
    const output = {
        timestamp: new Date().toISOString(),
        totalRequests: allRequests.length,
        videoUrls: Array.from(videoUrls),
        requests: allRequests,
    };

    const filename = `maxseries_capture_${Date.now()}.json`;
    fs.writeFileSync(filename, JSON.stringify(output, null, 2));
    console.log(`💾 Dados completos salvos em: ${filename}`);

    console.log('='.repeat(80) + '\n');
}

/**
 * Main
 */
async function main() {
    const targetUrl = process.argv[2] || 'https://playerthree.online/embed/synden/';

    const browser = await chromium.launch({
        headless: CONFIG.headless,
        args: [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
        ],
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        ignoreHTTPSErrors: true,
    });

    const page = await context.newPage();

    try {
        await captureAllRequests(page, context, targetUrl);
        displayResults();
    } catch (error) {
        console.error('❌ Erro fatal:', error);
    } finally {
        await browser.close();
    }
}

main().catch(console.error);
