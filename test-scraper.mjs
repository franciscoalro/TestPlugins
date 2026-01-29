/**
 * Teste PlayerEmbedAPI - Node.js (ES Modules)
 * Usa Puppeteer para testar a raspagem
 */

import puppeteer from 'puppeteer';

const testUrl = process.argv[2] || 'https://playerembedapi.link/?v=rTxfmoIhd';
const referer = 'https://playerthree.online/';

console.log('========================================');
console.log('  TESTE PLAYEREMBEDAPI - SCRAPER      ');
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

const capturedUrls = {
  sssrr: [],
  googleapis: [],
  all: []
};

page.on('request', request => {
  const url = request.url();
  capturedUrls.all.push(url);
  
  if (url.includes('sssrr.org')) {
    console.log(`🎯 SSSRR: ${url.substring(0, 80)}...`);
    capturedUrls.sssrr.push(url);
  }
  if (url.includes('googleapis.com') && url.includes('.mp4')) {
    console.log(`📹 GOOGLEAPIS: ${url.substring(0, 80)}...`);
    capturedUrls.googleapis.push(url);
  }
});

// Interceptar responses para capturar redirects
page.on('response', response => {
  const url = response.url();
  const status = response.status();
  
  if (url.includes('sssrr.org') || url.includes('googleapis.com')) {
    console.log(`📡 [${status}] ${url.substring(0, 60)}...`);
  }
});

console.log('⏳ Navegando...');

await page.goto(testUrl, { 
  waitUntil: 'networkidle2',
  timeout: 30000 
});

const finalUrl = page.url();
console.log(`\n📄 Página final: ${finalUrl}`);

if (finalUrl.includes('abyss.to')) {
  console.log('❌ ABYSS.TO - Site bloqueou automação');
  await browser.close();
  process.exit(1);
}

// Injetar clicks
console.log('💉 Clicando no player...');

await page.evaluate(() => {
  const selectors = ['#overlay', '.overlay', '.play-button', 'video'];
  selectors.forEach(sel => {
    const el = document.querySelector(sel);
    if (el) {
      console.log(`✅ Click: ${sel}`);
      el.click();
    }
  });
});

// Aguardar
console.log('⏳ Aguardando 10 segundos...');
await new Promise(r => setTimeout(r, 10000));

console.log('\n========================================');
console.log('  RESULTADO                           ');
console.log('========================================');

if (capturedUrls.sssrr.length > 0) {
  console.log(`\n✅ ${capturedUrls.sssrr.length} URL(s) SSSRR capturada(s):`);
  capturedUrls.sssrr.forEach((url, i) => {
    console.log(`  ${i + 1}. ${url}`);
  });
  
  // Tentar seguir redirect da primeira URL
  const urlIntermediaria = capturedUrls.sssrr[0];
  console.log(`\n🔄 Testando redirect...`);
  
  try {
    const redirectPage = await browser.newPage();
    await redirectPage.setExtraHTTPHeaders({
      'Referer': referer,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });
    
    const redirectResponse = await redirectPage.goto(urlIntermediaria, {
      waitUntil: 'networkidle0',
      timeout: 15000
    });
    
    const finalVideoUrl = redirectPage.url();
    console.log(`✅ URL FINAL: ${finalVideoUrl}`);
    
    await redirectPage.close();
  } catch (e) {
    console.log(`❌ Erro no redirect: ${e.message}`);
  }
} else {
  console.log('❌ Nenhuma URL SSSRR capturada');
}

if (capturedUrls.googleapis.length > 0) {
  console.log(`\n📹 ${capturedUrls.googleapis.length} URL(s) Googleapis direta(s):`);
  capturedUrl.googleapis.forEach((url, i) => {
    console.log(`  ${i + 1}. ${url}`);
  });
}

console.log(`\n📊 Total de requisições: ${capturedUrls.all.length}`);

await browser.close();
console.log('\n✅ Teste concluído');
