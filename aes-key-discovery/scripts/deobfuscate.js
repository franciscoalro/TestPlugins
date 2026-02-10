#!/usr/bin/env node

// Deobfuscador JavaScript simples

const fs = require('fs');

const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
    console.error('Uso: node deobfuscate.js <input.js> <output.js>');
    process.exit(1);
}

console.log('📖 Lendo arquivo...');
let code = fs.readFileSync(inputFile, 'utf8');

console.log('🔧 Aplicando transformações...');

// 1. Adicionar quebras de linha após ; e {
code = code.replace(/;/g, ';\n');
code = code.replace(/{/g, '{\n');
code = code.replace(/}/g, '\n}\n');

// 2. Expandir strings hexadecimais
code = code.replace(/\\x([0-9a-fA-F]{2})/g, (match, hex) => {
    return String.fromCharCode(parseInt(hex, 16));
});

// 3. Expandir unicode
code = code.replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => {
    return String.fromCharCode(parseInt(hex, 16));
});

// 4. Remover espaços múltiplos
code = code.replace(/ +/g, ' ');

// 5. Adicionar indentação básica
let indentLevel = 0;
const lines = code.split('\n');
const indentedLines = lines.map(line => {
    line = line.trim();
    
    if (line.includes('}')) {
        indentLevel = Math.max(0, indentLevel - 1);
    }
    
    const indented = '  '.repeat(indentLevel) + line;
    
    if (line.includes('{')) {
        indentLevel++;
    }
    
    return indented;
});

code = indentedLines.join('\n');

// 6. Adicionar comentários em seções importantes
code = code.replace(/(crypto\.subtle\.importKey)/g, '\n// ⚠️ CRYPTO IMPORT KEY\n$1');
code = code.replace(/(crypto\.subtle\.decrypt)/g, '\n// ⚠️ CRYPTO DECRYPT\n$1');
code = code.replace(/(user_id|slug|md5_id)/g, '\n// 🔑 PARÂMETRO: $1\n$1');

console.log('💾 Salvando arquivo deobfuscado...');
fs.writeFileSync(outputFile, code, 'utf8');

console.log('✓ Deobfuscação completa!');
console.log(`  Tamanho original: ${fs.statSync(inputFile).size} bytes`);
console.log(`  Tamanho deobfuscado: ${fs.statSync(outputFile).size} bytes`);
