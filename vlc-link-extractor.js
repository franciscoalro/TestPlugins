/**
 * MaxSeries VLC Link Extractor
 * Captura link de vídeo real para reprodução no VLC
 * 
 * INSTRUÇÕES:
 * 1. O navegador abrirá automaticamente
 * 2. VOCÊ deve clicar no botão de PLAY manualmente
 * 3. O script capturará o link do vídeo automaticamente
 * 4. O link será exibido e salvo em arquivo
 */

const { chromium } = require('playwright');
const fs = require('fs');

// URLs de vídeo capturadas
const videoLinks = new Set();
let foundM3U8 = false;

async function captureVideoForVLC() {
    console.log('\n🎬 MaxSeries VLC Link Extractor');
    console.log('='.repeat(80));
    console.log('\n📋 INSTRUÇÕES:');
    console.log('   1. O navegador abrirá em instantes');
    console.log('   2. CLIQUE NO BOTÃO DE PLAY quando o player carregar');
    console.log('   3. Aguarde o vídeo começar a carregar');
    console.log('   4. O link será capturado automaticamente\n');
    console.log('='.repeat(80) + '\n');

    const browser = await chromium.launch({
        headless: false,
        args: [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--autoplay-policy=no-user-gesture-required',
        ],
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        ignoreHTTPSErrors: true,
    });

    const page = await context.newPage();

    // Intercepta TODAS as requisições
    page.on('request', request => {
        const url = request.url();

        // Detecta vídeos
        if (url.includes('.m3u8') ||
            url.includes('.mp4') ||
            url.includes('/playlist') ||
            url.includes('/master')) {

            // Ignora placeholders
            if (!url.includes('blank.mp4') &&
                !url.includes('placeholder') &&
                !url.includes('preview')) {

                videoLinks.add(url);

                if (url.includes('.m3u8')) {
                    foundM3U8 = true;
                    console.log('\n🎯 VÍDEO M3U8 CAPTURADO!');
                    console.log('='.repeat(80));
                    console.log(`\n📹 URL: ${url}\n`);
                    console.log('='.repeat(80));
                    console.log('\n✅ Link capturado com sucesso!');
                    console.log('💾 Salvando em arquivo...\n');

                    // Salva imediatamente
                    const output = {
                        timestamp: new Date().toISOString(),
                        videoUrl: url,
                        type: 'm3u8',
                        vlcCommand: `vlc "${url}"`,
                        headers: request.headers(),
                    };

                    fs.writeFileSync('vlc-video-link.json', JSON.stringify(output, null, 2));
                    fs.writeFileSync('vlc-video-link.txt', url);

                    console.log('📁 Arquivos salvos:');
                    console.log('   - vlc-video-link.json (dados completos)');
                    console.log('   - vlc-video-link.txt (apenas URL)\n');
                    console.log('🎬 Para reproduzir no VLC, execute:');
                    console.log(`   vlc "${url}"\n`);
                    console.log('='.repeat(80) + '\n');
                }
            }
        }
    });

    // Intercepta respostas
    page.on('response', async response => {
        const url = response.url();
        const contentType = response.headers()['content-type'] || '';

        if (url.includes('.m3u8') || contentType.includes('mpegurl')) {
            console.log(`\n📥 Resposta M3U8: ${response.status()} ${url}\n`);
        }
    });

    try {
        const targetUrl = process.argv[2] || 'https://playerthree.online/embed/synden/';

        console.log(`🌐 Navegando para: ${targetUrl}\n`);

        await page.goto(targetUrl, {
            waitUntil: 'domcontentloaded',
            timeout: 60000
        });

        console.log('✅ Página carregada!\n');
        console.log('⏳ Aguardando você clicar no PLAY...\n');
        console.log('💡 DICA: Clique no botão de play grande no centro do player\n');

        // Aguarda 3 minutos para captura
        console.log('⏰ Tempo de captura: 3 minutos\n');
        console.log('='.repeat(80) + '\n');

        let elapsed = 0;
        const interval = setInterval(() => {
            elapsed += 10;
            if (foundM3U8) {
                console.log(`✅ Link capturado! Aguardando mais ${180 - elapsed}s para possíveis outros links...\n`);
            } else {
                console.log(`⏳ Aguardando... ${elapsed}s / 180s`);
            }
        }, 10000);

        await page.waitForTimeout(180000); // 3 minutos
        clearInterval(interval);

        console.log('\n' + '='.repeat(80));
        console.log('📊 RESULTADOS FINAIS');
        console.log('='.repeat(80) + '\n');

        if (videoLinks.size === 0) {
            console.log('❌ Nenhum link de vídeo capturado\n');
            console.log('💡 Possíveis motivos:');
            console.log('   - Você não clicou no play');
            console.log('   - O player não carregou');
            console.log('   - O vídeo usa outro método de streaming\n');
            console.log('🔄 Tente novamente e certifique-se de clicar no play!\n');
        } else {
            console.log(`✅ ${videoLinks.size} link(s) de vídeo capturado(s):\n`);

            Array.from(videoLinks).forEach((url, i) => {
                console.log(`${i + 1}. ${url}\n`);
            });

            // Salva todos os links
            const allLinks = {
                timestamp: new Date().toISOString(),
                totalLinks: videoLinks.size,
                links: Array.from(videoLinks),
                vlcCommands: Array.from(videoLinks).map(url => `vlc "${url}"`),
            };

            fs.writeFileSync('all-video-links.json', JSON.stringify(allLinks, null, 2));
            console.log('💾 Todos os links salvos em: all-video-links.json\n');
        }

        console.log('='.repeat(80) + '\n');
        console.log('⏳ Navegador fechará em 10 segundos...\n');
        await page.waitForTimeout(10000);

    } catch (error) {
        console.error('\n❌ Erro:', error.message, '\n');
    } finally {
        await browser.close();
        console.log('✅ Concluído!\n');
    }
}

// Executa
captureVideoForVLC().catch(console.error);
