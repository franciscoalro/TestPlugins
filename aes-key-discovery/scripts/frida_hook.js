// Frida script para hook em crypto.subtle
// Uso: frida -U Chrome -l frida_hook.js

console.log("[*] Frida Crypto Hook iniciado");

// Hook em crypto.subtle.importKey
if (typeof crypto !== 'undefined' && crypto.subtle) {
    const originalImportKey = crypto.subtle.importKey;
    
    crypto.subtle.importKey = function() {
        console.log("\n[+] ═══════════════════════════════════════");
        console.log("[+] crypto.subtle.importKey() chamado!");
        console.log("[+] ═══════════════════════════════════════");
        
        // Argumentos
        console.log("[+] Argumentos:");
        console.log("    format:", arguments[0]);
        console.log("    keyData:", arguments[1]);
        
        // Tentar converter keyData para string
        try {
            if (arguments[1] instanceof ArrayBuffer) {
                const uint8 = new Uint8Array(arguments[1]);
                const keyString = Array.from(uint8)
                    .map(b => b.toString(16).padStart(2, '0'))
                    .join('');
                console.log("    keyData (hex):", keyString);
                
                // Tentar como texto
                const decoder = new TextDecoder();
                const keyText = decoder.decode(uint8);
                console.log("    keyData (text):", keyText);
            }
        } catch (e) {
            console.log("    [!] Erro ao converter keyData:", e);
        }
        
        console.log("    algorithm:", JSON.stringify(arguments[2]));
        console.log("    extractable:", arguments[3]);
        console.log("    keyUsages:", arguments[4]);
        
        // Stack trace
        console.log("\n[+] Stack trace:");
        console.log(new Error().stack);
        
        // Chamar função original
        return originalImportKey.apply(this, arguments);
    };
    
    console.log("[✓] Hook em crypto.subtle.importKey instalado");
}

// Hook em crypto.subtle.decrypt
if (typeof crypto !== 'undefined' && crypto.subtle) {
    const originalDecrypt = crypto.subtle.decrypt;
    
    crypto.subtle.decrypt = function() {
        console.log("\n[+] ═══════════════════════════════════════");
        console.log("[+] crypto.subtle.decrypt() chamado!");
        console.log("[+] ═══════════════════════════════════════");
        
        console.log("[+] Argumentos:");
        console.log("    algorithm:", JSON.stringify(arguments[0]));
        console.log("    key:", arguments[1]);
        
        try {
            if (arguments[2] instanceof ArrayBuffer) {
                const uint8 = new Uint8Array(arguments[2]);
                console.log("    data (primeiros 100 bytes):", 
                    Array.from(uint8.slice(0, 100))
                        .map(b => b.toString(16).padStart(2, '0'))
                        .join(''));
            }
        } catch (e) {
            console.log("    [!] Erro ao converter data:", e);
        }
        
        return originalDecrypt.apply(this, arguments);
    };
    
    console.log("[✓] Hook em crypto.subtle.decrypt instalado");
}

// Hook em TextEncoder.encode (usado para converter string em bytes)
if (typeof TextEncoder !== 'undefined') {
    const originalEncode = TextEncoder.prototype.encode;
    
    TextEncoder.prototype.encode = function(text) {
        if (text && (
            text.includes('user_id') || 
            text.includes('slug') || 
            text.includes('md5_id') ||
            text.length === 32 || // Possível MD5
            text.length === 64    // Possível SHA256
        )) {
            console.log("\n[+] ═══════════════════════════════════════");
            console.log("[+] TextEncoder.encode() - SUSPEITO!");
            console.log("[+] ═══════════════════════════════════════");
            console.log("[+] Text:", text);
            console.log("[+] Length:", text.length);
            console.log("\n[+] Stack trace:");
            console.log(new Error().stack);
        }
        
        return originalEncode.call(this, text);
    };
    
    console.log("[✓] Hook em TextEncoder.encode instalado");
}

// Hook em funções MD5 (se existirem)
setTimeout(() => {
    // Procurar por funções MD5 no window
    for (let key in window) {
        if (key.toLowerCase().includes('md5') && typeof window[key] === 'function') {
            console.log(`[*] Encontrada função MD5: ${key}`);
            
            const originalMD5 = window[key];
            window[key] = function() {
                console.log("\n[+] ═══════════════════════════════════════");
                console.log(`[+] ${key}() chamado!`);
                console.log("[+] ═══════════════════════════════════════");
                console.log("[+] Argumentos:", arguments);
                
                const result = originalMD5.apply(this, arguments);
                console.log("[+] Resultado:", result);
                
                return result;
            };
            
            console.log(`[✓] Hook em ${key} instalado`);
        }
    }
}, 2000);

console.log("\n[*] ═══════════════════════════════════════");
console.log("[*] Todos os hooks instalados!");
console.log("[*] Aguardando chamadas...");
console.log("[*] ═══════════════════════════════════════\n");
