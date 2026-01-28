import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class PlayerEmbedAPICDPExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-CDP';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);

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

      // Use CDP to intercept ALL network requests
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && u.includes('/sora/')) {
          this.logger.success(`🎯 CDP: ${u}`);
          videoUrls.push(u);
        }
      });

      // Load iframe
      const html = `<!DOCTYPE html><html><body><iframe src="${url}" style="width:100%;height:100vh;border:none"></iframe></body></html>`;
      
      await page.setContent(html);
      await new Promise(r => setTimeout(r, 10000));

      const iframe = page.frames().find((f: any) => f.url().includes('playerembedapi'));
      if (iframe) {
        try { await iframe.click('#overlay'); } catch (e) {}
        await new Promise(r => setTimeout(r, 8000));
        
        const src = await iframe.evaluate(() => {
          const v = document.querySelector('video') as HTMLVideoElement;
          return v?.src || null;
        });
        
        if (src) {
          this.logger.success(`📹 ${src}`);
          videoUrls.push(src);
        }
      }

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
