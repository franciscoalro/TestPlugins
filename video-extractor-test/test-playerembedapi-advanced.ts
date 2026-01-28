import { PlayerEmbedAPIAdvancedExtractor } from './src/extractors/playerembedapi-advanced';

async function testPlayerEmbedAPIAdvanced() {
  console.log('🚀 Testing PlayerEmbedAPI Advanced Extractor\n');
  console.log('━'.repeat(60));
  console.log('URL: https://playerembedapi.link/?v=KHT_sZqprG');
  console.log('Method: Puppeteer-extra + Stealth plugins');
  console.log('Features:');
  console.log('  - Anti-detection plugins');
  console.log('  - AdBlocker');
  console.log('  - Network interception');
  console.log('  - CDP (Chrome DevTools Protocol)');
  console.log('  - DOM extraction from iframe');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIAdvancedExtractor();
  const url = 'https://playerembedapi.link/?v=KHT_sZqprG';
  const referer = 'https://viewplayer.online';

  console.log('⏳ Starting extraction...');
  console.log('⚠️  Browser will open (headless=false for debugging)');
  console.log('⏱️  This may take 20-30 seconds...');
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
    console.log('  2. Port logic to Kotlin');
    console.log('  3. Implement in MaxSeriesProvider');
  } else {
    console.log('❌ Status: FAILED');
    console.log(`Error: ${result.error}`);
    console.log('');
    console.log('💡 Debug files:');
    console.log('  - playerembedapi-advanced-debug.png');
    console.log('  - playerembedapi-advanced-requests.json');
  }

  console.log('━'.repeat(60));
  console.log(`⏱️  Duration: ${result.duration}ms`);
  console.log('━'.repeat(60));
}

testPlayerEmbedAPIAdvanced().catch(console.error);
