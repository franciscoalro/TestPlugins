import { PlayerEmbedAPIFinalExtractor } from './src/extractors/playerembedapi-final';

async function test() {
  console.log('🔥 Testing PlayerEmbedAPI Final Extractor\n');
  console.log('━'.repeat(60));
  console.log('Techniques:');
  console.log('  ✅ Block DevTools detection');
  console.log('  ✅ Block security alert iframe');
  console.log('  ✅ Fake iframe context');
  console.log('  ✅ Auto-click play overlay');
  console.log('  ✅ Block ads and tracking');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIFinalExtractor();
  const url = 'https://playerembedapi.link/?v=KHT_sZqprG';
  const referer = 'https://viewplayer.online';

  console.log('⏳ Starting extraction (20-30 seconds)...\n');

  const result = await extractor.extract(url, referer);

  console.log('\n' + '━'.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS!');
    console.log(`📹 Found ${result.links.length} link(s):\n`);
    result.links.forEach((link, i) => {
      console.log(`${i + 1}. ${link.url}`);
      console.log(`   Quality: ${link.quality}`);
      console.log(`   Type: ${link.isM3U8 ? 'M3U8' : 'MP4'}`);
      console.log('');
    });
  } else {
    console.log('❌ FAILED');
    console.log(`Error: ${result.error}`);
  }
  console.log('━'.repeat(60));
}

test().catch(console.error);
