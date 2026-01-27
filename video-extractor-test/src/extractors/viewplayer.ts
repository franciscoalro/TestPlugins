import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { HttpClient } from '../utils/http';
import * as cheerio from 'cheerio';

/**
 * ViewPlayer Extractor
 * Based on network logs analysis
 */
export class ViewPlayerExtractor extends BaseExtractor {
  name = 'ViewPlayer';
  domains = ['viewplayer.online', 'playerthree.online'];

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

      // Method 1: Look for data-source attributes (from network logs)
      $('[data-source]').each((_, element) => {
        const source = $(element).attr('data-source');
        if (source && source.startsWith('http')) {
          this.logger.success(`Found data-source: ${source}`);
          links.push({
            url: source,
            name: 'ViewPlayer',
            quality: VideoQuality.UNKNOWN,
            isM3U8: source.includes('.m3u8'),
            referer: url
          });
        }
      });

      // Method 2: Look for sssrr.org URLs (from network logs)
      const sssrrPattern = /https?:\/\/[a-z0-9]+\.sssrr\.org\/[^"'\s]+/g;
      const sssrrMatches = html.match(sssrrPattern);
      if (sssrrMatches) {
        sssrrMatches.forEach(sssrrUrl => {
          this.logger.success(`Found sssrr.org URL: ${sssrrUrl}`);
          links.push({
            url: sssrrUrl,
            name: 'ViewPlayer (sssrr.org)',
            quality: VideoQuality.UNKNOWN,
            isM3U8: false,
            referer: url
          });
        });
      }

      // Method 3: Look for CloudFlare tunnel URLs
      const cfPattern = /https?:\/\/[a-z0-9-]+\.trycloudflare\.com\/[^"'\s]+/g;
      const cfMatches = html.match(cfPattern);
      if (cfMatches) {
        cfMatches.forEach(cfUrl => {
          this.logger.success(`Found CloudFlare tunnel: ${cfUrl}`);
          links.push({
            url: cfUrl,
            name: 'ViewPlayer (CloudFlare)',
            quality: VideoQuality.UNKNOWN,
            isM3U8: false,
            referer: url
          });
        });
      }

      // Method 4: Look for PlayerEmbedAPI URLs
      const playerEmbedPattern = /https?:\/\/playerembedapi\.link[^"'\s]*/g;
      const playerEmbedMatches = html.match(playerEmbedPattern);
      if (playerEmbedMatches) {
        playerEmbedMatches.forEach(embedUrl => {
          this.logger.success(`Found PlayerEmbedAPI: ${embedUrl}`);
          links.push({
            url: embedUrl,
            name: 'PlayerEmbedAPI',
            quality: VideoQuality.UNKNOWN,
            isM3U8: false,
            referer: url
          });
        });
      }

      // Method 5: Look for iframe sources
      $('iframe[src]').each((_, element) => {
        const src = $(element).attr('src');
        if (src && src.startsWith('http')) {
          this.logger.success(`Found iframe: ${src}`);
          links.push({
            url: src,
            name: 'ViewPlayer (iframe)',
            quality: VideoQuality.UNKNOWN,
            isM3U8: src.includes('.m3u8'),
            referer: url
          });
        }
      });

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

  /**
   * Follow redirect from sssrr.org or CloudFlare tunnel
   */
  async followRedirect(url: string, referer?: string): Promise<string | null> {
    try {
      this.logger.debug(`Following redirect: ${url}`);
      const response = await HttpClient.get(url, referer);
      
      // Check for Location header (302 redirect)
      if (response.status === 302 && response.headers.location) {
        const redirectUrl = response.headers.location;
        this.logger.success(`Redirect found: ${redirectUrl}`);
        return redirectUrl;
      }

      // Check for meta refresh
      const $ = cheerio.load(response.data);
      const metaRefresh = $('meta[http-equiv="refresh"]').attr('content');
      if (metaRefresh) {
        const urlMatch = metaRefresh.match(/url=(.+)/i);
        if (urlMatch) {
          const redirectUrl = urlMatch[1];
          this.logger.success(`Meta refresh found: ${redirectUrl}`);
          return redirectUrl;
        }
      }

      return null;
    } catch (error: any) {
      this.logger.error(`Failed to follow redirect: ${error.message}`);
      return null;
    }
  }
}
