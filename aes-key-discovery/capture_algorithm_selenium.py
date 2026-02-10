#!/usr/bin/env python3

"""
Script Automatizado - Captura de Algoritmo de Decriptação
Usa Selenium com Chrome headless (funciona no WSL)
"""

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VIDEO_SLUG = 'kBJLtxCD3'
URL = f'https://playerembedapi.link/?v={VIDEO_SLUG}'
OUTPUT_DIR = 'output'

print("╔════════════════════════════════════════════════════════════╗")
print("║  🤖 CAPTURA AUTOMATIZADA - Algoritmo de Decriptação      ║")
print("╚════════════════════════════════════════════════════════════╝")
print("")

def setup_driver():
    """Configura o Chrome em modo headless"""
    print("🚀 Configurando Chrome headless...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Habilitar logs do console
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Erro ao iniciar Chrome: {e}")
        print("")
        print("💡 Instale o Chrome e ChromeDriver:")
        print("  sudo apt-get update")
        print("  sudo apt-get install -y chromium-browser chromium-chromedriver")
        return None

def inject_interceptors(driver):
    """Injeta código JavaScript para interceptar crypto.subtle"""
    print("📡 Injetando interceptadores...")
    
    interceptor_script = """
    // Armazenar dados capturados
    window.capturedData = {
        raw: null,
        decrypted: null,
        key: null,
        algorithm: null,
        keyDetails: null,
        logs: []
    };
    
    // Função para logar
    window.logCapture = function(msg) {
        window.capturedData.logs.push(msg);
        console.log('[CAPTURE] ' + msg);
    };
    
    // Interceptar window.SoTrym
    (function() {
        const originalSoTrym = window.SoTrym;
        window.SoTrym = function(data) {
            window.logCapture('🎯 SoTrym CHAMADO!');
            
            // Salvar dados brutos
            window.capturedData.raw = data;
            
            // Gerar chave
            const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
            window.capturedData.key = key;
            window.logCapture('🔑 CHAVE: ' + key);
            
            // Chamar função original
            const result = originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
            return result;
        };
    })();
    
    // Interceptar crypto.subtle.importKey
    if (crypto && crypto.subtle) {
        const originalImportKey = crypto.subtle.importKey;
        
        crypto.subtle.importKey = function(format, keyData, algorithm, extractable, keyUsages) {
            window.logCapture('🔑 crypto.subtle.importKey CHAMADO!');
            window.logCapture('Format: ' + format);
            window.logCapture('Algorithm: ' + JSON.stringify(algorithm));
            
            // Tentar extrair a chave
            try {
                if (keyData.byteLength) {
                    const keyArray = new Uint8Array(keyData);
                    const keyHex = Array.from(keyArray).map(b => b.toString(16).padStart(2, '0')).join('');
                    window.logCapture('Key (hex, primeiros 64 chars): ' + keyHex.substring(0, 64));
                    
                    window.capturedData.keyDetails = {
                        format: format,
                        algorithm: algorithm,
                        length: keyData.byteLength,
                        hex: keyHex
                    };
                }
            } catch(e) {
                window.logCapture('Erro ao extrair chave: ' + e.message);
            }
            
            return originalImportKey.apply(this, arguments);
        };
    }
    
    // Interceptar crypto.subtle.decrypt
    if (crypto && crypto.subtle) {
        const originalDecrypt = crypto.subtle.decrypt;
        
        crypto.subtle.decrypt = function(algorithm, key, data) {
            window.logCapture('🔓 crypto.subtle.decrypt CHAMADO!');
            window.logCapture('Algorithm: ' + JSON.stringify(algorithm));
            window.logCapture('Data length: ' + data.byteLength);
            
            // Salvar algoritmo
            window.capturedData.algorithm = {
                name: algorithm.name,
                details: JSON.parse(JSON.stringify(algorithm))
            };
            
            // Tentar extrair IV/Counter se houver
            if (algorithm.counter) {
                const counterArray = new Uint8Array(algorithm.counter);
                const counterHex = Array.from(counterArray).map(b => b.toString(16).padStart(2, '0')).join('');
                window.logCapture('Counter (hex): ' + counterHex);
                window.capturedData.algorithm.counterHex = counterHex;
            }
            
            if (algorithm.iv) {
                const ivArray = new Uint8Array(algorithm.iv);
                const ivHex = Array.from(ivArray).map(b => b.toString(16).padStart(2, '0')).join('');
                window.logCapture('IV (hex): ' + ivHex);
                window.capturedData.algorithm.ivHex = ivHex;
            }
            
            return originalDecrypt.apply(this, arguments).then(result => {
                window.logCapture('✅ DECRIPTADO COM SUCESSO!');
                window.logCapture('Result length: ' + result.byteLength);
                
                try {
                    const text = new TextDecoder().decode(result);
                    window.logCapture('📄 TEXTO DECRIPTADO (primeiros 200 chars): ' + text.substring(0, 200));
                    
                    // Tentar parsear como JSON
                    try {
                        const json = JSON.parse(text);
                        window.logCapture('📊 JSON DECRIPTADO!');
                        window.capturedData.decrypted = json;
                    } catch(e) {
                        window.capturedData.decrypted = text;
                    }
                } catch(e) {
                    window.logCapture('Erro ao decodificar: ' + e.message);
                }
                
                return result;
            }).catch(error => {
                window.logCapture('❌ ERRO NA DECRIPTAÇÃO: ' + error.message);
                throw error;
            });
        };
    }
    
    window.logCapture('✅ Interceptadores instalados!');
    """
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': interceptor_script
    })

def capture_algorithm():
    """Executa a captura do algoritmo"""
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        # Injetar interceptadores
        inject_interceptors(driver)
        
        print(f"🌐 Navegando para: {URL}")
        print("⏳ Aguardando carregamento...")
        
        driver.get(URL)
        
        print("✅ Página carregada!")
        
        # Aguardar decriptação
        print("⏳ Aguardando decriptação (15 segundos)...")
        time.sleep(15)
        
        # Recuperar dados capturados
        print("\n📊 Recuperando dados capturados...")
        captured_data = driver.execute_script("return window.capturedData;")
        
        # Recuperar logs do console
        console_logs = driver.get_log('browser')
        for log in console_logs:
            if '[CAPTURE]' in log['message']:
                print(f"  [Browser] {log['message']}")
        
        # Criar diretório de saída
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Salvar resultados
        output_file = os.path.join(OUTPUT_DIR, 'algorithm_captured.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(captured_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DA CAPTURA")
        print("=" * 60)
        
        if captured_data.get('key'):
            print("\n✅ CHAVE CAPTURADA:")
            print("━" * 60)
            print(f"  {captured_data['key']}")
        else:
            print("\n❌ Chave não foi capturada")
        
        if captured_data.get('algorithm'):
            print("\n✅ ALGORITMO CAPTURADO:")
            print("━" * 60)
            print(json.dumps(captured_data['algorithm'], indent=2))
        else:
            print("\n❌ Algoritmo não foi capturado")
        
        if captured_data.get('keyDetails'):
            print("\n✅ DETALHES DA CHAVE:")
            print("━" * 60)
            details = captured_data['keyDetails']
            print(f"  Format: {details.get('format')}")
            print(f"  Algorithm: {json.dumps(details.get('algorithm'))}")
            print(f"  Length: {details.get('length')} bytes")
            if details.get('hex'):
                print(f"  Hex (primeiros 64 chars): {details['hex'][:64]}")
        
        if captured_data.get('decrypted'):
            print("\n✅ DADOS DECRIPTADOS:")
            print("━" * 60)
            decrypted = captured_data['decrypted']
            if isinstance(decrypted, dict):
                print(json.dumps(decrypted, indent=2)[:1000])
            else:
                print(str(decrypted)[:500])
        else:
            print("\n❌ Dados decriptados não foram capturados")
        
        print(f"\n💾 Resultados salvos em:")
        print(f"  {output_file}")
        
        # Verificar sucesso
        success = (captured_data.get('key') and 
                  captured_data.get('algorithm') and 
                  captured_data.get('decrypted'))
        
        print("\n" + "=" * 60)
        if success:
            print("╔════════════════════════════════════════════════════════════╗")
            print("║  ✅ CAPTURA BEM-SUCEDIDA!                                 ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print("")
            print("🎉 Algoritmo capturado com sucesso!")
            print("")
            print("📝 Informações capturadas:")
            print(f"  • Chave: {captured_data['key']}")
            print(f"  • Algoritmo: {captured_data['algorithm']['name']}")
            print(f"  • Dados decriptados: {'JSON' if isinstance(captured_data['decrypted'], dict) else 'String'}")
            print("")
            print("🚀 Próximo passo:")
            print("  Implementar no plugin BRCloudstream usando IMPLEMENTACAO_PLUGIN.md")
        else:
            print("╔════════════════════════════════════════════════════════════╗")
            print("║  ⚠️  CAPTURA PARCIAL                                      ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print("")
            print("💡 Alguns dados não foram capturados.")
            print("   Verifique os logs acima para mais detalhes.")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Erro durante captura:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == '__main__':
    try:
        success = capture_algorithm()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
