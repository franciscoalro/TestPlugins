#!/usr/bin/env python3
"""
Captura COMPLETA de rede do MegaEmbed
- Intercepta TODAS as requisições e respostas
- Salva headers completos
- Analisa cookies e tokens
- Permite replicar requisições
"""

import json
import time
import subprocess
import sys
from datetime import datetime

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    print("Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

# URL de teste
TEST_URL = "https://megaembed.link/#Yzg0NjI0NjI="
OUTPUT_FILE = "network_capture_full.json"

def capture_network():
    print(f"\n{'='*70}")
    print("CAPTURA COMPLETA DE REDE - MEGAEMBED")
    print(f"{'='*70}")
    print(f"URL: {TEST_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Configurar selenium-wire para capturar tudo
    seleniumwire_options = {
        'disable_encoding': True,
        'suppress_connection_errors': False,
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    all_requests = []
    video_urls = []
    
    try:
        print(f"\n[*] Abrindo página...")
        driver.get(TEST_URL)
        time.sleep(3)
        
        # Tentar clicar no play
        print("[*] Tentando clicar no play...")
        try:
            for selector in ["#play", ".play-button", "button", "[class*='play']"]:
                try:
                    btn = driver.find_element(By.CSS_SELECTOR, selector)
                    btn.click()
                    print(f"  [+] Clicou em: {selector}")
                    break
                except:
                    pass
        except:
            pass
        
        print("[*] Aguardando requisições (15s)...")
        time.sleep(15)
        
        print(f"\n[*] Processando {len(driver.requests)} requisições...")
        
        for req in driver.requests:
            req_data = {
                "url": req.url,
                "method": req.method,
                "request_headers": dict(req.headers) if req.headers else {},
                "response": None
            }
            
            if req.response:
                resp_headers = dict(req.response.headers) if req.response.headers else {}
                content_type = resp_headers.get('Content-Type', '')
                
                # Tentar decodificar body
                body = None
                body_preview = None
                if req.response.body:
                    try:
                        body = req.response.body.decode('utf-8', errors='ignore')
                        body_preview = body[:500] if len(body) > 500 else body
                    except:
                        body_preview = f"[Binary: {len(req.response.body)} bytes]"
                
                req_data["response"] = {
                    "status_code": req.response.status_code,
                    "headers": resp_headers,
                    "content_type": content_type,
                    "body_preview": body_preview,
                    "body_full": body if body and len(body) < 10000 else None
                }
                
                # Identificar URLs de vídeo
                url_lower = req.url.lower()
                if any(ext in url_lower for ext in ['.m3u8', '.mp4', 'master.txt', '/hls/', '/stream/']):
                    if '.js' not in url_lower:
                        video_urls.append({
                            "url": req.url,
                            "headers": req_data["request_headers"],
                            "response_headers": resp_headers
                        })
            
            all_requests.append(req_data)
            
            # Mostrar requisições importantes
            if 'megaembed' in req.url or 'api' in req.url:
                status = req.response.status_code if req.response else "N/A"
                print(f"\n  [{req.method}] {req.url[:80]}")
                print(f"      Status: {status}")
        
        # Capturar cookies
        cookies = driver.get_cookies()
        
        # Executar JS para capturar variáveis
        js_vars = driver.execute_script("""
            var result = {};
            try {
                if (window.source) result.source = window.source;
                if (window.file) result.file = window.file;
                if (window.videoUrl) result.videoUrl = window.videoUrl;
                if (window.hls) result.hlsUrl = window.hls.url || 'HLS exists';
                if (window.player) result.player = 'Player exists';
                
                var video = document.querySelector('video');
                if (video) {
                    result.videoSrc = video.src;
                    result.videoCurrentSrc = video.currentSrc;
                }
            } catch(e) {
                result.error = e.message;
            }
            return result;
        """)
        
        # Resultado final
        result = {
            "timestamp": datetime.now().isoformat(),
            "url": TEST_URL,
            "total_requests": len(all_requests),
            "video_urls_found": video_urls,
            "cookies": cookies,
            "js_variables": js_vars,
            "requests": all_requests
        }
        
        # Salvar JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print("RESULTADO")
        print(f"{'='*70}")
        print(f"Total de requisições: {len(all_requests)}")
        print(f"URLs de vídeo encontradas: {len(video_urls)}")
        print(f"Cookies: {len(cookies)}")
        print(f"Variáveis JS: {json.dumps(js_vars, indent=2)}")
        
        if video_urls:
            print(f"\n[+] URLs DE VÍDEO:")
            for v in video_urls:
                print(f"  - {v['url']}")
        
        # Mostrar requisição da API
        api_reqs = [r for r in all_requests if '/api/' in r['url']]
        if api_reqs:
            print(f"\n[+] REQUISIÇÕES DA API:")
            for api in api_reqs:
                print(f"\n  URL: {api['url']}")
                print(f"  Headers de Request:")
                for k, v in api['request_headers'].items():
                    print(f"    {k}: {v}")
                if api['response']:
                    print(f"  Status: {api['response']['status_code']}")
                    print(f"  Headers de Response:")
                    for k, v in api['response']['headers'].items():
                        print(f"    {k}: {v}")
                    if api['response']['body_preview']:
                        print(f"  Body: {api['response']['body_preview'][:200]}...")
        
        print(f"\n[*] Resultado salvo em: {OUTPUT_FILE}")
        
        return result
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_network()
