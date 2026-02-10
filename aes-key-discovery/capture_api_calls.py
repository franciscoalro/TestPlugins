#!/usr/bin/env python3

"""
Script para capturar chamadas da API usando o navegador
Intercepta requisições e extrai dados criptografados
"""

import json
import time
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
except ImportError:
    print("❌ Selenium não instalado!")
    print("   Instale com: pip install selenium")
    sys.exit(1)

def setup_driver():
    """Configura o driver do Chrome com logging de rede"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Remova para ver o navegador
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Habilitar logging de rede
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_api_calls(driver):
    """Extrai chamadas da API dos logs de performance"""
    logs = driver.get_log('performance')
    api_calls = []
    
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            
            # Procurar por requisições de rede
            if log['method'] == 'Network.responseReceived':
                response = log['params']['response']
                url = response['url']
                
                # Filtrar apenas chamadas da API
                if 'playerembedapi.link' in url and '/api/' in url:
                    api_calls.append({
                        'url': url,
                        'status': response['status'],
                        'headers': response['headers'],
                        'requestId': log['params']['requestId']
                    })
        except:
            pass
    
    return api_calls

def get_response_body(driver, request_id):
    """Obtém o corpo da resposta de uma requisição"""
    try:
        body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
        return body
    except:
        return None

def capture_video_data(video_id):
    """Captura dados do vídeo"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🌐 Captura de Chamadas da API                           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    url = f"https://playerembedapi.link/?v={video_id}"
    print(f"📡 Acessando: {url}")
    print()
    
    driver = setup_driver()
    
    try:
        # Acessar a página
        driver.get(url)
        print("✅ Página carregada")
        
        # Aguardar um pouco para as requisições serem feitas
        print("⏳ Aguardando requisições da API...")
        time.sleep(5)
        
        # Extrair chamadas da API
        print("🔍 Analisando logs de rede...")
        api_calls = extract_api_calls(driver)
        
        if not api_calls:
            print("❌ Nenhuma chamada da API encontrada")
            print()
            print("💡 Possíveis razões:")
            print("  1. Vídeo não existe ou foi removido")
            print("  2. API mudou de endpoint")
            print("  3. Requisição bloqueada por CORS")
            print()
            print("🔧 Tente:")
            print("  1. Usar um vídeo diferente")
            print("  2. Abrir o navegador sem --headless")
            print("  3. Usar DevTools manualmente")
            return None
        
        print(f"✅ Encontradas {len(api_calls)} chamadas da API\n")
        
        # Processar cada chamada
        results = []
        for i, call in enumerate(api_calls, 1):
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Chamada #{i}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  URL: {call['url']}")
            print(f"  Status: {call['status']}")
            
            # Tentar obter o corpo da resposta
            body = get_response_body(driver, call['requestId'])
            if body:
                try:
                    data = json.loads(body['body'])
                    print(f"  ✅ Resposta capturada!")
                    print()
                    print("📄 Dados:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    results.append(data)
                except:
                    print(f"  ⚠️  Resposta não é JSON")
                    print(f"  Body: {body.get('body', 'N/A')[:200]}...")
            else:
                print(f"  ❌ Não foi possível obter o corpo da resposta")
            print()
        
        return results
        
    except TimeoutException:
        print("❌ Timeout ao carregar a página")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        driver.quit()

def main():
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = "kBJLtxCD3"
    
    print("\n" + "="*60)
    print("  🌐 CAPTURA DE CHAMADAS DA API")
    print("="*60 + "\n")
    
    results = capture_video_data(video_id)
    
    if results:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ✅ CAPTURA CONCLUÍDA!                                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print(f"📊 Total de respostas capturadas: {len(results)}")
        print()
        
        # Salvar em arquivo
        output_file = f"output/api_response_{video_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos em: {output_file}")
        print()
        print("🚀 Próximo passo:")
        print(f"   python test_manual_decryption.py")
    else:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ❌ FALHA NA CAPTURA                                      ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("💡 Alternativas:")
        print("  1. Usar DevTools do navegador manualmente")
        print("  2. Usar Burp Suite para interceptar")
        print("  3. Usar mitmproxy")
        print("  4. Verificar se o vídeo existe")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
