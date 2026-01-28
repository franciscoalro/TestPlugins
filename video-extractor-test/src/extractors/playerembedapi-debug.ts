import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class PlayerEmbedAPIDebugExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Debug';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('🔍 Debug mode - inspect page structure');

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

      // Capture everything
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if (u.includes('sssrr.org') || u.includes('trycloudflare.com') || 
            u.includes('googleapis.com') || u.includes('.mp4') || u.includes('.m3u8')) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
        }
      });

      // Load directly
      this.logger.debug('Loading PlayerEmbedAPI directly...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      
      // Wait and take screenshot
      this.logger.debug('Waiting 5s...');
      await new Promise(r => setTimeout(r, 5000));
      await page.screenshot({ path: 'playerembedapi-debug-1.png', fullPage: true });
      
      // Get HTML structure
      const html = await page.content();
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-debug.html', html);
      this.logger.success('✅ Saved HTML to playerembedapi-debug.html');
      
      // Check for elements
      const elements = await page.evaluate(() => {
        return {
          hasOverlay: !!document.getElementById('overlay'),
          hasPlayback: !!document.getElementById('playback'),
          hasPlayer: !!document.getElementById('player'),
          hasVideo: !!document.querySelector('video'),
          hasIframe: !!document.querySelector('iframe'),
          bodyText: document.body.innerText.substring(0, 500),
          allIds: Array.from(document.querySelectorAll('[id]')).map(el => el.id),
          allClasses: Array.from(document.querySelectorAll('[class]')).map(el => el.className).slice(0, 20)
        };
      });
      
      this.logger.info('Page structure:');
      console.log(JSON.stringify(elements, null, 2));
      
      // Wait longer
      this.logger.debug('Waiting 30s more...');
      await new Promise(r => setTimeout(r, 30000));
      await page.screenshot({ path: 'playerembedapi-debug-2.png', fullPage: true });
      
      // Check again
      const elements2 = await page.evaluate(() => {
        const video = document.querySelector('video') as HTMLVideoElement;
        return {
          hasVideo: !!video,
          videoSrc: video?.src || null,
          videoCurrentSrc: video?.currentSrc || null,
          hasOverlay: !!document.getElementById('overlay'),
          hasPlayback: !!document.getElementById('playback')
        };
      });
      
      this.logger.info('After 30s:');
      console.log(JSON.stringify(elements2, null, 2));
      
      this.logger.info(`Total URLs captured: ${videoUrls.length}`);

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs - check debug files', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'PlayerEmbedAPI-Debug',
        quality: VideoQuality.UNKNOWN,
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      return this.createResult(url, unique, [], startTime);

    } catch (error: any) {
      this.logger.error(`Failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      if (browser) {
        this.logger.info('Browser will stay open for 60s for manual inspection...');
        await new Promise(r => setTimeout(r, 60000));
        await browser.close();
      }
    }
  }
}
