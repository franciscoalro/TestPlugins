import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

/**
 * PlayerEmbedAPI Real Browser Extractor
 * Uses puppeteer-real-browser with rebrowser patches
 */
export class PlayerEmbedAPIRealExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Real';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🔥 Using puppeteer-real-browser (rebrowser patches)');

    let browser: any = null;

    try {
      // Connect with real browser
      this.logger.debug('Connecting to real browser...');
      const connection = await connect({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        turnstile: false,
        disableXvfb: true,
        connectOption: {
          defaultViewport: null
        }
      });

      browser = connection.browser;
      const page = connection.page;

      this.logger.success('✅ Connected');

      // Capture URLs
      const videoUrls: string[] = [];
      
      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && u.includes('/sora/')) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
        }
      });

      // Create iframe page
      const html = `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#000">
  <iframe src="${url}" style="width:100%;height:100vh;border:none" allowfullscreen></iframe>
</body>
</html>
      `;

      this.logger.debug('Loading iframe...');
      await page.setContent(html).catch(() => {
        this.logger.debug('setContent timeout, continuing...');
      });
      
      this.logger.debug('Waiting 40s for iframe to fully load...');
      await new Promise(r => setTimeout(r, 40000));

      // Find iframe
      const frames = page.frames();
      this.logger.debug(`Found ${frames.length} frames`);
      
      const iframe = frames.find((f: any) => f.url().includes('playerembedapi'));
      
      if (iframe) {
        this.logger.debug('Found PlayerEmbedAPI iframe');
        this.logger.debug('Waiting 20s for player to initialize...');
        await new Promise(r => setTimeout(r, 20000));
        
        // Check if overlay exists
        const overlayExists = await iframe.evaluate(() => {
          const overlay = document.getElementById('overlay') || document.getElementById('playback');
          return !!overlay;
        }).catch(() => false);
        
        if (overlayExists) {
          this.logger.debug('Overlay found, clicking...');
          try {
            await iframe.click('#overlay, #playback');
            this.logger.success('Clicked!');
          } catch (e) {
            this.logger.debug('Click failed, trying JS click...');
            await iframe.evaluate(() => {
              const overlay = document.getElementById('overlay') || document.getElementById('playback');
              if (overlay) (overlay as HTMLElement).click();
            });
          }
        } else {
          this.logger.debug('No overlay found, video might auto-play');
        }
        
        this.logger.debug('Waiting 90s for video to load...');
        await new Promise(r => setTimeout(r, 90000));
        
        // Extract from DOM
        this.logger.debug('Extracting video src from DOM...');
        const src = await iframe.evaluate(() => {
          const v = document.querySelector('video') as HTMLVideoElement;
          return v?.src || null;
        });
        
        if (src) {
          this.logger.success(`📹 Found in DOM: ${src}`);
          videoUrls.push(src);
        } else {
          this.logger.debug('No video src in DOM');
        }
      } else {
        this.logger.error('PlayerEmbedAPI iframe not found!');
      }

      this.logger.debug('Taking screenshot...');
      await page.screenshot({ path: 'playerembedapi-real.png' });
      this.logger.debug(`Total URLs captured: ${videoUrls.length}`);

      if (videoUrls.length === 0) {
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
