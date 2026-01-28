import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { chromium, Browser, Page } from 'playwright';

/**
 * PlayerEmbedAPI Iframe Extractor
 * Load in iframe to bypass abyss.to redirect, then extract video src
 */
export class PlayerEmbedAPIIframeExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Iframe';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🎬 Using iframe + network interception');

    let browser: Browser | null = null;
    let page: Page | null = null;

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
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        locale: 'pt-BR',
        timezoneId: 'America/Sao_Paulo'
      });

      page = await context.newPage();

      // Capture video URLs from network
      const videoUrls: string[] = [];
      
      page.on('request', (request) => {
        const reqUrl = request.url();
        
        // Look for sssrr.org URLs
        if (reqUrl.includes('sssrr.org') && reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 Found sssrr.org URL: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
        
        // Look for CloudFlare tunnel URLs
        if (reqUrl.includes('trycloudflare.com') && reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 Found CloudFlare tunnel: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
        
        // Look for M3U8/MP4
        if (reqUrl.includes('.m3u8') || reqUrl.includes('.mp4')) {
          this.logger.success(`🎯 Found video URL: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
      });

      // Create a parent page with iframe
      this.logger.debug('Creating parent page with iframe...');
      const parentHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>PlayerEmbedAPI Test</title>
  <style>
    body { margin: 0; padding: 0; background: #000; }
    iframe { width: 100%; height: 100vh; border: none; }
  </style>
</head>
<body>
  <iframe id="player" src="${url}" allowfullscreen></iframe>
</body>
</html>
      `;

      await page.setContent(parentHtml);
      this.logger.success('✅ Parent page loaded with iframe');

      // Wait for network requests
      this.logger.debug('Waiting for video to load (15 seconds)...');
      await page.waitForTimeout(15000);

      if (videoUrls.length === 0) {
        this.logger.error('❌ No video URLs captured from network');
        this.logger.info('💡 Taking screenshot for debugging...');
        await page.screenshot({ path: 'playerembedapi-iframe-debug.png', fullPage: true });
        this.logger.debug('Screenshot saved: playerembedapi-iframe-debug.png');
        
        return this.createErrorResult(url, 'No video URLs captured from network', startTime);
      }

      this.logger.success(`📹 Captured ${videoUrls.length} video URL(s)`);

      // Create links
      const links: ExtractorLink[] = videoUrls.map(videoUrl => {
        // Normalize URL
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

      // Remove duplicates
      const uniqueLinks = links.filter((link, index, self) =>
        index === self.findIndex(l => l.url === link.url)
      );

      this.logger.success(`✅ Extracted ${uniqueLinks.length} unique link(s)`);
      return this.createResult(url, uniqueLinks, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      
      // Take screenshot on error
      if (page) {
        try {
          await page.screenshot({ path: 'playerembedapi-iframe-error.png', fullPage: true });
          this.logger.debug('Error screenshot saved: playerembedapi-iframe-error.png');
        } catch (e) {
          // Ignore screenshot errors
        }
      }
      
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      // Cleanup
      if (browser) {
        await browser.close();
        this.logger.debug('Browser closed');
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
