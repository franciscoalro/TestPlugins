#!/usr/bin/env python3
"""
Script para extrair URL real de poster que está dentro de um frame/iframe
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

def extract_poster_from_frame(page_url):
    """Extrai a URL do poster que está dentro de um frame"""
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🔍 Acessando: {page_url}")
        driver.get(page_url)
        time.sleep(3)
        
        results = {
            "page_url": page_url,
            "posters_found": []
        }
        
        # Procurar por iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"📦 Encontrados {len(iframes)} iframes")
        
        # Procurar imagens na página principal
        main_images = driver.find_elements(By.TAG_NAME, "img")
        for img in main_images:
            src = img.get_attribute("src")
            if src and ("tmdb" in src or "image" in src):
                results["posters_found"].append({
                    "location": "main_page",
                    "url": src,
                    "alt": img.get_attribute("alt")
                })
        
        # Procurar dentro de cada iframe
        for idx, iframe in enumerate(iframes):
            try:
                print(f"🔎 Analisando iframe {idx + 1}...")
                driver.switch_to.frame(iframe)
                
                # Procurar imagens dentro do iframe
                frame_images = driver.find_elements(By.TAG_NAME, "img")
                for img in frame_images:
                    src = img.get_attribute("src")
                    if src:
                        results["posters_found"].append({
                            "location": f"iframe_{idx}",
                            "url": src,
                            "alt": img.get_attribute("alt")
                        })
                
                # Voltar para o contexto principal
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"⚠️ Erro ao acessar iframe {idx}: {e}")
                driver.switch_to.default_content()
        
        # Procurar por backgrounds com imagens
        elements_with_bg = driver.execute_script("""
            const elements = document.querySelectorAll('*');
            const results = [];
            elements.forEach(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none') {
                    const match = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                    if (match) {
                        results.push(match[1]);
                    }
                }
            });
            return results;
        """)
        
        for bg_url in elements_with_bg:
            if "tmdb" in bg_url or "image" in bg_url:
                results["posters_found"].append({
                    "location": "background_image",
                    "url": bg_url
                })
        
        print(f"\n✅ Total de imagens encontradas: {len(results['posters_found'])}")
        
        # Salvar resultados
        output_file = "poster_extraction_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {output_file}")
        
        # Mostrar resultados
        print("\n📸 Imagens encontradas:")
        for poster in results["posters_found"]:
            print(f"  - [{poster['location']}] {poster['url']}")
        
        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Coloque aqui a URL da página que você quer analisar
    test_url = input("Digite a URL da página para extrair o poster: ").strip()
    
    if test_url:
        extract_poster_from_frame(test_url)
    else:
        print("❌ URL não fornecida")
