import { ViewPlayerAutoExtractor } from './src/extractors/viewplayer-auto';

async function test() {
  console.log('🚀 Testing NEW URL via ViewPlayer\n');
  console.log('PlayerEmbedAPI ID: PtWmll25F');
  console.log('Strategy: Load through ViewPlayer (working method)\n');
  console.log('='.repeat(60) + '\n');

  // Need to find the ViewPlayer URL for this video
  // For now, let's test if we can extract the ID pattern
  
  console.log('⚠️  Need ViewPlayer URL that contains PlayerEmbedAPI button');
  console.log('Example: https://viewplayer.online/filme/tt13893970');
  console.log('\nPlease provide the ViewPlayer URL that has this PlayerEmbedAPI video');
}

test().catch(console.error);
