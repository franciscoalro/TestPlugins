import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class ViewPlayerRealExtractor extends BaseExtractor {
  name = 'ViewPlayer-Real';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🎬 Loading real ViewPlayer page');

    let browser: any = null;

    try {
      const connection = await connect({
        headless: false,
        args: ['--no-sandbox'],
        turnstile: false,
        disableXvfb: true
      });

      browser = connection.browser;
      const page = connection.page;

      const videoUrls: string[] = [];

      // Method 1: CDP Network
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && u.includes('/sora/')) {
          this.logger.success(`🎯 CDP: ${u}`);
          videoUrls.push(u);
        }
      });

      // Method 2: Page request listener
      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && u.includes('/sora/')) {
          this.logger.success(`🎯 Request: ${u}`);
          videoUrls.push(u);
        }
      });

      // Method 3: Response listener
      page.on('response', (res: any) => {
        const u = res.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && u.includes('/sora/')) {
          this.logger.success(`🎯 Response: ${u}`);
          videoUrls.push(u);
        }
      });

      // Load ViewPlayer
      this.logger.debug('Loading ViewPlayer...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      this.logger.success('✅ ViewPlayer loaded');

      // Wait for buttons
      this.logger.debug('Waiting 10s for buttons...');
      await new Promise(r => setTimeout(r, 10000));

      // Find PlayerEmbedAPI button
      this.logger.debug('Looking for PlayerEmbedAPI button...');
      const buttonExists = await page.evaluate(() => {
        const btn = document.querySelector('button[data-source*="playerembedapi"]');
        return !!btn;
      });
      
      if (!buttonExists) {
        this.logger.error('PlayerEmbedAPI button not found');
        return this.createErrorResult(url, 'Button not found', startTime);
      }

      this.logger.success('Found button, clicking with JS...');
      await page.evaluate(() => {
        const btn = document.querySelector('button[data-source*="playerembedapi"]') as HTMLButtonElement;
        btn?.click();
      });

      // Wait for player to load
      this.logger.debug('Waiting 30s for player...');
      await new Promise(r => setTimeout(r, 30000));

      // Try to click play overlay
      try {
        this.logger.debug('Looking for play overlay...');
        const frames = page.frames();
        const playerFrame = frames.find((f: any) => f.url().includes('playerembedapi'));
        
        if (playerFrame) {
          this.logger.debug('Found player frame, clicking overlay...');
          await playerFrame.click('#overlay, #playback').catch(() => {});
          this.logger.debug('Waiting 60s for video...');
          await new Promise(r => setTimeout(r, 60000));
          
          // Extract from DOM
          const src = await playerFrame.evaluate(() => {
            const v = document.querySelector('video') as HTMLVideoElement;
            return v?.src || null;
          });
          
          if (src) {
            this.logger.success(`📹 Video src: ${src}`);
            videoUrls.push(src);
          }

          // Also try to get from all video elements
          const allSrcs = await playerFrame.evaluate(() => {
            const videos = Array.from(document.querySelectorAll('video'));
            return videos.map(v => v.src).filter(s => s);
          });
          
          allSrcs.forEach(s => {
            this.logger.success(`📹 Video element: ${s}`);
            videoUrls.push(s);
          });
        }
      } catch (e: any) {
        this.logger.debug(`Overlay click: ${e.message}`);
      }

      // Method 4: Check all frames for video elements
      this.logger.debug('Checking all frames for video elements...');
      const allFrames = page.frames();
      for (const frame of allFrames) {
        try {
          const frameSrcs = await frame.evaluate(() => {
            const videos = Array.from(document.querySelectorAll('video'));
            return videos.map(v => v.src).filter(s => s && s.includes('sssrr.org'));
          });
          
          frameSrcs.forEach(s => {
            this.logger.success(`📹 Frame video: ${s}`);
            videoUrls.push(s);
          });
        } catch (e) {
          // Frame might not be accessible
        }
      }

      await page.screenshot({ path: 'viewplayer-real.png' });
      this.logger.debug(`Captured ${videoUrls.length} URLs`);

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'ViewPlayer-PlayerEmbedAPI',
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
