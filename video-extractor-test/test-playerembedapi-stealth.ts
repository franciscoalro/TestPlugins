import { PlayerEmbedAPIStealthExtractor } from './src/extractors/playerembedapi-stealth';
import { Logger } from './src/utils/logger';

const logger = new Logger('TestPlayerEmbedAPI-Stealth');

/**
 * Test PlayerEmbedAPI with STEALTH mode
 * Advanced anti-detection to bypass abyss.to redirect
 */
async function testPlayerEmbedAPIStealth() {
  logger.info('🥷 Testing PlayerEmbedAPI with STEALTH MODE');
  logger.info('Advanced anti-detection techniques enabled\n');

  const extractor = new PlayerEmbedAPIStealthExtractor();
  
  const testUrl = 'https://playerembedapi.link/?v=NUHegbGwJ';
  const referer = 'https://viewplayer.online/filme/tt39376546';

  logger.info(`Testing URL: ${testUrl}`);
  logger.info(`Referer: ${referer}\n`);

  logger.warn('🔧 STEALTH FEATURES:');
  logger.warn('   ✓ navigator.webdriver = undefined');
  logger.warn('   ✓ window.chrome injected');
  logger.warn('   ✓ Real Chrome user agent');
  logger.warn('   ✓ Realistic viewport (1920x1080)');
  logger.warn('   ✓ Brazil geolocation');
  logger.warn('   ✓ Portuguese locale');
  logger.warn('   ✓ Mouse movement simulation');
  logger.warn('   ✓ Random delays');
  logger.warn('   ✓ Native function toString override\n');

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

      // Show how to test
      if (result.links.length > 0) {
        const firstLink = result.links[0];
        logger.info('🎬 Test this URL:\n');
        
        if (firstLink.isM3U8) {
          logger.info('VLC:');
          logger.info(`  vlc "${firstLink.url}"\n`);
          
          logger.info('FFmpeg:');
          logger.info(`  ffmpeg -i "${firstLink.url}" -c copy output.mp4\n`);
        }
      }

      // Save results
      const fs = require('fs');
      fs.writeFileSync('playerembedapi-stealth-results.json', JSON.stringify(result, null, 2));
      logger.info(`💾 Results saved to: playerembedapi-stealth-results.json`);

    } else {
      logger.error(`\n❌ EXTRACTION FAILED`);
      logger.error(`Error: ${result.error}`);
      logger.error(`Extraction time: ${result.extractionTime}ms`);
      
      logger.info('\n🔍 Debug files created:');
      logger.info('   - playerembedapi-final.png (screenshot)');
      logger.info('   - playerembedapi-page.html (page source)');
      
      if (result.error?.includes('abyss.to')) {
        logger.error('\n❌ STILL DETECTED!');
        logger.error('Anti-bot is very strong. Possible solutions:');
        logger.error('   1. Use residential proxy');
        logger.error('   2. Use real browser profile');
        logger.error('   3. Add more delays');
        logger.error('   4. Try different user agent');
        logger.error('   5. Use undetected-chromedriver');
      }
    }

  } catch (error: any) {
    logger.error(`\n❌ TEST FAILED`);
    logger.error(`Error: ${error.message}`);
  }
}

// Run test
testPlayerEmbedAPIStealth()
  .then(() => {
    logger.success('\n✅ Test completed');
    process.exit(0);
  })
  .catch(error => {
    logger.error(`\n❌ Test failed: ${error.message}`);
    process.exit(1);
  });
