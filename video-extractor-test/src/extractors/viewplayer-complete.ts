import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

/**
 * ViewPlayer Complete Extractor
 * Extract all PlayerEmbedAPI sources from ViewPlayer buttons
 */
export class ViewPlayerCompleteExtractor extends BaseExtractor {
  name = 'ViewPlayer-Complete';
  domains = ['viewplayer.online'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🎬 ViewPlayer → PlayerEmbedAPI sources');

    let browser: any = null;

    try {
      browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });

      const page = await browser.newPage();
      await page.setViewport({ width: 1920, height: 1080 });

      // Navigate to ViewPlayer
      this.logger.debug('Loading ViewPlayer page...');
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      this.logger.success('✅ ViewPlayer loaded');

      // Extract all PlayerEmbedAPI sources from buttons
      this.logger.debug('Extracting PlayerEmbedAPI sources from buttons...');
      const sources = await page.evaluate(() => {
        const buttons = document.querySelectorAll('button[data-source]');
        const result: Array<{source: string, type: string, id: string, label: string}> = [];
        
        buttons.forEach((btn) => {
          const source = btn.getAttribute('data-source');
          const type = btn.getAttribute('data-type');
          const id = btn.getAttribute('data-id');
          const label = btn.textContent?.trim() || '';
          
          if (source && source.includes('playerembedapi.link')) {
            result.push({ source, type: type || '', id: id || '', label });
          }
        });
        
        return result;
      });

      if (sources.length === 0) {
        this.logger.error('❌ No PlayerEmbedAPI sources found');
        return this.createErrorResult(url, 'No PlayerEmbedAPI sources found', startTime);
      }

      this.logger.success(`📹 Found ${sources.length} PlayerEmbedAPI source(s)`);
      sources.forEach((s, i) => {
        this.logger.info(`  ${i + 1}. ${s.label} → ${s.source}`);
      });

      // Now extract video URLs from each PlayerEmbedAPI source
      const allVideoUrls: Array<{source: string, label: string, videoUrl: string}> = [];

      for (let i = 0; i < sources.length; i++) {
        const source = sources[i];
        this.logger.info(`\n🔍 Processing source ${i + 1}/${sources.length}: ${source.label}`);
        
        try {
          const videoUrl = await this.extractFromPlayerEmbedAPI(page, source.source);
          if (videoUrl) {
            this.logger.success(`  ✅ Found: ${videoUrl}`);
            allVideoUrls.push({
              source: source.source,
              label: source.label,
              videoUrl
            });
          } else {
            this.logger.error(`  ❌ No video URL found`);
          }
        } catch (error: any) {
          this.logger.error(`  ❌ Error: ${error.message}`);
        }
      }

      if (allVideoUrls.length === 0) {
        this.logger.error('❌ No video URLs extracted');
        return this.createErrorResult(url, 'No video URLs extracted', startTime);
      }

      // Create links
      const links: ExtractorLink[] = allVideoUrls.map(item => {
        let normalizedUrl = item.videoUrl;
        if (normalizedUrl.startsWith('//')) {
          normalizedUrl = `https:${normalizedUrl}`;
        }

        return {
          url: normalizedUrl,
          name: `ViewPlayer - ${item.label}`,
          quality: this.detectQuality(normalizedUrl),
          isM3U8: normalizedUrl.includes('.m3u8'),
          referer: item.source
        };
      });

      this.logger.success(`\n✅ Extracted ${links.length} video URL(s)`);
      return this.createResult(url, links, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }

  /**
   * Extract video URL from a single PlayerEmbedAPI source
   */
  private async extractFromPlayerEmbedAPI(page: any, playerEmbedUrl: string): Promise<string | null> {
    this.logger.debug(`  Loading PlayerEmbedAPI in iframe...`);

    // Create iframe with PlayerEmbedAPI
    const iframeHtml = `
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#000">
  <iframe id="player" 
          src="${playerEmbedUrl}" 
          style="width:100%;height:100vh;border:none"
          allowfullscreen>
  </iframe>
</body>
</html>
    `;

    // Track video URLs
    let capturedVideoUrl: string | null = null;

    // Set up request interception
    const requestHandler = (request: any) => {
      const reqUrl = request.url();
      
      // Capture sssrr.org URLs
      if (reqUrl.includes('sssrr.org') && reqUrl.includes('/sora/')) {
        this.logger.debug(`    🎯 Captured sssrr.org: ${reqUrl}`);
        if (!capturedVideoUrl) {
          capturedVideoUrl = reqUrl;
        }
      }
    };

    page.on('request', requestHandler);

    try {
      // Load iframe
      await page.setContent(iframeHtml, { waitUntil: 'domcontentloaded', timeout: 30000 });
      
      // Wait for player to load
      this.logger.debug(`    Waiting for player to load (15s)...`);
      await new Promise(resolve => setTimeout(resolve, 15000));

      // Try to extract from iframe DOM
      if (!capturedVideoUrl) {
        this.logger.debug(`    Trying to extract from iframe DOM...`);
        capturedVideoUrl = await page.evaluate(() => {
          const iframe = document.querySelector('#player') as HTMLIFrameElement;
          if (!iframe || !iframe.contentDocument) return null;

          const video = iframe.contentDocument.querySelector('video') as HTMLVideoElement;
          if (video && video.src) {
            return video.src;
          }

          return null;
        });
      }

      return capturedVideoUrl;

    } finally {
      // Remove listener
      page.off('request', requestHandler);
    }
  }

  private detectQuality(url: string): VideoQuality {
    if (url.includes('1080') || url.includes('1920')) return VideoQuality.Q1080;
    if (url.includes('720') || url.includes('1280')) return VideoQuality.Q720;
    if (url.includes('480')) return VideoQuality.Q480;
    if (url.includes('360')) return VideoQuality.Q360;
    return VideoQuality.UNKNOWN;
  }
}
