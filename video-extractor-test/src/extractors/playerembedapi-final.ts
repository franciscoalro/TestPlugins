import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

/**
 * PlayerEmbedAPI Final Extractor
 * Bypass DevTools detection and security alerts
 */
export class PlayerEmbedAPIFinalExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Final';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🔥 Final technique: Block DevTools detection');

    let browser: any = null;

    try {
      browser = await puppeteer.launch({
        headless: false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-blink-features=AutomationControlled',
          '--disable-dev-shm-usage'
        ]
      });

      const page = await browser.newPage();

      // Block the security alert iframe
      await page.setRequestInterception(true);
      page.on('request', (request: any) => {
        const url = request.url();
        
        // Block ads and tracking
        if (url.includes('usheebainaut.com') ||
            url.includes('attirecideryeah.com') ||
            url.includes('fuckadblock') ||
            url.includes('googletagmanager') ||
            url.includes('cloudflareinsights')) {
          request.abort();
          return;
        }
        
        request.continue();
      });

      // Capture video URLs
      const videoUrls: string[] = [];
      
      page.on('response', async (response: any) => {
        const resUrl = response.url();
        
        if (resUrl.includes('sssrr.org') && resUrl.includes('/sora/')) {
          this.logger.success(`🎯 Found sssrr.org: ${resUrl}`);
          videoUrls.push(resUrl);
        }
        
        if (resUrl.includes('trycloudflare.com') && resUrl.includes('/sora/')) {
          this.logger.success(`🎯 Found CloudFlare: ${resUrl}`);
          videoUrls.push(resUrl);
        }
      });

      // Inject anti-detection scripts BEFORE page loads
      await page.evaluateOnNewDocument(() => {
        // 1. Fake iframe context
        Object.defineProperty(window, 'top', {
          get: () => ({
            location: {
              hostname: 'viewplayer.online',
              href: 'https://viewplayer.online/'
            }
          })
        });

        // 2. Block DevTools detection
        const devtools = /./;
        devtools.toString = function() {
          return 'function toString() { [native code] }';
        };

        // 3. Override console to prevent detection
        const noop = () => {};
        Object.keys(console).forEach(key => {
          if (typeof (console as any)[key] === 'function') {
            const original = (console as any)[key];
            (console as any)[key] = function(...args: any[]) {
              // Call original but don't trigger detection
              return original.apply(console, args);
            };
          }
        });

        // 4. Block security alert iframe
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node: any) => {
              if (node.tagName === 'IFRAME' && 
                  (node.className === 'notify' || 
                   node.srcdoc?.includes('Security alert'))) {
                node.remove();
                console.log('Blocked security alert iframe');
              }
            });
          });
        });

        observer.observe(document.documentElement, {
          childList: true,
          subtree: true
        });

        // 5. Auto-click to start player
        setTimeout(() => {
          const overlay = document.getElementById('overlay') || 
                         document.getElementById('playback');
          if (overlay) {
            overlay.click();
            console.log('Clicked play overlay');
          }
        }, 2000);
      });

      // Set headers
      await page.setExtraHTTPHeaders({
        'Referer': referer || 'https://viewplayer.online/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site'
      });

      // Navigate
      this.logger.debug('Loading PlayerEmbedAPI...');
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      this.logger.success('✅ Page loaded');

      // Wait for player
      this.logger.debug('Waiting for player to initialize (20s)...');
      await new Promise(resolve => setTimeout(resolve, 20000));

      // Try to extract from DOM
      this.logger.debug('Extracting from DOM...');
      const videoSrc = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        if (video && video.src) {
          return video.src;
        }
        return null;
      });

      if (videoSrc) {
        this.logger.success(`📹 Found video src: ${videoSrc}`);
        videoUrls.push(videoSrc);
      }

      // Screenshot
      await page.screenshot({ path: 'playerembedapi-final-debug.png', fullPage: true });
      this.logger.debug('Screenshot saved');

      if (videoUrls.length === 0) {
        this.logger.error('❌ No video URLs found');
        this.logger.info('💡 Check playerembedapi-final-debug.png');
        return this.createErrorResult(url, 'No video URLs found', startTime);
      }

      // Create links
      const links: ExtractorLink[] = videoUrls.map(videoUrl => {
        let normalizedUrl = videoUrl;
        if (videoUrl.startsWith('//')) {
          normalizedUrl = `https:${videoUrl}`;
        }

        return {
          url: normalizedUrl,
          name: 'PlayerEmbedAPI',
          quality: this.detectQuality(normalizedUrl),
          isM3U8: normalizedUrl.includes('.m3u8'),
          referer: url
        };
      });

      const uniqueLinks = links.filter((link, index, self) =>
        index === self.findIndex(l => l.url === link.url)
      );

      this.logger.success(`✅ Extracted ${uniqueLinks.length} unique link(s)`);
      return this.createResult(url, uniqueLinks, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      if (browser) {
        await browser.close();
      }
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
