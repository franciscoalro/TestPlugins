/**
 * MaxSeries Video Extractor - JavaScript (Versão compilada para navegador)
 * 
 * COMO USAR:
 * 1. Abra https://maxseries.one/episodio/[ID] no navegador
 * 2. Pressione F12 para abrir DevTools
 * 3. Vá na aba "Console"
 * 4. Cole TODO este código e pressione Enter
 * 5. Aguarde a análise automática
 */

class MaxSeriesExtractor {
    constructor() {
        this.results = [];
        this.capturedUrls = new Set();
        console.log('🎬 MaxSeries Video Extractor v1.0');
        console.log('================================\n');
    }

    async analyzeIframes() {
        const iframes = document.querySelectorAll('iframe');
        console.log(`📊 Encontrados ${iframes.length} iframes na página\n`);

        for (let i = 0; i < iframes.length; i++) {
            await this.analyzeIframe(iframes[i], i + 1);
        }

        this.printResults();
    }

    async analyzeIframe(iframe, index) {
        const src = iframe.src;

        if (!src) {
            console.log(`⚠️  Iframe ${index}: Sem URL`);
            return;
        }

        console.log(`\n🎥 Iframe ${index}:`);
        console.log(`   URL: ${src}`);

        const playerType = this.identifyPlayer(src);
        console.log(`   Tipo: ${playerType}`);

        const videoSource = {
            playerType,
            iframeUrl: src,
            videoUrls: [],
            index
        };

        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;

            if (iframeDoc) {
                console.log(`   ✅ Acesso ao conteúdo do iframe permitido`);

                const html = iframeDoc.documentElement.innerHTML;
                const videoUrls = this.extractVideoUrls(html);

                videoSource.videoUrls = videoUrls;

                if (videoUrls.length > 0) {
                    console.log(`   🎯 Encontrados ${videoUrls.length} URLs de vídeo:`);
                    videoUrls.forEach(url => console.log(`      - ${url}`));
                } else {
                    console.log(`   ⚠️  Nenhuma URL de vídeo encontrada no HTML`);
                }
            } else {
                console.log(`   ❌ Acesso bloqueado (CORS)`);
                console.log(`   💡 Abra ${src} em nova aba e execute lá`);
            }
        } catch (error) {
            console.log(`   ❌ Erro: ${error.message}`);
        }

        this.results.push(videoSource);
    }

    identifyPlayer(url) {
        const urlLower = url.toLowerCase();

        if (urlLower.includes('megaembed')) return 'MegaEmbed';
        if (urlLower.includes('playerembedapi') || urlLower.includes('playerthree')) return 'PlayerEmbedAPI';
        if (urlLower.includes('doodstream') || urlLower.includes('dood')) return 'DoodStream';
        if (urlLower.includes('streamtape')) return 'StreamTape';

        return 'Desconhecido';
    }

    extractVideoUrls(html) {
        const urls = [];

        // M3U8
        const m3u8Regex = /https?:\/\/[^\s"'<>]+\.m3u8[^\s"'<>]*/gi;
        const m3u8Matches = html.match(m3u8Regex) || [];

        // MP4
        const mp4Regex = /https?:\/\/[^\s"'<>]+\.mp4[^\s"'<>]*/gi;
        const mp4Matches = html.match(mp4Regex) || [];

        // TS
        const tsRegex = /https?:\/\/[^\s"'<>]+\.ts[^\s"'<>]*/gi;
        const tsMatches = html.match(tsRegex) || [];

        const allMatches = [...m3u8Matches, ...mp4Matches, ...tsMatches];

        allMatches.forEach(url => {
            if (!this.capturedUrls.has(url)) {
                this.capturedUrls.add(url);
                urls.push(url);
            }
        });

        return urls;
    }

    interceptNetworkRequests() {
        console.log('\n🔍 Iniciando interceptação de requisições...\n');

        const originalFetch = window.fetch;
        const self = this;

        window.fetch = async function (...args) {
            const response = await originalFetch(...args);
            const url = typeof args[0] === 'string' ? args[0] : args[0].url;

            if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('.ts') || url.includes('.woff2')) {
                console.log(`📡 Requisição capturada: ${url}`);
                self.capturedUrls.add(url);
            }

            return response;
        };

        // Interceptar XMLHttpRequest também
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function (method, url) {
            if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('.ts') || url.includes('.woff2')) {
                console.log(`📡 XHR capturado: ${url}`);
                self.capturedUrls.add(url);
            }
            return originalOpen.apply(this, arguments);
        };

        console.log('✅ Interceptação ativada!\n');
    }

    printResults() {
        console.log('\n\n' + '='.repeat(60));
        console.log('📊 RESUMO DA ANÁLISE');
        console.log('='.repeat(60));

        this.results.forEach(result => {
            console.log(`\n🎥 Player ${result.index} - ${result.playerType}`);
            console.log(`   URL: ${result.iframeUrl}`);

            if (result.videoUrls.length > 0) {
                console.log(`   ✅ Vídeos encontrados:`);
                result.videoUrls.forEach(url => console.log(`      ${url}`));
            } else {
                console.log(`   ⚠️  Nenhum vídeo encontrado diretamente`);
            }
        });

        if (this.capturedUrls.size > 0) {
            console.log(`\n\n📡 TODAS AS URLs CAPTURADAS (${this.capturedUrls.size}):`);
            Array.from(this.capturedUrls).forEach(url => console.log(`   ${url}`));
        }

        console.log('\n' + '='.repeat(60));
        console.log('✅ Análise concluída!\n');
    }

    copyToClipboard() {
        const urls = Array.from(this.capturedUrls).join('\n');

        navigator.clipboard.writeText(urls).then(() => {
            console.log('✅ URLs copiadas para área de transferência!');
        }).catch(err => {
            console.error('❌ Erro ao copiar:', err);
            console.log('\n📋 URLs (copie manualmente):');
            console.log(urls);
        });
    }

    // Método para analisar um iframe específico em nova aba
    openIframeInNewTab(index) {
        const result = this.results[index - 1];
        if (result) {
            window.open(result.iframeUrl, '_blank');
            console.log(`✅ Iframe ${index} aberto em nova aba`);
            console.log(`💡 Execute este script novamente na nova aba para analisar o player`);
        } else {
            console.log(`❌ Iframe ${index} não encontrado`);
        }
    }
}

// ============================================
// EXECUÇÃO AUTOMÁTICA
// ============================================

(async () => {
    const extractor = new MaxSeriesExtractor();

    // 1. Interceptar requisições
    extractor.interceptNetworkRequests();

    // 2. Aguardar 2 segundos
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 3. Analisar iframes
    await extractor.analyzeIframes();

    // 4. Disponibilizar globalmente
    window.extractor = extractor;

    console.log('\n💡 COMANDOS DISPONÍVEIS:');
    console.log('   extractor.copyToClipboard()        - Copiar URLs');
    console.log('   extractor.analyzeIframes()         - Reanalizar');
    console.log('   extractor.openIframeInNewTab(1)    - Abrir iframe 1 em nova aba');
    console.log('\n⏳ Aguarde o vídeo carregar para capturar mais URLs...\n');
})();
