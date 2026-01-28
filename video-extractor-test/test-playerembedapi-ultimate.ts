import { PlayerEmbedAPIUltimateExtractor } from './src/extractors/playerembedapi-ultimate';

async function test() {
  console.log('🎯 Testing PlayerEmbedAPI Ultimate Extractor\n');
  console.log('━'.repeat(60));
  console.log('Technique: Inject iframe context to bypass abyss.to');
  console.log('━'.repeat(60));
  console.log('');

  const extractor = new PlayerEmbedAPIUltimateExtractor();
  const url = 'https://playerembedapi.link/?v=KHT_sZqprG';
  const referer = 'https://viewplayer.online';

  const result = await extractor.extract(url, referer);

  console.log('\n' + '━'.repeat(60));
  if (result.success) {
    console.log('✅ SUCCESS!');
    console.log(`📹 Found ${result.links.length} link(s):\n`);
    result.links.forEach((link, i) => {
      console.log(`${i + 1}. ${link.url}`);
    });
  } else {
    console.log('❌ FAILED');
    console.log(`Error: ${result.error}`);
  }
  console.log('━'.repeat(60));
}

test().catch(console.error);
