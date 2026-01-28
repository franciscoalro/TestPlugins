import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class ViewPlayerTurboExtractor extends BaseExtractor {
  name = 'ViewPlayer-Turbo';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🚀 TURBO mode - maximum speed');

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
      let firstUrlTime = 0;

      // Block popups and new tabs
      await page.evaluateOnNewDocument(() => {
        window.open = () => null;
      });

      // Auto-close any new pages (but not iframes)
      browser.on('targetcreated', async (target: any) => {
        if (target.type() === 'page') {
          const newPage = await target.page();
          if (newPage && newPage !== page) {
            const url = newPage.url();
            if (url.includes('usheebainaut.com') || url.includes('attirecideryeah.com')) {
              this.logger.debug('Blocked popup');
              await newPage.close().catch(() => {});
            }
          }
        }
      });

      // CDP capture
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') && u.includes('?timestamp=')) || 
            (u.includes('googleapis.com') && u.includes('.mp4'))) {
          if (firstUrlTime === 0) firstUrlTime = Date.now() - startTime;
          this.logger.success(`🎯 ${u} (${Date.now() - startTime}ms)`);
          videoUrls.push(u);
        }
      });

      // Also capture responses
      client.on('Network.responseReceived', (params: any) => {
        const u = params.response.url;
        if ((u.includes('sssrr.org') && u.includes('?timestamp=')) || 
            (u.includes('googleapis.com') && u.includes('.mp4'))) {
          if (firstUrlTime === 0) firstUrlTime = Date.now() - startTime;
          this.logger.success(`📥 ${u} (${Date.now() - startTime}ms)`);
          if (!videoUrls.includes(u)) videoUrls.push(u);
        }
      });

      // Page listener
      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') && u.includes('?timestamp=')) || 
            (u.includes('googleapis.com') && u.includes('.mp4'))) {
          if (firstUrlTime === 0) firstUrlTime = Date.now() - startTime;
          this.logger.success(`📡 ${u} (${Date.now() - startTime}ms)`);
          if (!videoUrls.includes(u)) videoUrls.push(u);
        }
      });

      // Load ViewPlayer
      this.logger.debug('Loading...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      
      // Click button ASAP
      await page.waitForSelector('button[data-source*="playerembedapi"]', { timeout: 10000 });
      await page.click('button[data-source*="playerembedapi"]');
      this.logger.success(`✅ Clicked (${Date.now() - startTime}ms)`);

      // Find iframe quickly
      let iframe: any = null;
      for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 300));
        const frames = page.frames();
        iframe = frames.find((f: any) => f.url().includes('playerembedapi'));
        if (iframe) break;
      }

      if (!iframe) {
        return this.createErrorResult(url, 'Iframe not found', startTime);
      }

      // Click overlay quickly
      try {
        await iframe.waitForSelector('#overlay', { timeout: 10000 });
        await iframe.evaluate(() => {
          const overlay = document.getElementById('overlay');
          if (overlay) (overlay as HTMLElement).click();
        });
        this.logger.success(`✅ Playing (${Date.now() - startTime}ms)`);
        
        // Wait 3s and click again to ensure playback
        await new Promise(r => setTimeout(r, 3000));
        await iframe.evaluate(() => {
          const overlay = document.getElementById('overlay');
          if (overlay) (overlay as HTMLElement).click();
        });
        this.logger.success(`✅ Clicked again (${Date.now() - startTime}ms)`);
      } catch (e) {
        this.logger.debug('No overlay found');
      }

      // Wait only until we get first URL, then 2s more
      const maxWait = 40;
      for (let i = 0; i < maxWait; i++) {
        await new Promise(r => setTimeout(r, 1000));
        
        // Also check video element every 3 seconds
        if (i % 3 === 0 && iframe) {
          try {
            const videoSrc = await iframe.evaluate(() => {
              const video = document.querySelector('video') as HTMLVideoElement;
              return {
                src: video?.src || null,
                currentSrc: video?.currentSrc || null
              };
            });
            
            if (videoSrc.src && !videoUrls.includes(videoSrc.src)) {
              this.logger.success(`📹 Video.src: ${videoSrc.src}`);
              videoUrls.push(videoSrc.src);
            }
            if (videoSrc.currentSrc && !videoUrls.includes(videoSrc.currentSrc)) {
              this.logger.success(`📹 Video.currentSrc: ${videoSrc.currentSrc}`);
              videoUrls.push(videoSrc.currentSrc);
            }
          } catch (e) {}
        }
        
        if (videoUrls.length > 0) {
          this.logger.success(`✅ Got URL! Waiting 2s more...`);
          await new Promise(r => setTimeout(r, 2000));
          break;
        }
        
        if (i % 5 === 0 && i > 0) {
          this.logger.debug(`Waiting... (${i}s, ${videoUrls.length} URLs)`);
        }
      }

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'ViewPlayer-Turbo',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      const elapsed = Date.now() - startTime;
      this.logger.success(`✅ ${unique.length} link(s) in ${elapsed}ms (first: ${firstUrlTime}ms)`);
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
