/**
 * MaxSeries Series Page Analyzer - Puppeteer
 * 
 * Analisa páginas de SÉRIES (não episódios individuais)
 * Extrai lista de episódios e seus iframes/sources
 * 
 * Uso:
 * node analyze-series-page.js https://www.maxseries.pics/series/assistir-sandokan-online
 */

const puppeteer = require('puppeteer');

class SeriesPageAnalyzer {
    constructor() {
        this.browser = null;
        this.page = null;
        this.episodes = [];
        this.iframeData = [];
    }

    async init() {
        console.log('🚀 Iniciando análise de série...\n');

        this.browser = await puppeteer.launch({
            headless: false,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        });

        this.page = await this.browser.newPage();

        await this.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        );

        console.log('✅ Navegador configurado\n');
    }

    async analyzeSeriesPage(seriesUrl) {
        console.log(`🔍 Analisando série: ${seriesUrl}\n`);

        try {
            // 1. Navegar para página da série
            console.log('📥 Carregando página da série...');
            await this.page.goto(seriesUrl, {
                waitUntil: 'networkidle2',
                timeout: 30000
            });

            console.log('✅ Página carregada\n');

            // 2. Extrair informações da série
            const seriesInfo = await this.extractSeriesInfo();
            console.log('📺 Informações da Série:');
            console.log(`   Título: ${seriesInfo.title}`);
            console.log(`   Temporadas: ${seriesInfo.seasons}`);
            console.log('');

            // 3. Extrair lista de episódios
            console.log('📋 Extraindo lista de episódios...\n');
            const episodes = await this.extractEpisodesList();

            console.log(`✅ Encontrados ${episodes.length} episódios\n`);

            // 4. Analisar estrutura dos episódios
            await this.analyzeEpisodeStructure(episodes.slice(0, 3)); // Analisar apenas 3 primeiros

            // 5. Analisar iframes da página principal
            await this.analyzeMainIframes();

            // 6. Resultados
            this.printResults();

        } catch (error) {
            console.error(`❌ Erro: ${error.message}`);
        }
    }

    async extractSeriesInfo() {
        return await this.page.evaluate(() => {
            const title = document.querySelector('h1, .title, .serie-title')?.textContent?.trim() || 'Desconhecido';

            // Contar temporadas
            const seasonElements = document.querySelectorAll('[data-season], .season, .se-c');
            const seasons = seasonElements.length || 1;

            return { title, seasons };
        });
    }

    async extractEpisodesList() {
        return await this.page.evaluate(() => {
            const episodes = [];

            // Tentar diferentes seletores comuns
            const selectors = [
                '.episodios li',
                '.se-c .episodios li',
                '.episodes-list li',
                '[data-episode]',
                '.episode-item'
            ];

            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);

                if (elements.length > 0) {
                    elements.forEach((el, index) => {
                        // Extrair informações do episódio
                        const episodeNumber = el.querySelector('.numerando, .episode-number')?.textContent?.trim() || `${index + 1}`;
                        const episodeTitle = el.querySelector('.episodiotitle, .episode-title, a')?.textContent?.trim() || 'Sem título';
                        const episodeUrl = el.querySelector('a')?.href || '';

                        // Extrair data-post ou data-episode
                        const dataPost = el.getAttribute('data-post') || '';
                        const dataEpisode = el.getAttribute('data-episode') || '';

                        episodes.push({
                            number: episodeNumber,
                            title: episodeTitle,
                            url: episodeUrl,
                            dataPost,
                            dataEpisode,
                            element: selector
                        });
                    });

                    break; // Parar no primeiro seletor que funcionar
                }
            }

            return episodes;
        });
    }

    async analyzeEpisodeStructure(episodes) {
        console.log('🔬 Analisando estrutura dos episódios...\n');

        for (let i = 0; i < episodes.length; i++) {
            const episode = episodes[i];
            console.log(`📺 Episódio ${episode.number}: ${episode.title}`);
            console.log(`   URL: ${episode.url || 'N/A'}`);
            console.log(`   Data-Post: ${episode.dataPost || 'N/A'}`);
            console.log(`   Data-Episode: ${episode.dataEpisode || 'N/A'}`);
            console.log('');

            this.episodes.push(episode);
        }
    }

    async analyzeMainIframes() {
        console.log('🎬 Analisando iframes da página principal...\n');

        const iframes = await this.page.$$('iframe');
        console.log(`📊 Encontrados ${iframes.length} iframes\n`);

        for (let i = 0; i < iframes.length; i++) {
            const iframe = iframes[i];
            const src = await iframe.evaluate(el => el.src);

            if (!src) continue;

            console.log(`🎥 Iframe ${i + 1}:`);
            console.log(`   URL: ${src}`);

            const playerType = this.identifyPlayer(src);
            console.log(`   Tipo: ${playerType}`);

            // Tentar extrair HTML do iframe
            try {
                const frame = await iframe.contentFrame();

                if (frame) {
                    console.log(`   ✅ Acesso ao frame permitido`);

                    // Aguardar frame carregar
                    await frame.waitForTimeout(2000);

                    // Extrair estrutura de episódios dentro do iframe
                    const episodesInIframe = await frame.evaluate(() => {
                        const episodes = [];

                        // Procurar por elementos de episódio
                        const episodeElements = document.querySelectorAll('[data-episode], .episode, .ep-item');

                        episodeElements.forEach(el => {
                            const episodeData = {
                                dataEpisode: el.getAttribute('data-episode') || '',
                                dataSrc: el.getAttribute('data-src') || '',
                                dataUrl: el.getAttribute('data-url') || '',
                                text: el.textContent?.trim() || '',
                                html: el.outerHTML?.substring(0, 200) || ''
                            };

                            episodes.push(episodeData);
                        });

                        return episodes;
                    });

                    if (episodesInIframe.length > 0) {
                        console.log(`   🎯 Encontrados ${episodesInIframe.length} episódios dentro do iframe:`);
                        episodesInIframe.slice(0, 3).forEach((ep, idx) => {
                            console.log(`      Episódio ${idx + 1}:`);
                            console.log(`         data-episode: ${ep.dataEpisode}`);
                            console.log(`         data-src: ${ep.dataSrc}`);
                            console.log(`         data-url: ${ep.dataUrl}`);
                        });
                    } else {
                        console.log(`   ⚠️  Nenhum episódio encontrado dentro do iframe`);
                    }

                    this.iframeData.push({
                        index: i + 1,
                        url: src,
                        type: playerType,
                        episodesCount: episodesInIframe.length,
                        episodes: episodesInIframe
                    });

                } else {
                    console.log(`   ❌ Acesso ao frame bloqueado (CORS)`);
                }
            } catch (error) {
                console.log(`   ❌ Erro ao acessar frame: ${error.message}`);
            }

            console.log('');
        }
    }

    identifyPlayer(url) {
        const urlLower = url.toLowerCase();

        if (urlLower.includes('megaembed')) return 'MegaEmbed';
        if (urlLower.includes('playerembedapi') || urlLower.includes('playerthree')) return 'PlayerEmbedAPI';
        if (urlLower.includes('doodstream') || urlLower.includes('dood')) return 'DoodStream';
        if (urlLower.includes('streamtape')) return 'StreamTape';

        return 'Desconhecido';
    }

    printResults() {
        console.log('\n' + '='.repeat(70));
        console.log('📊 RESUMO DA ANÁLISE');
        console.log('='.repeat(70));

        // Episódios na página
        console.log(`\n📺 Episódios na Página Principal: ${this.episodes.length}`);

        if (this.episodes.length > 0) {
            console.log('\nPrimeiros 5 episódios:');
            this.episodes.slice(0, 5).forEach(ep => {
                console.log(`   ${ep.number} - ${ep.title}`);
            });
        }

        // Iframes
        console.log(`\n\n🎬 Iframes Analisados: ${this.iframeData.length}`);

        this.iframeData.forEach(iframe => {
            console.log(`\n   Iframe ${iframe.index} - ${iframe.type}`);
            console.log(`   URL: ${iframe.url}`);
            console.log(`   Episódios dentro: ${iframe.episodesCount}`);

            if (iframe.episodesCount > 0) {
                console.log(`   ✅ Este iframe contém a lista de episódios!`);
            }
        });

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
            iframes: this.iframeData,
            summary: {
                totalEpisodes: this.episodes.length,
                totalIframes: this.iframeData.length,
                iframesWithEpisodes: this.iframeData.filter(i => i.episodesCount > 0).length
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
        console.log('❌ Uso: node analyze-series-page.js <URL_SERIE>');
        console.log('   Exemplo: node analyze-series-page.js https://www.maxseries.pics/series/assistir-sandokan-online');
        process.exit(1);
    }

    const seriesUrl = args[0];

    if (!seriesUrl.startsWith('http')) {
        console.log('❌ URL inválida. Deve começar com http:// ou https://');
        process.exit(1);
    }

    const analyzer = new SeriesPageAnalyzer();

    try {
        await analyzer.init();
        await analyzer.analyzeSeriesPage(seriesUrl);

        // Exportar resultados
        const results = analyzer.exportResults();
        const fs = require('fs');
        const outputFile = 'series-analysis.json';
        fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
        console.log(`\n💾 Resultados salvos em: ${outputFile}\n`);

    } catch (error) {
        console.error(`\n❌ Erro fatal: ${error.message}`);
    } finally {
        await analyzer.close();
    }
}

main();
