import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class ViewPlayerAutoExtractor extends BaseExtractor {
  name = 'ViewPlayer-Auto';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🤖 Automated extraction with puppeteer-real-browser');

    let browser: any = null;

    try {
      const connection = await connect({
        headless: false,
        args: ['--no-sandbox', '--start-maximized'],
        turnstile: false,
        disableXvfb: true
      });

      browser = connection.browser;
      const page = connection.page;

      const videoUrls: string[] = [];

      // Capture with CDP
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if (u.includes('sssrr.org') && (u.includes('?timestamp=') || u.includes('/sora/'))) {
          this.logger.success(`🎯 CDP: ${u}`);
          videoUrls.push(u);
        }
        if (u.includes('trycloudflare.com') && u.includes('/sora/')) {
          this.logger.success(`🎯 CDP: ${u}`);
          videoUrls.push(u);
        }
      });

      // Also capture with page listener
      page.on('request', (req: any) => {
        const u = req.url();
        if (u.includes('sssrr.org') && (u.includes('?timestamp=') || u.includes('/sora/'))) {
          this.logger.success(`📡 Request: ${u}`);
          videoUrls.push(u);
        }
      });

      // Load ViewPlayer
      this.logger.debug('Loading ViewPlayer...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      this.logger.success('✅ ViewPlayer loaded');

      // Wait for page to settle
      this.logger.debug('Waiting 5s for buttons...');
      await new Promise(r => setTimeout(r, 5000));

      // Click PlayerEmbedAPI button
      this.logger.debug('Clicking PlayerEmbedAPI button...');
      const clicked = await page.evaluate(() => {
        const btn = document.querySelector('button[data-source*="playerembedapi"]') as HTMLButtonElement;
        if (btn) {
          btn.click();
          return true;
        }
        return false;
      });

      if (!clicked) {
        this.logger.error('Button not found');
        return this.createErrorResult(url, 'Button not found', startTime);
      }

      this.logger.success('✅ Button clicked');

      // Wait for player iframe to load
      this.logger.debug('Waiting 15s for player iframe...');
      await new Promise(r => setTimeout(r, 15000));

      // Close any popups
      this.logger.debug('Closing popups...');
      const pages = await browser.pages();
      for (const p of pages) {
        if (p !== page && p.url().includes('usheebainaut.com') || p.url().includes('attirecideryeah.com')) {
          await p.close();
          this.logger.debug('Closed popup');
        }
      }

      // Find player frame and click play
      this.logger.debug('Looking for player frame...');
      const frames = page.frames();
      const playerFrame = frames.find((f: any) => f.url().includes('playerembedapi'));
      
      if (playerFrame) {
        this.logger.success('Found player frame');
        
        // Wait a bit more
        await new Promise(r => setTimeout(r, 5000));
        
        // Click overlay
        try {
          this.logger.debug('Clicking play overlay...');
          await playerFrame.evaluate(() => {
            const overlay = document.getElementById('overlay') || document.getElementById('playback');
            if (overlay) {
              (overlay as HTMLElement).click();
            }
          });
          this.logger.success('✅ Clicked overlay');
        } catch (e) {
          this.logger.debug('No overlay or already playing');
        }

        // Wait for video to start
        this.logger.debug('Waiting 30s for video to load...');
        await new Promise(r => setTimeout(r, 30000));

        // Extract from video element
        try {
          const videoData = await playerFrame.evaluate(() => {
            const videos = Array.from(document.querySelectorAll('video'));
            return videos.map(v => ({
              src: v.src,
              currentSrc: v.currentSrc
            })).filter(s => s.src || s.currentSrc);
          });
          
          videoData.forEach(v => {
            if (v.src) {
              this.logger.success(`📹 Video.src: ${v.src}`);
              videoUrls.push(v.src);
            }
            if (v.currentSrc && v.currentSrc !== v.src) {
              this.logger.success(`📹 Video.currentSrc: ${v.currentSrc}`);
              videoUrls.push(v.currentSrc);
            }
          });
        } catch (e) {
          this.logger.debug('Could not extract from video element');
        }
      } else {
        this.logger.error('Player frame not found');
      }

      await page.screenshot({ path: 'viewplayer-auto.png', fullPage: true });
      this.logger.debug(`Total URLs: ${videoUrls.length}`);

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs captured', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'ViewPlayer-PlayerEmbedAPI',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      this.logger.success(`✅ SUCCESS: ${unique.length} link(s)`);
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
