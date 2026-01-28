import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class ViewPlayerInstantExtractor extends BaseExtractor {
  name = 'ViewPlayer-Instant';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('⚡ INSTANT mode - click immediately when ready');

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
      let urlCaptured = false;

      // CDP capture
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com') || u.includes('googleapis.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp=') || u.includes('.mp4'))) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
          urlCaptured = true;
        }
      });

      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com') || u.includes('googleapis.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp=') || u.includes('.mp4'))) {
          this.logger.success(`📡 ${u}`);
          videoUrls.push(u);
          urlCaptured = true;
        }
      });

      // Load ViewPlayer
      this.logger.debug('Loading ViewPlayer...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      this.logger.success(`✅ Loaded (${Date.now() - startTime}ms)`);

      // Wait for button and click ASAP
      this.logger.debug('Waiting for PlayerEmbedAPI button...');
      await page.waitForSelector('button[data-source*="playerembedapi"]', { timeout: 15000 });
      const btnTime = Date.now() - startTime;
      this.logger.success(`✅ Button ready (${btnTime}ms)`);
      
      await page.click('button[data-source*="playerembedapi"]');
      this.logger.success(`✅ Clicked (${Date.now() - startTime}ms)`);

      // Wait for iframe to appear
      this.logger.debug('Waiting for player iframe...');
      let iframe: any = null;
      for (let i = 0; i < 30; i++) {
        await new Promise(r => setTimeout(r, 500));
        const frames = page.frames();
        iframe = frames.find((f: any) => f.url().includes('playerembedapi'));
        if (iframe) {
          this.logger.success(`✅ Iframe ready (${Date.now() - startTime}ms)`);
          break;
        }
      }

      if (!iframe) {
        return this.createErrorResult(url, 'Iframe not found', startTime);
      }

      // Close popups immediately
      const pages = await browser.pages();
      for (const p of pages) {
        if (p !== page) {
          await p.close().catch(() => {});
        }
      }

      // Wait for overlay and click ASAP
      this.logger.debug('Waiting for overlay...');
      try {
        await iframe.waitForSelector('#overlay, #playback', { timeout: 20000 });
        const overlayTime = Date.now() - startTime;
        this.logger.success(`✅ Overlay ready (${overlayTime}ms)`);
        
        await iframe.evaluate(() => {
          const overlay = document.getElementById('overlay') || document.getElementById('playback');
          if (overlay) (overlay as HTMLElement).click();
        });
        this.logger.success(`✅ Clicked overlay (${Date.now() - startTime}ms)`);
      } catch (e) {
        this.logger.debug('No overlay or already playing');
      }

      // Smart wait - stop as soon as we get URLs
      this.logger.debug('Waiting for video URLs...');
      const maxWait = 40;
      for (let i = 0; i < maxWait; i++) {
        await new Promise(r => setTimeout(r, 1000));
        
        if (urlCaptured && videoUrls.length > 0) {
          // Wait 3 more seconds for additional URLs
          await new Promise(r => setTimeout(r, 3000));
          
          // Check video element too
          try {
            const src = await iframe.evaluate(() => {
              const v = document.querySelector('video') as HTMLVideoElement;
              return v?.src || v?.currentSrc || null;
            });
            if (src && !videoUrls.includes(src)) {
              this.logger.success(`📹 ${src}`);
              videoUrls.push(src);
            }
          } catch (e) {}
          
          this.logger.success(`✅ Complete (${Date.now() - startTime}ms)`);
          break;
        }
        
        if (i % 5 === 0 && i > 0) {
          this.logger.debug(`Waiting... (${i}s)`);
        }
      }

      await page.screenshot({ path: 'viewplayer-instant.png' });

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'ViewPlayer-Instant',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      const elapsed = Date.now() - startTime;
      this.logger.success(`✅ SUCCESS: ${unique.length} link(s) in ${elapsed}ms`);
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
