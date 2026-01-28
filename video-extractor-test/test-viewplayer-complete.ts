import { ViewPlayerCompleteExtractor } from './src/extractors/viewplayer-complete';

async function test() {
  console.log('🎬 Testing ViewPlayer Complete Extractor\n');
  console.log('━'.repeat(60));
  console.log('URL: https://viewplayer.online/filme/tt39376546');
  console.log('Strategy: Extract all PlayerEmbedAPI sources from buttons');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new ViewPlayerCompleteExtractor();
  const url = 'https://viewplayer.online/filme/tt39376546';
  const referer = 'https://maxseries.pics';

  console.log('⏳ Starting extraction...');
  console.log('⚠️  This may take 1-2 minutes (multiple sources)');
  console.log('');

  const result = await extractor.extract(url, referer);

  console.log('\n' + '━'.repeat(60));
  console.log('📊 FINAL RESULT');
  console.log('━'.repeat(60));
  
  if (result.success) {
    console.log('✅ SUCCESS!');
    console.log(`📹 Extracted ${result.links.length} video URL(s):\n`);
    
    result.links.forEach((link, i) => {
      console.log(`${i + 1}. ${link.name}`);
      console.log(`   URL: ${link.url}`);
      console.log(`   Quality: ${link.quality}`);
      console.log(`   Type: ${link.isM3U8 ? 'M3U8' : 'MP4'}`);
      console.log('');
    });

    console.log('🎯 NEXT STEPS:');
    console.log('  1. Test URLs in VLC');
    console.log('  2. Port to Kotlin (MaxSeriesProvider)');
    console.log('  3. Use WebView to load ViewPlayer');
    console.log('  4. Extract data-source from buttons');
    console.log('  5. Load each in iframe and capture sssrr.org URLs');
  } else {
    console.log('❌ FAILED');
    console.log(`Error: ${result.error}`);
  }

  console.log('━'.repeat(60));
  console.log(`⏱️  Total duration: ${result.duration}ms`);
  console.log('━'.repeat(60));
}

test().catch(console.error);
