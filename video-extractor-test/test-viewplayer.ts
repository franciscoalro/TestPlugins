import { ViewPlayerExtractor } from './src/extractors/viewplayer';
import { Logger } from './src/utils/logger';

const logger = new Logger('TestViewPlayer');

/**
 * Test ViewPlayer with real URL from network logs
 */
async function testViewPlayer() {
  logger.info('🚀 Testing ViewPlayer Extractor');
  logger.info('Based on network logs analysis\n');

  const extractor = new ViewPlayerExtractor();
  
  // URL from network logs
  const testUrl = 'https://viewplayer.online/filme/tt39376546';
  const referer = 'https://maxseries.pics';

  logger.info(`Testing URL: ${testUrl}`);
  logger.info(`Referer: ${referer}\n`);

  try {
    const result = await extractor.extract(testUrl, referer);

    if (result.success) {
      logger.success(`\n✅ EXTRACTION SUCCESSFUL!`);
      logger.info(`Extraction time: ${result.extractionTime}ms`);
      logger.info(`Links found: ${result.links.length}\n`);

      result.links.forEach((link, index) => {
        logger.info(`Link ${index + 1}:`);
        logger.info(`  Name: ${link.name}`);
        logger.info(`  URL: ${link.url}`);
        logger.info(`  Quality: ${link.quality}`);
        logger.info(`  M3U8: ${link.isM3U8}`);
        logger.info(`  Referer: ${link.referer}\n`);
      });

      // Test following redirects for sssrr.org URLs
      const sssrrLinks = result.links.filter(link => link.url.includes('sssrr.org'));
      if (sssrrLinks.length > 0) {
        logger.info('\n🔄 Testing redirects for sssrr.org URLs...\n');
        
        for (const link of sssrrLinks) {
          logger.info(`Following: ${link.url}`);
          const redirectUrl = await extractor.followRedirect(link.url, testUrl);
          if (redirectUrl) {
            logger.success(`  → Redirects to: ${redirectUrl}\n`);
          } else {
            logger.warn(`  → No redirect found\n`);
          }
        }
      }

      // Test following redirects for CloudFlare URLs
      const cfLinks = result.links.filter(link => link.url.includes('trycloudflare.com'));
      if (cfLinks.length > 0) {
        logger.info('\n🔄 Testing redirects for CloudFlare URLs...\n');
        
        for (const link of cfLinks) {
          logger.info(`Following: ${link.url}`);
          const redirectUrl = await extractor.followRedirect(link.url, testUrl);
          if (redirectUrl) {
            logger.success(`  → Redirects to: ${redirectUrl}\n`);
          } else {
            logger.warn(`  → No redirect found\n`);
          }
        }
      }

    } else {
      logger.error(`\n❌ EXTRACTION FAILED`);
      logger.error(`Error: ${result.error}`);
      logger.error(`Extraction time: ${result.extractionTime}ms`);
    }

  } catch (error: any) {
    logger.error(`\n❌ TEST FAILED`);
    logger.error(`Error: ${error.message}`);
    logger.error(`Stack: ${error.stack}`);
  }
}

// Run test
testViewPlayer()
  .then(() => {
    logger.success('\n✅ Test completed');
    process.exit(0);
  })
  .catch(error => {
    logger.error(`\n❌ Test failed: ${error.message}`);
    process.exit(1);
  });
