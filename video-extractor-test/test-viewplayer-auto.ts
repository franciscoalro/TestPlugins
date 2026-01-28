import { ViewPlayerAutoExtractor } from './src/extractors/viewplayer-auto';

async function test() {
  console.log('🤖 Testing Automated ViewPlayer Extraction\n');
  console.log('This will:');
  console.log('  1. Load ViewPlayer');
  console.log('  2. Click PlayerEmbedAPI button');
  console.log('  3. Close popups');
  console.log('  4. Click play');
  console.log('  5. Capture video URL');
  console.log('');
  
  const extractor = new ViewPlayerAutoExtractor();
  const result = await extractor.extract('https://viewplayer.online/filme/tt13893970');

  console.log('\n' + '='.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS!');
    console.log(`📹 Captured ${result.links.length} URL(s):\n`);
    result.links.forEach((l, i) => {
      console.log(`${i + 1}. ${l.url}`);
      console.log(`   Quality: ${l.quality}`);
      console.log(`   Type: ${l.isM3U8 ? 'M3U8' : 'MP4'}`);
      console.log('');
    });
    
    console.log('🎯 NEXT STEPS:');
    console.log('  1. Test URL in VLC');
    console.log('  2. Port to Kotlin (MaxSeriesProvider)');
    console.log('  3. Use WebView to replicate this flow');
  } else {
    console.log('❌ FAILED:', result.error);
  }
  console.log('='.repeat(60));
  console.log(`⏱️  Duration: ${result.duration}ms`);
  console.log('='.repeat(60));
}

test().catch(console.error);
