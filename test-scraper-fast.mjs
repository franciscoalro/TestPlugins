/**
 * Teste PlayerEmbedAPI - Versão Rápida
 * Captura URL imediatamente ao encontrar
 */

import puppeteer from 'puppeteer';

const testUrl = process.argv[2] || 'https://playerembedapi.link/?v=rTxfmoIhd';

console.log('========================================');
console.log('  TESTE PLAYEREMBEDAPI - FAST CAPTURE ');
console.log('========================================\n');

let videoUrl = null;
let browser = null;

async function captureVideo() {
  browser = await puppeteer.launch({
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
      '--no-sandbox'
    ]
  });

  const page = await browser.newPage();
  
  // User-Agent realista
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  
  // COOKIE ANTI-DETECÇÃO
  await page.setCookie(
    { name: 'visited', value: 'true', domain: '.playerembedapi.link' },
    { name: 'session', value: Date.now().toString(), domain: '.playerembedapi.link' }
  );

  // Capturar IMEDIATAMENTE
  page.on('request', async request => {
    const url = request.url();
    
    // Se encontrar URL do Google Storage, salvar e fechar
    if (url.includes('googleapis.com') && url.includes('.mp4')) {
      if (!videoUrl) {
        videoUrl = url;
        console.log(`🎬 VÍDEO CAPTURADO!`);
        console.log(`URL: ${url}`);
        
        // Fechar browser imediatamente
        await browser.close();
      }
    }
  });

  console.log('⏳ Carregando...');
  
  try {
    await page.goto(testUrl, { 
      waitUntil: 'domcontentloaded',
      timeout: 10000 
    });
    
    const finalUrl = page.url();
    console.log(`📄 URL final: ${finalUrl}`);
    
    if (finalUrl.includes('abyss.to')) {
      console.log('⚠️ ABYSS.TO detectado');
    }
    
    // Aguardar um pouco para capturar requests
    await new Promise(r => setTimeout(r, 3000));
    
  } catch (e) {
    // Ignorar erros de navegação
  }
  
  if (!videoUrl && browser) {
    await browser.close();
  }
  
  return videoUrl;
}

const result = await captureVideo();

console.log('\n========================================');
console.log('  RESULTADO                           ');
console.log('========================================');

if (result) {
  console.log(`✅ SUCESSO!`);
  console.log(`\n📹 URL do vídeo:`);
  console.log(result);
} else {
  console.log('❌ Não conseguiu capturar URL');
}
