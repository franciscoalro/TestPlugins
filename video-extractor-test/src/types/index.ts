/**
 * Video quality types
 */
export enum VideoQuality {
  Q360 = "360p",
  Q480 = "480p",
  Q720 = "720p",
  Q1080 = "1080p",
  Q1440 = "1440p",
  Q4K = "4K",
  UNKNOWN = "Unknown"
}

/**
 * Extractor link result
 */
export interface ExtractorLink {
  url: string;
  name: string;
  quality: VideoQuality;
  isM3U8: boolean;
  headers?: Record<string, string>;
  referer?: string;
}

/**
 * Subtitle file
 */
export interface SubtitleFile {
  url: string;
  lang: string;
}

/**
 * Extractor result
 */
export interface ExtractorResult {
  success: boolean;
  links: ExtractorLink[];
  subtitles: SubtitleFile[];
  error?: string;
  extractorName: string;
  sourceUrl: string;
  extractionTime: number; // milliseconds
}

/**
 * Base extractor interface
 */
export interface IExtractor {
  name: string;
  domains: string[];
  extract(url: string, referer?: string): Promise<ExtractorResult>;
}

/**
 * Test result
 */
export interface TestResult {
  extractor: string;
  url: string;
  success: boolean;
  linksFound: number;
  subtitlesFound: number;
  extractionTime: number;
  error?: string;
  links?: ExtractorLink[];
}
