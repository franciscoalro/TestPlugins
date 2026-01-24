/**
 * MaxSeries Video Extractor - Puppeteer Test
 * 
 * Instalação:
 * npm install puppeteer
 * 
 * Uso:
 * node test-puppeteer-extractor.js https://www.maxseries.pics/series/assistir-sandokan-online
 */

const puppeteer = require('puppeteer');

class PuppeteerVideoExtractor {
    constructor() {
        this.browser = null;
        this.page = null;
        this.capturedUrls = new Set();
        this.iframeData = [];
    }

    async init() {
        console.log('🚀 Iniciando Puppeteer...\n');

        this.browser = await puppeteer.launch({
            headless: false, // Mostrar navegador para debug
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security', // Permitir CORS para testes
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        });

        this.page = await this.browser.newPage();

        // Configurar User-Agent
        await this.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        );

        // Interceptar requisições de rede
        await this.setupNetworkInterception();

        console.log('✅ Puppeteer configurado\n');
    }

    async setupNetworkInterception() {
        await this.page.setRequestInterception(true);

        this.page.on('request', request => {
            const url = request.url();

            // Log de requisições de vídeo
            if (this.isVideoUrl(url)) {
                console.log(`📡 Requisição: ${url}`);
                this.capturedUrls.add(url);
            }

            request.continue();
        });

        this.page.on('response', async response => {
            const url = response.url();

            if (this.isVideoUrl(url)) {
                console.log(`📥 Resposta: ${url} (Status: ${response.status()})`);

                // Capturar headers importantes
                const headers = response.headers();
                if (headers['content-type']) {
                    console.log(`   Content-Type: ${headers['content-type']}`);
                }
            }
        });
    }

    isVideoUrl(url) {
        const videoExtensions = ['.m3u8', '.mp4', '.ts', '.woff2', '.txt'];
        const videoKeywords = ['video', 'stream', 'playlist', 'segment'];

        return videoExtensions.some(ext => url.includes(ext)) ||
            videoKeywords.some(kw => url.toLowerCase().includes(kw));
    }

    async extractFromEpisode(episodeUrl) {
        console.log(`🔍 Analisando: ${episodeUrl}\n`);

        try {
            // 1. Navegar para página do episódio
            console.log('📥 Carregando página...');
            await this.page.goto(episodeUrl, {
                waitUntil: 'networkidle2',
                timeout: 30000
            });

            console.log('✅ Página carregada\n');

            // 2. Aguardar iframes carregarem
            await this.page.waitForSelector('iframe', { timeout: 10000 });

            // 3. Extrair informações dos iframes
            const iframes = await this.page.$$('iframe');
            console.log(`📊 Encontrados ${iframes.length} iframes\n`);

            for (let i = 0; i < iframes.length; i++) {
                await this.analyzeIframe(iframes[i], i + 1);
            }

            // 4. Aguardar mais requisições
            console.log('\n⏳ Aguardando 10 segundos para capturar mais requisições...\n');
            await this.page.waitForTimeout(10000);

            // 5. Resultados
            this.printResults();

        } catch (error) {
            console.error(`❌ Erro: ${error.message}`);
        }
    }

    async analyzeIframe(iframe, index) {
        try {
            const src = await iframe.evaluate(el => el.src);

            if (!src) {
                console.log(`⚠️  Iframe ${index}: Sem URL`);
                return;
            }

            console.log(`🎥 Iframe ${index}:`);
            console.log(`   URL: ${src}`);

            const playerType = this.identifyPlayer(src);
            console.log(`   Tipo: ${playerType}`);

            const iframeInfo = {
                index,
                url: src,
                type: playerType,
                videoUrls: []
            };

            // Tentar acessar conteúdo do iframe
            try {
                const frame = await iframe.contentFrame();

                if (frame) {
                    console.log(`   ✅ Acesso ao frame permitido`);

                    // Aguardar frame carregar
                    await frame.waitForTimeout(2000);

                    // Extrair HTML do frame
                    const html = await frame.content();

                    // Buscar URLs de vídeo no HTML
                    const videoUrls = this.extractVideoUrlsFromHtml(html);

                    if (videoUrls.length > 0) {
                        console.log(`   🎯 Encontrados ${videoUrls.length} URLs no HTML:`);
                        videoUrls.forEach(url => {
                            console.log(`      - ${url}`);
                            this.capturedUrls.add(url);
                        });
                        iframeInfo.videoUrls = videoUrls;
                    } else {
                        console.log(`   ⚠️  Nenhuma URL encontrada no HTML`);
                    }
                } else {
                    console.log(`   ❌ Acesso ao frame bloqueado`);
                }
            } catch (error) {
                console.log(`   ❌ Erro ao acessar frame: ${error.message}`);
            }

            this.iframeData.push(iframeInfo);
            console.log('');

        } catch (error) {
            console.error(`❌ Erro ao analisar iframe ${index}: ${error.message}`);
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

    extractVideoUrlsFromHtml(html) {
        const urls = [];

        // Regex para diferentes formatos
        const patterns = [
            /https?:\/\/[^\s"'<>]+\.m3u8[^\s"'<>]*/gi,
            /https?:\/\/[^\s"'<>]+\.mp4[^\s"'<>]*/gi,
            /https?:\/\/[^\s"'<>]+\.ts[^\s"'<>]*/gi,
            /https?:\/\/[^\s"'<>]+\.woff2[^\s"'<>]*/gi
        ];

        patterns.forEach(pattern => {
            const matches = html.match(pattern) || [];
            matches.forEach(url => {
                if (!urls.includes(url)) {
                    urls.push(url);
                }
            });
        });

        return urls;
    }

    printResults() {
        console.log('\n' + '='.repeat(70));
        console.log('📊 RESUMO DA EXTRAÇÃO');
        console.log('='.repeat(70));

        // Iframes
        this.iframeData.forEach(iframe => {
            console.log(`\n🎥 Player ${iframe.index} - ${iframe.type}`);
            console.log(`   URL: ${iframe.url}`);

            if (iframe.videoUrls.length > 0) {
                console.log(`   ✅ Vídeos encontrados:`);
                iframe.videoUrls.forEach(url => console.log(`      ${url}`));
            } else {
                console.log(`   ⚠️  Nenhum vídeo encontrado diretamente`);
            }
        });

        // Todas as URLs capturadas
        if (this.capturedUrls.size > 0) {
            console.log(`\n\n📡 TODAS AS URLs CAPTURADAS (${this.capturedUrls.size}):`);
            console.log('─'.repeat(70));

            const urlsByType = this.categorizeUrls();

            Object.keys(urlsByType).forEach(type => {
                console.log(`\n${type}:`);
                urlsByType[type].forEach(url => console.log(`   ${url}`));
            });
        } else {
            console.log('\n⚠️  Nenhuma URL de vídeo capturada');
        }

        console.log('\n' + '='.repeat(70));
        console.log('✅ Análise concluída!\n');
    }

    categorizeUrls() {
        const categories = {
            '🎬 M3U8 Playlists': [],
            '📹 MP4 Videos': [],
            '📦 TS Segments': [],
            '🎭 Disfarçados (.woff2, .txt)': [],
            '🔗 Outros': []
        };

        Array.from(this.capturedUrls).forEach(url => {
            if (url.includes('.m3u8')) {
                categories['🎬 M3U8 Playlists'].push(url);
            } else if (url.includes('.mp4')) {
                categories['📹 MP4 Videos'].push(url);
            } else if (url.includes('.ts')) {
                categories['📦 TS Segments'].push(url);
            } else if (url.includes('.woff2') || url.includes('.txt')) {
                categories['🎭 Disfarçados (.woff2, .txt)'].push(url);
            } else {
                categories['🔗 Outros'].push(url);
            }
        });

        // Remover categorias vazias
        Object.keys(categories).forEach(key => {
            if (categories[key].length === 0) {
                delete categories[key];
            }
        });

        return categories;
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 Navegador fechado');
        }
    }

    // Método para exportar resultados como JSON
    exportResults() {
        return {
            iframes: this.iframeData,
            capturedUrls: Array.from(this.capturedUrls),
            summary: {
                totalIframes: this.iframeData.length,
                totalUrls: this.capturedUrls.size,
                urlsByType: this.categorizeUrls()
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
        console.log('❌ Uso: node test-puppeteer-extractor.js <URL_EPISODIO>');
        console.log('   Exemplo: node test-puppeteer-extractor.js https://maxseries.one/episodio/258444');
        process.exit(1);
    }

    const episodeUrl = args[0];

    if (!episodeUrl.startsWith('http')) {
        console.log('❌ URL inválida. Deve começar com http:// ou https://');
        process.exit(1);
    }

    const extractor = new PuppeteerVideoExtractor();

    try {
        await extractor.init();
        await extractor.extractFromEpisode(episodeUrl);

        // Exportar resultados
        const results = extractor.exportResults();
        const fs = require('fs');
        const outputFile = 'puppeteer-results.json';
        fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
        console.log(`\n💾 Resultados salvos em: ${outputFile}\n`);

    } catch (error) {
        console.error(`\n❌ Erro fatal: ${error.message}`);
    } finally {
        await extractor.close();
    }
}

main();
