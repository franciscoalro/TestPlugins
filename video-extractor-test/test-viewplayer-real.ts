import { ViewPlayerRealExtractor } from './src/extractors/viewplayer-real';

async function test() {
  console.log('🎬 Testing ViewPlayer Real (3 min)\n');
  
  const extractor = new ViewPlayerRealExtractor();
  const result = await extractor.extract('https://viewplayer.online/filme/tt13893970');

  console.log('\n' + '='.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS!');
    result.links.forEach((l, i) => console.log(`${i + 1}. ${l.url}`));
  } else {
    console.log('❌ FAILED:', result.error);
  }
  console.log('='.repeat(60));
}

test().catch(console.error);
