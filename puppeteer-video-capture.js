/**
 * Captura de URLs de Vídeo com Puppeteer Stealth
 * Alternativa ao Python para capturar vídeos de sites protegidos
 * 
 * Uso: node puppeteer-video-capture.js [URL]
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

// Usar plugin stealth para evitar detecção
puppeteer.use(StealthPlugin());

// Configurações
const CONFIG = {
    headless: false,  // Mude para true para rodar sem janela
    timeout: 60000,
    waitForVideo: 15000,
    
    // Padrões de URL de vídeo
    videoPatterns: ['.m3u8', '.mp4', '.ts', '/hls/', 'master.txt', '/video/', 'stream'],
    
    // Domínios conhecidos
    doodStreamDomains: [
        'myvidplay.com', 'bysebuho.com', 'g9r6.com',
        'doodstream.com', 'dood.to', 'dood.watch', 'dood.pm',
        'dood.wf', 'dood.re', 'dood.so', 'dood.cx'
    ],
    
    playerHosts: ['playerthree.online', 'megaembed.link', 'playerembedapi.link']
};

class VideoCapture {
    constructor() {
        this.browser = null;
        this.page = null;
        this.foundVideos = [];
        this.allRequests = [];
    }
    
    log(message, type = 'INFO') {
        const timestamp = new Date().toLocaleTimeString();
        const emoji = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'VIDEO': '🎬',
            'DEBUG': '🔍'
        }[type] || '';
        console.log(`[${timestamp}] ${emoji} ${message}`);
    }
    
    async init() {
        this.log('Iniciando Puppeteer com stealth...');
        
        this.browser = await puppeteer.launch({
            headless: CONFIG.headless,
            args: [
                '--window-size=1920,1080',
                '--disable-notifications',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--lang=pt-BR'
            ]
        });
        
        this.page = await this.browser.newPage();
        
        // Configurar viewport
        await this.page.setViewport({ width: 1920, height: 1080 });
        
        // Configurar user agent
        await this.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        );
        
        // Interceptar requisições de rede
        await this.page.setRequestInterception(true);
        
        this.page.on('request', (request) => {
            const url = request.url();
            
            this.allRequests.push({
                url: url,
                headers: request.headers(),
                type: 'request'
            });
            
            // Verificar se é vídeo
            if (this.isVideoUrl(url)) {
                this.foundVideos.push({
                    url: url,
                    headers: request.headers(),
                    source_type: this.getVideoType(url),
                    host: this.identifyHost(url),
                    found_at: new Date().toISOString()
                });
                this.log(`VÍDEO ENCONTRADO: ${url.substring(0, 80)}...`, 'VIDEO');
            }
            
            request.continue();
        });
        
        this.page.on('response', async (response) => {
            const url = response.url();
            
            if (this.isVideoUrl(url)) {
                // Já foi capturado no request
            }
        });
        
        this.log('Browser iniciado com sucesso!', 'SUCCESS');
    }
    
    isVideoUrl(url) {
        const urlLower = url.toLowerCase();
        return CONFIG.videoPatterns.some(pattern => urlLower.includes(pattern));
    }
    
    getVideoType(url) {
        const urlLower = url.toLowerCase();
        if (urlLower.includes('.m3u8')) return 'm3u8';
        if (urlLower.includes('.mp4')) return 'mp4';
        if (urlLower.includes('.ts')) return 'ts';
        return 'stream';
    }
    
    identifyHost(url) {
        const urlLower = url.toLowerCase();
        
        if (CONFIG.doodStreamDomains.some(d => urlLower.includes(d))) {
            return 'doodstream';
        }
        if (urlLower.includes('megaembed')) return 'megaembed';
        if (urlLower.includes('playerembedapi')) return 'playerembedapi';
        if (urlLower.includes('playerthree')) return 'playerthree';
        if (urlLower.includes('storage.googleapis')) return 'google_storage';
        if (urlLower.includes('akamai')) return 'akamai';
        if (urlLower.includes('cloudfront')) return 'cloudfront';
        
        try {
            const urlObj = new URL(url);
            return urlObj.hostname;
        } catch {
            return 'unknown';
        }
    }
    
    async delay(ms) {
        const jitter = Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, ms + jitter));
    }
    
    async extractIframes() {
        const iframes = await this.page.$$eval('iframe', frames => 
            frames.map(f => f.src || f.getAttribute('data-src')).filter(Boolean)
        );
        
        return iframes.map(src => {
            if (src.startsWith('//')) return 'https:' + src;
            return src;
        });
    }
    
    async extractPlayerSources() {
        const sources = await this.page.$$eval(
            'button[data-source], li[data-source], a[data-source], [data-video], [data-url]',
            elements => elements.map(el => ({
                source: el.getAttribute('data-source') || 
                        el.getAttribute('data-video') || 
                        el.getAttribute('data-url'),
                text: el.innerText.trim()
            })).filter(s => s.source && s.source.startsWith('http'))
        );
        
        // Filtrar YouTube
        return sources.filter(s => 
            !s.source.toLowerCase().includes('youtube') && 
            !s.source.toLowerCase().includes('youtu.be')
        );
    }
    
    async navigateAndCapture(url, waitTime = CONFIG.waitForVideo) {
        this.log(`Navegando para: ${url.substring(0, 60)}...`);
        
        try {
            await this.page.goto(url, { 
                waitUntil: 'networkidle2',
                timeout: CONFIG.timeout 
            });
            
            this.log(`Aguardando ${waitTime/1000}s para capturar requisições...`);
            await this.delay(waitTime);
            
        } catch (error) {
            this.log(`Erro ao navegar: ${error.message}`, 'ERROR');
        }
    }
    
    async captureFromMaxSeries(url) {
        this.log(`=== Capturando de MaxSeries: ${url} ===`, 'INFO');
        
        await this.navigateAndCapture(url, 5000);
        
        // Extrair iframes
        const iframes = await this.extractIframes();
        this.log(`Encontrados ${iframes.length} iframes`);
        
        // Encontrar player iframes
        const playerIframes = iframes.filter(iframe => 
            CONFIG.playerHosts.some(host => iframe.includes(host))
        );
        
        for (const iframe of playerIframes.slice(0, 2)) {
            this.log(`Processando player: ${iframe.substring(0, 60)}...`);
            
            await this.navigateAndCapture(iframe, 5000);
            
            // Extrair fontes do player
            const sources = await this.extractPlayerSources();
            this.log(`Encontradas ${sources.length} fontes no player`);
            
            // Testar cada fonte
            for (const source of sources.slice(0, 5)) {
                this.log(`Testando fonte: ${source.text} - ${source.source.substring(0, 50)}...`);
                await this.navigateAndCapture(source.source, 12000);
            }
        }
    }
    
    async captureFromPlayer(url) {
        this.log(`=== Capturando de player: ${url} ===`, 'INFO');
        
        await this.navigateAndCapture(url, 10000);
        
        // Extrair fontes
        const sources = await this.extractPlayerSources();
        
        for (const source of sources.slice(0, 5)) {
            this.log(`Testando fonte: ${source.source.substring(0, 60)}...`);
            await this.navigateAndCapture(source.source, 12000);
        }
    }
    
    async run(url) {
        console.log('\n' + '='.repeat(70));
        console.log('  PUPPETEER VIDEO CAPTURE - Stealth Mode');
        console.log('  Para uso com Cloudstream plugins');
        console.log('='.repeat(70));
        console.log(`\n  URL: ${url}\n`);
        
        const results = {
            input_url: url,
            videos: [],
            total_requests: 0,
            started_at: new Date().toISOString(),
            success: false
        };
        
        try {
            await this.init();
            
            // Determinar tipo de URL
            if (url.toLowerCase().includes('maxseries')) {
                await this.captureFromMaxSeries(url);
            } else if (CONFIG.playerHosts.some(host => url.includes(host))) {
                await this.captureFromPlayer(url);
            } else {
                await this.navigateAndCapture(url, 20000);
            }
            
            // Remover duplicatas
            const uniqueVideos = [];
            const seen = new Set();
            
            for (const video of this.foundVideos) {
                if (!seen.has(video.url)) {
                    seen.add(video.url);
                    uniqueVideos.push(video);
                }
            }
            
            results.videos = uniqueVideos;
            results.total_requests = this.allRequests.length;
            results.success = uniqueVideos.length > 0;
            results.finished_at = new Date().toISOString();
            
            // Log resumo
            console.log('\n' + '='.repeat(70));
            console.log('  RESULTADOS');
            console.log('='.repeat(70));
            console.log(`\n  Total de requisições: ${this.allRequests.length}`);
            console.log(`  Vídeos encontrados: ${uniqueVideos.length}\n`);
            
            uniqueVideos.forEach((video, i) => {
                console.log(`  ${i + 1}. [${video.host}] ${video.url}`);
            });
            
        } catch (error) {
            this.log(`Erro fatal: ${error.message}`, 'ERROR');
            results.error = error.message;
        } finally {
            if (this.browser) {
                await this.browser.close();
                this.log('Browser encerrado', 'INFO');
            }
        }
        
        return results;
    }
    
    saveResults(results, filename = null) {
        if (!filename) {
            const now = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
            filename = `video_capture_${now}.json`;
        }
        
        const fs = require('fs');
        fs.writeFileSync(filename, JSON.stringify(results, null, 2));
        this.log(`Resultados salvos em: ${filename}`, 'SUCCESS');
    }
}

// Main
async function main() {
    const defaultUrl = 'https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/';
    const url = process.argv[2] || defaultUrl;
    
    const capturer = new VideoCapture();
    const results = await capturer.run(url);
    capturer.saveResults(results);
    
    if (results.videos.length > 0) {
        console.log('\n' + '='.repeat(70));
        console.log('  VÍDEOS ENCONTRADOS - Use estas URLs no Cloudstream');
        console.log('='.repeat(70));
        
        results.videos.forEach((video, i) => {
            console.log(`\n  ${i + 1}. Host: ${video.host}`);
            console.log(`     Tipo: ${video.source_type}`);
            console.log(`     URL:  ${video.url}`);
        });
    } else {
        console.log('\n  ❌ Nenhum vídeo encontrado.');
        console.log('     Tente com uma URL diferente ou verifique se o site está online.');
    }
    
    console.log('\n');
}

main().catch(console.error);
