import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

export class PlayerEmbedAPIHeadersExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Headers';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);

    let browser: any = null;

    try {
      browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });

      const page = await browser.newPage();

      // Set EXACT Firefox headers
      await page.setExtraHTTPHeaders({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://viewplayer.online/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1'
      });

      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0');

      const videoUrls: string[] = [];
      
      page.on('request', (req: any) => {
        const u = req.url();
        if (u.includes('sssrr.org') || u.includes('trycloudflare.com')) {
          if (u.includes('/sora/')) {
            this.logger.success(`🎯 ${u}`);
            videoUrls.push(u);
          }
        }
      });

      // Load in iframe context
      const html = `<!DOCTYPE html><html><body><iframe src="${url}" style="width:100%;height:100vh;border:none"></iframe></body></html>`;
      
      await page.setContent(html);
      this.logger.debug('Waiting 15s...');
      await new Promise(r => setTimeout(r, 15000));

      const frame = page.frames().find((f: any) => f.url().includes('playerembedapi'));
      if (frame) {
        this.logger.debug('Found frame, clicking...');
        try {
          await frame.click('#overlay');
        } catch (e) {}
        await new Promise(r => setTimeout(r, 10000));
        
        const src = await frame.evaluate(() => {
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
