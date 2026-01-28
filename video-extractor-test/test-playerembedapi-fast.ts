import { PlayerEmbedAPIFastExtractor } from './src/extractors/playerembedapi-fast';

async function test() {
  console.log('🚀 Testing PlayerEmbedAPI Fast Extractor\n');
  console.log('URL: https://playerembedapi.link/?v=PtWmll25F');
  console.log('Strategy: Click as soon as elements are ready\n');
  console.log('='.repeat(60) + '\n');

  const extractor = new PlayerEmbedAPIFastExtractor();
  
  const result = await extractor.extract('https://playerembedapi.link/?v=PtWmll25F');
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULT:\n');
  console.log(JSON.stringify(result, null, 2));
  
  if (result.links.length > 0) {
    console.log('\n✅ SUCCESS!');
    console.log(`\n📹 Captured ${result.links.length} URL(s):`);
    result.links.forEach((link, i) => {
      console.log(`\n${i + 1}. ${link.url}`);
      console.log(`   Quality: ${link.quality}`);
      console.log(`   M3U8: ${link.isM3U8}`);
    });
  } else {
    console.log('\n❌ FAILED - No URLs captured');
  }
}

test().catch(console.error);
