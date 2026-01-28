import { PlayerEmbedAPIDebugExtractor } from './src/extractors/playerembedapi-debug';

async function test() {
  console.log('🔍 Testing PlayerEmbedAPI Debug Mode\n');
  console.log('URL: https://playerembedapi.link/?v=PtWmll25F');
  console.log('Will inspect page structure and save debug files\n');
  console.log('='.repeat(60) + '\n');

  const extractor = new PlayerEmbedAPIDebugExtractor();
  
  const result = await extractor.extract('https://playerembedapi.link/?v=PtWmll25F');
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULT:\n');
  console.log(JSON.stringify(result, null, 2));
  
  console.log('\n📁 Check these files:');
  console.log('  - playerembedapi-debug.html');
  console.log('  - playerembedapi-debug-1.png');
  console.log('  - playerembedapi-debug-2.png');
}

test().catch(console.error);
