export { BaseExtractor } from './base';
export { MyVidPlayExtractor } from './myvidplay';
export { DoodStreamExtractor } from './doodstream';
export { MegaEmbedExtractor } from './megaembed';
export { ViewPlayerExtractor } from './viewplayer';
export { PlayerEmbedAPIExtractor } from './playerembedapi';

import { IExtractor } from '../types';
import { MyVidPlayExtractor } from './myvidplay';
import { DoodStreamExtractor } from './doodstream';
import { MegaEmbedExtractor } from './megaembed';
import { ViewPlayerExtractor } from './viewplayer';
import { PlayerEmbedAPIExtractor } from './playerembedapi';

/**
 * All available extractors
 */
export const ALL_EXTRACTORS: IExtractor[] = [
  new ViewPlayerExtractor(),
  new PlayerEmbedAPIExtractor(),
  new MyVidPlayExtractor(),
  new DoodStreamExtractor(),
  new MegaEmbedExtractor()
];

/**
 * Find extractor for URL
 */
export function findExtractor(url: string): IExtractor | null {
  return ALL_EXTRACTORS.find(extractor => extractor.domains.some(domain => url.includes(domain))) || null;
}
