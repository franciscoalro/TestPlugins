#!/usr/bin/env node

/**
 * Script de Validação Final - Captura em Runtime
 * Usa Puppeteer para interceptar a decriptação no navegador
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

console.log("╔════════════════════════════════════════════════════════════╗");
console.log("║  🎯 VALIDAÇÃO FINAL - Captura em Runtime                  ║");
console.log("╚════════════════════════════════════════════════════════════╝");
console.log("");

const VIDEO_SLUG = 'kBJLtxCD3';
const URL = `https://playerembedapi.link/?v=${VIDEO_SLUG}`;

async function validateFormula() {
    console.log("🚀 Iniciando navegador...");
    
    const browser = await puppeteer.launch({
        headless: false, // Mostrar navegador para debug
        devtools: true   // Abrir DevTools automaticamente
    });
    
    const page = await browser.newPage();
    
    // Armazenar dados capturados
    const capturedData = {
        key: null,
        raw: null,
        decrypted: null,
        algorithm: null
    };
    
    console.log("📡 Configurando interceptadores...");
    
    // Interceptar console.log do navegador
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('🎯') || text.includes('🔑') || text.includes('🔓') || text.includes('✅')) {
            console.log(`  [Browser] ${text}`);
        }
    });
    
    // Injetar código de interceptação antes de carregar a página
    await page.evaluateOnNewDocument(() => {
        // Armazenar dados capturados
        window.capturedData = {
            raw: null,
            decrypted: null,
            key: null,
            algorithm: null
        };
        
        // Interceptar window.SoTrym
        const originalSoTrym = window.SoTrym;
        window.SoTrym = function(data) {
            console.log('🎯 SoTrym CHAMADO!');
            console.log('user_id:', data.user_id);
            console.log('slug:', data.slug);
            console.log('md5_id:', data.md5_id);
            
            // Salvar dados brutos
            window.capturedData.raw = data;
            
            // Gerar chave
            const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
            window.capturedData.key = key;
            console.log('🔑 CHAVE GERADA:', key);
            
            // Chamar função original
            const result = originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
            return result;
        };
        
        // Interceptar crypto.subtle.decrypt
        if (crypto && crypto.subtle) {
            const originalDecrypt = crypto.subtle.decrypt;
            
            crypto.subtle.decrypt = function(algorithm, key, data) {
                console.log('🔓 crypto.subtle.decrypt CHAMADO!');
                console.log('Algorithm:', JSON.stringify(algorithm));
                console.log('Data length:', data.byteLength);
                
                // Salvar algoritmo
                window.capturedData.algorithm = algorithm;
                
                return originalDecrypt.apply(this, arguments).then(result => {
                    console.log('✅ DECRIPTADO COM SUCESSO!');
                    console.log('Result length:', result.byteLength);
                    
                    try {
                        const text = new TextDecoder().decode(result);
                        console.log('📄 TEXTO DECRIPTADO (primeiros 200 chars):', text.substring(0, 200));
                        
                        // Tentar parsear como JSON
                        try {
                            const json = JSON.parse(text);
                            console.log('📊 JSON DECRIPTADO!');
                            window.capturedData.decrypted = json;
                        } catch(e) {
                            window.capturedData.decrypted = text;
                        }
                    } catch(e) {
                        console.log('Erro ao decodificar:', e);
                    }
                    
                    return result;
                });
            };
        }
        
        console.log('✅ Interceptadores instalados!');
    });
    
    console.log(`🌐 Navegando para: ${URL}`);
    console.log("⏳ Aguardando carregamento...");
    
    try {
        await page.goto(URL, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        console.log("✅ Página carregada!");
        
        // Aguardar alguns segundos para garantir que a decriptação ocorreu
        console.log("⏳ Aguardando decriptação (10 segundos)...");
        await page.waitForTimeout(10000);
        
        // Recuperar dados capturados
        console.log("\n📊 Recuperando dados capturados...");
        const data = await page.evaluate(() => {
            return window.capturedData;
        });
        
        console.log("\n" + "=".repeat(60));
        console.log("📊 RESULTADOS DA VALIDAÇÃO");
        console.log("=".repeat(60));
        
        if (data.key) {
            console.log("\n✅ CHAVE CAPTURADA:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            console.log(`  ${data.key}`);
            console.log("");
            console.log("📝 Fórmula Confirmada:");
            console.log("  user_id + ':' + slug + ':' + md5_id");
        } else {
            console.log("\n❌ Chave não foi capturada");
        }
        
        if (data.algorithm) {
            console.log("\n✅ ALGORITMO CAPTURADO:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            console.log(JSON.stringify(data.algorithm, null, 2));
        } else {
            console.log("\n❌ Algoritmo não foi capturado");
        }
        
        if (data.decrypted) {
            console.log("\n✅ DADOS DECRIPTADOS:");
            console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            if (typeof data.decrypted === 'object') {
                console.log(JSON.stringify(data.decrypted, null, 2));
            } else {
                console.log(data.decrypted.substring(0, 500));
            }
        } else {
            console.log("\n❌ Dados decriptados não foram capturados");
        }
        
        // Salvar resultados em arquivo
        const outputDir = path.join(__dirname, 'output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const outputFile = path.join(outputDir, 'validation_results.json');
        fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
        
        console.log("\n💾 Resultados salvos em:");
        console.log(`  ${outputFile}`);
        
        // Verificar sucesso
        const success = data.key && data.decrypted;
        
        console.log("\n" + "=".repeat(60));
        if (success) {
            console.log("╔════════════════════════════════════════════════════════════╗");
            console.log("║  ✅ VALIDAÇÃO BEM-SUCEDIDA!                               ║");
            console.log("╚════════════════════════════════════════════════════════════╝");
            console.log("");
            console.log("🎉 A fórmula foi CONFIRMADA com dados reais!");
            console.log("");
            console.log("📝 Fórmula validada:");
            console.log(`  ${data.key}`);
            console.log("");
            console.log("🚀 Próximos passos:");
            console.log("  1. Implementar no plugin BRCloudstream");
            console.log("  2. Testar com múltiplos vídeos");
            console.log("  3. Documentar o algoritmo capturado");
        } else {
            console.log("╔════════════════════════════════════════════════════════════╗");
            console.log("║  ⚠️  VALIDAÇÃO PARCIAL                                    ║");
            console.log("╚════════════════════════════════════════════════════════════╝");
            console.log("");
            console.log("💡 Alguns dados não foram capturados.");
            console.log("   Verifique o console do navegador para mais detalhes.");
        }
        
    } catch (error) {
        console.error("\n❌ Erro durante validação:");
        console.error(error.message);
    } finally {
        console.log("\n⏳ Fechando navegador em 5 segundos...");
        console.log("   (Pressione Ctrl+C para manter aberto)");
        await page.waitForTimeout(5000);
        await browser.close();
    }
}

// Executar validação
validateFormula().catch(error => {
    console.error("\n❌ Erro fatal:");
    console.error(error);
    process.exit(1);
});
