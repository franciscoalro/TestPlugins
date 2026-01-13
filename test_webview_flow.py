import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("="*60)
print("TESTE COM WEBVIEW - CAPTURA M3U8 REAL")
print("="*60)

# Configurar Chrome com DevTools Protocol para interceptar rede
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-site-isolation-trials")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Network.enable", {})

# Lista para armazenar URLs capturadas
captured_urls = []
m3u8_urls = []

def process_logs():
    """Processa logs de rede do Chrome DevTools"""
    logs = driver.get_log("performance")
    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
            if message["method"] == "Network.responseReceived":
                url = message["params"]["response"]["url"]
                if any(x in url for x in [".m3u8", "cf-master", ".txt", "master.txt"]):
                    m3u8_urls.append(url)
                    print(f"  [M3U8] {url}")
                elif any(x in url for x in ["megaembed", "playerthree", "api/v1"]):
                    captured_urls.append(url)
        except:
            pass

try:
    # Passo 1: Acessar página da série
    print("\n[1] Acessando MaxSeries...")
    driver.get("https://www.maxseries.one/series/assistir-terra-de-pecados-online")
    time.sleep(3)
    process_logs()
    
    # Passo 2: Encontrar e clicar no iframe do player
    print("\n[2] Buscando iframe do player...")
    iframe_src = driver.execute_script("""
        var iframes = document.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) {
            if (iframes[i].src.includes('playerthree')) {
                return iframes[i].src;
            }
        }
        return null;
    """)
    
    if iframe_src:
        print(f"  Iframe encontrado: {iframe_src}")
        driver.get(iframe_src)
        time.sleep(3)
        process_logs()
    
    # Passo 3: Clicar no primeiro episódio
    print("\n[3] Clicando no episodio...")
    try:
        ep_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-episode-id]"))
        )
        ep_btn.click()
        time.sleep(3)
        process_logs()
    except Exception as e:
        print(f"  Erro ao clicar: {e}")
    
    # Passo 4: Buscar source do MegaEmbed
    print("\n[4] Buscando source MegaEmbed...")
    megaembed_src = driver.execute_script("""
        var sources = document.querySelectorAll('[data-source]');
        for (var i = 0; i < sources.length; i++) {
            if (sources[i].getAttribute('data-source').includes('megaembed')) {
                sources[i].click();
                return sources[i].getAttribute('data-source');
            }
        }
        return null;
    """)
    
    if megaembed_src:
        print(f"  MegaEmbed source: {megaembed_src}")
        time.sleep(2)
        process_logs()
        
        # Passo 5: Navegar para o MegaEmbed
        print("\n[5] Acessando MegaEmbed...")
        driver.get(megaembed_src)
        
        # Aguardar carregamento e capturar requisições
        for i in range(15):
            time.sleep(2)
            process_logs()
            print(f"  Aguardando... ({i+1}/15)")
            if m3u8_urls:
                print("  M3U8 encontrado!")
                break
    
    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO")
    print("="*60)
    
    print("\nURLs capturadas:")
    for url in captured_urls[-10:]:
        print(f"  {url}")
    
    print("\nM3U8 URLs encontradas:")
    for url in m3u8_urls:
        print(f"  {url}")
    
    if m3u8_urls:
        print("\n[SUCESSO] M3U8 capturado via WebView!")
        # Salvar resultado
        with open("webview_capture_result.json", "w") as f:
            json.dump({
                "m3u8_urls": m3u8_urls,
                "captured_urls": captured_urls[-20:]
            }, f, indent=2)
    else:
        print("\n[INFO] Nenhum M3U8 capturado diretamente")
        print("O player pode usar blob: URLs ou streams encriptados")

except Exception as e:
    print(f"\nErro: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("\nPressione ENTER para fechar o navegador...")
    driver.quit()
