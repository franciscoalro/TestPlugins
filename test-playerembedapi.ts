/**
 * Teste PlayerEmbedAPI - TypeScript
 * Simula o fluxo do WebView para capturar URL do vídeo
 */

import { chromium, Browser, Page } from 'playwright';

interface VideoResult {
  success: boolean;
  urlIntermediaria?: string;
  urlFinal?: string;
  error?: string;
  logs: string[];
}

async function testPlayerEmbedAPI(sourceUrl: string, referer: string): Promise<VideoResult> {
  const logs: string[] = [];
  
  function log(msg: string) {
    const timestamp = new Date().toLocaleTimeString();
    const fullMsg = `[${timestamp}] ${msg}`;
    logs.push(fullMsg);
    console.log(fullMsg);
  }

  log('🚀 Iniciando teste PlayerEmbedAPI');
  log(`🌐 URL: ${sourceUrl}`);
  log(`📄 Referer: ${referer}`);

  let browser: Browser | null = null;
  
  try {
    // Launch browser com headers anti-detecção
    browser = await chromium.launch({
      headless: false, // true para headless
      args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
      ]
    });

    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 720 },
      extraHTTPHeaders: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      }
    });

    const page = await context.newPage();
    
    // Capturar todas as requisições
    const capturedUrls = {
      sssrr: [] as string[],
      googleapis: [] as string[],
      mp4: [] as string[],
      all: [] as string[]
    };

    page.on('request', request => {
      const url = request.url();
      capturedUrls.all.push(url);
      
      if (url.includes('sssrr.org')) {
        log(`🎯 SSSRR CAPTURADO: ${url.substring(0, 80)}...`);
        capturedUrls.sssrr.push(url);
      }
      if (url.includes('googleapis.com')) {
        log(`📹 GOOGLEAPIS CAPTURADO: ${url.substring(0, 80)}...`);
        capturedUrls.googleapis.push(url);
      }
      if (url.includes('.mp4') || url.includes('.m3u8')) {
        log(`🎬 VIDEO CAPTURADO: ${url.substring(0, 80)}...`);
        capturedUrls.mp4.push(url);
      }
    });

    // Navegar para a URL
    log('⏳ Navegando...');
    
    const response = await page.goto(sourceUrl, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    const finalUrl = page.url();
    log(`📄 Página carregada: ${finalUrl}`);

    // Verificar se redirecionou para abyss.to
    if (finalUrl.includes('abyss.to')) {
      log('❌ ABYSS.TO DETECTADO - Site bloqueou automação');
      return {
        success: false,
        error: 'Redirecionado para abyss.to',
        logs
      };
    }

    // Injetar script de automação
    log('💉 Injetando script de automação...');
    
    await page.evaluate(() => {
      console.log('🚀 Script injetado');
      
      // Clicks automáticos
      const selectors = ['#overlay', '.overlay', '.play-button', 'video', '[class*="play"]'];
      
      let clicks = 0;
      const interval = setInterval(() => {
        clicks++;
        selectors.forEach(sel => {
          const el = document.querySelector(sel) as HTMLElement;
          if (el && el.offsetParent !== null) {
            console.log(`✅ Click em: ${sel}`);
            el.click();
          }
        });
        
        if (clicks >= 10) clearInterval(interval);
      }, 500);
      
      // Monitorar vídeo
      const videoCheck = setInterval(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        if (video && video.src) {
          console.log(`📹 VÍDEO ENCONTRADO: ${video.src}`);
          clearInterval(videoCheck);
        }
      }, 500);
      
      setTimeout(() => clearInterval(videoCheck), 15000);
    });

    // Aguardar captura de URL
    log('⏳ Aguardando URLs de vídeo (15s)...');
    await page.waitForTimeout(15000);

    // Verificar resultados
    log('📊 Verificando resultados...');
    
    if (capturedUrls.sssrr.length > 0) {
      log(`✅ ${capturedUrls.sssrr.length} URL(s) SSSRR capturada(s)`);
    }
    if (capturedUrls.googleapis.length > 0) {
      log(`✅ ${capturedUrls.googleapis.length} URL(s) Googleapis capturada(s)`);
    }
    if (capturedUrls.mp4.length > 0) {
      log(`✅ ${capturedUrls.mp4.length} URL(s) de vídeo capturada(s)`);
    }

    // Tentar seguir redirect da URL intermediária
    let urlFinal: string | undefined;
    
    if (capturedUrls.sssrr.length > 0) {
      const urlIntermediaria = capturedUrls.sssrr[0];
      log(`🔄 Seguindo redirect: ${urlIntermediaria.substring(0, 60)}...`);
      
      try {
        const redirectResponse = await page.evaluate(async (url) => {
          const resp = await fetch(url, {
            method: 'GET',
            redirect: 'follow',
            headers: {
              'Accept': '*/*',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
          });
          return resp.url;
        }, urlIntermediaria);
        
        urlFinal = redirectResponse;
        log(`✅ URL FINAL: ${urlFinal?.substring(0, 80)}...`);
      } catch (e) {
        log(`❌ Erro ao seguir redirect: ${e}`);
      }
    }

    await browser.close();

    // Retornar resultado
    if (urlFinal || capturedUrls.googleapis.length > 0) {
      const finalVideoUrl = urlFinal || capturedUrls.googleapis[0];
      log('✅ SUCESSO - URL do vídeo obtida!');
      
      return {
        success: true,
        urlIntermediaria: capturedUrls.sssrr[0],
        urlFinal: finalVideoUrl,
        logs
      };
    } else if (capturedUrls.sssrr.length > 0) {
      log('⚠️ URL intermediária capturada, mas não conseguiu seguir redirect');
      return {
        success: false,
        urlIntermediaria: capturedUrls.sssrr[0],
        error: 'Não conseguiu seguir redirect',
        logs
      };
    } else {
      log('❌ Nenhuma URL de vídeo capturada');
      return {
        success: false,
        error: 'Timeout - nenhuma URL capturada',
        logs
      };
    }

  } catch (error) {
    log(`❌ ERRO: ${error}`);
    await browser?.close();
    
    return {
      success: false,
      error: String(error),
      logs
    };
  }
}

// Testar com URL de exemplo
async function main() {
  // URL de exemplo - substitua por uma real
  const testUrl = 'https://playerembedapi.link/?v=rTxfmoIhd';
  const referer = 'https://playerthree.online/';
  
  console.log('========================================');
  console.log('  TESTE PLAYEREMBEDAPI - TYPESCRIPT    ');
  console.log('========================================\n');
  
  const result = await testPlayerEmbedAPI(testUrl, referer);
  
  console.log('\n========================================');
  console.log('  RESULTADO FINAL                      ');
  console.log('========================================');
  console.log(`Sucesso: ${result.success}`);
  console.log(`URL Intermediária: ${result.urlIntermediaria || 'N/A'}`);
  console.log(`URL Final: ${result.urlFinal || 'N/A'}`);
  console.log(`Erro: ${result.error || 'Nenhum'}`);
  console.log('\n📋 Logs completos:');
  result.logs.forEach(log => console.log(log));
}

// Executar
main().catch(console.error);
