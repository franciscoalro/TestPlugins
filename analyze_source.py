import argparse
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time, urllib.parse
import sys

def main():
    parser = argparse.ArgumentParser(description='Analyze video source network requests.')
    parser.add_argument('url', help='The URL of the episode/player to analyze')
    args = parser.parse_args()

    print(f"Starting analysis for: {args.url}")

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Keep visible for now
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--mute-audio")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome failed: {e}")
        try:
             driver = webdriver.Firefox()
        except Exception as e2:
             print(f"Firefox also failed: {e2}")
             return

    driver.set_page_load_timeout(30)
    
    try:
        driver.get(args.url)
    except Exception as e:
        print(f"Error loading page: {e}")

    # Aguarda carregamento inicial
    time.sleep(5)

    # Common Play Button Selectors
    selectors = [
        "button[class*='play']", 
        ".play", 
        ".btn-play",
        ".jw-display-icon-container", # JWPlayer
        ".vjs-big-play-button",       # VideoJS
        ".art-control-play",          # ArtPlayer
        ".plyr__control--overlaid",   # Plyr
        "div[class*='play']",
        "svg[class*='play']",
        "video"                       # Direct click on video
    ]

    clicked = False
    for selector in selectors:
        try:
            print(f"Trying selector: {selector}")
            element = driver.find_element(By.CSS_SELECTOR, selector)
            if element.is_displayed():
                print(f"Found displayed element: {selector}")
                
                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)
                
                try:
                    element.click()
                    print("Standard click success.")
                except:
                    print("Standard click failed, trying JS click.")
                    driver.execute_script("arguments[0].click();", element)
                
                clicked = True
                break
        except:
            continue
    
    if not clicked:
        print("⚠️ Botão de play não encontrado automaticamente com os seletores padrões.")
        print("Tentando clicar no centro da tela...")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            print("Clicou no centro da tela.")
        except Exception as e:
            print(f"Clique central falhou: {e}")

    # Aguarda o player iniciar e requests fluírem
    print("Aguardando buffer de rede (15s)...")
    time.sleep(15)

    print("\n🔍 ANALISANDO REQUISIÇÕES DE REDE...\n")

    found_video = False
    
    # Filter for interesting extensions
    TARGET_EXTS = [".m3u8", ".mp4", ".ts", ".mpd"]
    
    for req in driver.requests:
        url = urllib.parse.unquote(req.url)
        
        if any(ext in url for ext in TARGET_EXTS):
            found_video = True
            print("🎬 VIDEO REQUEST ENCONTRADO")
            print(f"URL: {url}")
            print(f"METHOD: {req.method}")
            print("HEADERS RELEVANTES:")
            for k, v in req.headers.items():
                if k.lower() in ['referer', 'user-agent', 'origin', 'host']:
                     print(f"  {k}: {v}")
            print("-" * 60)
            
    if not found_video:
        print("❌ Nenhum vídeo (.m3u8, .mp4, .ts, .mpd) encontrado nas requisições capturadas.")

    driver.quit()

if __name__ == "__main__":
    main()
