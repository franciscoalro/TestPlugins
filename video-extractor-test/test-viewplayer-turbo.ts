import { ViewPlayerTurboExtractor } from './src/extractors/viewplayer-turbo';

async function test() {
  console.log('🚀 Testing TURBO ViewPlayer Extraction\n');
  console.log('URL: https://viewplayer.online/filme/tt13893970');
  console.log('Strategy: Maximum speed - stop as soon as first URL captured\n');
  console.log('='.repeat(60) + '\n');

  const extractor = new ViewPlayerTurboExtractor();
  
  const result = await extractor.extract('https://viewplayer.online/filme/tt13893970');
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULT:\n');
  
  if (result.links.length > 0) {
    console.log('✅ SUCCESS!\n');
    console.log(`📹 Captured ${result.links.length} URL(s):`);
    result.links.forEach((link, i) => {
      console.log(`\n${i + 1}. ${link.url}`);
      console.log(`   Quality: ${link.quality}`);
    });
    console.log(`\n⚡ Total time: ${result.extractionTime}ms`);
  } else {
    console.log('❌ FAILED');
    console.log(`Error: ${result.error}`);
  }
}

test().catch(console.error);
