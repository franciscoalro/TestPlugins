import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { HttpClient } from '../utils/http';

/**
 * DoodStream Extractor
 * Popular video host
 */
export class DoodStreamExtractor extends BaseExtractor {
  name = 'DoodStream';
  domains = ['doodstream.com', 'dood.to', 'dood.watch', 'dood.so', 'dood.pm'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);

    try {
      // Fetch page HTML
      const response = await HttpClient.get(url, referer);
      const html = response.data;

      this.logger.debug('HTML loaded, searching for video URL...');

      // DoodStream uses a specific pattern to generate video URLs
      // Pattern: /pass_md5/...
      const passMd5Pattern = /\/pass_md5\/[^'"]+/;
      const match = html.match(passMd5Pattern);

      if (!match) {
        this.logger.error('pass_md5 URL not found');
        return this.createErrorResult(url, 'pass_md5 URL not found', startTime);
      }

      const passMd5Path = match[0];
      const domain = new URL(url).origin;
      const passMd5Url = `${domain}${passMd5Path}`;

      this.logger.debug(`Found pass_md5 URL: ${passMd5Url}`);

      // Get the token
      const tokenResponse = await HttpClient.get(passMd5Url, url);
      const token = tokenResponse.data;

      this.logger.debug(`Got token: ${token}`);

      // Generate final video URL
      // DoodStream format: https://domain/download/video_id?token=...&expiry=...
      const videoUrl = `${token}${this.generateRandomString()}?token=${token}&expiry=${Date.now()}`;

      this.logger.success(`Generated video URL: ${videoUrl}`);

      const links: ExtractorLink[] = [{
        url: videoUrl,
        name: 'DoodStream',
        quality: VideoQuality.UNKNOWN,
        isM3U8: false,
        referer: url,
        headers: {
          'Range': 'bytes=0-',
          'Referer': url
        }
      }];

      return this.createResult(url, links, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    }
  }

  /**
   * Generate random string for DoodStream URL
   */
  private generateRandomString(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }
}
