/**
 * SCRIPT PARA CAPTURAR A CHAVE DE DESCRIPTOGRAFIA DO MEGAEMBED
 * 
 * COMO USAR:
 * 1. Abra https://megaembed.link/#3wnuij no Chrome/Firefox
 * 2. Abra DevTools (F12)
 * 3. Vá na aba Console
 * 4. Cole este script completo e pressione Enter
 * 5. Recarregue a página (F5)
 * 6. Aguarde o vídeo carregar
 * 7. A chave e o IV serão exibidos no console
 */

console.log('🔓 MEGAEMBED KEY CAPTURER - INICIADO');
console.log('=' .repeat(80));

// Interceptar crypto.subtle.importKey
const originalImportKey = crypto.subtle.importKey;
crypto.subtle.importKey = function(...args) {
  const [format, keyData, algorithm, extractable, keyUsages] = args;
  
  console.log('\n🔑 crypto.subtle.importKey() CHAMADO:');
  console.log('   Format:', format);
  console.log('   Algorithm:', algorithm);
  console.log('   Extractable:', extractable);
  console.log('   Key Usages:', keyUsages);
  
  if (keyData instanceof ArrayBuffer || ArrayBuffer.isView(keyData)) {
    const keyBytes = new Uint8Array(keyData);
    const keyHex = Array.from(keyBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    
    console.log('   📦 Key Data (bytes):', keyBytes);
    console.log('   📦 Key Data (hex):', keyHex);
    console.log('   📦 Key Length:', keyBytes.length, 'bytes');
    
    // Salvar no localStorage para fácil acesso
    localStorage.setItem('megaembed_key_hex', keyHex);
    localStorage.setItem('megaembed_key_length', keyBytes.length);
    
    console.log('   ✅ Chave salva em localStorage.megaembed_key_hex');
  }
  
  return originalImportKey.apply(this, args);
};

// Interceptar crypto.subtle.decrypt
const originalDecrypt = crypto.subtle.decrypt;
crypto.subtle.decrypt = function(...args) {
  const [algorithm, key, data] = args;
  
  console.log('\n🔓 crypto.subtle.decrypt() CHAMADO:');
  console.log('   Algorithm:', algorithm);
  
  if (algorithm.iv) {
    const ivBytes = new Uint8Array(algorithm.iv);
    const ivHex = Array.from(ivBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    
    console.log('   🔢 IV (bytes):', ivBytes);
    console.log('   🔢 IV (hex):', ivHex);
    console.log('   🔢 IV Length:', ivBytes.length, 'bytes');
    
    // Salvar no localStorage
    localStorage.setItem('megaembed_iv_hex', ivHex);
    localStorage.setItem('megaembed_iv_length', ivBytes.length);
    
    console.log('   ✅ IV salvo em localStorage.megaembed_iv_hex');
  }
  
  if (data instanceof ArrayBuffer || ArrayBuffer.isView(data)) {
    const dataBytes = new Uint8Array(data);
    const dataHex = Array.from(dataBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    
    console.log('   📦 Encrypted Data Length:', dataBytes.length, 'bytes');
    console.log('   📦 Encrypted Data (first 100 bytes hex):', dataHex.substring(0, 200));
    
    // Salvar no localStorage
    localStorage.setItem('megaembed_encrypted_hex', dataHex);
  }
  
  // Chamar original e interceptar resultado
  return originalDecrypt.apply(this, args).then(result => {
    const resultBytes = new Uint8Array(result);
    const resultText = new TextDecoder().decode(resultBytes);
    
    console.log('   ✅ Decrypted Data Length:', resultBytes.length, 'bytes');
    console.log('   ✅ Decrypted Data (text):', resultText.substring(0, 500));
    
    // Tentar parsear como JSON
    try {
      const json = JSON.parse(resultText);
      console.log('   🎯 É JSON! Chaves:', Object.keys(json));
      console.log('   🎯 JSON completo:', json);
      
      // Salvar no localStorage
      localStorage.setItem('megaembed_decrypted_json', JSON.stringify(json, null, 2));
      
      // Se tiver URL, destacar
      if (json.url) {
        console.log('\n   🎬 URL DO VÍDEO ENCONTRADA:');
        console.log('   ', json.url);
        localStorage.setItem('megaembed_video_url', json.url);
      }
    } catch (e) {
      console.log('   ⚠️  Não é JSON, é texto puro');
    }
    
    return result;
  });
};

// Interceptar fetch para capturar requisições
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const [url, options] = args;
  
  if (typeof url === 'string' && url.includes('/api/v1/player')) {
    console.log('\n🌐 FETCH /api/v1/player DETECTADO:');
    console.log('   URL:', url);
    
    // Extrair token da URL
    const tokenMatch = url.match(/[?&]t=([a-f0-9]+)/);
    if (tokenMatch) {
      const token = tokenMatch[1];
      console.log('   🎫 Token:', token);
      console.log('   🎫 Token Length:', token.length, 'chars');
      
      // Salvar no localStorage
      localStorage.setItem('megaembed_token', token);
      localStorage.setItem('megaembed_token_length', token.length);
    }
    
    // Interceptar resposta
    return originalFetch.apply(this, args).then(response => {
      console.log('   ✅ Response Status:', response.status);
      console.log('   ✅ Response Headers:', [...response.headers.entries()]);
      
      // Clonar para não consumir o body
      return response.clone().text().then(body => {
        console.log('   📦 Response Body Length:', body.length, 'chars');
        console.log('   📦 Response Body (first 200 chars):', body.substring(0, 200));
        
        // Salvar no localStorage
        localStorage.setItem('megaembed_response_hex', body);
        
        return response;
      });
    });
  }
  
  return originalFetch.apply(this, args);
};

// Interceptar XMLHttpRequest também
const originalXHROpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(...args) {
  const [method, url] = args;
  
  if (typeof url === 'string' && url.includes('/api/v1/player')) {
    console.log('\n🌐 XHR /api/v1/player DETECTADO:');
    console.log('   Method:', method);
    console.log('   URL:', url);
    
    // Extrair token
    const tokenMatch = url.match(/[?&]t=([a-f0-9]+)/);
    if (tokenMatch) {
      const token = tokenMatch[1];
      console.log('   🎫 Token:', token);
      localStorage.setItem('megaembed_token', token);
    }
  }
  
  return originalXHROpen.apply(this, args);
};

console.log('\n✅ Interceptors instalados!');
console.log('📝 Agora recarregue a página (F5) e aguarde o vídeo carregar');
console.log('🔍 Todos os dados serão salvos em localStorage');
console.log('\n💡 Para ver os dados capturados, execute:');
console.log('   localStorage.getItem("megaembed_key_hex")');
console.log('   localStorage.getItem("megaembed_iv_hex")');
console.log('   localStorage.getItem("megaembed_token")');
console.log('   localStorage.getItem("megaembed_video_url")');
console.log('=' .repeat(80));
