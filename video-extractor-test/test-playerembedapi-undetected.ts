import { PlayerEmbedAPIUndetectedExtractor } from './src/extractors/playerembedapi-undetected';

async function test() {
  console.log('🥷 Testing PlayerEmbedAPI Undetected Mode\n');
  console.log('URL: https://playerembedapi.link/?v=PtWmll25F');
  console.log('Strategy: Maximum evasion + ViewPlayer referer\n');
  console.log('='.repeat(60) + '\n');

  const extractor = new PlayerEmbedAPIUndetectedExtractor();
  
  const result = await extractor.extract('https://playerembedapi.link/?v=PtWmll25F');
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULT:\n');
  console.log(JSON.stringify(result, null, 2));
  
  if (result.links.length > 0) {
    console.log('\n✅ SUCCESS!');
    result.links.forEach((link, i) => {
      console.log(`\n${i + 1}. ${link.url}`);
    });
  } else {
    console.log('\n❌ FAILED');
  }
}

test().catch(console.error);
