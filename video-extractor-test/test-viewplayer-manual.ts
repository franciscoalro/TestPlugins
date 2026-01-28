import { ViewPlayerManualExtractor } from './src/extractors/viewplayer-manual';

async function test() {
  console.log('👆 MANUAL MODE - You click, I capture!\n');
  
  const extractor = new ViewPlayerManualExtractor();
  const result = await extractor.extract('https://viewplayer.online/filme/tt13893970');

  console.log('\n' + '='.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS!');
    console.log(`📹 Captured ${result.links.length} URL(s):\n`);
    result.links.forEach((l, i) => {
      console.log(`${i + 1}. ${l.url}`);
      console.log(`   Quality: ${l.quality}`);
      console.log('');
    });
  } else {
    console.log('❌ FAILED:', result.error);
  }
  console.log('='.repeat(60));
}

test().catch(console.error);
