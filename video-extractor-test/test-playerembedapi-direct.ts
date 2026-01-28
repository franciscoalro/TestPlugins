import { PlayerEmbedAPIRealExtractor } from './src/extractors/playerembedapi-real';

async function test() {
  console.log('🔥 Testing PlayerEmbedAPI Direct Link\n');
  console.log('URL: https://playerembedapi.link/?v=PtWmll25F');
  console.log('');
  
  const extractor = new PlayerEmbedAPIRealExtractor();
  const result = await extractor.extract(
    'https://playerembedapi.link/?v=PtWmll25F',
    'https://viewplayer.online'
  );

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
