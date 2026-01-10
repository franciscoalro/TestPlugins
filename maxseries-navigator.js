/**
 * MaxSeries Navigator - Playwright
 * Navega no MaxSeries, encontra um episódio e extrai a URL do player
 */

const { chromium } = require('playwright');

async function getMaxSeriesPlayerUrl() {
    console.log('🚀 MaxSeries Navigator - Playwright\n');

    const browser = await chromium.launch({
        headless: false,
        args: ['--disable-blink-features=AutomationControlled'],
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
    });

    const page = await context.newPage();

    try {
        // Navega para a série que você já está vendo
        console.log('📺 Navegando para Terra de Pecados...');
        await page.goto('https://www.maxseries.one/series/assistir-terra-de-pecados-online', {
            waitUntil: 'domcontentloaded',
            timeout: 30000,
        });

        console.log('✅ Página carregada\n');
        await page.waitForTimeout(3000);

        // Procura por links de episódios
        console.log('🔍 Procurando episódios...');

        // Tenta vários seletores comuns para episódios
        const episodeSelectors = [
            'a[href*="episodio"]',
            'a[href*="episode"]',
            '.episode-link',
            '.episodio',
            'a:has-text("Episódio")',
            'a:has-text("EP")',
        ];

        let episodeLink = null;
        for (const selector of episodeSelectors) {
            try {
                episodeLink = await page.$(selector);
                if (episodeLink) {
                    console.log(`✅ Episódio encontrado com seletor: ${selector}`);
                    break;
                }
            } catch (e) {
                // Continua tentando
            }
        }

        if (!episodeLink) {
            console.log('⚠️ Não encontrou link de episódio automaticamente');
            console.log('📋 Listando todos os links da página...\n');

            const allLinks = await page.$$eval('a', links =>
                links.map(a => ({ text: a.textContent.trim(), href: a.href }))
                    .filter(l => l.text && l.href)
                    .slice(0, 20)
            );

            allLinks.forEach((link, i) => {
                console.log(`${i + 1}. ${link.text} -> ${link.href}`);
            });

            console.log('\n💡 Clique manualmente em um episódio no navegador aberto');
            console.log('⏳ Aguardando 30 segundos para você clicar...\n');
            await page.waitForTimeout(30000);
        } else {
            // Clica no episódio
            console.log('🎬 Clicando no episódio...');
            await episodeLink.click();
            await page.waitForTimeout(5000);
        }

        // Aguarda a página do player carregar
        console.log('⏳ Aguardando player carregar...\n');
        await page.waitForTimeout(3000);

        // Extrai URL do iframe
        console.log('🔍 Procurando iframe do player...\n');

        const iframeUrl = await page.evaluate(() => {
            const iframes = document.querySelectorAll('iframe');
            const urls = [];

            iframes.forEach((iframe, index) => {
                const src = iframe.src;
                if (src) {
                    urls.push({
                        index: index + 1,
                        url: src,
                        id: iframe.id || 'N/A',
                        class: iframe.className || 'N/A',
                    });
                }
            });

            return urls;
        });

        if (iframeUrl.length === 0) {
            console.log('❌ Nenhum iframe encontrado!');
            console.log('💡 Verifique se está na página do episódio');
        } else {
            console.log('✅ Iframes encontrados:\n');
            iframeUrl.forEach(iframe => {
                console.log(`📹 Iframe #${iframe.index}`);
                console.log(`   URL: ${iframe.url}`);
                console.log(`   ID: ${iframe.id}`);
                console.log(`   Class: ${iframe.class}`);
                console.log('');

                // Detecta player conhecido
                if (iframe.url.includes('playerthree') ||
                    iframe.url.includes('playerembedapi') ||
                    iframe.url.includes('megaembed')) {
                    console.log('🎯 PLAYER DETECTADO!\n');
                    console.log('='.repeat(80));
                    console.log('📋 COPIE E EXECUTE:');
                    console.log('='.repeat(80));
                    console.log(`\nnode playwright-video-extractor.js "${iframe.url}"\n`);
                    console.log('='.repeat(80) + '\n');

                    // Salva em arquivo
                    const fs = require('fs');
                    fs.writeFileSync('maxseries-player-url.txt', iframe.url);
                    console.log('💾 URL salva em: maxseries-player-url.txt\n');
                }
            });
        }

        console.log('⏳ Navegador ficará aberto por 60 segundos para inspeção...');
        await page.waitForTimeout(60000);

    } catch (error) {
        console.error('❌ Erro:', error.message);
    } finally {
        await browser.close();
    }
}

// Executa
getMaxSeriesPlayerUrl().catch(console.error);
