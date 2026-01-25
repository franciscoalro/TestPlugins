/**
 * MaxSeries Video Extractor - TypeScript Browser Script v2.0
 * 
 * Como usar:
 * 1. Abra a página do episódio no navegador (https://maxseries.pics/...)
 * 2. Abra o Console do DevTools (F12)
 * 3. Cole este script e pressione Enter
 * 4. O script irá analisar todos os iframes e capturar URLs de vídeo
 * 
 * Compatível com:
 * - MegaEmbed V9
 * - PlayerEmbedAPI
 * - MyVidPlay
 * - DoodStream
 * - E outros players
 */

interface VideoSource {
  playerType: string;
  iframeUrl: string;
  videoUrls: string[];
  index: number;
}

class MaxSeriesExtractor {
  private results: VideoSource[] = [];
  private capturedUrls: Set<string> = new Set();

  constructor() {
    console.log('🎬 MaxSeries Video Extractor v1.0');
    console.log('================================\n');
  }

  /**
   * Analisa todos os iframes da página
   */
  async analyzeIframes(): Promise<void> {
    const iframes = document.querySelectorAll('iframe');
    
    console.log(`📊 Encontrados ${iframes.length} iframes na página\n`);

    for (let i = 0; i < iframes.length; i++) {
      const iframe = iframes[i];
      await this.analyzeIframe(iframe, i + 1);
    }

    this.printResults();
  }

  /**
   * Analisa um iframe específico
   */
  private async analyzeIframe(iframe: HTMLIFrameElement, index: number): Promise<void> {
    const src = iframe.src;
    
    if (!src) {
      console.log(`⚠️  Iframe ${index}: Sem URL`);
      return;
    }

    console.log(`\n🎥 Iframe ${index}:`);
    console.log(`   URL: ${src}`);

    // Identificar tipo de player
    const playerType = this.identifyPlayer(src);
    console.log(`   Tipo: ${playerType}`);

    const videoSource: VideoSource = {
      playerType,
      iframeUrl: src,
      videoUrls: [],
      index
    };

    // Tentar acessar conteúdo do iframe (se same-origin)
    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
      
      if (iframeDoc) {
        console.log(`   ✅ Acesso ao conteúdo do iframe permitido`);
        
        // Procurar por URLs de vídeo no HTML
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
        console.log(`   ❌ Acesso bloqueado (CORS/Same-Origin Policy)`);
        console.log(`   💡 Solução: Abra o iframe em nova aba e execute o script lá`);
      }
    } catch (error) {
      console.log(`   ❌ Erro ao acessar iframe: ${error}`);
    }

    this.results.push(videoSource);
  }

  /**
   * Identifica o tipo de player baseado na URL
   */
  private identifyPlayer(url: string): string {
    const urlLower = url.toLowerCase();
    
    if (urlLower.includes('megaembed')) return 'MegaEmbed';
    if (urlLower.includes('playerembedapi')) return 'PlayerEmbedAPI';
    if (urlLower.includes('playerthree')) return 'PlayerThree';
    if (urlLower.includes('myvidplay')) return 'MyVidPlay';
    if (urlLower.includes('doodstream') || urlLower.includes('dood')) return 'DoodStream';
    if (urlLower.includes('streamtape')) return 'StreamTape';
    if (urlLower.includes('mixdrop')) return 'Mixdrop';
    
    return 'Desconhecido';
  }

  /**
   * Extrai URLs de vídeo do HTML
   */
  private extractVideoUrls(html: string): string[] {
    const urls: string[] = [];
    
    // Regex para M3U8 (HLS)
    const m3u8Regex = /https?:\/\/[^\s"'<>]+\.m3u8[^\s"'<>]*/gi;
    const m3u8Matches = html.match(m3u8Regex) || [];
    
    // Regex para MP4
    const mp4Regex = /https?:\/\/[^\s"'<>]+\.mp4[^\s"'<>]*/gi;
    const mp4Matches = html.match(mp4Regex) || [];
    
    // Regex para segmentos TS
    const tsRegex = /https?:\/\/[^\s"'<>]+\.ts[^\s"'<>]*/gi;
    const tsMatches = html.match(tsRegex) || [];
    
    // Regex para WebM
    const webmRegex = /https?:\/\/[^\s"'<>]+\.webm[^\s"'<>]*/gi;
    const webmMatches = html.match(webmRegex) || [];
    
    // Regex para MKV
    const mkvRegex = /https?:\/\/[^\s"'<>]+\.mkv[^\s"'<>]*/gi;
    const mkvMatches = html.match(mkvRegex) || [];
    
    // Combinar e remover duplicatas
    const allMatches = [...m3u8Matches, ...mp4Matches, ...tsMatches, ...webmMatches, ...mkvMatches];
    
    allMatches.forEach(url => {
      // Filtrar URLs muito curtas ou inválidas
      if (url.length > 20 && !this.capturedUrls.has(url)) {
        this.capturedUrls.add(url);
        urls.push(url);
      }
    });
    
    return urls;
  }

  /**
   * Intercepta requisições de rede (usando Fetch API e XMLHttpRequest)
   */
  interceptNetworkRequests(): void {
    console.log('\n🔍 Iniciando interceptação de requisições de rede...\n');

    // Interceptar Fetch API
    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      const response = await originalFetch(...args);
      const url = typeof args[0] === 'string' ? args[0] : args[0].url;
      
      // Filtrar URLs de vídeo
      if (this.isVideoUrl(url)) {
        console.log(`📡 Fetch capturado: ${url}`);
        this.capturedUrls.add(url);
      }
      
      return response;
    };

    // Interceptar XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    const self = this;
    
    XMLHttpRequest.prototype.open = function(...args: any[]) {
      const url = args[1];
      
      if (typeof url === 'string' && self.isVideoUrl(url)) {
        console.log(`📡 XHR capturado: ${url}`);
        self.capturedUrls.add(url);
      }
      
      return originalOpen.apply(this, args as any);
    };

    console.log('✅ Interceptação ativada (Fetch + XHR). Aguardando requisições...\n');
  }

  /**
   * Verifica se uma URL é de vídeo
   */
  private isVideoUrl(url: string): boolean {
    const videoExtensions = ['.m3u8', '.mp4', '.ts', '.webm', '.mkv', '.avi', '.flv'];
    return videoExtensions.some(ext => url.includes(ext));
  }

  /**
   * Imprime resultados finais
   */
  private printResults(): void {
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

  /**
   * Copia URLs para área de transferência
   */
  copyToClipboard(): void {
    const urls = Array.from(this.capturedUrls).join('\n');
    
    navigator.clipboard.writeText(urls).then(() => {
      console.log('✅ URLs copiadas para área de transferência!');
    }).catch(err => {
      console.error('❌ Erro ao copiar:', err);
    });
  }

  /**
   * Exporta resultados em formato JSON
   */
  exportJSON(): string {
    const data = {
      timestamp: new Date().toISOString(),
      totalUrls: this.capturedUrls.size,
      players: this.results.map(r => ({
        index: r.index,
        type: r.playerType,
        iframeUrl: r.iframeUrl,
        videoUrls: r.videoUrls
      })),
      allUrls: Array.from(this.capturedUrls)
    };
    
    const json = JSON.stringify(data, null, 2);
    console.log('\n📄 JSON exportado:');
    console.log(json);
    
    return json;
  }

  /**
   * Baixa resultados como arquivo JSON
   */
  downloadJSON(): void {
    const json = this.exportJSON();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `maxseries-extract-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    console.log('✅ Arquivo JSON baixado!');
  }
}

// ============================================
// EXECUÇÃO AUTOMÁTICA
// ============================================

(async () => {
  const extractor = new MaxSeriesExtractor();
  
  // 1. Interceptar requisições de rede
  extractor.interceptNetworkRequests();
  
  // 2. Aguardar 2 segundos para capturar requisições iniciais
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // 3. Analisar iframes
  await extractor.analyzeIframes();
  
  // 4. Disponibilizar globalmente para uso manual
  (window as any).extractor = extractor;
  
  console.log('\n💡 Dicas:');
  console.log('   - Para copiar URLs: extractor.copyToClipboard()');
  console.log('   - Para exportar JSON: extractor.exportJSON()');
  console.log('   - Para baixar JSON: extractor.downloadJSON()');
  console.log('   - Para reanalizar: extractor.analyzeIframes()');
  console.log('   - Aguarde o vídeo carregar e verifique o console para novas requisições');
})();
