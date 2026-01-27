import { ALL_EXTRACTORS } from './extractors';
import { TestResult } from './types';
import { Logger } from './utils/logger';
import * as fs from 'fs';

const logger = new Logger('TestAll');

/**
 * Test URLs for each extractor
 */
const TEST_URLS: Record<string, { url: string; referer?: string }[]> = {
  'MyVidPlay': [
    { url: 'https://myvidplay.com/e/example1' },
    { url: 'https://myvidplay.com/e/example2' }
  ],
  'DoodStream': [
    { url: 'https://doodstream.com/e/example1' },
    { url: 'https://dood.to/e/example2' }
  ],
  'MegaEmbed': [
    { url: 'https://megaembed.link/#example1' }
  ]
};

/**
 * Run all tests
 */
async function runAllTests() {
  logger.info('🚀 Starting extractor tests...\n');
  
  const results: TestResult[] = [];
  let totalTests = 0;
  let passedTests = 0;

  for (const extractor of ALL_EXTRACTORS) {
    logger.info(`\n${'='.repeat(60)}`);
    logger.info(`Testing: ${extractor.name}`);
    logger.info('='.repeat(60));

    const testUrls = TEST_URLS[extractor.name] || [];
    
    if (testUrls.length === 0) {
      logger.warn(`No test URLs configured for ${extractor.name}`);
      continue;
    }

    for (const { url, referer } of testUrls) {
      totalTests++;
      logger.info(`\nTest ${totalTests}: ${url}`);
      
      try {
        const result = await extractor.extract(url, referer);
        
        const testResult: TestResult = {
          extractor: extractor.name,
          url,
          success: result.success,
          linksFound: result.links.length,
          subtitlesFound: result.subtitles.length,
          extractionTime: result.extractionTime,
          error: result.error,
          links: result.links
        };

        results.push(testResult);

        if (result.success) {
          passedTests++;
          logger.success(`✅ PASSED - ${result.links.length} link(s) found in ${result.extractionTime}ms`);
        } else {
          logger.error(`❌ FAILED - ${result.error}`);
        }

      } catch (error: any) {
        logger.error(`❌ EXCEPTION - ${error.message}`);
        results.push({
          extractor: extractor.name,
          url,
          success: false,
          linksFound: 0,
          subtitlesFound: 0,
          extractionTime: 0,
          error: error.message
        });
      }
    }
  }

  // Summary
  logger.info(`\n${'='.repeat(60)}`);
  logger.info('TEST SUMMARY');
  logger.info('='.repeat(60));
  logger.info(`Total tests: ${totalTests}`);
  logger.info(`Passed: ${passedTests} (${Math.round(passedTests / totalTests * 100)}%)`);
  logger.info(`Failed: ${totalTests - passedTests}`);

  // Save results to JSON
  const outputPath = './test-results.json';
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  logger.info(`\n📄 Results saved to: ${outputPath}`);

  return results;
}

// Run tests
if (require.main === module) {
  runAllTests()
    .then(() => {
      logger.success('\n✅ All tests completed');
      process.exit(0);
    })
    .catch(error => {
      logger.error(`\n❌ Test suite failed: ${error.message}`);
      process.exit(1);
    });
}

export { runAllTests };
