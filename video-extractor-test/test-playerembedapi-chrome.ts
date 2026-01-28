import { PlayerEmbedAPIChromeExtractor } from './src/extractors/playerembedapi-chrome';

async function test() {
  const extractor = new PlayerEmbedAPIChromeExtractor();
  const result = await extractor.extract(
    'https://playerembedapi.link/?v=KHT_sZqprG',
    'https://viewplayer.online'
  );

  console.log('\n' + '='.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS');
    result.links.forEach((l, i) => console.log(`${i + 1}. ${l.url}`));
  } else {
    console.log('❌ FAILED:', result.error);
  }
  console.log('='.repeat(60));
}

test().catch(console.error);
