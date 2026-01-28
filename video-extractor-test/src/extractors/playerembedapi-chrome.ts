import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { chromium } from 'playwright';

/**
 * PlayerEmbedAPI Chrome Extractor
 * Use real Chrome with persistent context
 */
export class PlayerEmbedAPIChromeExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Chrome';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🌐 Using real Chrome with persistent context');

    let browser: any = null;

    try {
      // Use Chrome executable (not Chromium)
      const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
      
      this.logger.debug('Launching Chrome...');
      browser = await chromium.launch({
        headless: false,
        executablePath: chromePath,
        args: [
          '--disable-blink-features=AutomationControlled',
          '--no-sandbox',
          '--disable-web-security',
          '--disable-features=IsolateOrigins,site-per-process'
        ]
      });

      const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        locale: 'pt-BR',
        permissions: ['geolocation'],
        geolocation: { latitude: -23.5505, longitude: -46.6333 }
      });

      const page = await context.newPage();

      // Inject anti-detection
      await page.addInitScript(() => {
        // Remove webdriver
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        
        // Fake iframe
        Object.defineProperty(window, 'top', {
          get: () => ({ location: { hostname: 'viewplayer.online' } })
        });

        // Block alert iframe
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node: any) => {
              if (node.tagName === 'IFRAME' && node.className === 'notify') {
                node.remove();
              }
            });
          });
        });
        observer.observe(document.documentElement, { childList: true, subtree: true });
      });

      // Capture URLs
      const videoUrls: string[] = [];
      
      page.on('request', (request) => {
        const reqUrl = request.url();
        if ((reqUrl.includes('sssrr.org') || reqUrl.includes('trycloudflare.com')) && 
            reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
      });

      // Navigate
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      this.logger.success('✅ Loaded');

      // Wait and click
      await page.waitForTimeout(5000);
      
      try {
        await page.click('#overlay, #playback');
        this.logger.debug('Clicked overlay');
      } catch (e) {}

      await page.waitForTimeout(15000);

      // Extract from DOM
      const videoSrc = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        return video?.src || null;
      });

      if (videoSrc) {
        this.logger.success(`📹 ${videoSrc}`);
        videoUrls.push(videoSrc);
      }

      await page.screenshot({ path: 'playerembedapi-chrome.png' });

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'PlayerEmbedAPI',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      this.logger.success(`✅ ${unique.length} link(s)`);
      return this.createResult(url, unique, [], startTime);

    } catch (error: any) {
      this.logger.error(`Failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      if (browser) await browser.close();
    }
  }

  private detectQuality(url: string): VideoQuality {
    if (url.includes('1080')) return VideoQuality.Q1080;
    if (url.includes('720')) return VideoQuality.Q720;
    if (url.includes('480')) return VideoQuality.Q480;
    return VideoQuality.UNKNOWN;
  }
}
