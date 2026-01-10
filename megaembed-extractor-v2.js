/**
 * MegaEmbed Video Link Extractor - Versão Completa
 * Baseado no HAR capturado
 */

const https = require('https');
const fs = require('fs');

const MEGAEMBED_ID = '3wnuij';

function makeRequest(url, headers = {}) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);

        const options = {
            hostname: urlObj.hostname,
            path: urlObj.pathname + urlObj.search,
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://playerthree.online/',
                'Origin': 'https://megaembed.link',
                ...headers,
            },
        };

        https.get(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    status: res.statusCode,
                    headers: res.headers,
                    data,
                });
            });
        }).on('error', reject);
    });
}

async function extractVideo() {
    console.log('🎬 MegaEmbed Video Extractor\n');
    console.log('='.repeat(80));
    console.log(`\n📋 ID do vídeo: ${MEGAEMBED_ID}\n`);

    try {
        // 1. Tenta /api/v1/video
        console.log('📹 Tentando /api/v1/video...');
        const videoUrl = `https://megaembed.link/api/v1/video?id=${MEGAEMBED_ID}&w=1920&h=1080&r=playerthree.online`;

        const videoRes = await makeRequest(videoUrl);
        console.log(`Status: ${videoRes.status}`);
        console.log(`Content-Type: ${videoRes.headers['content-type']}`);
        console.log(`Size: ${videoRes.data.length} bytes\n`);

        // Salva resposta bruta
        fs.writeFileSync('megaembed-video-response.txt', videoRes.data);
        console.log('💾 Resposta salva em: megaembed-video-response.txt\n');

        // Tenta parsear como JSON
        try {
            const videoData = JSON.parse(videoRes.data);
            console.log('✅ JSON parseado com sucesso!\n');
            console.log(JSON.stringify(videoData, null, 2));

            // Procura por links
            const findLinks = (obj, path = '') => {
                const links = [];

                if (typeof obj === 'string') {
                    if (obj.includes('.m3u8') || obj.includes('.mp4') || obj.startsWith('http')) {
                        links.push({ path, url: obj });
                    }
                } else if (Array.isArray(obj)) {
                    obj.forEach((item, i) => {
                        links.push(...findLinks(item, `${path}[${i}]`));
                    });
                } else if (typeof obj === 'object' && obj !== null) {
                    Object.keys(obj).forEach(key => {
                        links.push(...findLinks(obj[key], path ? `${path}.${key}` : key));
                    });
                }

                return links;
            };

            const links = findLinks(videoData);

            if (links.length > 0) {
                console.log('\n\n' + '='.repeat(80));
                console.log('🎯 LINKS ENCONTRADOS!');
                console.log('='.repeat(80) + '\n');

                links.forEach((link, i) => {
                    console.log(`${i + 1}. ${link.path}`);
                    console.log(`   ${link.url}\n`);

                    if (link.url.includes('.m3u8')) {
                        console.log(`   🎬 VLC: vlc "${link.url}"\n`);
                    }
                });

                // Salva links
                fs.writeFileSync('video-links.json', JSON.stringify({ links, fullData: videoData }, null, 2));
                console.log('💾 Links salvos em: video-links.json');
            } else {
                console.log('\n⚠️ Nenhum link de vídeo encontrado no JSON');
            }

        } catch (e) {
            console.log('⚠️ Resposta não é JSON válido');
            console.log('Primeiros 500 caracteres:');
            console.log(videoRes.data.substring(0, 500));
            console.log('\n💡 Verifique o arquivo megaembed-video-response.txt para ver a resposta completa');
        }

        console.log('\n' + '='.repeat(80) + '\n');

    } catch (error) {
        console.error('❌ Erro:', error.message);
    }
}

extractVideo();
