import { MyVidPlayExtractor } from './src/extractors/myvidplay';
import { Logger } from './src/utils/logger';

const logger = new Logger('TestMyVidPlay');

/**
 * Test MyVidPlay with real URL from ViewPlayer
 */
async function testMyVidPlay() {
  logger.info('🚀 Testing MyVidPlay Extractor');
  logger.info('URL extracted from ViewPlayer\n');

  const extractor = new MyVidPlayExtractor();
  
  // Real URL from ViewPlayer
  const testUrl = 'https://myvidplay.com/e/l1tmmzzjcmv1';
  const referer = 'https://viewplayer.online/filme/tt39376546';

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
        if (link.referer) logger.info(`  Referer: ${link.referer}`);
        if (link.headers) logger.info(`  Headers: ${JSON.stringify(link.headers, null, 2)}`);
        logger.info('');
      });

      // Test if M3U8 is accessible
      if (result.links.length > 0 && result.links[0].isM3U8) {
        logger.info('🎬 M3U8 URL found! You can test it with:');
        logger.info(`   VLC: vlc "${result.links[0].url}"`);
        logger.info(`   FFmpeg: ffmpeg -i "${result.links[0].url}" -c copy output.mp4\n`);
      }

    } else {
      logger.error(`\n❌ EXTRACTION FAILED`);
      logger.error(`Error: ${result.error}`);
      logger.error(`Extraction time: ${result.extractionTime}ms`);
    }

  } catch (error: any) {
    logger.error(`\n❌ TEST FAILED`);
    logger.error(`Error: ${error.message}`);
  }
}

// Run test
testMyVidPlay()
  .then(() => {
    logger.success('\n✅ Test completed');
    process.exit(0);
  })
  .catch(error => {
    logger.error(`\n❌ Test failed: ${error.message}`);
    process.exit(1);
  });
