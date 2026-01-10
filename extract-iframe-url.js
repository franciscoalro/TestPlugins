/**
 * Helper Script - Extrair URL do Iframe do MaxSeries
 * 
 * INSTRUÇÕES:
 * 1. Abra https://www.maxseries.one no seu navegador
 * 2. Escolha um anime/série
 * 3. Clique em um episódio
 * 4. Quando o player carregar, abra o Console do navegador (F12)
 * 5. Cole este código no console e pressione Enter
 * 6. A URL do iframe será exibida e copiada automaticamente
 */

(function extractPlayerUrl() {
    console.log('🔍 Procurando iframe do player...\n');

    // Procura por iframes na página
    const iframes = document.querySelectorAll('iframe');

    if (iframes.length === 0) {
        console.error('❌ Nenhum iframe encontrado na página!');
        console.log('💡 Certifique-se de estar na página de um episódio.');
        return;
    }

    console.log(`✅ Encontrados ${iframes.length} iframe(s):\n`);

    iframes.forEach((iframe, index) => {
        const src = iframe.src;
        console.log(`📹 Iframe #${index + 1}:`);
        console.log(`   URL: ${src}`);
        console.log(`   ID: ${iframe.id || 'N/A'}`);
        console.log(`   Class: ${iframe.className || 'N/A'}`);
        console.log('');

        // Se for um player conhecido, destaca
        if (src.includes('playerthree') ||
            src.includes('playerembedapi') ||
            src.includes('megaembed')) {
            console.log('🎯 PLAYER DETECTADO!');
            console.log('📋 URL copiada para área de transferência!');
            console.log('');
            console.log('🚀 Execute agora:');
            console.log(`node playwright-video-extractor.js "${src}"`);
            console.log('');

            // Tenta copiar para área de transferência
            if (navigator.clipboard) {
                navigator.clipboard.writeText(src).then(() => {
                    console.log('✅ URL copiada com sucesso!');
                }).catch(err => {
                    console.log('⚠️ Não foi possível copiar automaticamente');
                });
            }
        }
    });

    // Retorna a primeira URL de iframe
    if (iframes.length > 0) {
        return iframes[0].src;
    }
})();
