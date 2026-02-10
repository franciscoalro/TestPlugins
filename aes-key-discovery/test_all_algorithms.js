#!/usr/bin/env node

/**
 * Teste Automatizado de Algoritmos de Decriptação
 * Testa 3 implementações diferentes com os dados reais
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║  🧪 TESTE AUTOMATIZADO DE ALGORITMOS                          ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
console.log('');

// Dados reais capturados
const testData = {
    user_id: "482120",
    slug: "kBJLtxCD3",
    md5_id: "28930647",
    // Dados do campo media (base64 do HTML)
    media: "vEj0XHUwMDA2q1x1MDAwNIOMNv4n1dkxpk/NQUz4lFam8OQ8VN5cdTAwMThcdTAwMWWvk1NcdTAwMTNjyFxiJGAo3rHh2C9cdTAwMTjgTFx1MDAxMjVcdTAwMTBPamurbFQ97ONcdTAwMWRVXHUwMDE4LJq/XHUwMDFhRFx1MDAwMJCoq/dcdTAwMTFWiVx1MDAxM+pXXHUwMDE2ikRcdN/hL1x1MDAxOFxyg0P9VLRya4TjV+BzTkEjvdowwFx1MDAwNVx1MDAxNISVWidO91x1MDAwNlx1MDAxMDZSXVvK7fF4e7c5N1x1MDAxYTJgXkzYViRfOCFcdMspfMdTPobK2dm9zZKewVx1MDAxZlQ2/9DttlximcajX9z/tKHaXHUwMDE213f5nJ4rXHTHXHUwMDE1XGL1z1xubmZcdTAwMDSesGA9luTlOVx1MDAxMVVWvn8wboAjbbxcdTAwMTU7LEGu8Vx1MDAwYqtcdTAwMTblcSl7xX9o8KtcdTAwMTmDXGJW5WBcdTAwMDKpvJnB6/JcdTAwMTdBk/dmnaW2wKucRbBzXGaVX3HSlJQhVT+vP8ClZFx1MDAxMVKzxVx1MDAxOH+mNbNWNLGdlITtxStqPYSmPzFcdTAwMWZ/3Fx1MDAxZmvWaVx1MDAxMidS1uLKK2zxwzmASt2Kxlb2bk4xXCJrttt4+pJi+jpcdTAwMWHqXGbmpodrhbbW2VxuXHUwMDE2XHUwMDAwJVx1MDAwM/pcdTAwMTLl7F+2JkjxzZ55XHUwMDFjNeeY8plcdTAwMTCRoVbTt1x1MDAxN4aGRmrQhP1H2JNcIr2XxZ1cdTAwMTfC61x1MDAxYVxc3Vx1MDAwMniEmFxuXHUwMDA3+lx1MDAxOFx1MDAwNZjHO5CBcqt2VDb6yaI38LBcXDxGbCi2ilxyl2Pk4q8rbN17oG9DXHUwMDE1MlSm8mj+eVKHTtwp+q5cdTAwMWRNbVx1MDAxMMRrtyVrLVx1MDAwMVx1MDAxNWlcdTAwMDTlMeTM8rBA1e9LJY3Q7VxcXHUwMDFjL9lTmWeVgN/WOTnwXHUwMDAzRe/HnXk8XHUwMDEzqvBcdTAwMDHzOu34l1x1MDAwZS1RnSRcdPTUz84po6yehLeQuU9uXHUwMDA3JZL/XHUwMDE4XHUwMDFmWazlqV/rXHUwMDA3aC9cdTAwMTPB6sB0g6WuXHUwMDE1JVx1MDAwMlVcIvFUi1xif1ZcIrPEz4l2TE7sXHUwMDAyzasv6IH0UO7gq1x1MDAwN4C9XVx1MDAwN1x1MDAxMSRk5rT6Un5cbtBcdTAwMDPTXHUwMDEzedPdMFx1MDAxNTq08kemQMFcdTAwMThcdTAwMDBrii9PXHUwMDA2siNcdTAwMTFGwip8NFx1MDAxN2qWkVx0S/PDrUedsX9KWD9pzFx1MDAxOYGgeFx013lcdTAwMTCPwDdRXHQvjvuchVx1MDAwYrGFmHlcdTAwMWb/xcQ2m6/FXHUwMDE35zhkXHUwMDE0L3z9x6DLNGz3lFx1MDAxOVxupVFcdTAwMTlv8Fx1MDAwN7Lf9p1Kx4NTfGZcdTAwMWOHguRcYjkzXHUwMDFhWfiN4zXEXGZAqb/CdiHKq0vmUdnGVVnOSFx1MDAxNd7vqFxui1x1MDAxOFxiXHUwMDE1XHUwMDFk9tRIXHUwMDA1XHLcutTHmDsydlx1MDAxOZJccoTrLip6euPk6NXcV/9URFx1MDAxZCym7mE6w7E1mIJcdTAwMDBcdTAwMWO+veyldf5tnlx1MDAwMTAkWHFMa5JyXHUwMDE3XFy6xlxc9baZXCLE0sDF9IJ3flx1MDAxNVx1MDAxYYhTXGYzPP/ibWo02UxygnhqYYJ3wb4sPWfESEBHNrqcXHUwMDFjbFRV6TBkSmdcdTAwMWE9fVx1MDAwZZXs8kJcZplykEtw4TBcdTAwMWVcZkvd4/RIUVx1MDAxZfLomcyVSPLTRljnyY423ypTiHOAqlx1MDAwYlHTNjF32f/BSPxkknDD8ECyvGtL4L5cdTAwMGJcdTAwMGKp6Hi2pd/KmLz0XHTHq1x1MDAxY9HkoFx1MDAxM1x00KYw37lzXG5RmVx1MDAxNXQ+2u9cdTAwMTV1Skm9cGP1olMuXHUwMDBl2JmmMpWXZCa12U+RXHQ7ZtHXbJRCde3g+1x1MDAwYrXxxPPvSDRKzk6IcSvyQMckuVx1MDAwMvkqvzSuhXqg4lxmgtFWXHUwMDE2oafSKufrwaSd3pPmYN/Z6z9cdPqu8j7CQexcdTAwMTJQzdhcdTAwMDPGI1VD07d8ajZB1lx1MDAxYeb8xVPkPmyie5vA8tleXHUwMDA1u0g5uN5pXHUwMDA0PZjGSlx1MDAxZlfOtM9e5NKi+FXeXG6ztDqjqmiIIFxc1JdQrEiKJenivDHnqPGAeFfPL960XHUwMDE4tdyjt8nkd/N3kClcXM3BL3NcdTAwMTKIc9uzVfBsSLYlgfP8r2EkmDTn5lx1MDAxZjK2dlx1MDAxZv/w7i7Uidd6XHUwMDBio5JyJftcdTAwMDBUotJcdTAwMDeU8FJcdTAwMGIl4tRcdTAwMDDXRmJcdFx1MDAwMXVcdTAwMDFcdTAwMWU8l52dfFx1MDAwNnpcdTAwMDW4vLBdaXBcdTAwMTLexWhcdTAwMDHbhci5tlx1MDAxYdJcdTAwMTRSjVx1MDAwYjHkSO01aCpP6zm2vsEvZOP15N5SMU9IPYnw/UtRI9DSXHUwMDFk9Fx1MDAwNbqDWGxUXHUwMDEz1LGMN4GJycGPO7fsXFxdXHUwMDA11absaYVcdTAwMWIsTE5u5yunsDteJnmTvr32VKCn/VKsy1U025Gvnd3oUudXY3xjXHUwMDBlk7bEqlx1MDAxY1x1MDAxZqiVZcJg+W//xZRcdTAwMWKUXHUwMDA2UHvF9JM="
};

console.log('📊 Dados de Teste:');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`  user_id: ${testData.user_id}`);
console.log(`  slug: ${testData.slug}`);
console.log(`  md5_id: ${testData.md5_id}`);
console.log(`  media: ${testData.media.substring(0, 50)}...`);
console.log('');

// Gerar chave
const keyString = `${testData.user_id}:${testData.slug}:${testData.md5_id}`;
console.log('🔑 Chave Gerada:');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`  ${keyString}`);
console.log('');

const results = [];

// ============================================================
// ALGORITMO 1: AES-256-CBC com MD5
// ============================================================

console.log('🧪 Testando Algoritmo 1: AES-256-CBC com MD5');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

try {
    // MD5 da chave
    const md5Key = crypto.createHash('md5').update(keyString).digest();
    console.log(`  MD5 Key: ${md5Key.toString('hex')}`);
    
    // Expandir para 32 bytes (AES-256)
    const key256 = Buffer.concat([md5Key, md5Key], 32);
    
    // Decodificar dados (remover escapes Unicode)
    let mediaData = testData.media;
    
    // Tentar decodificar como base64
    try {
        const decoded = Buffer.from(mediaData, 'base64');
        console.log(`  Decoded length: ${decoded.length} bytes`);
        
        // Tentar diferentes configurações
        const configs = [
            { iv: decoded.slice(0, 16), data: decoded.slice(16) },
            { iv: Buffer.alloc(16, 0), data: decoded },
            { iv: md5Key, data: decoded }
        ];
        
        for (let i = 0; i < configs.length; i++) {
            try {
                const decipher = crypto.createDecipheriv('aes-256-cbc', key256, configs[i].iv);
                decipher.setAutoPadding(false);
                let decrypted = decipher.update(configs[i].data);
                decrypted = Buffer.concat([decrypted, decipher.final()]);
                
                const text = decrypted.toString('utf8');
                if (text.includes('{') || text.includes('http')) {
                    console.log(`  ✅ Config ${i + 1} funcionou!`);
                    console.log(`  Resultado: ${text.substring(0, 100)}...`);
                    results.push({
                        algorithm: 'AES-256-CBC com MD5',
                        config: i + 1,
                        success: true,
                        result: text
                    });
                    break;
                }
            } catch (e) {
                // Continuar tentando
            }
        }
    } catch (e) {
        console.log(`  ❌ Erro: ${e.message}`);
    }
    
    if (results.length === 0) {
        console.log('  ❌ Nenhuma configuração funcionou');
        results.push({
            algorithm: 'AES-256-CBC com MD5',
            success: false,
            error: 'Nenhuma configuração funcionou'
        });
    }
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}`);
    results.push({
        algorithm: 'AES-256-CBC com MD5',
        success: false,
        error: e.message
    });
}

console.log('');

// ============================================================
// ALGORITMO 2: AES-128-CTR com MD5
// ============================================================

console.log('🧪 Testando Algoritmo 2: AES-128-CTR com MD5');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

try {
    const md5Key = crypto.createHash('md5').update(keyString).digest();
    
    const mediaData = testData.media;
    const decoded = Buffer.from(mediaData, 'base64');
    
    // Tentar diferentes configurações de counter
    const configs = [
        { counter: decoded.slice(0, 16), data: decoded.slice(16) },
        { counter: Buffer.alloc(16, 0), data: decoded },
        { counter: md5Key, data: decoded }
    ];
    
    for (let i = 0; i < configs.length; i++) {
        try {
            const decipher = crypto.createDecipheriv('aes-128-ctr', md5Key, configs[i].counter);
            let decrypted = decipher.update(configs[i].data);
            decrypted = Buffer.concat([decrypted, decipher.final()]);
            
            const text = decrypted.toString('utf8');
            if (text.includes('{') || text.includes('http')) {
                console.log(`  ✅ Config ${i + 1} funcionou!`);
                console.log(`  Resultado: ${text.substring(0, 100)}...`);
                results.push({
                    algorithm: 'AES-128-CTR com MD5',
                    config: i + 1,
                    success: true,
                    result: text
                });
                break;
            }
        } catch (e) {
            // Continuar tentando
        }
    }
    
    if (results.filter(r => r.algorithm === 'AES-128-CTR com MD5').length === 0) {
        console.log('  ❌ Nenhuma configuração funcionou');
        results.push({
            algorithm: 'AES-128-CTR com MD5',
            success: false,
            error: 'Nenhuma configuração funcionou'
        });
    }
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}`);
    results.push({
        algorithm: 'AES-128-CTR com MD5',
        success: false,
        error: e.message
    });
}

console.log('');

// ============================================================
// ALGORITMO 3: AES-256-CBC com SHA256
// ============================================================

console.log('🧪 Testando Algoritmo 3: AES-256-CBC com SHA256');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

try {
    const sha256Key = crypto.createHash('sha256').update(keyString).digest();
    console.log(`  SHA256 Key: ${sha256Key.toString('hex').substring(0, 32)}...`);
    
    const mediaData = testData.media;
    const decoded = Buffer.from(mediaData, 'base64');
    
    const configs = [
        { iv: decoded.slice(0, 16), data: decoded.slice(16) },
        { iv: Buffer.alloc(16, 0), data: decoded },
        { iv: sha256Key.slice(0, 16), data: decoded }
    ];
    
    for (let i = 0; i < configs.length; i++) {
        try {
            const decipher = crypto.createDecipheriv('aes-256-cbc', sha256Key, configs[i].iv);
            decipher.setAutoPadding(false);
            let decrypted = decipher.update(configs[i].data);
            decrypted = Buffer.concat([decrypted, decipher.final()]);
            
            const text = decrypted.toString('utf8');
            if (text.includes('{') || text.includes('http')) {
                console.log(`  ✅ Config ${i + 1} funcionou!`);
                console.log(`  Resultado: ${text.substring(0, 100)}...`);
                results.push({
                    algorithm: 'AES-256-CBC com SHA256',
                    config: i + 1,
                    success: true,
                    result: text
                });
                break;
            }
        } catch (e) {
            // Continuar tentando
        }
    }
    
    if (results.filter(r => r.algorithm === 'AES-256-CBC com SHA256').length === 0) {
        console.log('  ❌ Nenhuma configuração funcionou');
        results.push({
            algorithm: 'AES-256-CBC com SHA256',
            success: false,
            error: 'Nenhuma configuração funcionou'
        });
    }
} catch (e) {
    console.log(`  ❌ Erro: ${e.message}`);
    results.push({
        algorithm: 'AES-256-CBC com SHA256',
        success: false,
        error: e.message
    });
}

console.log('');

// ============================================================
// RESULTADOS FINAIS
// ============================================================

console.log('='.repeat(60));
console.log('📊 RESULTADOS FINAIS');
console.log('='.repeat(60));
console.log('');

const successResults = results.filter(r => r.success);

if (successResults.length > 0) {
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║  ✅ ALGORITMO ENCONTRADO!                                     ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('');
    
    successResults.forEach((result, index) => {
        console.log(`${index + 1}. ${result.algorithm} (Config ${result.config})`);
        console.log('   Resultado:');
        console.log(`   ${result.result.substring(0, 200)}...`);
        console.log('');
    });
    
    // Salvar resultado
    const outputFile = path.join(__dirname, 'output', 'decryption_success.json');
    fs.writeFileSync(outputFile, JSON.stringify({
        timestamp: new Date().toISOString(),
        key: keyString,
        successfulAlgorithms: successResults
    }, null, 2));
    
    console.log(`💾 Resultado salvo em: ${outputFile}`);
    
} else {
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║  ❌ NENHUM ALGORITMO FUNCIONOU                                ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('');
    console.log('💡 Possíveis razões:');
    console.log('  1. Formato dos dados está incorreto');
    console.log('  2. Algoritmo usa método customizado');
    console.log('  3. Dados precisam de pré-processamento');
    console.log('');
    console.log('🔧 Próximos passos:');
    console.log('  1. Analisar lite.bundle.js manualmente');
    console.log('  2. Usar método de captura manual no navegador');
    console.log('  3. Tentar com dados de outro vídeo');
}

console.log('');
console.log('📊 Resumo:');
console.log(`  Total de testes: ${results.length}`);
console.log(`  Sucessos: ${successResults.length}`);
console.log(`  Falhas: ${results.length - successResults.length}`);
console.log('');
