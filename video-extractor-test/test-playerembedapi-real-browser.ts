import { PlayerEmbedAPIRealBrowserExtractor } from './src/extractors/playerembedapi-real-browser';

async function test() {
  console.log('🔥 Testing PlayerEmbedAPI Real Browser (Undetectable)\n');
  console.log('━'.repeat(60));
  console.log('Using: puppeteer-real-browser');
  console.log('Features: Complete anti-detection, real Chrome profile');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIRealBrowserExtractor();
  const url = 'https://playerembedapi.link/?v=KHT_sZqprG';
  const referer = 'https://viewplayer.online';

  console.log('⏳ Starting (may take 30-40 seconds)...\n');

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
  console.log(`Duration: ${result.duration}ms`);
  console.log('━'.repeat(60));
}

test().catch(console.error);
