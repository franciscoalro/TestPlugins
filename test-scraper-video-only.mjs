/**
 * Teste PlayerEmbedAPI - Captura APENAS URLs de vídeo
 * Ignora arquivos JS/CSS do player
 */

import puppeteer from 'puppeteer';

const testUrl = process.argv[2] || 'https://playerembedapi.link/?v=rTxfmoIhd';

console.log('========================================');
console.log('  TESTE - CAPTURA URL VIDEO ONLY      ');
console.log('========================================\n');
console.log(`🌐 URL: ${testUrl}\n`);

const browser = await puppeteer.launch({
  headless: false,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security'
  ]
});

const page = await browser.newPage();

await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

const videoUrls = {
  intermediaria: null,  // sssrr.org/?timestamp=...
  final: null,          // googleapis.com/...mp4
  m3u8: null            // playlist m3u8
};

page.on('request', request => {
  const url = request.url();
  
  // APENAS capturar URLs de vídeo, NÃO arquivos JS/CSS
  // URL intermediária: sssrr.org/?timestamp=...
  if (url.includes('sssrr.org') && url.includes('timestamp=') && url.includes('id=')) {
    if (!videoUrls.intermediaria) {
      videoUrls.intermediaria = url;
      console.log(`🎯 URL INTERMEDIÁRIA CAPTURADA:`);
      console.log(`   ${url}\n`);
    }
  }
  
  // URL final: googleapis.com com .mp4 ou .m3u8
  if (url.includes('googleapis.com') && (url.includes('.mp4') || url.includes('.m3u8'))) {
    if (!videoUrls.final) {
      videoUrls.final = url;
      console.log(`📹 URL FINAL CAPTURADA:`);
      console.log(`   ${url}\n`);
    }
  }
  
  // Também capturar .m3u8 ou .mp4 de outras fontes
  if ((url.includes('.m3u8') || url.includes('.mp4')) && 
      !url.includes('.js') && !url.includes('.css')) {
    console.log(`🎬 Possível vídeo: ${url.substring(0, 80)}`);
  }
});

console.log('⏳ Navegando...\n');

await page.goto(testUrl, { 
  waitUntil: 'networkidle2',
  timeout: 30000 
});

const finalUrl = page.url();
console.log(`\n📄 URL final da página: ${finalUrl}`);

// Injetar clicks no player
console.log('\n💉 Clicando no player...');
await page.evaluate(() => {
  const clickSelectors = ['#overlay', '.overlay', '.jwplayer', '.play-button', 'video'];
  clickSelectors.forEach(sel => {
    const el = document.querySelector(sel);
    if (el) {
      console.log(`Click: ${sel}`);
      el.click();
      el.click();
      el.click();
    }
  });
});

// Aguardar mais requests
console.log('⏳ Aguardando 8 segundos por requests de vídeo...');
await new Promise(r => setTimeout(r, 8000));

console.log('\n========================================');
console.log('  RESULTADO                           ');
console.log('========================================');

if (videoUrls.intermediaria) {
  console.log(`\n✅ URL INTERMEDIÁRIA:`);
  console.log(`   ${videoUrls.intermediaria}`);
  
  // Tentar seguir redirect
  console.log(`\n🔄 Seguindo redirect...`);
  try {
    const redirectPage = await browser.newPage();
    await redirectPage.setExtraHTTPHeaders({
      'Referer': 'https://playerembedapi.link/',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
    
    const response = await redirectPage.goto(videoUrls.intermediaria, {
      waitUntil: 'networkidle0',
      timeout: 15000
    });
    
    const urlFinal = redirectPage.url();
    console.log(`\n✅ URL FINAL DO VÍDEO:`);
    console.log(`   ${urlFinal}`);
    
    await redirectPage.close();
  } catch (e) {
    console.log(`❌ Erro: ${e.message}`);
  }
} else {
  console.log('\n❌ Nenhuma URL intermediária capturada');
}

if (videoUrls.final) {
  console.log(`\n📹 URL GOOGLEAPIS DIRETA:`);
  console.log(`   ${videoUrls.final}`);
}

await browser.close();

console.log('\n========================================');
console.log('✅ Teste concluído');
