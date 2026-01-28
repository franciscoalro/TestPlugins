import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { chromium } from 'playwright';

/**
 * PlayerEmbedAPI Extractor with Stealth Mode
 * Advanced anti-detection techniques to bypass abyss.to redirect
 */
export class PlayerEmbedAPIStealthExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Stealth';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.warn('🥷 Using STEALTH mode to bypass detection');

    let browser;
    try {
      // Launch with stealth args
      this.logger.debug('Launching browser with stealth configuration...');
      browser = await chromium.launch({ 
        headless: false, // Keep visible for now
        args: [
          // Anti-detection
          '--disable-blink-features=AutomationControlled',
          '--disable-features=IsolateOrigins,site-per-process',
          '--disable-site-isolation-trials',
          '--disable-web-security',
          '--disable-features=BlockInsecurePrivateNetworkRequests',
          
          // Performance
          '--disable-dev-shm-usage',
          '--no-sandbox',
          '--disable-setuid-sandbox',
          
          // Avoid detection
          '--disable-infobars',
          '--window-size=1920,1080',
          '--start-maximized',
          
          // User agent
          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
      });
      
      const context = await browser.newContext({
        // Real Chrome user agent
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        viewport: { width: 1920, height: 1080 },
        
        // Accept language
        locale: 'pt-BR',
        
        // Timezone
        timezoneId: 'America/Sao_Paulo',
        
        // Geolocation (Brazil)
        geolocation: { latitude: -23.5505, longitude: -46.6333 },
        permissions: ['geolocation'],
        
        // Extra headers
        extraHTTPHeaders: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
          'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
          'Accept-Encoding': 'gzip, deflate, br',
          'DNT': '1',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Sec-Fetch-Dest': 'document',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'none',
          'Sec-Fetch-User': '?1',
          'Cache-Control': 'max-age=0',
          ...(referer && { 'Referer': referer })
        }
      });
      
      const page = await context.newPage();

      // Inject anti-detection scripts BEFORE navigation
      await page.addInitScript(() => {
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        });

        // Override chrome property
        (window as any).chrome = {
          runtime: {}
        };

        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters: any) => (
          parameters.name === 'notifications' ?
            Promise.resolve({ state: 'denied' } as PermissionStatus) :
            originalQuery(parameters)
        );

        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
          get: () => [1, 2, 3, 4, 5]
        });

        // Override languages
        Object.defineProperty(navigator, 'languages', {
          get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });

        // Add realistic properties
        Object.defineProperty(navigator, 'hardwareConcurrency', {
          get: () => 8
        });

        Object.defineProperty(navigator, 'deviceMemory', {
          get: () => 8
        });

        // Override toString
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
          if (this === window.navigator.permissions.query) {
            return 'function query() { [native code] }';
          }
          return originalToString.call(this);
        };
      });

      // Track captured URLs
      const capturedUrls = new Set<string>();
      const links: ExtractorLink[] = [];

      // Intercept network requests
      page.on('response', async (response) => {
        const responseUrl = response.url();
        
        // Log all responses for debugging
        this.logger.debug(`Response: ${response.status()} ${responseUrl}`);
        
        // Check for abyss.to redirect
        if (responseUrl.includes('abyss.to')) {
          this.logger.error('❌ Detected redirect to abyss.to - Anti-bot triggered!');
        }
        
        // Capture M3U8 URLs
        if (responseUrl.includes('.m3u8')) {
          if (!capturedUrls.has(responseUrl)) {
            capturedUrls.add(responseUrl);
            this.logger.success(`📹 Captured M3U8: ${responseUrl}`);
            links.push({
              url: responseUrl,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(responseUrl),
              isM3U8: true,
              referer: page.url()
            });
          }
        }
        
        // Capture MP4 URLs
        if (responseUrl.includes('.mp4') && !responseUrl.includes('favicon')) {
          if (!capturedUrls.has(responseUrl)) {
            capturedUrls.add(responseUrl);
            this.logger.success(`📹 Captured MP4: ${responseUrl}`);
            links.push({
              url: responseUrl,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(responseUrl),
              isM3U8: false,
              referer: page.url()
            });
          }
        }

        // Log sssrr.org and CloudFlare URLs
        if (responseUrl.includes('sssrr.org')) {
          this.logger.debug(`🔗 sssrr.org: ${responseUrl}`);
        }
        if (responseUrl.includes('trycloudflare.com')) {
          this.logger.debug(`☁️  CloudFlare: ${responseUrl}`);
        }
      });

      // Navigate with realistic behavior
      this.logger.info(`🌐 Navigating to: ${url}`);
      
      // Add random delay before navigation (simulate human)
      await page.waitForTimeout(Math.random() * 1000 + 500);
      
      const response = await page.goto(url, { 
        waitUntil: 'domcontentloaded',
        timeout: 30000 
      });

      // Check if redirected to abyss.to
      const currentUrl = page.url();
      if (currentUrl.includes('abyss.to')) {
        this.logger.error('❌ Redirected to abyss.to immediately!');
        await page.screenshot({ path: 'playerembedapi-abyss-redirect.png' });
        await browser.close();
        return this.createErrorResult(url, 'Redirected to abyss.to - Anti-bot detection', startTime);
      }

      this.logger.success('✅ Page loaded without redirect!');
      this.logger.info('⏳ Waiting for video sources...');

      // Wait for page to fully load
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
        this.logger.warn('Network not idle after 10s, continuing...');
      });

      // Simulate human behavior - move mouse
      await page.mouse.move(100, 100);
      await page.waitForTimeout(500);
      await page.mouse.move(500, 500);

      // Wait for video sources (max 60 seconds)
      const timeout = 60000;
      const startWait = Date.now();
      
      while (links.length === 0 && (Date.now() - startWait) < timeout) {
        await page.waitForTimeout(1000);
        
        // Check for redirect during wait
        if (page.url().includes('abyss.to')) {
          this.logger.error('❌ Redirected to abyss.to during wait!');
          break;
        }
        
        // Log progress
        const elapsed = Math.floor((Date.now() - startWait) / 1000);
        if (elapsed % 10 === 0 && elapsed > 0) {
          this.logger.debug(`⏱️  Waiting... ${elapsed}s elapsed`);
        }
      }

      // Try to find video element
      const videoElement = await page.$('video');
      if (videoElement) {
        this.logger.success('✅ Video element found');
        const videoSrc = await videoElement.getAttribute('src');
        if (videoSrc && !capturedUrls.has(videoSrc)) {
          this.logger.success(`📹 Video src: ${videoSrc}`);
          links.push({
            url: videoSrc,
            name: 'PlayerEmbedAPI',
            quality: VideoQuality.UNKNOWN,
            isM3U8: videoSrc.includes('.m3u8'),
            referer: page.url()
          });
        }
      }

      // Take screenshot
      await page.screenshot({ path: 'playerembedapi-final.png' });
      this.logger.debug('📸 Screenshot saved: playerembedapi-final.png');

      // Save page HTML for analysis
      const html = await page.content();
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-page.html', html);
      this.logger.debug('💾 HTML saved: playerembedapi-page.html');

      await browser.close();

      if (links.length === 0) {
        this.logger.error('No video sources captured');
        return this.createErrorResult(url, 'No video sources found', startTime);
      }

      this.logger.success(`Extracted ${links.length} link(s)`);
      return this.createResult(url, links, [], startTime);

    } catch (error: any) {
      if (browser) await browser.close();
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    }
  }

  private detectQuality(url: string): VideoQuality {
    if (url.includes('1080') || url.includes('1920')) return VideoQuality.Q1080;
    if (url.includes('720') || url.includes('1280')) return VideoQuality.Q720;
    if (url.includes('480')) return VideoQuality.Q480;
    if (url.includes('360')) return VideoQuality.Q360;
    return VideoQuality.UNKNOWN;
  }
}
