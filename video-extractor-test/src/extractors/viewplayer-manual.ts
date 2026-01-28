import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class ViewPlayerManualExtractor extends BaseExtractor {
  name = 'ViewPlayer-Manual';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('👆 MANUAL MODE - Click yourself!');

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
      const allRequests: string[] = [];

      // Capture EVERYTHING
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        allRequests.push(u);
        
        if (u.includes('sssrr.org') || u.includes('trycloudflare.com')) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
        }
      });

      page.on('request', (req: any) => {
        const u = req.url();
        if (u.includes('sssrr.org') || u.includes('trycloudflare.com')) {
          this.logger.success(`📡 ${u}`);
          videoUrls.push(u);
        }
      });

      // Track clicks
      await page.evaluateOnNewDocument(() => {
        document.addEventListener('click', (e: any) => {
          const target = e.target;
          console.log('CLICK:', {
            tag: target.tagName,
            id: target.id,
            class: target.className,
            text: target.textContent?.substring(0, 50)
          });
        }, true);
      });

      // Load page
      this.logger.info('Loading ViewPlayer...');
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      this.logger.success('✅ Page loaded');

      // Wait for manual interaction
      this.logger.info('');
      this.logger.info('👆 NOW:');
      this.logger.info('  1. Click the PlayerEmbedAPI button');
      this.logger.info('  2. Close any popups');
      this.logger.info('  3. Click play on the video');
      this.logger.info('  4. Wait for video to start playing');
      this.logger.info('');
      this.logger.info('⏳ Waiting 3 minutes for you to interact...');
      this.logger.info('   (URLs will be captured automatically)');
      this.logger.info('');

      // Wait 3 minutes
      for (let i = 180; i > 0; i -= 10) {
        await new Promise(r => setTimeout(r, 10000));
        this.logger.debug(`⏱️  ${i}s remaining... (${videoUrls.length} URLs captured)`);
      }

      // Final check - extract from all video elements
      this.logger.info('');
      this.logger.info('🔍 Final check - extracting from video elements...');
      
      const allFrames = page.frames();
      for (const frame of allFrames) {
        try {
          const frameSrcs = await frame.evaluate(() => {
            const videos = Array.from(document.querySelectorAll('video'));
            return videos.map(v => ({
              src: v.src,
              currentSrc: v.currentSrc
            })).filter(s => s.src || s.currentSrc);
          });
          
          frameSrcs.forEach(s => {
            if (s.src) {
              this.logger.success(`📹 Video.src: ${s.src}`);
              videoUrls.push(s.src);
            }
            if (s.currentSrc && s.currentSrc !== s.src) {
              this.logger.success(`📹 Video.currentSrc: ${s.currentSrc}`);
              videoUrls.push(s.currentSrc);
            }
          });
        } catch (e) {}
      }

      // Save all requests
      const fs = require('fs');
      fs.writeFileSync('viewplayer-manual-requests.json', JSON.stringify(allRequests, null, 2));
      this.logger.info(`💾 Saved ${allRequests.length} requests to viewplayer-manual-requests.json`);

      await page.screenshot({ path: 'viewplayer-manual.png', fullPage: true });

      if (videoUrls.length === 0) {
        this.logger.error('❌ No URLs captured');
        this.logger.info('💡 Check viewplayer-manual-requests.json for all requests');
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'ViewPlayer-Manual',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      this.logger.success(`✅ ${unique.length} unique link(s)`);
      return this.createResult(url, unique, [], startTime);

    } catch (error: any) {
      this.logger.error(`Failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      if (browser) {
        this.logger.info('Closing browser...');
        await browser.close();
      }
    }
  }

  private detectQuality(url: string): VideoQuality {
    if (url.includes('1080')) return VideoQuality.Q1080;
    if (url.includes('720')) return VideoQuality.Q720;
    if (url.includes('480')) return VideoQuality.Q480;
    return VideoQuality.UNKNOWN;
  }
}
