import { PlayerEmbedAPIExtractor } from './src/extractors/playerembedapi';
import { Logger } from './src/utils/logger';

const logger = new Logger('TestPlayerEmbedAPI');

/**
 * Test PlayerEmbedAPI with real URL from ViewPlayer
 */
async function testPlayerEmbedAPI() {
  logger.info('🚀 Testing PlayerEmbedAPI Extractor');
  logger.info('URL extracted from ViewPlayer\n');

  const extractor = new PlayerEmbedAPIExtractor();
  
  // Real URL from ViewPlayer
  const testUrl = 'https://playerembedapi.link/?v=NUHegbGwJ';
  const referer = 'https://viewplayer.online/filme/tt39376546';

  logger.info(`Testing URL: ${testUrl}`);
  logger.info(`Referer: ${referer}\n`);

  logger.warn('⚠️  IMPORTANT:');
  logger.warn('   - Browser will open in visible mode');
  logger.warn('   - You may need to click overlays to remove them');
  logger.warn('   - Wait for video to start loading');
  logger.warn('   - Network requests will be captured automatically\n');

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
        logger.info('');
      });

      // Show how to test the URLs
      if (result.links.length > 0) {
        const firstLink = result.links[0];
        logger.info('🎬 How to test this URL:\n');
        
        if (firstLink.isM3U8) {
          logger.info('VLC Player:');
          logger.info(`  vlc "${firstLink.url}"\n`);
          
          logger.info('FFmpeg (download):');
          logger.info(`  ffmpeg -i "${firstLink.url}" -c copy output.mp4\n`);
          
          logger.info('cURL (test):');
          logger.info(`  curl -I "${firstLink.url}"\n`);
        } else {
          logger.info('Browser:');
          logger.info(`  Open: ${firstLink.url}\n`);
          
          logger.info('wget (download):');
          logger.info(`  wget "${firstLink.url}" -O video.mp4\n`);
        }
      }

      // Save results to file
      const fs = require('fs');
      const resultsPath = 'playerembedapi-results.json';
      fs.writeFileSync(resultsPath, JSON.stringify(result, null, 2));
      logger.info(`💾 Results saved to: ${resultsPath}`);

    } else {
      logger.error(`\n❌ EXTRACTION FAILED`);
      logger.error(`Error: ${result.error}`);
      logger.error(`Extraction time: ${result.extractionTime}ms`);
      
      logger.info('\n🔍 Troubleshooting:');
      logger.info('   1. Check if site is accessible');
      logger.info('   2. Try clicking overlays manually');
      logger.info('   3. Check screenshot: playerembedapi-screenshot.png');
      logger.info('   4. Increase timeout if needed');
    }

  } catch (error: any) {
    logger.error(`\n❌ TEST FAILED`);
    logger.error(`Error: ${error.message}`);
    logger.error(`Stack: ${error.stack}`);
  }
}

// Run test
testPlayerEmbedAPI()
  .then(() => {
    logger.success('\n✅ Test completed');
    process.exit(0);
  })
  .catch(error => {
    logger.error(`\n❌ Test failed: ${error.message}`);
    process.exit(1);
  });
