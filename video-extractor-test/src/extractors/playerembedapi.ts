import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { chromium } from 'playwright';

/**
 * PlayerEmbedAPI Extractor
 * Based on network logs analysis
 * 
 * Flow:
 * 1. Load https://playerembedapi.link/?v={id}
 * 2. Service Worker loads: sw.import.js, sw.bundle.js
 * 3. Core bundle loads: core.bundle.js from iamcdn.net
 * 4. WebSocket connects to wss.morphify.net
 * 5. Video requests go through sssrr.org → CloudFlare tunnel
 * 6. Capture M3U8/MP4 URLs from network
 */
export class PlayerEmbedAPIExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.warn('⚠️  PlayerEmbedAPI requires browser automation');

    let browser;
    try {
      // Launch browser
      this.logger.debug('Launching browser...');
      browser = await chromium.launch({ 
        headless: false,
        args: [
          '--disable-blink-features=AutomationControlled',
          '--disable-dev-shm-usage',
          '--no-sandbox'
        ]
      });
      
      const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
        viewport: { width: 1920, height: 1080 },
        extraHTTPHeaders: referer ? { 'Referer': referer } : {}
      });
      
      const page = await context.newPage();

      // Track captured URLs
      const capturedUrls = new Set<string>();
      const links: ExtractorLink[] = [];

      // Intercept network requests
      page.on('response', async (response) => {
        const url = response.url();
        
        // Capture M3U8 URLs
        if (url.includes('.m3u8')) {
          if (!capturedUrls.has(url)) {
            capturedUrls.add(url);
            this.logger.success(`📹 Captured M3U8: ${url}`);
            links.push({
              url,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(url),
              isM3U8: true,
              referer: page.url()
            });
          }
        }
        
        // Capture MP4 URLs
        if (url.includes('.mp4') && !url.includes('favicon')) {
          if (!capturedUrls.has(url)) {
            capturedUrls.add(url);
            this.logger.success(`📹 Captured MP4: ${url}`);
            links.push({
              url,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(url),
              isM3U8: false,
              referer: page.url()
            });
          }
        }

        // Capture sssrr.org URLs
        if (url.includes('sssrr.org')) {
          this.logger.debug(`🔗 sssrr.org request: ${url}`);
        }

        // Capture CloudFlare tunnel URLs
        if (url.includes('trycloudflare.com')) {
          this.logger.debug(`☁️  CloudFlare tunnel: ${url}`);
        }
      });

      // Navigate to page
      this.logger.info(`Loading: ${url}`);
      await page.goto(url, { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });

      this.logger.info('⏳ Page loaded, waiting for video sources...');
      this.logger.info('👆 If you see overlays, click to remove them');

      // Wait for video sources (max 45 seconds)
      const timeout = 45000;
      const startWait = Date.now();
      
      while (links.length === 0 && (Date.now() - startWait) < timeout) {
        await page.waitForTimeout(1000);
        
        // Log progress every 5 seconds
        const elapsed = Math.floor((Date.now() - startWait) / 1000);
        if (elapsed % 5 === 0 && elapsed > 0) {
          this.logger.debug(`⏱️  Waiting... ${elapsed}s elapsed`);
        }
      }

      // Try to find video element
      const videoElement = await page.$('video');
      if (videoElement) {
        this.logger.success('✅ Video element found on page');
        
        // Try to get src from video element
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

      // Take screenshot for debugging
      await page.screenshot({ path: 'playerembedapi-screenshot.png' });
      this.logger.debug('📸 Screenshot saved: playerembedapi-screenshot.png');

      await browser.close();

      if (links.length === 0) {
        this.logger.error('No video sources captured after 45 seconds');
        return this.createErrorResult(url, 'Timeout waiting for video sources', startTime);
      }

      this.logger.success(`Extracted ${links.length} link(s)`);
      return this.createResult(url, links, [], startTime);

    } catch (error: any) {
      if (browser) await browser.close();
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    }
  }

  /**
   * Detect quality from URL
   */
  private detectQuality(url: string): VideoQuality {
    if (url.includes('1080') || url.includes('1920')) return VideoQuality.Q1080;
    if (url.includes('720') || url.includes('1280')) return VideoQuality.Q720;
    if (url.includes('480')) return VideoQuality.Q480;
    if (url.includes('360')) return VideoQuality.Q360;
    return VideoQuality.UNKNOWN;
  }
}
