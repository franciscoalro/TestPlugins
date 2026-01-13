import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("="*60)
print("TESTE WEBVIEW V2 - INTERCEPTA API E BLOB")
print("="*60)

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Network.enable", {})

captured_responses = {}

def get_response_body(request_id):
    try:
        return driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
    except:
        return None

def process_logs():
    logs = driver.get_log("performance")
    for entry in logs:
        try:
            msg = json.loads(entry["message"])["message"]
            method = msg["method"]
            params = msg.get("params", {})
            
            if method == "Network.responseReceived":
                url = params["response"]["url"]
                request_id = params["requestId"]
                
                # Capturar respostas importantes
                if any(x in url for x in ["api/v1/video", ".m3u8", "cf-master", "master.txt"]):
                    body = get_response_body(request_id)
                    if body:
                        captured_responses[url] = body.get("body", "")
                        print(f"\n[CAPTURADO] {url[:80]}...")
                        print(f"  Body: {body.get('body', '')[:300]}...")
                        
        except Exception as e:
            pass

try:
    # Ir direto para o MegaEmbed com um ID conhecido
    print("\n[1] Acessando MegaEmbed diretamente...")
    driver.get("https://megaembed.link/#3wnuij")
    time.sleep(5)
    process_logs()
    
    # Clicar no player para iniciar
    print("\n[2] Tentando iniciar player...")
    try:
        driver.execute_script("""
            var playBtn = document.querySelector('.play-button, .vjs-big-play-button, [class*="play"]');
            if (playBtn) playBtn.click();
            
            var video = document.querySelector('video');
            if (video) video.play();
        """)
    except:
        pass
    
    # Aguardar e capturar
    for i in range(20):
        time.sleep(2)
        process_logs()
        print(f"  Aguardando... ({i+1}/20)")
        
        # Verificar se há video element com src
        video_src = driver.execute_script("""
            var video = document.querySelector('video');
            if (video) {
                return {
                    src: video.src,
                    currentSrc: video.currentSrc,
                    networkState: video.networkState,
                    readyState: video.readyState
                };
            }
            return null;
        """)
        
        if video_src:
            print(f"  Video element: {video_src}")
            if video_src.get('src') and 'blob:' not in video_src.get('src', ''):
                print(f"\n[ENCONTRADO] Video src: {video_src['src']}")
                break
    
    # Resultado
    print("\n" + "="*60)
    print("RESPOSTAS CAPTURADAS")
    print("="*60)
    
    for url, body in captured_responses.items():
        print(f"\nURL: {url}")
        print(f"Body: {body[:500] if body else 'vazio'}")
    
    # Salvar
    with open("webview_v2_result.json", "w") as f:
        json.dump(captured_responses, f, indent=2)

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("\nENTER para fechar...")
    driver.quit()
