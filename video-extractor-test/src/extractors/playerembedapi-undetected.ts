import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class PlayerEmbedAPIUndetectedExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Undetected';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🥷 Maximum evasion mode');

    let browser: any = null;

    try {
      const connection = await connect({
        headless: false,
        args: [
          '--no-sandbox',
          '--disable-blink-features=AutomationControlled',
          '--disable-dev-shm-usage'
        ],
        turnstile: true,
        disableXvfb: true
      });

      browser = connection.browser;
      const page = connection.page;

      const videoUrls: string[] = [];

      // CDP capture
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com') || u.includes('googleapis.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp=') || u.includes('.mp4'))) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
        }
      });

      // Remove automation flags
      await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
        
        (window as any).chrome = { runtime: {} };
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters: any) => (
          parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission } as PermissionStatus) :
            originalQuery(parameters)
        );
      });

      this.logger.debug('Loading with ViewPlayer referer...');
      await page.setExtraHTTPHeaders({
        'Referer': 'https://viewplayer.online/',
        'Origin': 'https://viewplayer.online'
      });

      await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
      
      this.logger.debug('Waiting 10s...');
      await new Promise(r => setTimeout(r, 10000));

      // Check for redirect
      const currentUrl = page.url();
      if (currentUrl.includes('abyss.to')) {
        this.logger.error('❌ Detected - redirected to abyss.to');
        return this.createErrorResult(url, 'Automation detected', startTime);
      }

      this.logger.success('✅ No redirect - page loaded');

      // Look for overlay
      const hasOverlay = await page.evaluate(() => {
        return !!(document.getElementById('overlay') || document.getElementById('playback'));
      });

      if (hasOverlay) {
        this.logger.success('✅ Overlay found - clicking...');
        await page.evaluate(() => {
          const overlay = document.getElementById('overlay') || document.getElementById('playback');
          if (overlay) (overlay as HTMLElement).click();
        });
        
        this.logger.debug('Waiting 30s for video...');
        await new Promise(r => setTimeout(r, 30000));
      } else {
        this.logger.debug('No overlay - waiting 30s anyway...');
        await new Promise(r => setTimeout(r, 30000));
      }

      // Extract from video
      const videoData = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        return {
          src: video?.src || null,
          currentSrc: video?.currentSrc || null
        };
      });

      if (videoData.src) {
        this.logger.success(`📹 ${videoData.src}`);
        videoUrls.push(videoData.src);
      }
      if (videoData.currentSrc && videoData.currentSrc !== videoData.src) {
        this.logger.success(`📹 ${videoData.currentSrc}`);
        videoUrls.push(videoData.currentSrc);
      }

      await page.screenshot({ path: 'playerembedapi-undetected.png' });

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'PlayerEmbedAPI-Undetected',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      this.logger.success(`✅ ${unique.length} link(s) in ${Date.now() - startTime}ms`);
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
