import { PlayerEmbedAPIHttpExtractor } from './src/extractors/playerembedapi-http';

async function testPlayerEmbedAPIHttp() {
  console.log('🧪 Testing PlayerEmbedAPI HTTP-only Extractor\n');
  console.log('━'.repeat(60));
  console.log('URL: https://playerembedapi.link/?v=NUHegbGwJ');
  console.log('Method: HTTP-only (no browser automation)');
  console.log('Goal: Extract video URLs from HTML without triggering anti-bot');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIHttpExtractor();
  const url = 'https://playerembedapi.link/?v=NUHegbGwJ';
  const referer = 'https://maxseries.pics';

  console.log('⏳ Starting extraction...\n');
  
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
      console.log('');
    });
  } else {
    console.log('❌ Status: FAILED');
    console.log(`Error: ${result.error}`);
    console.log('');
    console.log('💡 Next steps:');
    console.log('  1. Check playerembedapi-http.html for patterns');
    console.log('  2. Look for obfuscated JavaScript');
    console.log('  3. Search for API endpoints');
    console.log('  4. Consider reverse engineering the JS');
  }

  console.log('━'.repeat(60));
  console.log(`⏱️  Duration: ${result.duration}ms`);
  console.log('━'.repeat(60));
}

testPlayerEmbedAPIHttp().catch(console.error);
