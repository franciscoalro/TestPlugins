import { IExtractor, ExtractorResult, ExtractorLink, SubtitleFile } from '../types';
import { Logger } from '../utils/logger';

/**
 * Base extractor class
 */
export abstract class BaseExtractor implements IExtractor {
  abstract name: string;
  abstract domains: string[];
  protected logger: Logger;

  constructor() {
    this.logger = new Logger(this.name);
  }

  /**
   * Check if URL matches this extractor
   */
  matches(url: string): boolean {
    return this.domains.some(domain => url.includes(domain));
  }

  /**
   * Extract video links from URL
   */
  abstract extract(url: string, referer?: string): Promise<ExtractorResult>;

  /**
   * Create success result
   */
  protected createResult(
    url: string,
    links: ExtractorLink[],
    subtitles: SubtitleFile[],
    startTime: number
  ): ExtractorResult {
    return {
      success: true,
      links,
      subtitles,
      extractorName: this.name,
      sourceUrl: url,
      extractionTime: Date.now() - startTime
    };
  }

  /**
   * Create error result
   */
  protected createErrorResult(url: string, error: string, startTime: number): ExtractorResult {
    return {
      success: false,
      links: [],
      subtitles: [],
      error,
      extractorName: this.name,
      sourceUrl: url,
      extractionTime: Date.now() - startTime
    };
  }
}
