#!/usr/bin/env node

/**
 * Script para testar a fórmula descoberta da chave AES
 * Fórmula: user_id + ':' + slug + ':' + md5_id
 */

const CryptoJS = require('crypto-js');

console.log("╔════════════════════════════════════════════════════════════╗");
console.log("║  🧪 Teste da Fórmula AES Descoberta                       ║");
console.log("╚════════════════════════════════════════════════════════════╝");
console.log("");

// Dados de teste
const testData = {
    user_id: "482120",
    slug: "kBJLtxCD3",
    md5_id: "28930647",
    // Este é um exemplo - você precisa obter o valor real da API
    media: "U2FsdGVkX1..." // Substituir com valor real
};

console.log("📊 Dados de Teste:");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log(`  user_id: ${testData.user_id}`);
console.log(`  slug:    ${testData.slug}`);
console.log(`  md5_id:  ${testData.md5_id}`);
console.log("");

// Gerar a chave usando a fórmula descoberta
const key = `${testData.user_id}:${testData.slug}:${testData.md5_id}`;

console.log("🔑 Chave AES Gerada:");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log(`  ${key}`);
console.log("");

console.log("📝 Fórmula Usada:");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("  user_id + ':' + slug + ':' + md5_id");
console.log("");

// Tentar decriptar
console.log("🔓 Tentando Decriptar:");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

try {
    const decrypted = CryptoJS.AES.decrypt(testData.media, key);
    const decryptedStr = decrypted.toString(CryptoJS.enc.Utf8);
    
    if (decryptedStr) {
        console.log("✅ SUCESSO! Decriptação bem-sucedida!");
        console.log("");
        console.log("📄 Dados Decriptados:");
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        
        try {
            const parsed = JSON.parse(decryptedStr);
            console.log(JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log(decryptedStr);
        }
        
        console.log("");
        console.log("🎉 A fórmula está CORRETA!");
    } else {
        console.log("❌ FALHA! Decriptação retornou vazio.");
        console.log("");
        console.log("💡 Possíveis causas:");
        console.log("  1. Campo 'media' está incorreto");
        console.log("  2. Fórmula precisa de ajustes");
        console.log("  3. Algoritmo de criptografia diferente");
    }
} catch (error) {
    console.log("❌ ERRO durante decriptação:");
    console.log(`  ${error.message}`);
    console.log("");
    console.log("💡 Possíveis causas:");
    console.log("  1. Campo 'media' não está em formato válido");
    console.log("  2. Chave incorreta");
    console.log("  3. Algoritmo de criptografia diferente");
}

console.log("");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("");
console.log("📋 PRÓXIMOS PASSOS:");
console.log("");
console.log("1. Obter o campo 'media' real da API:");
console.log("   curl 'https://playerembedapi.link/api/media?v=kBJLtxCD3'");
console.log("");
console.log("2. Substituir o valor de 'media' neste script");
console.log("");
console.log("3. Executar novamente:");
console.log("   node test_final_formula.js");
console.log("");
console.log("4. Se funcionar, implementar no plugin BRCloudstream");
console.log("");

// Função auxiliar para testar com dados reais
console.log("💡 DICA: Para testar com dados reais, use:");
console.log("");
console.log("const testWithRealData = async () => {");
console.log("  const response = await fetch(");
console.log("    'https://playerembedapi.link/api/media?v=kBJLtxCD3'");
console.log("  );");
console.log("  const data = await response.json();");
console.log("  ");
console.log("  const key = `${data.user_id}:${data.slug}:${data.md5_id}`;");
console.log("  const decrypted = CryptoJS.AES.decrypt(data.media, key);");
console.log("  console.log(decrypted.toString(CryptoJS.enc.Utf8));");
console.log("};");
console.log("");
