import { PlayerEmbedAPIRealExtractor } from './src/extractors/playerembedapi-real';

async function test() {
  console.log('🔥 Testing puppeteer-real-browser (3 min timeout)\n');
  
  const extractor = new PlayerEmbedAPIRealExtractor();
  const result = await extractor.extract('https://playerembedapi.link/?v=NqXylpG9v', 'https://viewplayer.online');

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
