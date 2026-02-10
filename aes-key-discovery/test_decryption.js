#!/usr/bin/env node

/**
 * Script para testar decriptação com as fórmulas descobertas
 * Testa todas as 6 combinações possíveis de MD5
 */

const crypto = require('crypto');

// Valores de teste do vídeo kBJLtxCD3
const TEST_DATA = {
    user_id: "482120",
    slug: "kBJLtxCD3",
    md5_id: "28930647",
    // Campo media criptografado (exemplo - você precisa fornecer o real)
    encrypted_media: "U2FsdGVkX1..." // Substituir com valor real
};

// Função para gerar MD5
function md5(text) {
    return crypto.createHash('md5').update(text).digest('hex');
}

// Função para tentar decriptar com AES
function tryDecrypt(key, encryptedData, algorithm = 'aes-256-cbc') {
    try {
        // Remover prefixo "Salted__" se existir (formato OpenSSL)
        let data = encryptedData;
        if (data.startsWith('U2FsdGVk')) {
            // É base64 com "Salted__"
            const buffer = Buffer.from(data, 'base64');
            
            // Verificar se começa com "Salted__"
            if (buffer.toString('utf8', 0, 8) === 'Salted__') {
                const salt = buffer.slice(8, 16);
                const ciphertext = buffer.slice(16);
                
                // Derivar chave e IV usando EVP_BytesToKey (compatível com OpenSSL)
                const keyIv = evpBytesToKey(key, salt, 32, 16);
                
                const decipher = crypto.createDecipheriv('aes-256-cbc', keyIv.key, keyIv.iv);
                let decrypted = decipher.update(ciphertext);
                decrypted = Buffer.concat([decrypted, decipher.final()]);
                
                return {
                    success: true,
                    data: decrypted.toString('utf8')
                };
            }
        }
        
        // Tentar decriptação direta
        const keyBuffer = Buffer.from(key, 'hex');
        const iv = Buffer.alloc(16, 0); // IV zero (pode precisar ajustar)
        
        const decipher = crypto.createDecipheriv(algorithm, keyBuffer, iv);
        let decrypted = decipher.update(Buffer.from(encryptedData, 'base64'));
        decrypted = Buffer.concat([decrypted, decipher.final()]);
        
        return {
            success: true,
            data: decrypted.toString('utf8')
        };
        
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

// Implementação de EVP_BytesToKey (compatível com OpenSSL)
function evpBytesToKey(password, salt, keyLen, ivLen) {
    const md5Hashes = [];
    let digest = Buffer.alloc(0);
    let keyIvLen = keyLen + ivLen;
    
    while (Buffer.concat(md5Hashes).length < keyIvLen) {
        const hash = crypto.createHash('md5');
        hash.update(digest);
        hash.update(password);
        hash.update(salt);
        digest = hash.digest();
        md5Hashes.push(digest);
    }
    
    const keyIv = Buffer.concat(md5Hashes);
    return {
        key: keyIv.slice(0, keyLen),
        iv: keyIv.slice(keyLen, keyLen + ivLen)
    };
}

// Todas as combinações possíveis
const formulas = [
    {
        name: "user_id + slug + md5_id",
        getValue: (d) => d.user_id + d.slug + d.md5_id
    },
    {
        name: "user_id + md5_id + slug",
        getValue: (d) => d.user_id + d.md5_id + d.slug
    },
    {
        name: "slug + user_id + md5_id",
        getValue: (d) => d.slug + d.user_id + d.md5_id
    },
    {
        name: "slug + md5_id + user_id",
        getValue: (d) => d.slug + d.md5_id + d.user_id
    },
    {
        name: "md5_id + user_id + slug",
        getValue: (d) => d.md5_id + d.user_id + d.slug
    },
    {
        name: "md5_id + slug + user_id",
        getValue: (d) => d.md5_id + d.slug + d.user_id
    }
];

console.log("╔════════════════════════════════════════════════════════════╗");
console.log("║  🔓 Teste de Decriptação AES                              ║");
console.log("╚════════════════════════════════════════════════════════════╝\n");

console.log("📊 Dados de Teste:");
console.log(`  user_id: ${TEST_DATA.user_id}`);
console.log(`  slug: ${TEST_DATA.slug}`);
console.log(`  md5_id: ${TEST_DATA.md5_id}`);
console.log(`  encrypted_media: ${TEST_DATA.encrypted_media.substring(0, 50)}...`);
console.log();

console.log("🔑 Testando Fórmulas:\n");

formulas.forEach((formula, index) => {
    const value = formula.getValue(TEST_DATA);
    const hash = md5(value);
    
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`${index + 1}. ${formula.name}`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`   Valor: ${value}`);
    console.log(`   MD5:   ${hash}`);
    
    // Tentar decriptar
    const result = tryDecrypt(hash, TEST_DATA.encrypted_media);
    
    if (result.success) {
        console.log(`   ✅ SUCESSO! Decriptação bem-sucedida!`);
        console.log(`   📄 Dados decriptados:`);
        console.log(`   ${result.data.substring(0, 200)}...`);
        console.log();
        console.log(`   🎯 FÓRMULA CORRETA ENCONTRADA!`);
    } else {
        console.log(`   ❌ Falhou: ${result.error}`);
    }
    console.log();
});

console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("\n💡 NOTA: Se nenhuma fórmula funcionou, você precisa:");
console.log("  1. Fornecer o valor real do campo 'media' criptografado");
console.log("  2. Verificar o algoritmo usado (AES-256-CBC, AES-128-CBC, etc.)");
console.log("  3. Verificar se há IV (Initialization Vector) específico");
console.log("  4. Usar ferramentas avançadas (Burp Suite, Frida) para capturar a chave em runtime");
