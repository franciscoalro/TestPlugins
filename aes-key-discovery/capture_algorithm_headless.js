#!/usr/bin/env node

/**
 * Script Automatizado - Captura de Algoritmo de Decriptação
 * Usa Playwright em modo headless (funciona no WSL)
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const VIDEO_SLUG = 'kBJLtxCD3';
const URL = `https://playerembedapi.link/?v=${VIDEO_SLUG}`;
const OUTPUT_DIR = path.join(__dirname, 'output');

console.log("╔════════════════════════════════════════════════════════════╗");
console.log("║  🤖 CAPTURA AUTOMATIZADA - Algoritmo de Decriptação      ║");
console.log("╚════════════════════════════════════════════════════════════╝");
console.log("");

async function captureAlgorithm() {
    let browser;
    
    try {
        console.log("🚀 Iniciando navegador headless...");
        
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });
        
        const page = await context.newPage();
        
        // Armazenar dados capturados
        const capturedData = {
            key: null,
            algorithm: null,
            decrypted: null,
            raw: null,
            logs: []
        };
        
        // Capturar console.log do navegador
        page.on('console', msg => {
            const text = msg.text();
            capturedData.logs.push(text);
            console.log(`  [Browser] ${text}`);
        });
        
        console.log("📡 Injetando interceptadores...");
        
        // Injetar código de interceptação
        await page.addInitScript(() => {
            // Armazenar dados capturados
            window.capturedData = {
                raw: null,
                decrypted: null,
                key: null,
                algorithm: null,
                keyDetails: null
            };
            
            // Interceptar window.SoTrym
            const originalSoTrym = window.SoTrym;
            window.SoTrym = function(data) {
                console.log('🎯 SoTrym CHAMADO!');
                
                // Salvar dados brutos
                window.capturedData.raw = data;
                
                // Gerar chave
                const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
                window.capturedData.key = key;
                console.log('🔑 CHAVE:', key);
                
                // Chamar função original
                const result = originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
                return result;
            };
            
            // Interceptar crypto.subtle.importKey
            if (crypto && crypto.subtle) {
                const originalImportKey = crypto.subtle.importKey;
                
                crypto.subtle.importKey = function(format, keyData, algorithm, extractable, keyUsages) {
                    console.log('🔑 crypto.subtle.importKey CHAMADO!');
                    console.log('Format:', format);
                    console.log('Algorithm:', JSON.stringify(algorithm));
                    console.log('Extractable:', extractable);
                    console.log('Key usages:', JSON.stringify(keyUsages));
                    
                    // Tentar extrair a chave
                    try {
                        if (keyData.byteLength) {
                            const keyArray = new Uint8Array(keyData);
                            const keyHex = Array.from(keyArray).map(b => b.toString(16).padStart(2, '0')).join('');
                            console.log('Key (hex, primeiros 64 chars):', keyHex.substring(0, 64));
                            
                            window.capturedData.keyDetails = {
                                format: format,
                                algorithm: algorithm,
                                length: keyData.byteLength,
                                hex: keyHex
                            };
                        }
                    } catch(e) {
                        console.log('Erro ao extrair chave:', e.message);
                    }
                    
                    return originalImportKey.apply(this, arguments);
                };
            }
            
            // Interceptar crypto.subtle.decrypt
            if (crypto && crypto.subtle) {
                const originalDecrypt = crypto.subtle.decrypt;
                
                crypto.subtle.decrypt = function(algorithm, key, data) {
                    console.log('🔓 crypto.subtle.decrypt CHAMADO!');
                    console.log('Algorithm:', JSON.stringify(algorithm));
                    console.log('Data length:', data.byteLength);
                    
                    // Salvar algoritmo
                    window.capturedData.algorithm = {
                        name: algorithm.name,
                        details: algorithm
                    };
                    
                    // Tentar extrair IV/Counter se houver
                    if (algorithm.counter) {
                        const counterArray = new Uint8Array(algorithm.counter);
                        const counterHex = Array.from(counterArray).map(b => b.toString(16).padStart(2, '0')).join('');
                        console.log('Counter (hex):', counterHex);
                        window.capturedData.algorithm.counterHex = counterHex;
                    }
                    
                    if (algorithm.iv) {
                        const ivArray = new Uint8Array(algorithm.iv);
                        const ivHex = Array.from(ivArray).map(b => b.toString(16).padStart(2, '0')).join('');
                        console.log('IV (hex):', ivHex);
                        window.capturedData.algorithm.ivHex = ivHex;
                    }
                    
                    return originalDecrypt.apply(this, arguments).then(result => {
                        console.log('✅ DECRIPTADO COM SUCESSO!');
                        console.log('Result length:', result.byteLength);
                        
                        try {
                            const text = new TextDecoder().decode(result);
                            console.log('📄 TEXTO DECRIPTADO (primeiros 500 chars):', text.substring(0, 500));
                            
                            // Tentar parsear como JSON
                            try {
                                const json = JSON.parse(text);
                                console.log('📊 JSON DECRIPTADO!');
                                window.capturedData.decrypted = json;
                            } catch(e) {
                                window.capturedData.decrypted = text;
                            }
                        } catch(e) {
                            console.log('Erro ao decodificar:', e.message);
                        }
                        
                        return result;
                    }).catch(error => {
                        console.error('❌ ERRO NA DECRIPTAÇÃO:', error.message);
                        throw error;
                    });
                };
            }
            
            console.log('✅ Interceptadores instalados!');
        });
        
        console.log(`🌐 Navegando para: ${URL}`);
        console.log("⏳ Aguardando carregamento...");
        
        await page.goto(URL, {
            waitUntil: 'networkidle',
            timeout: 30000
        });
        
        console.log("✅ Página carregada!");
        
        // Aguardar decriptação
        console.log("⏳ Aguardando decriptação (15 segundos)...");
        await page.waitForTimeout(15000);
        
        // Recuperar dados capturados
        console.log("\n📊 Recuperando dados capturados...");
        const data = await page.evaluate(() => {
            return window.capturedData;
        });
        
        // Mesclar com logs
        capturedData.key = data.key;
        capturedData.algorithm = data.algorithm;
        capturedData.decrypted = data.decrypted;
        capturedData.raw = data.raw;
        capturedData.keyDetails = data.keyDetails;
        
        // Salvar resultados
        if (!fs.existsSync(OUTPUT_DIR)) {
            fs.mkdirSync(OUTPUT_DIR, { recursive: true });
        }
        
        const outputFile = path.join(OUTPUT_DIR, 'algorithm_captured.json');
        fs.writeFileSync(outputFile, JSON.stringify(capturedData, null, 2));
        
        console.log("\n" + "=".repeat(60));
        console.log("📊 RESULTADOS DA CAPTURA");
        console.log("=".repeat(60));
        
        if (capturedData.key) {
            console.log("\n✅ CHAVE CAPTURADA:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            console.log(`  ${capturedData.key}`);
        } else {
            console.log("\n❌ Chave não foi capturada");
        }
        
        if (capturedData.algorithm) {
            console.log("\n✅ ALGORITMO CAPTURADO:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            console.log(JSON.stringify(capturedData.algorithm, null, 2));
        } else {
            console.log("\n❌ Algoritmo não foi capturado");
        }
        
        if (capturedData.keyDetails) {
            console.log("\n✅ DETALHES DA CHAVE:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            console.log(`  Format: ${capturedData.keyDetails.format}`);
            console.log(`  Algorithm: ${JSON.stringify(capturedData.keyDetails.algorithm)}`);
            console.log(`  Length: ${capturedData.keyDetails.length} bytes`);
            console.log(`  Hex (primeiros 64 chars): ${capturedData.keyDetails.hex.substring(0, 64)}`);
        }
        
        if (capturedData.decrypted) {
            console.log("\n✅ DADOS DECRIPTADOS:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            if (typeof capturedData.decrypted === 'object') {
                console.log(JSON.stringify(capturedData.decrypted, null, 2).substring(0, 1000));
            } else {
                console.log(capturedData.decrypted.substring(0, 500));
            }
        } else {
            console.log("\n❌ Dados decriptados não foram capturados");
        }
        
        console.log("\n💾 Resultados salvos em:");
        console.log(`  ${outputFile}`);
        
        // Verificar sucesso
        const success = capturedData.key && capturedData.algorithm && capturedData.decrypted;
        
        console.log("\n" + "=".repeat(60));
        if (success) {
            console.log("╔════════════════════════════════════════════════════════════╗");
            console.log("║  ✅ CAPTURA BEM-SUCEDIDA!                                 ║");
            console.log("╚════════════════════════════════════════════════════════════╝");
            console.log("");
            console.log("🎉 Algoritmo capturado com sucesso!");
            console.log("");
            console.log("📝 Informações capturadas:");
            console.log(`  • Chave: ${capturedData.key}`);
            console.log(`  • Algoritmo: ${capturedData.algorithm.name}`);
            console.log(`  • Dados decriptados: ${typeof capturedData.decrypted === 'object' ? 'JSON' : 'String'}`);
            console.log("");
            console.log("🚀 Próximo passo:");
            console.log("  Implementar no plugin BRCloudstream usando IMPLEMENTACAO_PLUGIN.md");
        } else {
            console.log("╔════════════════════════════════════════════════════════════╗");
            console.log("║  ⚠️  CAPTURA PARCIAL                                      ║");
            console.log("╚════════════════════════════════════════════════════════════╝");
            console.log("");
            console.log("💡 Alguns dados não foram capturados.");
            console.log("   Verifique os logs acima para mais detalhes.");
            console.log("");
            console.log("🔧 Possíveis soluções:");
            console.log("  1. Executar novamente (pode ser timing)");
            console.log("  2. Verificar se o vídeo ainda existe");
            console.log("  3. Usar método manual (SOLUCAO_FINAL.md)");
        }
        
        return success;
        
    } catch (error) {
        console.error("\n❌ Erro durante captura:");
        console.error(error.message);
        console.error(error.stack);
        return false;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Executar captura
captureAlgorithm().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error("\n❌ Erro fatal:");
    console.error(error);
    process.exit(1);
});
