/**
 * MaxSeries Series Analyzer v2 - Com Bloqueio de Ads
 * 
 * Analisa páginas de séries e extrai episódios do iframe PlayerThree
 * Bloqueia propagandas, popups e novas abas
 * 
 * Uso:
 * node analyze-series-v2.js https://www.maxseries.pics/series/assistir-sandokan-online
 */

const puppeteer = require('puppeteer');

class SeriesAnalyzerV2 {
    constructor() {
        this.browser = null;
        this.page = null;
        this.episodes = [];
        this.videoSources = [];
    }

    async init() {
        console.log('🚀 Iniciando MaxSeries Analyzer v2...\n');

        this.browser = await puppeteer.launch({
            headless: false,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-popup-blocking',
                '--disable-notifications',
                '--mute-audio' // Silenciar áudio
            ]
        });

        this.page = await this.browser.newPage();

        await this.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        );

        await this.setupAdBlocker();

        console.log('✅ Navegador configurado com bloqueio de ads\n');
    }

    async setupAdBlocker() {
        console.log('🛡️  Configurando bloqueio de propagandas...');

        // Lista de domínios de propaganda
        const adDomains = [
            'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
            'google-analytics.com', 'googletagmanager.com', 'facebook.com/tr',
            'outbrain.com', 'taboola.com', 'criteo.com', 'pubmatic.com',
            'morphify.net', 'attirecideryeah.com', 'hupdzirazt.com',
            'popads.net', 'popcash.net', 'propellerads.com', 'adsterra.com',
            'adnxs.com', 'advertising.com', 'adsrvr.org', 'rubiconproject.com'
        ];

        await this.page.setRequestInterception(true);

        this.page.on('request', request => {
            const url = request.url();

            // Bloquear domínios de propaganda
            if (adDomains.some(domain => url.includes(domain))) {
                request.abort();
                return;
            }

            request.continue();
        });

        // Bloquear popups
        this.browser.on('targetcreated', async (target) => {
            if (target.type() === 'page' && target.url() !== 'about:blank') {
                console.log(`🚫 Popup bloqueado: ${target.url().substring(0, 60)}...`);
                const page = await target.page();
                if (page) await page.close();
            }
        });

        // Bloquear window.open
        await this.page.evaluateOnNewDocument(() => {
            window.open = () => null;
        });

        // Bloquear dialogs
        this.page.on('dialog', async dialog => {
            await dialog.dismiss();
        });

        console.log('✅ Bloqueio configurado\n');
    }

    async analyzeSeries(seriesUrl) {
        console.log(`🔍 Analisando: ${seriesUrl}\n`);

        try {
            // 1. Carregar página
            console.log('📥 Carregando página...');
            await this.page.goto(seriesUrl, {
                waitUntil: 'networkidle2',
                timeout: 30000
            });

            console.log('✅ Página carregada\n');

            // 2. Extrair título
            const title = await this.page.evaluate(() => {
                return document.querySelector('h1, .sheader .data h1')?.textContent?.trim() || 'Desconhecido';
            });

            console.log(`📺 Série: ${title}\n`);

            // 3. Encontrar iframe PlayerThree
            console.log('🎬 Procurando iframe PlayerThree...');

            const iframes = await this.page.$$('iframe');
            let playerFrame = null;
            let playerUrl = null;

            for (const iframe of iframes) {
                const src = await iframe.evaluate(el => el.src);
                if (src && src.includes('playerthree.online')) {
                    playerFrame = await iframe.contentFrame();
                    playerUrl = src;
                    break;
                }
            }

            if (!playerFrame) {
                console.log('❌ Iframe PlayerThree não encontrado');
                return;
            }

            console.log(`✅ PlayerThree encontrado: ${playerUrl}\n`);

            // 4. Aguardar frame carregar
            console.log('⏳ Aguardando frame carregar...');
            await playerFrame.waitForTimeout(3000);

            // 5. Extrair episódios do frame
            console.log('📋 Extraindo episódios do PlayerThree...\n');

            const episodes = await playerFrame.evaluate(() => {
                const eps = [];

                // Tentar diferentes seletores
                const selectors = [
                    '.episodios li',
                    '.se-c .episodios li',
                    '[data-episode]',
                    '.episode',
                    '.ep-item',
                    'li[onclick]'
                ];

                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);

                    if (elements.length > 0) {
                        console.log(`Encontrados ${elements.length} episódios com seletor: ${selector}`);

                        elements.forEach((el, index) => {
                            // Extrair dados
                            const number = el.querySelector('.numerando')?.textContent?.trim() || `${index + 1}`;
                            const title = el.querySelector('.episodiotitle, a')?.textContent?.trim() || 'Sem título';

                            // Extrair atributos data-*
                            const dataPost = el.getAttribute('data-post') || '';
                            const dataEpisode = el.getAttribute('data-episode') || '';
                            const dataSrc = el.getAttribute('data-src') || '';
                            const dataUrl = el.getAttribute('data-url') || '';
                            const onclick = el.getAttribute('onclick') || '';

                            eps.push({
                                number,
                                title,
                                dataPost,
                                dataEpisode,
                                dataSrc,
                                dataUrl,
                                onclick,
                                selector
                            });
                        });

                        break;
                    }
                }

                return eps;
            });

            console.log(`✅ Encontrados ${episodes.length} episódios\n`);

            if (episodes.length > 0) {
                console.log('📺 Primeiros 5 episódios:');
                episodes.slice(0, 5).forEach(ep => {
                    console.log(`   ${ep.number} - ${ep.title}`);
                    if (ep.dataSrc) console.log(`      data-src: ${ep.dataSrc}`);
                    if (ep.dataUrl) console.log(`      data-url: ${ep.dataUrl}`);
                    if (ep.onclick) console.log(`      onclick: ${ep.onclick.substring(0, 60)}...`);
                });
                console.log('');
            }

            this.episodes = episodes;

            // 6. Tentar clicar no primeiro episódio e capturar source
            if (episodes.length > 0) {
                await this.extractVideoSource(playerFrame, episodes[0]);
            }

            // 7. Resultados
            this.printResults(title);

        } catch (error) {
            console.error(`❌ Erro: ${error.message}`);
        }
    }

    async extractVideoSource(frame, episode) {
        console.log(`\n🎯 Tentando extrair source do episódio: ${episode.number}\n`);

        try {
            // Clicar no episódio
            await frame.evaluate((ep) => {
                const selector = ep.selector;
                const elements = document.querySelectorAll(selector);

                // Encontrar o elemento correto
                for (const el of elements) {
                    const num = el.querySelector('.numerando')?.textContent?.trim();
                    if (num === ep.number) {
                        el.click();
                        console.log(`Clicado em: ${ep.number}`);
                        break;
                    }
                }
            }, episode);

            // Aguardar player carregar
            await frame.waitForTimeout(5000);

            // Extrair source do vídeo
            const videoData = await frame.evaluate(() => {
                const sources = [];

                // Procurar por elementos <source>
                const sourceElements = document.querySelectorAll('source, video source');
                sourceElements.forEach(src => {
                    sources.push({
                        type: 'source-tag',
                        url: src.src || src.getAttribute('src'),
                        quality: src.getAttribute('label') || src.getAttribute('size') || 'auto'
                    });
                });

                // Procurar por URLs no JavaScript
                const scripts = document.querySelectorAll('script');
                scripts.forEach(script => {
                    const content = script.textContent || '';

                    // Buscar M3U8
                    const m3u8Matches = content.match(/https?:\/\/[^\s"']+\.m3u8[^\s"']*/g);
                    if (m3u8Matches) {
                        m3u8Matches.forEach(url => {
                            sources.push({ type: 'm3u8', url, quality: 'auto' });
                        });
                    }

                    // Buscar MP4
                    const mp4Matches = content.match(/https?:\/\/[^\s"']+\.mp4[^\s"']*/g);
                    if (mp4Matches) {
                        mp4Matches.forEach(url => {
                            sources.push({ type: 'mp4', url, quality: 'auto' });
                        });
                    }
                });

                return sources;
            });

            if (videoData.length > 0) {
                console.log(`✅ Encontrados ${videoData.length} sources:\n`);
                videoData.forEach((src, idx) => {
                    console.log(`   ${idx + 1}. [${src.type}] ${src.url}`);
                });

                this.videoSources = videoData;
            } else {
                console.log('⚠️  Nenhum source encontrado diretamente');
                console.log('💡 O vídeo pode estar carregando via JavaScript dinâmico');
            }

        } catch (error) {
            console.log(`❌ Erro ao extrair source: ${error.message}`);
        }
    }

    printResults(title) {
        console.log('\n' + '='.repeat(70));
        console.log('📊 RESUMO FINAL');
        console.log('='.repeat(70));
        console.log(`\n📺 Série: ${title}`);
        console.log(`📋 Total de Episódios: ${this.episodes.length}`);
        console.log(`🎬 Sources Capturados: ${this.videoSources.length}`);
        console.log('\n' + '='.repeat(70));
        console.log('✅ Análise concluída!\n');
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 Navegador fechado');
        }
    }

    exportResults() {
        return {
            episodes: this.episodes,
            videoSources: this.videoSources,
            summary: {
                totalEpisodes: this.episodes.length,
                totalSources: this.videoSources.length
            }
        };
    }
}

// ============================================
// EXECUÇÃO
// ============================================

async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log('❌ Uso: node analyze-series-v2.js <URL_SERIE>');
        console.log('   Exemplo: node analyze-series-v2.js https://www.maxseries.pics/series/assistir-sandokan-online');
        process.exit(1);
    }

    const seriesUrl = args[0];
    const analyzer = new SeriesAnalyzerV2();

    try {
        await analyzer.init();
        await analyzer.analyzeSeries(seriesUrl);

        // Salvar resultados
        const results = analyzer.exportResults();
        const fs = require('fs');
        fs.writeFileSync('series-analysis-v2.json', JSON.stringify(results, null, 2));
        console.log('\n💾 Resultados salvos em: series-analysis-v2.json\n');

    } catch (error) {
        console.error(`\n❌ Erro fatal: ${error.message}`);
    } finally {
        await analyzer.close();
    }
}

main();
