import { BaseExtractor } from './base';
import { ExtractorResult, ExtractorLink, VideoQuality } from '../types';
import { HttpClient } from '../utils/http';
import * as cheerio from 'cheerio';

/**
 * PlayerEmbedAPI HTTP-only Extractor
 * Bypass browser detection by using pure HTTP requests
 */
export class PlayerEmbedAPIHttpExtractor extends BaseExtractor {
  name = 'PlayerEmbedAPI-HTTP';
  domains = ['playerembedapi.link'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    this.logger.info(`Extracting from: ${url}`);
    this.logger.info('🌐 Using HTTP-only approach (no browser)');

    try {
      // Step 1: Fetch page HTML with realistic headers
      this.logger.debug('Fetching page HTML...');
      const response = await HttpClient.get(url, referer, {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
      });

      const html = response.data;
      const $ = cheerio.load(html);

      this.logger.debug(`HTML loaded (${html.length} bytes)`);

      // Save HTML for manual analysis (always save, even on error)
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-http.html', html);
      this.logger.debug('💾 HTML saved: playerembedapi-http.html');

      // Check if redirected to abyss.to
      if (html.includes('abyss.to') || html.includes('ERR_BLOCKED')) {
        this.logger.error('❌ HTML contains abyss.to redirect');
        this.logger.info('💡 Check playerembedapi-http.html to see the redirect mechanism');
        return this.createErrorResult(url, 'Redirected to abyss.to in HTML', startTime);
      }

      const links: ExtractorLink[] = [];

      // Method 1: Look for video sources in script tags
      this.logger.debug('Searching for video sources in scripts...');
      $('script').each((_, element) => {
        const scriptContent = $(element).html() || '';
        
        // Pattern 1: M3U8 URLs
        const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8[^"'\s]*/g;
        const m3u8Matches = scriptContent.match(m3u8Pattern);
        if (m3u8Matches) {
          m3u8Matches.forEach(m3u8Url => {
            this.logger.success(`📹 Found M3U8 in script: ${m3u8Url}`);
            links.push({
              url: m3u8Url,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(m3u8Url),
              isM3U8: true,
              referer: url
            });
          });
        }

        // Pattern 2: MP4 URLs
        const mp4Pattern = /https?:\/\/[^"'\s]+\.mp4[^"'\s]*/g;
        const mp4Matches = scriptContent.match(mp4Pattern);
        if (mp4Matches) {
          mp4Matches.forEach(mp4Url => {
            if (!mp4Url.includes('favicon')) {
              this.logger.success(`📹 Found MP4 in script: ${mp4Url}`);
              links.push({
                url: mp4Url,
                name: 'PlayerEmbedAPI',
                quality: this.detectQuality(mp4Url),
                isM3U8: false,
                referer: url
              });
            }
          });
        }

        // Pattern 3: sssrr.org URLs
        const sssrrPattern = /https?:\/\/[a-z0-9]+\.sssrr\.org\/[^"'\s]+/g;
        const sssrrMatches = scriptContent.match(sssrrPattern);
        if (sssrrMatches) {
          sssrrMatches.forEach(sssrrUrl => {
            this.logger.debug(`🔗 Found sssrr.org URL: ${sssrrUrl}`);
            // We'll try to follow these redirects
          });
        }

        // Pattern 4: Base64 encoded data
        const base64Pattern = /data:video\/[^;]+;base64,([A-Za-z0-9+/=]+)/g;
        let base64Match;
        while ((base64Match = base64Pattern.exec(scriptContent)) !== null) {
          this.logger.debug(`🔐 Found base64 video data (${base64Match[1].length} chars)`);
        }

        // Pattern 5: JSON with file URLs
        const jsonFilePattern = /"(?:file|src|url|source)"\s*:\s*"([^"]+)"/g;
        let jsonMatch;
        while ((jsonMatch = jsonFilePattern.exec(scriptContent)) !== null) {
          const fileUrl = jsonMatch[1];
          if (fileUrl.includes('.m3u8') || fileUrl.includes('.mp4')) {
            this.logger.success(`📹 Found URL in JSON: ${fileUrl}`);
            links.push({
              url: fileUrl,
              name: 'PlayerEmbedAPI',
              quality: this.detectQuality(fileUrl),
              isM3U8: fileUrl.includes('.m3u8'),
              referer: url
            });
          }
        }
      });

      // Method 2: Look for video/source elements
      this.logger.debug('Searching for video elements...');
      $('video source, video').each((_, element) => {
        const src = $(element).attr('src') || $(element).attr('data-src');
        if (src && (src.includes('.m3u8') || src.includes('.mp4'))) {
          this.logger.success(`📹 Found in video element: ${src}`);
          links.push({
            url: src,
            name: 'PlayerEmbedAPI',
            quality: this.detectQuality(src),
            isM3U8: src.includes('.m3u8'),
            referer: url
          });
        }
      });

      // Method 3: Look for iframes (might contain video URL)
      this.logger.debug('Searching for iframes...');
      $('iframe').each((_, element) => {
        const src = $(element).attr('src');
        if (src && !src.includes('ads') && !src.includes('analytics')) {
          this.logger.debug(`🔗 Found iframe: ${src}`);
          // Could recursively extract from iframe, but skip for now
        }
      });

      // Method 4: Look for data attributes
      $('[data-video], [data-source], [data-file]').each((_, element) => {
        const dataVideo = $(element).attr('data-video') || 
                         $(element).attr('data-source') || 
                         $(element).attr('data-file');
        if (dataVideo) {
          this.logger.success(`📹 Found in data attribute: ${dataVideo}`);
          links.push({
            url: dataVideo,
            name: 'PlayerEmbedAPI',
            quality: VideoQuality.UNKNOWN,
            isM3U8: dataVideo.includes('.m3u8'),
            referer: url
          });
        }
      });

      // Remove duplicates
      const uniqueLinks = links.filter((link, index, self) =>
        index === self.findIndex(l => l.url === link.url)
      );

      if (uniqueLinks.length === 0) {
        this.logger.error('No video sources found in HTML');
        this.logger.info('💡 The video URL might be loaded dynamically via JavaScript');
        this.logger.info('💡 Check playerembedapi-http.html for clues');
        return this.createErrorResult(url, 'No video sources found in HTML', startTime);
      }

      this.logger.success(`Extracted ${uniqueLinks.length} link(s)`);
      return this.createResult(url, uniqueLinks, [], startTime);

    } catch (error: any) {
      this.logger.error(`Extraction failed: ${error.message}`);
      return this.createErrorResult(url, error.message, startTime);
    }
  }

  /**
   * Try to follow sssrr.org redirect
   */
  async followSssrrRedirect(sssrrUrl: string, referer: string): Promise<string | null> {
    try {
      this.logger.debug(`Following redirect: ${sssrrUrl}`);
      const response = await HttpClient.get(sssrrUrl, referer, {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      });

      // Check for Location header (302 redirect)
      if (response.status === 302 && response.headers.location) {
        const redirectUrl = response.headers.location;
        this.logger.success(`→ Redirects to: ${redirectUrl}`);
        return redirectUrl;
      }

      // Check for meta refresh in HTML
      const $ = cheerio.load(response.data);
      const metaRefresh = $('meta[http-equiv="refresh"]').attr('content');
      if (metaRefresh) {
        const urlMatch = metaRefresh.match(/url=(.+)/i);
        if (urlMatch) {
          const redirectUrl = urlMatch[1];
          this.logger.success(`→ Meta refresh to: ${redirectUrl}`);
          return redirectUrl;
        }
      }

      return null;
    } catch (error: any) {
      this.logger.error(`Failed to follow redirect: ${error.message}`);
      return null;
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
