import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import AdblockerPlugin from 'puppeteer-extra-plugin-adblocker';

// Add stealth plugin to avoid detection
puppeteer.use(StealthPlugin());
puppeteer.use(AdblockerPlugin({ blockTrackers: true }));

/**
 * PlayerEmbedAPI Advanced Extractor
 * Uses Puppeteer-extra with stealth plugins and advanced techniques
 */
export class PlayerEmbedAPIAdvancedExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Advanced';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🚀 Using Puppeteer-extra with stealth plugins');

    let browser: any = null;

    try {
      // Launch browser with stealth
      this.logger.debug('Launching stealth browser...');
      browser = await puppeteer.launch({
        headless: false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu',
          '--disable-blink-features=AutomationControlled',
          '--disable-features=IsolateOrigins,site-per-process',
          '--window-size=1920,1080'
        ],
        defaultViewport: {
          width: 1920,
          height: 1080
        }
      });

      const page = await browser.newPage();

      // Set extra headers
      await page.setExtraHTTPHeaders({
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': referer || 'https://viewplayer.online/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site'
      });

      // Set geolocation to Brazil
      await page.setGeolocation({ latitude: -23.5505, longitude: -46.6333 });

      // Capture video URLs from network
      const videoUrls: string[] = [];
      const allRequests: string[] = [];

      page.on('request', (request: any) => {
        const reqUrl = request.url();
        allRequests.push(reqUrl);
        
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
        if (reqUrl.includes('.m3u8') || (reqUrl.includes('.mp4') && !reqUrl.includes('favicon'))) {
          this.logger.success(`🎯 Found video URL: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
      });

      // Method 1: Load in parent page with iframe
      this.logger.debug('Method 1: Creating parent page with iframe...');
      const parentHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Player</title>
  <style>
    body { margin: 0; padding: 0; background: #000; }
    iframe { width: 100%; height: 100vh; border: none; }
  </style>
</head>
<body>
  <iframe id="player" src="${url}" allowfullscreen allow="autoplay"></iframe>
</body>
</html>
      `;

      await page.setContent(parentHtml, { waitUntil: 'networkidle0' });
      this.logger.success('✅ Parent page loaded');

      // Wait for iframe to load
      this.logger.debug('Waiting for iframe to load (10 seconds)...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Try to click play button if exists
      try {
        this.logger.debug('Looking for play button...');
        const playButton = await page.$('#overlay, #playback, .jw-display-icon-container');
        if (playButton) {
          this.logger.debug('Clicking play button...');
          await playButton.click();
          await new Promise(resolve => setTimeout(resolve, 3000));
        }
      } catch (e) {
        this.logger.debug('No play button found or click failed');
      }

      // Wait more for video to load
      this.logger.debug('Waiting for video to load (10 more seconds)...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Method 2: Try to extract from iframe DOM
      this.logger.debug('Method 2: Extracting from iframe DOM...');
      const iframeVideoSrc = await page.evaluate(() => {
        const iframe = document.querySelector('#player') as HTMLIFrameElement;
        if (!iframe || !iframe.contentDocument) return null;

        // Look for video element
        const video = iframe.contentDocument.querySelector('video') as HTMLVideoElement;
        if (video && video.src) {
          return video.src;
        }

        // Look for source element
        const source = iframe.contentDocument.querySelector('video source') as HTMLSourceElement;
        if (source && source.src) {
          return source.src;
        }

        return null;
      });

      if (iframeVideoSrc) {
        this.logger.success(`📹 Found video src in iframe: ${iframeVideoSrc}`);
        videoUrls.push(iframeVideoSrc);
      }

      // Method 3: Use CDP to get all resources
      this.logger.debug('Method 3: Using CDP to get resources...');
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      // Get all loaded resources
      const resources = await page.evaluate(() => {
        return performance.getEntriesByType('resource').map((r: any) => r.name);
      });

      resources.forEach((resource: string) => {
        if (resource.includes('sssrr.org') || 
            resource.includes('trycloudflare.com') ||
            resource.includes('.m3u8') ||
            (resource.includes('.mp4') && !resource.includes('favicon'))) {
          this.logger.success(`🎯 Found resource: ${resource}`);
          videoUrls.push(resource);
        }
      });

      // Take screenshot for debugging
      await page.screenshot({ path: 'playerembedapi-advanced-debug.png', fullPage: true });
      this.logger.debug('Screenshot saved: playerembedapi-advanced-debug.png');

      // Log all requests for analysis
      this.logger.debug(`Total requests captured: ${allRequests.length}`);
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-advanced-requests.json', JSON.stringify(allRequests, null, 2));
      this.logger.debug('All requests saved: playerembedapi-advanced-requests.json');

      if (videoUrls.length === 0) {
        this.logger.error('❌ No video URLs found');
        this.logger.info('💡 Check screenshot and requests.json for debugging');
        return this.createErrorResult(url, 'No video URLs found', startTime);
      }

      this.logger.success(`📹 Found ${videoUrls.length} video URL(s)`);

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
      return this.createErrorResult(url, error.message, startTime);
    } finally {
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
