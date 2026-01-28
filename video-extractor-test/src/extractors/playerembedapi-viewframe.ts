import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

/**
 * PlayerEmbedAPI ViewFrame Extractor
 * Load inside ViewPlayer frame to avoid detection
 */
export class PlayerEmbedAPIViewFrameExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-ViewFrame';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🎭 Loading inside ViewPlayer frame');

    let browser: any = null;

    try {
      browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });

      const page = await browser.newPage();
      await page.setViewport({ width: 1920, height: 1080 });

      // Capture video URLs
      const videoUrls: string[] = [];
      const allRequests: string[] = [];
      
      page.on('request', (request: any) => {
        const reqUrl = request.url();
        allRequests.push(reqUrl);
        
        if ((reqUrl.includes('sssrr.org') || reqUrl.includes('trycloudflare.com')) && 
            reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
      });

      // Create ViewPlayer-like page with iframe
      const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ViewPlayer</title>
  <style>
    body { margin: 0; padding: 0; background: #000; }
    .container { width: 100%; height: 100vh; }
    iframe { width: 100%; height: 100%; border: none; }
  </style>
</head>
<body>
  <div class="container">
    <iframe id="player" src="${url}" allowfullscreen allow="autoplay"></iframe>
  </div>
  <script>
    // Simulate ViewPlayer behavior
    window.addEventListener('message', function(e) {
      console.log('Message from iframe:', e.data);
    });
  </script>
</body>
</html>
      `;

      this.logger.debug('Loading ViewPlayer page...');
      await page.setContent(html, { waitUntil: 'domcontentloaded' });
      this.logger.success('✅ Page loaded');

      // Wait for iframe to load
      this.logger.debug('Waiting for iframe (10s)...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Try to interact with iframe
      try {
        this.logger.debug('Trying to click inside iframe...');
        const frame = page.frames().find(f => f.url().includes('playerembedapi'));
        
        if (frame) {
          this.logger.debug('Found iframe frame');
          
          // Click overlay
          try {
            await frame.click('#overlay, #playback').catch(() => {});
            this.logger.debug('Clicked overlay');
          } catch (e) {}
          
          // Wait
          await new Promise(resolve => setTimeout(resolve, 8000));
          
          // Extract video src from iframe
          const videoSrc = await frame.evaluate(() => {
            const video = document.querySelector('video') as HTMLVideoElement;
            return video?.src || null;
          });
          
          if (videoSrc) {
            this.logger.success(`📹 Found in iframe: ${videoSrc}`);
            videoUrls.push(videoSrc);
          }
        }
      } catch (e: any) {
        this.logger.debug(`Iframe interaction: ${e.message}`);
      }

      await page.screenshot({ path: 'playerembedapi-viewframe.png', fullPage: true });

      // Save all requests
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-viewframe-requests.json', JSON.stringify(allRequests, null, 2));
      this.logger.debug(`Captured ${allRequests.length} requests`);

      if (videoUrls.length === 0) {
        this.logger.error('❌ No URLs');
        this.logger.info('Check playerembedapi-viewframe-requests.json');
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
