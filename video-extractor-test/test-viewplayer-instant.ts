import { ViewPlayerInstantExtractor } from './src/extractors/viewplayer-instant';

async function test() {
  console.log('⚡ Testing INSTANT ViewPlayer Extraction\n');
  console.log('URL: https://viewplayer.online/filme/tt13893970');
  console.log('Strategy: Click immediately when elements are ready\n');
  console.log('='.repeat(60) + '\n');

  const extractor = new ViewPlayerInstantExtractor();
  
  const result = await extractor.extract('https://viewplayer.online/filme/tt13893970');
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULT:\n');
  console.log(JSON.stringify(result, null, 2));
  
  if (result.links.length > 0) {
    console.log('\n✅ SUCCESS!');
    console.log(`\n📹 Captured ${result.links.length} URL(s):`);
    result.links.forEach((link, i) => {
      console.log(`\n${i + 1}. ${link.url}`);
      console.log(`   Quality: ${link.quality}`);
    });
    console.log(`\n⏱️  Total time: ${result.extractionTime}ms`);
  } else {
    console.log('\n❌ FAILED');
  }
}

test().catch(console.error);
