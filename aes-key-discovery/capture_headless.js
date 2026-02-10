#!/usr/bin/env node

/**
 * Captura Headless - PlayerEmbedAPI
 * Contorna proteção anti-debug automaticamente
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const VIDEO_SLUG = 'kBJLtxCD3';
const URL = `https://playerembedapi.link/?v=${VIDEO_SLUG}`;

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║  🎯 CAPTURA HEADLESS - PlayerEmbedAPI                         ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
console.log('');

async function captureAlgorithm() {
    console.log('🚀 Iniciando navegador headless...');
    
    const browser = await puppeteer.launch({
        headless: false, // Mostrar navegador para debug
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', // Usar Chrome do sistema
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ],
        ignoreDefaultArgs: ['--enable-automation']
    });
    
    const page = await browser.newPage();
    
    // Configurar user agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Remover webdriver flag
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
    });
    
    console.log('📡 Configurando interceptadores...');
    
    // Armazenar dados capturados
    const capturedData = {
        key: null,
        algorithm: null,
        decrypted: null,
        rawData: null,
        logs: []
    };
    
    // Capturar logs do console
    page.on('console', msg => {
        const text = msg.text();
        capturedData.logs.push(text);
        
        if (text.includes('🎯') || text.includes('🔑') || text.includes('🔓') || text.includes('✅')) {
            console.log(`  [Browser] ${text}`);
        }
    });
    
    // Injetar código ANTES da página carregar
    await page.evaluateOnNewDocument(() => {
        // ============================================================
        // ANTI-DEBUG: Desabilitar debugger
        // ============================================================
        
        (function() {
            // Sobrescrever Function constructor
            const OriginalFunction = Function;
            window.Function = new Proxy(OriginalFunction, {
                construct(target, args) {
                    const code = args[args.length - 1];
                    if (typeof code === 'string' && code.includes('debugger')) {
                        // Remover todos os debugger statements
                        args[args.length - 1] = code.replace(/debugger/g, '');
                    }
                    return new target(...args);
                }
            });
            
            // Desabilitar debugger global
            window.debugger = () => {};
        })();
        
        // ============================================================
        // CAPTURA: Interceptar dados
        // ============================================================
        
        window.algorithmData = {
            key: null,
            algorithm: null,
            decrypted: null,
            rawData: null
        };
        
        // Interceptar window.SoTrym
        setTimeout(() => {
            const originalSoTrym = window.SoTrym;
            
            window.SoTrym = function(data) {
                console.log('🎯 DADOS CAPTURADOS!');
                
                window.algorithmData.rawData = data;
                
                console.log('user_id:', data.user_id);
                console.log('slug:', data.slug);
                console.log('md5_id:', data.md5_id);
                
                const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
                window.algorithmData.key = key;
                
                console.log('🔑 CHAVE:', key);
                
                return originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
            };
        }, 100);
        
        // Interceptar crypto.subtle.importKey
        setTimeout(() => {
            if (!crypto || !crypto.subtle) return;
            
            const originalImportKey = crypto.subtle.importKey;
            
            crypto.subtle.importKey = function(format, keyData, algorithm, extractable, keyUsages) {
                console.log('🔑 IMPORTANDO CHAVE');
                console.log('Format:', format);
                console.log('Algorithm:', JSON.stringify(algorithm));
                
                try {
                    if (keyData.byteLength) {
                        const keyArray = new Uint8Array(keyData);
                        const keyHex = Array.from(keyArray).map(b => b.toString(16).padStart(2, '0')).join('');
                        console.log('Key (hex):', keyHex.substring(0, 64) + '...');
                        console.log('Key length:', keyArray.length, 'bytes');
                    }
                } catch(e) {}
                
                return originalImportKey.apply(this, arguments);
            };
        }, 100);
        
        // Interceptar crypto.subtle.decrypt
        setTimeout(() => {
            if (!crypto || !crypto.subtle) return;
            
            const originalDecrypt = crypto.subtle.decrypt;
            
            crypto.subtle.decrypt = function(algorithm, key, data) {
                console.log('🔓 ALGORITMO CAPTURADO!');
                
                window.algorithmData.algorithm = {
                    name: algorithm.name,
                    ...algorithm
                };
                
                console.log('Algoritmo:', JSON.stringify(algorithm, null, 2));
                console.log('Data length:', data.byteLength);
                
                return originalDecrypt.apply(this, arguments).then(result => {
                    console.log('✅ DECRIPTADO!');
                    console.log('Result length:', result.byteLength);
                    
                    try {
                        const text = new TextDecoder().decode(result);
                        const json = JSON.parse(text);
                        
                        console.log('📄 DADOS:', JSON.stringify(json).substring(0, 200) + '...');
                        
                        window.algorithmData.decrypted = json;
                        
                    } catch(e) {
                        console.log('Erro ao parsear:', e.message);
                    }
                    
                    return result;
                });
            };
        }, 100);
        
        console.log('✅ INTERCEPTADORES INSTALADOS!');
    });
    
    console.log(`🌐 Navegando para: ${URL}`);
    console.log('⏳ Aguardando carregamento...');
    
    try {
        await page.goto(URL, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        console.log('✅ Página carregada!');
        
        // Aguardar decriptação
        console.log('⏳ Aguardando decriptação (15 segundos)...');
        await page.waitForTimeout(15000);
        
        // Recuperar dados capturados
        console.log('\n📊 Recuperando dados capturados...');
        const data = await page.evaluate(() => {
            return window.algorithmData;
        });
        
        // Processar dados
        console.log('\n' + '='.repeat(60));
        console.log('📊 RESULTADOS DA CAPTURA');
        console.log('='.repeat(60));
        
        if (data.key) {
            console.log('\n✅ CHAVE CAPTURADA:');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`  ${data.key}`);
            console.log('');
            console.log('📝 Fórmula:');
            console.log('  user_id + ":" + slug + ":" + md5_id');
            capturedData.key = data.key;
        } else {
            console.log('\n❌ Chave não foi capturada');
        }
        
        if (data.algorithm) {
            console.log('\n✅ ALGORITMO CAPTURADO:');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(JSON.stringify(data.algorithm, null, 2));
            capturedData.algorithm = data.algorithm;
        } else {
            console.log('\n❌ Algoritmo não foi capturado');
        }
        
        if (data.decrypted) {
            console.log('\n✅ DADOS DECRIPTADOS:');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(JSON.stringify(data.decrypted, null, 2));
            capturedData.decrypted = data.decrypted;
        } else {
            console.log('\n❌ Dados decriptados não foram capturados');
        }
        
        if (data.rawData) {
            capturedData.rawData = data.rawData;
        }
        
        // Salvar resultados
        const outputDir = path.join(__dirname, 'output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const outputFile = path.join(outputDir, 'algorithm_captured.json');
        fs.writeFileSync(outputFile, JSON.stringify({
            timestamp: new Date().toISOString(),
            video_slug: VIDEO_SLUG,
            key: capturedData.key,
            algorithm: capturedData.algorithm,
            decrypted: capturedData.decrypted,
            rawData: capturedData.rawData,
            logs: capturedData.logs
        }, null, 2));
        
        console.log('\n💾 Resultados salvos em:');
        console.log(`  ${outputFile}`);
        
        // Verificar sucesso
        const success = capturedData.key && capturedData.algorithm && capturedData.decrypted;
        
        console.log('\n' + '='.repeat(60));
        if (success) {
            console.log('╔════════════════════════════════════════════════════════════════╗');
            console.log('║  ✅ CAPTURA BEM-SUCEDIDA!                                     ║');
            console.log('╚════════════════════════════════════════════════════════════════╝');
            console.log('');
            console.log('🎉 Todos os dados foram capturados com sucesso!');
            console.log('');
            console.log('📝 Resumo:');
            console.log(`  • Chave: ${capturedData.key}`);
            console.log(`  • Algoritmo: ${capturedData.algorithm?.name || 'N/A'}`);
            console.log(`  • Dados decriptados: ${capturedData.decrypted ? 'Sim' : 'Não'}`);
            console.log('');
            console.log('🚀 Próximos passos:');
            console.log('  1. Abra: output/algorithm_captured.json');
            console.log('  2. Analise o algoritmo capturado');
            console.log('  3. Implemente no plugin BRCloudstream');
        } else {
            console.log('╔════════════════════════════════════════════════════════════════╗');
            console.log('║  ⚠️  CAPTURA PARCIAL                                          ║');
            console.log('╚════════════════════════════════════════════════════════════════╝');
            console.log('');
            console.log('⚠️  Alguns dados não foram capturados.');
            console.log('');
            console.log('📊 Status:');
            console.log(`  • Chave: ${capturedData.key ? '✅' : '❌'}`);
            console.log(`  • Algoritmo: ${capturedData.algorithm ? '✅' : '❌'}`);
            console.log(`  • Dados decriptados: ${capturedData.decrypted ? '✅' : '❌'}`);
            console.log('');
            console.log('💡 Possíveis causas:');
            console.log('  1. Página não carregou completamente');
            console.log('  2. Proteção anti-bot mais forte');
            console.log('  3. Estrutura do site mudou');
            console.log('');
            console.log('🔧 Tente:');
            console.log('  1. Executar novamente');
            console.log('  2. Aumentar o tempo de espera');
            console.log('  3. Usar método manual (CAPTURAR_SEM_DEBUGGER.md)');
        }
        
    } catch (error) {
        console.error('\n❌ Erro durante captura:');
        console.error(error.message);
        
        // Salvar erro
        const errorFile = path.join(__dirname, 'output', 'capture_error.txt');
        fs.writeFileSync(errorFile, `
Erro: ${error.message}
Stack: ${error.stack}
Timestamp: ${new Date().toISOString()}
        `);
        
        console.log(`\n💾 Erro salvo em: ${errorFile}`);
    } finally {
        console.log('\n⏳ Fechando navegador...');
        await browser.close();
    }
}

// Executar captura
captureAlgorithm().catch(error => {
    console.error('\n❌ Erro fatal:');
    console.error(error);
    process.exit(1);
});
