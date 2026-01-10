/**
 * Exemplo de Teste - Playwright Video Extractor
 * 
 * Este é um exemplo simples de como usar o extrator.
 * Substitua a URL pelo link do player que você quer testar.
 */

// URLs de exemplo para testar (comente/descomente conforme necessário)
const TEST_URLS = {
    // MaxSeries Player
    maxseries: 'https://playerthree.online/embed/...',

    // PlayerEmbedAPI
    playerembed: 'https://playerembedapi.link/...',

    // MegaEmbed
    megaembed: 'https://megaembed.link/...',

    // Exemplo genérico
    example: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
};

// Selecione qual URL testar
const URL_TO_TEST = TEST_URLS.example;

console.log(`
╔════════════════════════════════════════════════════════════════════════════╗
║                    PLAYWRIGHT VIDEO EXTRACTOR - TESTE                      ║
╚════════════════════════════════════════════════════════════════════════════╝

📝 INSTRUÇÕES:

1. Edite este arquivo (test-example.js)
2. Substitua a URL em TEST_URLS com o link real do player
3. Execute: node test-example.js

📋 EXEMPLO DE USO:

   const TEST_URLS = {
     maxseries: 'https://playerthree.online/embed/abc123',
   };
   
   const URL_TO_TEST = TEST_URLS.maxseries;

🚀 EXECUTANDO TESTE COM:
   ${URL_TO_TEST}

────────────────────────────────────────────────────────────────────────────────
`);

// Importa e executa o extrator
const { spawn } = require('child_process');

const extractor = spawn('node', ['playwright-video-extractor.js', URL_TO_TEST], {
    cwd: __dirname,
    stdio: 'inherit',
});

extractor.on('close', (code) => {
    console.log(`\n\n✅ Processo finalizado com código: ${code}\n`);
});
