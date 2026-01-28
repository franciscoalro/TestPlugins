import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

/**
 * PlayerEmbedAPI Ultimate Extractor
 * Trick the page into thinking it's in an iframe
 */
export class PlayerEmbedAPIUltimateExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Ultimate';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🎯 Ultimate technique: Inject iframe context');

    let browser: any = null;

    try {
      browser = await puppeteer.launch({
        headless: false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-blink-features=AutomationControlled',
          '--window-size=1920,1080'
        ]
      });

      const page = await browser.newPage();

      // Set headers to simulate iframe
      await page.setExtraHTTPHeaders({
        'Referer': referer || 'https://viewplayer.online/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site'
      });

      // Capture all network requests
      const videoUrls: string[] = [];
      const allRequests: Map<string, any> = new Map();

      page.on('request', (request: any) => {
        const reqUrl = request.url();
        allRequests.set(reqUrl, {
          url: reqUrl,
          method: request.method(),
          headers: request.headers()
        });
      });

      page.on('response', async (response: any) => {
        const resUrl = response.url();
        
        // Capture sssrr.org URLs
        if (resUrl.includes('sssrr.org') && resUrl.includes('/sora/')) {
          this.logger.success(`🎯 Found sssrr.org: ${resUrl}`);
          videoUrls.push(resUrl);
          
          // Check for redirect
          if (response.status() === 302) {
            const location = response.headers()['location'];
            if (location) {
              this.logger.success(`  → Redirects to: ${location}`);
              videoUrls.push(location);
            }
          }
        }
        
        // Capture CloudFlare tunnels
        if (resUrl.includes('trycloudflare.com')) {
          this.logger.success(`🎯 Found CloudFlare: ${resUrl}`);
          videoUrls.push(resUrl);
        }
        
        // Capture M3U8/MP4
        if (resUrl.includes('.m3u8') || (resUrl.includes('.mp4') && !resUrl.includes('favicon'))) {
          this.logger.success(`🎯 Found video: ${resUrl}`);
          videoUrls.push(resUrl);
        }
      });

      // Navigate to page
      this.logger.debug('Navigating to PlayerEmbedAPI...');
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

      // CRITICAL: Inject script to fake iframe context BEFORE page loads
      await page.evaluateOnNewDocument(() => {
        // Override window properties to fake iframe
        Object.defineProperty(window, 'top', {
          get: function() {
            return {
              location: {
                hostname: 'viewplayer.online',
                href: 'https://viewplayer.online/'
              }
            };
          }
        });

        Object.defineProperty(window, 'self', {
          get: function() {
            return window;
          }
        });

        // Make it look like we're in iframe
        Object.defineProperty(window, 'frameElement', {
          get: function() {
            return document.createElement('iframe');
          }
        });
      });

      this.logger.success('✅ Page loaded');

      // Wait for player to initialize
      this.logger.debug('Waiting for player (15 seconds)...');
      await new Promise(resolve => setTimeout(resolve, 15000));

      // Try to click play
      try {
        this.logger.debug('Looking for play overlay...');
        const overlay = await page.$('#overlay, #playback');
        if (overlay) {
          this.logger.debug('Clicking play overlay...');
          await overlay.click();
          await new Promise(resolve => setTimeout(resolve, 5000));
        }
      } catch (e) {
        this.logger.debug('No overlay found');
      }

      // Extract video src from DOM
      this.logger.debug('Extracting video src from DOM...');
      const videoSrc = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        if (video && video.src) {
          return video.src;
        }
        
        const source = document.querySelector('video source') as HTMLSourceElement;
        if (source && source.src) {
          return source.src;
        }
        
        return null;
      });

      if (videoSrc) {
        this.logger.success(`📹 Found video src: ${videoSrc}`);
        videoUrls.push(videoSrc);
      }

      // Get all resources from performance API
      const resources = await page.evaluate(() => {
        return performance.getEntriesByType('resource').map((r: any) => r.name);
      });

      resources.forEach((resource: string) => {
        if (resource.includes('sssrr.org') || 
            resource.includes('trycloudflare.com') ||
            resource.includes('.m3u8') ||
            (resource.includes('.mp4') && !resource.includes('favicon'))) {
          this.logger.success(`🎯 Found in resources: ${resource}`);
          videoUrls.push(resource);
        }
      });

      // Screenshot
      await page.screenshot({ path: 'playerembedapi-ultimate-debug.png', fullPage: true });
      this.logger.debug('Screenshot saved');

      // Save all requests
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-ultimate-requests.json', 
        JSON.stringify(Array.from(allRequests.values()), null, 2));
      this.logger.debug(`Captured ${allRequests.size} requests`);

      if (videoUrls.length === 0) {
        this.logger.error('❌ No video URLs found');
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
