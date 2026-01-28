import { PlayerEmbedAPIIframeExtractor } from './src/extractors/playerembedapi-iframe';

async function testPlayerEmbedAPIIframe() {
  console.log('🧪 Testing PlayerEmbedAPI Iframe Extractor\n');
  console.log('━'.repeat(60));
  console.log('URL: https://playerembedapi.link/?v=KHT_sZqprG');
  console.log('Method: Load in iframe to bypass abyss.to redirect');
  console.log('Goal: Extract video src from <video> element');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIIframeExtractor();
  const url = 'https://playerembedapi.link/?v=KHT_sZqprG';
  const referer = 'https://viewplayer.online';

  console.log('⏳ Starting extraction...');
  console.log('⚠️  Browser will open (headless=false for debugging)');
  console.log('');
  
  const result = await extractor.extract(url, referer);

  console.log('\n' + '━'.repeat(60));
  console.log('📊 RESULT');
  console.log('━'.repeat(60));
  
  if (result.success) {
    console.log('✅ Status: SUCCESS');
    console.log(`📹 Links found: ${result.links.length}`);
    console.log('');
    
    result.links.forEach((link, index) => {
      console.log(`Link ${index + 1}:`);
      console.log(`  URL: ${link.url}`);
      console.log(`  Quality: ${link.quality}`);
      console.log(`  Type: ${link.isM3U8 ? 'M3U8' : 'MP4'}`);
      console.log(`  Referer: ${link.referer}`);
      console.log('');
    });

    console.log('🎯 NEXT STEPS:');
    console.log('  1. Test URL in VLC or browser');
    console.log('  2. Port logic to Kotlin (MaxSeriesProvider)');
    console.log('  3. Use WebView to load iframe');
    console.log('  4. Extract video src from WebView');
  } else {
    console.log('❌ Status: FAILED');
    console.log(`Error: ${result.error}`);
    console.log('');
    console.log('💡 Check screenshots:');
    console.log('  - playerembedapi-iframe-debug.png');
    console.log('  - playerembedapi-iframe-error.png');
  }

  console.log('━'.repeat(60));
  console.log(`⏱️  Duration: ${result.duration}ms`);
  console.log('━'.repeat(60));
}

testPlayerEmbedAPIIframe().catch(console.error);
