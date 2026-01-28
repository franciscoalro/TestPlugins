import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class PlayerEmbedAPIOptimizedExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Optimized';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('⚡ Optimized - fast detection + reliable capture');

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
      let capturedCount = 0;

      // Capture with CDP (most reliable)
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com') || u.includes('googleapis.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp=') || u.includes('.mp4'))) {
          this.logger.success(`🎯 CDP: ${u}`);
          videoUrls.push(u);
          capturedCount++;
        }
      });

      // Also page listener
      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com') || u.includes('googleapis.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp=') || u.includes('.mp4'))) {
          this.logger.success(`📡 Request: ${u}`);
          videoUrls.push(u);
          capturedCount++;
        }
      });

      // Load in iframe with proper HTML
      const html = `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#000">
  <iframe id="player" src="${url}" style="width:100%;height:100vh;border:none" allowfullscreen></iframe>
</body>
</html>
      `;

      this.logger.debug('Loading iframe...');
      await page.setContent(html);
      
      // Wait for iframe to be ready
      await page.waitForFunction(() => {
        const iframe = document.querySelector('iframe');
        return iframe && iframe.contentWindow;
      }, { timeout: 10000 }).catch(() => {});

      // Find iframe frame
      this.logger.debug('Finding iframe frame...');
      let iframe: any = null;
      for (let i = 0; i < 15; i++) {
        await new Promise(r => setTimeout(r, 1000));
        const frames = page.frames();
        iframe = frames.find((f: any) => f.url().includes('playerembedapi'));
        if (iframe) {
          this.logger.success(`✅ Iframe found (${i + 1}s)`);
          break;
        }
      }

      if (!iframe) {
        return this.createErrorResult(url, 'Iframe not found', startTime);
      }

      // Wait for overlay to appear (check every 500ms)
      this.logger.debug('Waiting for overlay...');
      let overlayFound = false;
      for (let i = 0; i < 30; i++) {
        try {
          await iframe.waitForSelector('#overlay, #playback', { timeout: 500 });
          overlayFound = true;
          this.logger.success(`✅ Overlay ready (${i * 0.5}s)`);
          break;
        } catch (e) {
          // Keep trying
        }
      }

      if (overlayFound) {
        // Click immediately
        try {
          await iframe.evaluate(() => {
            const overlay = document.getElementById('overlay') || document.getElementById('playback');
            if (overlay) (overlay as HTMLElement).click();
          });
          this.logger.success('✅ Clicked overlay');
        } catch (e) {
          this.logger.debug('Click failed, trying alternative');
        }
      }

      // Wait for video with smart detection
      this.logger.debug('Waiting for video URLs...');
      const maxWait = 45; // 45 seconds max
      let lastCount = 0;
      
      for (let i = 0; i < maxWait; i++) {
        await new Promise(r => setTimeout(r, 1000));
        
        // Check if we got new URLs
        if (capturedCount > lastCount) {
          this.logger.success(`✅ Captured ${capturedCount} URL(s) (${i + 1}s)`);
          lastCount = capturedCount;
          
          // Wait 5 more seconds for additional URLs
          await new Promise(r => setTimeout(r, 5000));
          
          // If we have URLs and no new ones came, we're done
          if (capturedCount === lastCount && capturedCount > 0) {
            this.logger.success(`✅ Extraction complete (${i + 6}s total)`);
            break;
          }
        }
        
        // Also check video element
        if (i % 3 === 0) {
          try {
            const src = await iframe.evaluate(() => {
              const v = document.querySelector('video') as HTMLVideoElement;
              return v?.src || v?.currentSrc || null;
            });
            
            if (src && !videoUrls.includes(src)) {
              this.logger.success(`📹 Video element: ${src}`);
              videoUrls.push(src);
              capturedCount++;
            }
          } catch (e) {}
        }
        
        if (i % 10 === 0 && i > 0) {
          this.logger.debug(`Still waiting... (${i}s, ${capturedCount} URLs)`);
        }
      }

      await page.screenshot({ path: 'playerembedapi-optimized.png' });

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs captured', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'PlayerEmbedAPI-Optimized',
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
