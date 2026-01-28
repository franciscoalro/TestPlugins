/**
 * Decode PlayerEmbedAPI base64 data
 * Extract video URL from the encoded JSON
 */

const base64Data = "eyJzbHVnIjoiTlVIZWdiR3dKIiwibWQ1X2lkIjoyOTA4NTg2MiwidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6IkZcdTAwMTbjPk2hnr/lXcFcdTAwMDQ5mIc2RD6QfZlzw2qLI1JA3E9nRNFkTEWEttBcdTAwMTVLwkucinCdUu6ZmLf0cEHEwNHZhLKbzNfKLFx1MDAxN/tXQos7nlx1MDAxMFx1MDAxZVxyPWqvaLZcZlxi0sWG4qmJqFrW/FGvRK2g+Vx1MDAxMugjv8NOQr2EIWFTXHUwMDBieVx1MDAxNjxcdTAwMTDlprfrXFxcdTAwMDHKXHUwMDAxQZB8w83qXHUwMDFj9iWFi1x1MDAxMWwjMFxm/8+ZgjQ2iO3C9qHwXHUwMDFhWDjn41x1MDAwZrBcdTAwMDa6hbBXY5ZcdTAwMWIrQFx1MDAxZCg/f1KtMu6G94JF1ppcdTAwMDcmROKWQFx1MDAxM8lPXHUwMDEx2V3okbKF9Fx1MDAxN2dcdTAwMGViuK64v8xTsyxcdTAwMTOzb97SXHUwMDA1k9EhtSjnXHUwMDBi6ed55tuCXHUwMDFh1+45WYeFvWYkdj7NR1x1MDAwMdkhXHUwMDEw+3asYmrbXCLqLGi6XHUwMDE1TEVO0tD7Nlx0XHUwMDE5uGa21omgsoFLO9nLXHUwMDEw6JT5XHUwMDBma9pEUu9cXMa8nYFUg7HO0cnG4YKl6MU7eszayndcIuucquJ/+oTUi1qKTlx1MDAwNMD4Lfe5QEwwXHUwMDA39b3kh7DAzLfWjF0qwqD5XHUwMDA2PVEyifg191x1MDAwN2jhgFx1MDAxYiW0wqbYpd3Ay0k/XCJcdTAwMWVSNIYntUFcdTAwMTeSflx1MDAwN+JcdTAwMGYniMWwXFxiXHUwMDAwXFxcdTAwMTnlkZBFcIvPOEjS+K1u2NSLz1fVXHUwMDFiUrBd6Vx1MDAwNvVcdTAwMTfCuFx1MDAwNNv5l5aUrPj7V55cdTAwMGI1gLArw6qozf+vYl7E61XC1+vQrdYrWlx1MDAwYuyfqKikhFx1MDAwMYl5kVx1MDAwMq54fcsqxn1cdTAwMDBUcWzCf+uMO3JNXHUwMDFkReyuzE9ArfNcdTAwMTBcdTAwMDBF7/w0bFx1MDAwNKvAN1F+JFKTXHUwMDAzWlx1MDAxYZMmvffo2lx1MDAwNXxX/1xuXHUwMDFh91Y8Qqlr41x1MDAwYi9X3+NdMHUsaTytd2ik/HpcdTAwMWWp27B4vlx1MDAwMOkpck7eVE5ipaMt7+hcdTAwMDOxeUrob35cdTAwMTEkOEjkMGRrJ9XwrtNrqFx1MDAxZXi4QGLUaO+p0XR5u1ZcYq2k/c8gPFx1MDAxZizFlv+w7trHOkSz31x1MDAxYnexsr3w95Utg4DmS+RcdTAwMWX+c2zJte1IcKToXHUwMDFjMn77lfRcdJKdKnCk5Vx1MDAxOM6cbchOXHUwMDAzXHUwMDFm6o+nOryGQVx1MDAwNYqs03bmKeyyXHUwMDAyQ799XHUwMDFhOtqWOVx1MDAwMcvalrZzXHUwMDBiRYzX5+yK5Fx1MDAxNVNfeIuB6zxavCBem3fpZ1x1MDAxZMdcdTAwMTNcXFx1MDAxOCom60NVO1x1MDAxYaGSLYndac+oIb6JJv5mpEP9S4aSeKCh5XUuwMTSanZzXHUwMDE4srskyLrKa5G6pr5jK4t84pZ5MG/jZuqGylx1MDAxM9VyeTu4c1JKYFBcdTAwMDCpyI+SgL2HSKy2XG4neN18utJNUF/SXHUwMDFjcD36vFx1MDAxZte6QVx1MDAwNLTj1DPJXHUwMDFka2aCr1x1MDAwNZsiLCJjb25maWciOnsicG9zdGVyIjp0cnVlLCJwcmV2aWV3Ijp0cnVlLCJpc0Rvd25sb2FkIjp0cnVlfX0=";

console.log('🔓 Decoding PlayerEmbedAPI base64 data...\n');

try {
  // Decode base64
  const decoded = Buffer.from(base64Data, 'base64').toString('utf-8');
  console.log('📄 Decoded JSON:');
  console.log(decoded);
  console.log('\n' + '━'.repeat(60) + '\n');

  // Parse JSON
  const data = JSON.parse(decoded);
  console.log('📊 Parsed data:');
  console.log(JSON.stringify(data, null, 2));
  console.log('\n' + '━'.repeat(60) + '\n');

  // Check if media field exists
  if (data.media) {
    console.log('🔐 Media field found (appears to be encrypted/encoded)');
    console.log(`Length: ${data.media.length} characters`);
    console.log(`First 100 chars: ${data.media.substring(0, 100)}...`);
    
    // Try to decode media field (might be base64 or encrypted)
    console.log('\n🔍 Attempting to decode media field...');
    
    try {
      const mediaDecoded = Buffer.from(data.media, 'base64').toString('utf-8');
      console.log('✅ Media decoded (base64):');
      console.log(mediaDecoded);
    } catch (e) {
      console.log('❌ Media is not base64, might be encrypted');
    }
  }

  // Check config
  if (data.config) {
    console.log('\n⚙️  Config:');
    console.log(JSON.stringify(data.config, null, 2));
  }

  // Check other fields
  console.log('\n📋 Other fields:');
  console.log(`  slug: ${data.slug}`);
  console.log(`  md5_id: ${data.md5_id}`);
  console.log(`  user_id: ${data.user_id}`);

} catch (error: any) {
  console.error('❌ Error:', error.message);
}
