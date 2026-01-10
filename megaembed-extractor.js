/**
 * MegaEmbed API Extractor
 * Extrai link M3U8 real da API do MegaEmbed
 */

const https = require('https');
const http = require('http');

// ID extraído do HAR
const MEGAEMBED_ID = '3wnuij';

function httpsGet(url) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        lib.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve({ status: res.statusCode, data, headers: res.headers }));
        }).on('error', reject);
    });
}

async function extractMegaEmbedVideo() {
    console.log('🎬 MegaEmbed Video Extractor\n');
    console.log('='.repeat(80));

    try {
        // 1. Busca informações do vídeo
        console.log('\n📋 Buscando informações do vídeo...');
        const infoUrl = `https://megaembed.link/api/v1/info?id=${MEGAEMBED_ID}`;
        console.log(`URL: ${infoUrl}\n`);

        const infoResponse = await httpsGet(infoUrl);
        console.log(`Status: ${infoResponse.status}`);

        if (infoResponse.status === 200) {
            const info = JSON.parse(infoResponse.data);
            console.log('\n✅ Informações obtidas:');
            console.log(JSON.stringify(info, null, 2));
        }

        // 2. Busca URL do vídeo
        console.log('\n\n📹 Buscando URL do vídeo...');
        const videoUrl = `https://megaembed.link/api/v1/video?id=${MEGAEMBED_ID}&w=1920&h=1080&r=playerthree.online`;
        console.log(`URL: ${videoUrl}\n`);

        const videoResponse = await httpsGet(videoUrl);
        console.log(`Status: ${videoResponse.status}`);

        if (videoResponse.status === 200) {
            const videoData = JSON.parse(videoResponse.data);
            console.log('\n✅ Dados do vídeo obtidos:');
            console.log(JSON.stringify(videoData, null, 2));

            // Procura pelo link M3U8
            if (videoData.sources && videoData.sources.length > 0) {
                console.log('\n\n' + '='.repeat(80));
                console.log('🎯 LINKS DE VÍDEO ENCONTRADOS!');
                console.log('='.repeat(80) + '\n');

                videoData.sources.forEach((source, i) => {
                    console.log(`📹 Fonte ${i + 1}:`);
                    console.log(`   URL: ${source.file || source.src || source}`);
                    console.log(`   Tipo: ${source.type || 'N/A'}`);
                    console.log(`   Label: ${source.label || 'N/A'}`);
                    console.log('');

                    const url = source.file || source.src || source;
                    if (url && (url.includes('.m3u8') || url.includes('.mp4'))) {
                        console.log('🎬 Para reproduzir no VLC:');
                        console.log(`   vlc "${url}"`);
                        console.log('');
                    }
                });

                // Salva em arquivo
                const fs = require('fs');
                const output = {
                    id: MEGAEMBED_ID,
                    info: infoResponse.status === 200 ? JSON.parse(infoResponse.data) : null,
                    video: videoData,
                    m3u8Links: videoData.sources
                        .map(s => s.file || s.src || s)
                        .filter(url => url && url.includes('.m3u8')),
                };

                fs.writeFileSync('megaembed-video-links.json', JSON.stringify(output, null, 2));
                console.log('💾 Links salvos em: megaembed-video-links.json\n');
            } else {
                console.log('\n⚠️ Nenhuma fonte de vídeo encontrada na resposta');
            }
        }

        console.log('='.repeat(80) + '\n');

    } catch (error) {
        console.error('\n❌ Erro:', error.message);
    }
}

// Executa
extractMegaEmbedVideo();
