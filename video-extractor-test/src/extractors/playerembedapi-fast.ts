import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
const { connect } = require('puppeteer-real-browser');

export class PlayerEmbedAPIFastExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-Fast';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting: ${url}`);
    this.logger.info('⚡ Fast mode - click as soon as ready');

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

      // Capture with CDP
      const client = await page.target().createCDPSession();
      await client.send('Network.enable');
      
      client.on('Network.requestWillBeSent', (params: any) => {
        const u = params.request.url;
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp='))) {
          this.logger.success(`🎯 ${u}`);
          videoUrls.push(u);
        }
      });

      page.on('request', (req: any) => {
        const u = req.url();
        if ((u.includes('sssrr.org') || u.includes('trycloudflare.com')) && 
            (u.includes('/sora/') || u.includes('?timestamp='))) {
          this.logger.success(`📡 ${u}`);
          videoUrls.push(u);
        }
      });

      // Inject auto-click script in iframe
      const html = `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#000">
  <iframe id="player" src="${url}" style="width:100%;height:100vh;border:none" allowfullscreen></iframe>
  <script>
    // Auto-click overlay as soon as it appears
    const iframe = document.getElementById('player');
    
    iframe.addEventListener('load', () => {
      console.log('Iframe loaded, waiting for overlay...');
      
      // Check every 500ms for overlay
      const checkOverlay = setInterval(() => {
        try {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
          const overlay = iframeDoc.getElementById('overlay') || iframeDoc.getElementById('playback');
          
          if (overlay) {
            console.log('Overlay found! Clicking...');
            overlay.click();
            clearInterval(checkOverlay);
          }
        } catch (e) {
          // Cross-origin, can't access
        }
      }, 500);
      
      // Stop checking after 30s
      setTimeout(() => clearInterval(checkOverlay), 30000);
    });
  </script>
</body>
</html>
      `;

      this.logger.debug('Loading iframe with auto-click...');
      await page.setContent(html).catch(() => {});
      
      // Wait for iframe to load
      this.logger.debug('Waiting for iframe...');
      await page.waitForFunction(() => {
        const iframe = document.querySelector('iframe');
        return iframe && iframe.contentWindow;
      }, { timeout: 10000 }).catch(() => {});

      // Find iframe frame
      let iframe: any = null;
      for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 1000));
        const frames = page.frames();
        iframe = frames.find((f: any) => f.url().includes('playerembedapi'));
        if (iframe) {
          this.logger.success('✅ Iframe found');
          break;
        }
      }

      if (iframe) {
        // Wait for overlay and click
        this.logger.debug('Waiting for overlay...');
        try {
          await iframe.waitForSelector('#overlay, #playback', { timeout: 15000 });
          this.logger.success('Overlay ready!');
          
          await iframe.evaluate(() => {
            const overlay = document.getElementById('overlay') || document.getElementById('playback');
            if (overlay) (overlay as HTMLElement).click();
          });
          this.logger.success('✅ Clicked overlay');
        } catch (e) {
          this.logger.debug('No overlay or already playing');
        }

        // Wait for video to start (check every 2s)
        this.logger.debug('Waiting for video...');
        let videoFound = false;
        for (let i = 0; i < 30; i++) {
          await new Promise(r => setTimeout(r, 2000));
          
          // Check if we captured URLs
          if (videoUrls.length > 0) {
            this.logger.success(`✅ URLs captured (${videoUrls.length})`);
            videoFound = true;
            break;
          }
          
          // Check video element
          try {
            const src = await iframe.evaluate(() => {
              const v = document.querySelector('video') as HTMLVideoElement;
              return v?.src || null;
            });
            
            if (src) {
              this.logger.success(`📹 Video src: ${src}`);
              videoUrls.push(src);
              videoFound = true;
              break;
            }
          } catch (e) {}
          
          if (i % 5 === 0) {
            this.logger.debug(`Still waiting... (${i * 2}s)`);
          }
        }

        if (!videoFound) {
          this.logger.error('Timeout waiting for video');
        }
      }

      await page.screenshot({ path: 'playerembedapi-fast.png' });

      if (videoUrls.length === 0) {
        return this.createErrorResult(url, 'No URLs', startTime);
      }

      const links: ExtractorLink[] = videoUrls.map(v => ({
        url: v.startsWith('//') ? `https:${v}` : v,
        name: 'PlayerEmbedAPI-Fast',
        quality: this.detectQuality(v),
        isM3U8: v.includes('.m3u8'),
        referer: url
      }));

      const unique = links.filter((l, i, s) => i === s.findIndex(x => x.url === l.url));
      
      this.logger.success(`✅ ${unique.length} link(s) in ${Date.now() - startTime}ms`);
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
