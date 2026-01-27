import { findExtractor, ALL_EXTRACTORS } from './extractors';
import { Logger } from './utils/logger';

const logger = new Logger('Main');

/**
 * Test a single URL
 */
export async function testUrl(url: string, referer?: string) {
  logger.info(`Testing URL: ${url}`);
  
  const extractor = findExtractor(url);
  
  if (!extractor) {
    logger.error('No extractor found for this URL');
    return null;
  }

  logger.info(`Using extractor: ${extractor.name}`);
  
  const result = await extractor.extract(url, referer);
  
  if (result.success) {
    logger.success(`✅ Extraction successful!`);
    logger.info(`Links found: ${result.links.length}`);
    logger.info(`Extraction time: ${result.extractionTime}ms`);
    
    result.links.forEach((link, index) => {
      logger.info(`\nLink ${index + 1}:`);
      logger.info(`  URL: ${link.url}`);
      logger.info(`  Quality: ${link.quality}`);
      logger.info(`  M3U8: ${link.isM3U8}`);
      if (link.referer) logger.info(`  Referer: ${link.referer}`);
    });
  } else {
    logger.error(`❌ Extraction failed: ${result.error}`);
  }
  
  return result;
}

/**
 * List all available extractors
 */
export function listExtractors() {
  logger.info('Available extractors:');
  ALL_EXTRACTORS.forEach((extractor, index) => {
    logger.info(`\n${index + 1}. ${extractor.name}`);
    logger.info(`   Domains: ${extractor.domains.join(', ')}`);
  });
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    logger.info('Usage:');
    logger.info('  npm run dev <url> [referer]');
    logger.info('  npm run dev list');
    logger.info('\nExamples:');
    logger.info('  npm run dev https://myvidplay.com/e/abc123');
    logger.info('  npm run dev https://doodstream.com/e/xyz789');
    logger.info('  npm run dev list');
    process.exit(0);
  }
  
  if (args[0] === 'list') {
    listExtractors();
  } else {
    const url = args[0];
    const referer = args[1];
    testUrl(url, referer).then(() => {
      logger.info('\n✅ Test completed');
      process.exit(0);
    }).catch(error => {
      logger.error(`Test failed: ${error.message}`);
      process.exit(1);
    });
  }
}
