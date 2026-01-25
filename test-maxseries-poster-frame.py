#!/usr/bin/env python3
"""
Testa extração de poster do MaxSeries que está dentro de frame
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

def extract_maxseries_poster(url):
    """Extrai poster real do MaxSeries (incluindo dentro de frames)"""
    
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Comentado para debug visual
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🔍 Acessando: {url}")
        driver.get(url)
        time.sleep(5)  # Aguardar carregamento
        
        results = {
            "url": url,
            "posters": []
        }
        
        # 1. Procurar poster na página principal
        print("\n📸 Buscando posters na página principal...")
        main_posters = driver.find_elements(By.CSS_SELECTOR, ".poster img, .image img, img[alt*='poster'], img[alt*='capa']")
        for img in main_posters:
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            if src:
                print(f"  ✅ Main: {src}")
                results["posters"].append({
                    "location": "main_page",
                    "selector": ".poster img / .image img",
                    "src": src,
                    "alt": alt
                })
        
        # 2. Procurar meta tags og:image
        print("\n🏷️ Buscando meta tags...")
        meta_image = driver.find_elements(By.CSS_SELECTOR, "meta[property='og:image']")
        for meta in meta_image:
            content = meta.get_attribute("content")
            if content:
                print(f"  ✅ Meta: {content}")
                results["posters"].append({
                    "location": "meta_tag",
                    "selector": "meta[property='og:image']",
                    "src": content
                })
        
        # 3. Procurar TODAS as imagens do TMDB
        print("\n🎬 Buscando imagens do TMDB...")
        all_images = driver.find_elements(By.TAG_NAME, "img")
        for img in all_images:
            src = img.get_attribute("src")
            if src and "tmdb.org" in src:
                print(f"  ✅ TMDB: {src}")
                results["posters"].append({
                    "location": "tmdb_image",
                    "src": src,
                    "alt": img.get_attribute("alt")
                })
        
        # 4. Procurar iframes
        print("\n📦 Buscando iframes...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"  Total de iframes: {len(iframes)}")
        
        for idx, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute("src")
                print(f"\n  🔎 Iframe {idx + 1}: {iframe_src}")
                
                driver.switch_to.frame(iframe)
                time.sleep(2)
                
                # Procurar imagens dentro do iframe
                frame_images = driver.find_elements(By.TAG_NAME, "img")
                print(f"    Imagens no iframe: {len(frame_images)}")
                
                for img in frame_images:
                    src = img.get_attribute("src")
                    if src:
                        print(f"    ✅ {src}")
                        results["posters"].append({
                            "location": f"iframe_{idx}",
                            "iframe_src": iframe_src,
                            "src": src,
                            "alt": img.get_attribute("alt")
                        })
                
                # Procurar backgrounds no iframe
                bg_images = driver.execute_script("""
                    const elements = document.querySelectorAll('*');
                    const results = [];
                    elements.forEach(el => {
                        const bg = window.getComputedStyle(el).backgroundImage;
                        if (bg && bg !== 'none') {
                            const match = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                            if (match) results.push(match[1]);
                        }
                    });
                    return results;
                """)
                
                for bg in bg_images:
                    if bg:
                        print(f"    🎨 Background: {bg}")
                        results["posters"].append({
                            "location": f"iframe_{idx}_background",
                            "iframe_src": iframe_src,
                            "src": bg
                        })
                
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"    ⚠️ Erro no iframe {idx}: {e}")
                driver.switch_to.default_content()
        
        # 5. Procurar backgrounds na página principal
        print("\n🎨 Buscando background images...")
        bg_images = driver.execute_script("""
            const elements = document.querySelectorAll('*');
            const results = [];
            elements.forEach(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none') {
                    const match = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                    if (match && match[1].includes('tmdb')) {
                        results.push(match[1]);
                    }
                }
            });
            return results;
        """)
        
        for bg in bg_images:
            print(f"  ✅ {bg}")
            results["posters"].append({
                "location": "background_image",
                "src": bg
            })
        
        # Salvar resultados
        output_file = "maxseries_poster_analysis.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {output_file}")
        print(f"\n📊 Total de posters encontrados: {len(results['posters'])}")
        
        # Mostrar resumo
        print("\n" + "="*60)
        print("RESUMO DOS POSTERS ENCONTRADOS:")
        print("="*60)
        for i, poster in enumerate(results['posters'], 1):
            print(f"\n{i}. [{poster['location']}]")
            print(f"   URL: {poster['src']}")
            if 'alt' in poster and poster['alt']:
                print(f"   ALT: {poster['alt']}")
        
        input("\n⏸️ Pressione ENTER para fechar o browser...")
        
        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🎬 EXTRATOR DE POSTER DO MAXSERIES")
    print("="*60)
    
    # Exemplos de URLs para testar
    print("\nExemplos de URLs:")
    print("  - https://www.maxseries.pics/series/...")
    print("  - https://www.maxseries.pics/filmes/...")
    
    url = input("\n📝 Digite a URL do MaxSeries: ").strip()
    
    if url:
        extract_maxseries_poster(url)
    else:
        print("❌ URL não fornecida")
