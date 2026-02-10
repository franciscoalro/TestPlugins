#!/usr/bin/env node

/**
 * Decriptação Final - PlayerEmbedAPI
 * Algoritmo descoberto: AES-128-CTR com MD5
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║  🔓 DECRIPTAÇÃO FINAL - PlayerEmbedAPI                        ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
console.log('');

// Ler dados extraídos
const dataFile = path.join(__dirname, 'output', 'extracted_data.json');
const extractedData = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

console.log('📊 Dados Carregados:');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`  Chave: ${extractedData.key}`);
console.log(`  user_id: ${extractedData.data.user_id}`);
console.log(`  slug: ${extractedData.data.slug}`);
console.log(`  md5_id: ${extractedData.data.md5_id}`);
console.log('');

/**
 * Função de decriptação descoberta
 * Algoritmo: AES-128-CTR com MD5
 */
function decryptPlayerEmbedMedia(userId, slug, md5Id, encryptedMedia) {
    try {
        // 1. Gerar chave usando a fórmula descoberta
        const keyString = `${userId}:${slug}:${md5Id}`;
        console.log('🔑 Chave:', keyString);
        
        // 2. MD5 da chave (16 bytes para AES-128)
        const key = crypto.createHash('md5').update(keyString).digest();
        console.log('🔑 MD5:', key.toString('hex'));
        console.log('');
        
        // 3. Processar dados criptografados
        // Os dados estão como string com escapes Unicode, não base64
        let mediaData = encryptedMedia;
        
        // Converter string com escapes Unicode para Buffer
        // Exemplo: "\u0006" -> byte 0x06
        const bytes = [];
        for (let i = 0; i < mediaData.length; i++) {
            const charCode = mediaData.charCodeAt(i);
            if (charCode <= 0xFF) {
                bytes.push(charCode);
            } else {
                // Caractere Unicode multi-byte
                bytes.push(charCode & 0xFF);
                bytes.push((charCode >> 8) & 0xFF);
            }
        }
        
        const encryptedBuffer = Buffer.from(bytes);
        console.log(`📦 Dados criptografados: ${encryptedBuffer.length} bytes`);
        
        // 4. Extrair counter (primeiros 16 bytes)
        const counter = encryptedBuffer.slice(0, 16);
        const ciphertext = encryptedBuffer.slice(16);
        
        console.log(`🔢 Counter: ${counter.toString('hex')}`);
        console.log(`📄 Ciphertext: ${ciphertext.length} bytes`);
        console.log('');
        
        // 5. Decriptar com AES-128-CTR
        console.log('🔓 Decriptando...');
        const decipher = crypto.createDecipheriv('aes-128-ctr', key, counter);
        let decrypted = decipher.update(ciphertext);
        decrypted = Buffer.concat([decrypted, decipher.final()]);
        
        // 6. Converter para string
        const result = decrypted.toString('utf8');
        
        console.log('✅ Decriptação bem-sucedida!');
        console.log('');
        
        return result;
        
    } catch (error) {
        console.error('❌ Erro na decriptação:', error.message);
        throw error;
    }
}

// Executar decriptação
try {
    console.log('🚀 Iniciando decriptação...');
    console.log('');
    
    const decrypted = decryptPlayerEmbedMedia(
        extractedData.data.user_id,
        extractedData.data.slug,
        extractedData.data.md5_id,
        extractedData.data.media
    );
    
    console.log('='.repeat(60));
    console.log('📄 DADOS DECRIPTADOS');
    console.log('='.repeat(60));
    console.log('');
    
    // Tentar parsear como JSON
    try {
        const json = JSON.parse(decrypted);
        console.log(JSON.stringify(json, null, 2));
        
        // Salvar resultado
        const outputFile = path.join(__dirname, 'output', 'decrypted_media.json');
        fs.writeFileSync(outputFile, JSON.stringify(json, null, 2));
        
        console.log('');
        console.log(`💾 Resultado salvo em: ${outputFile}`);
        
        // Extrair informações importantes
        console.log('');
        console.log('='.repeat(60));
        console.log('📊 INFORMAÇÕES EXTRAÍDAS');
        console.log('='.repeat(60));
        console.log('');
        
        if (json.sources && Array.isArray(json.sources)) {
            console.log('🎬 Fontes de Vídeo:');
            json.sources.forEach((source, index) => {
                console.log(`  ${index + 1}. ${source.label || 'N/A'}`);
                console.log(`     URL: ${source.file || source.url || 'N/A'}`);
                console.log(`     Tipo: ${source.type || 'N/A'}`);
            });
        }
        
        if (json.tracks && Array.isArray(json.tracks)) {
            console.log('');
            console.log('📝 Legendas:');
            json.tracks.forEach((track, index) => {
                console.log(`  ${index + 1}. ${track.label || 'N/A'}`);
                console.log(`     URL: ${track.file || 'N/A'}`);
            });
        }
        
        console.log('');
        console.log('╔════════════════════════════════════════════════════════════════╗');
        console.log('║  🎉 SUCESSO! Algoritmo descoberto e validado!                ║');
        console.log('╚════════════════════════════════════════════════════════════════╝');
        console.log('');
        console.log('📝 Algoritmo Descoberto:');
        console.log('  • Tipo: AES-128-CTR');
        console.log('  • Derivação de chave: MD5');
        console.log('  • Fórmula: user_id + ":" + slug + ":" + md5_id');
        console.log('  • Counter: Primeiros 16 bytes dos dados');
        console.log('');
        console.log('🚀 Próximos passos:');
        console.log('  1. Implementar no plugin BRCloudstream');
        console.log('  2. Testar com múltiplos vídeos');
        console.log('  3. Ver IMPLEMENTACAO_PLUGIN.md para código Kotlin');
        
    } catch (e) {
        console.log('⚠️  Resultado não é JSON válido:');
        console.log(decrypted.substring(0, 500));
        console.log('...');
        
        // Salvar como texto
        const outputFile = path.join(__dirname, 'output', 'decrypted_media.txt');
        fs.writeFileSync(outputFile, decrypted);
        console.log('');
        console.log(`💾 Resultado salvo em: ${outputFile}`);
    }
    
} catch (error) {
    console.error('');
    console.error('╔════════════════════════════════════════════════════════════════╗');
    console.error('║  ❌ ERRO NA DECRIPTAÇÃO                                       ║');
    console.error('╚════════════════════════════════════════════════════════════════╝');
    console.error('');
    console.error('Erro:', error.message);
    console.error('');
    console.error('💡 Possíveis causas:');
    console.error('  1. Formato dos dados mudou');
    console.error('  2. Vídeo não existe mais');
    console.error('  3. Dados corrompidos');
    console.error('');
    console.error('🔧 Tente:');
    console.error('  1. Executar validate_page_access.py novamente');
    console.error('  2. Testar com outro vídeo');
    console.error('  3. Verificar output/extracted_data.json');
    
    process.exit(1);
}
