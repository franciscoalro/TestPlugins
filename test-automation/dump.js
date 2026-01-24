const puppeteer = require('puppeteer');
const TARGET_URL = 'https://playerthree.online/embed/sandokan/'; // URL da Lista

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    console.log('Navegando...');
    await page.goto(TARGET_URL, { waitUntil: 'networkidle2' });

    // Dump HTML
    const html = await page.content();
    console.log('HTML CAPTURADO:');
    console.log(html.substring(0, 5000)); // Primeiros 5000 chars

    await browser.close();
})();
