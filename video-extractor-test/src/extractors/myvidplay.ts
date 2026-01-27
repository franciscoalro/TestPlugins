import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { HttpClient } from '../utils/http';
import * as cheerio from 'cheerio';

/**
 * MyVidPlay Extractor
 * Works without iframe - direct HTML extraction
 */
export class MyVidPlayExtractor extends BaseExtractor {
  name = 'MyVidPlay';
  domains = ['myvidplay.com'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);

    try {
      // Fetch page HTML
      const response = await HttpClient.get(url, referer);
      const html = response.data;
      const $ = cheerio.load(html);

      this.logger.debug('HTML loaded, searching for video sources...');

      const links: ExtractorLink[] = [];

      // Method 1: Look for m3u8 URLs in script tags
      $('script').each((_, element) => {
        const scriptContent = $(element).html() || '';
        
        // Pattern: https://domain.com/path/master.m3u8
        const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8/g;
        const matches = scriptContent.match(m3u8Pattern);

        if (matches) {
          matches.forEach(m3u8Url => {
            this.logger.success(`Found M3U8: ${m3u8Url}`);
            links.push({
              url: m3u8Url,
              name: 'MyVidPlay',
              quality: VideoQuality.UNKNOWN,
              isM3U8: true,
              referer: url
            });
          });
        }
      });

      // Method 2: Look for video sources in data attributes
      $('video source, [data-src*=".m3u8"]').each((_, element) => {
        const src = $(element).attr('src') || $(element).attr('data-src');
        if (src && src.includes('.m3u8')) {
          this.logger.success(`Found M3U8 in video tag: ${src}`);
          links.push({
            url: src,
            name: 'MyVidPlay',
            quality: VideoQuality.UNKNOWN,
            isM3U8: true,
            referer: url
          });
        }
      });

      // Method 3: Look for JSON with file URLs
      const jsonPattern = /"file"\s*:\s*"([^"]+\.m3u8[^"]*)"/g;
      let jsonMatch;
      while ((jsonMatch = jsonPattern.exec(html)) !== null) {
        const m3u8Url = jsonMatch[1];
        this.logger.success(`Found M3U8 in JSON: ${m3u8Url}`);
        links.push({
          url: m3u8Url,
          name: 'MyVidPlay',
          quality: VideoQuality.UNKNOWN,
          isM3U8: true,
          referer: url
        });
      }

      // Remove duplicates
      const uniqueLinks = links.filter((link, index, self) =>
        index === self.findIndex(l => l.url === link.url)
      );

      if (uniqueLinks.length === 0) {
        this.logger.error('No video sources found');
        return this.createErrorResult(url, 'No video sources found', startTime);
      }

      this.logger.success(`Extracted ${uniqueLinks.length} link(s)`);
      return this.createResult(url, uniqueLinks, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    }
  }
}
