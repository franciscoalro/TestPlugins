import axios, { AxiosRequestConfig } from 'axios';

/**
 * Standard headers for requests
 */
export const STANDARD_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
  'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
  'Accept-Encoding': 'gzip, deflate, br',
  'DNT': '1',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Cache-Control': 'max-age=0'
};

/**
 * HTTP client with standard configuration
 */
export class HttpClient {
  /**
   * GET request
   */
  static async get(url: string, referer?: string, customHeaders?: Record<string, string>) {
    const headers = {
      ...STANDARD_HEADERS,
      ...(referer && { 'Referer': referer }),
      ...customHeaders
    };

    const config: AxiosRequestConfig = {
      headers,
      timeout: 30000,
      maxRedirects: 5,
      validateStatus: (status) => status < 500
    };

    return axios.get(url, config);
  }

  /**
   * POST request
   */
  static async post(url: string, data: any, referer?: string, customHeaders?: Record<string, string>) {
    const headers = {
      ...STANDARD_HEADERS,
      'Content-Type': 'application/json',
      ...(referer && { 'Referer': referer }),
      ...customHeaders
    };

    const config: AxiosRequestConfig = {
      headers,
      timeout: 30000,
      maxRedirects: 5,
      validateStatus: (status) => status < 500
    };

    return axios.post(url, data, config);
  }
}
