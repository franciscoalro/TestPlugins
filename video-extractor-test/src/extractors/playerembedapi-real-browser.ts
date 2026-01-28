import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';

/**
 * PlayerEmbedAPI Real Browser Extractor
 * Uses puppeteer-real-browser to completely bypass detection
 */
export class PlayerEmbedAPIRealBrowserExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-RealBrowser';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🔥 Using puppeteer-real-browser (undetectable)');

    let browser: any = null;
    let page: any = null;

    try {
      // Import puppeteer-real-browser dynamically
      const { connect } = await import('puppeteer-real-browser');

      this.logger.debug('Connecting to real browser...');
      const response = await connect({
        headless: false,
        args: [],
        customConfig: {},
        turnstile: true,
        connectOption: {},
        disableXvfb: true,
        ignoreAllFlags: false
      });

      browser = response.browser;
      page = response.page;

      this.logger.success('✅ Real browser connected (undetectable)');

      // Capture video URLs
      const videoUrls: string[] = [];

      page.on('request', (request: any) => {
        const reqUrl = request.url();
        
        if (reqUrl.includes('sssrr.org') && reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 sssrr.org: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
        
        if (reqUrl.includes('trycloudflare.com') && reqUrl.includes('/sora/')) {
          this.logger.success(`🎯 CloudFlare: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
        
        if (reqUrl.includes('.m3u8') || (reqUrl.includes('.mp4') && !reqUrl.includes('favicon'))) {
          this.logger.success(`🎯 Video: ${reqUrl}`);
          videoUrls.push(reqUrl);
        }
      });

      // Set referer
      await page.setExtraHTTPHeaders({
        'Referer': referer || 'https://viewplayer.online/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site'
      });

      // Navigate
      this.logger.debug('Navigating to PlayerEmbedAPI...');
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      this.logger.success('✅ Page loaded');

      // Wait for player
      this.logger.debug('Waiting for player to initialize (20 seconds)...');
      await new Promise(resolve => setTimeout(resolve, 20000));

      // Try to click play
      try {
        const overlay = await page.$('#overlay, #playback, .jw-display-icon-container');
        if (overlay) {
          this.logger.debug('Clicking play...');
          await overlay.click();
          await new Promise(resolve => setTimeout(resolve, 5000));
        }
      } catch (e) {
        this.logger.debug('No play button');
      }

      // Extract from DOM
      const videoSrc = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        return video?.src || null;
      });

      if (videoSrc) {
        this.logger.success(`📹 Video src: ${videoSrc}`);
        videoUrls.push(videoSrc);
      }

      // Screenshot
      await page.screenshot({ path: 'playerembedapi-real-browser.png', fullPage: true });
      this.logger.debug('Screenshot saved');

      if (videoUrls.length === 0) {
        this.logger.error('❌ No video URLs found');
        return this.createErrorResult(url, 'No video URLs found', startTime);
      }

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

      this.logger.success(`✅ Extracted ${uniqueLinks.length} link(s)`);
      return this.createResult(url, uniqueLinks, [], startTime);

    } catch (error: any) {
      this.logger.error(`Failed: ${error.message}`);
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
