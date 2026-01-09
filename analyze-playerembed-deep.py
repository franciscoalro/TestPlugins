#!/usr/bin/env python3
"""
Análise profunda do PlayerEmbedAPI e seus redirecionamentos
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_network_logs(driver):
    """Extrai URLs de requisições de rede"""
    logs = driver.get_log("performance")
    urls = []
    for log in logs:
        try:
            msg = json.loads(log["message"])["message"]
            if msg["method"] == "Network.requestWillBeSent":
                urls.append(msg["params"]["request"]["url"])
        except:
            pass
    return urls

def analyze_url_chain(driver, start_url, name):
    """Segue a cadeia de redirecionamentos e iframes"""
    print(f"\n{'='*80}")
    print(f"Analisando: {name}")
    print(f"URL inicial: {start_url}")
    print('='*80)
    
    results = {
        "name": name,
        "start_url": start_url,
        "redirects": [],
        "iframes": [],
        "video_urls": [],
        "all_requests": []
    }
    
    try:
        driver.get(start_url)
        time.sleep(3)
        
        # URL final após redirecionamentos
        final_url = driver.current_url
        if final_url != start_url:
            results["redirects"].append(final_url)
            print(f"[REDIRECT] {final_url}")
        
        # Capturar todas as requisições
        all_urls = get_network_logs(driver)
        results["all_requests"] = all_urls
        
        # Filtrar URLs de vídeo
        video_patterns = [".m3u8", ".mp4", ".ts", "master", "/hls/", "stream"]
        for url in all_urls:
            if any(p in url.lower() for p in video_patterns):
                results["video_urls"].append(url)
                print(f"[VIDEO] {url[:100]}...")
        
        # Verificar iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if src:
                results["iframes"].append(src)
                print(f"[IFRAME] {src[:100]}...")
        
        # Verificar código fonte
        source = driver.page_source
        
        # Procurar URLs no código
        url_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'file:\s*["\']([^"\']+)["\']',
            r'source:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, source)
            for m in matches:
                if m not in results["video_urls"] and "http" in str(m):
                    results["video_urls"].append(m)
                    print(f"[SOURCE] {str(m)[:100]}...")
        
        # Se houver iframe, entrar nele
        for iframe_src in results["iframes"][:3]:
            if iframe_src.startswith("http"):
                print(f"\n[ENTRANDO IFRAME] {iframe_src[:80]}...")
                try:
                    driver.get(iframe_src)
                    time.sleep(3)
                    
                    # Verificar redirecionamento
                    new_url = driver.current_url
                    if new_url != iframe_src:
                        print(f"[IFRAME REDIRECT] {new_url[:80]}...")
                        results["redirects"].append(new_url)
                    
                    # Capturar mais requisições
                    more_urls = get_network_logs(driver)
                    for url in more_urls:
                        if any(p in url.lower() for p in video_patterns):
                            if url not in results["video_urls"]:
                                results["video_urls"].append(url)
                                print(f"[IFRAME VIDEO] {url[:100]}...")
                    
                    # Verificar código do iframe
                    iframe_source = driver.page_source
                    for pattern in url_patterns:
                        matches = re.findall(pattern, iframe_source)
                        for m in matches:
                            if m not in results["video_urls"] and "http" in str(m):
                                results["video_urls"].append(m)
                                print(f"[IFRAME SOURCE] {str(m)[:100]}...")
                    
                    # Verificar se há mais iframes
                    nested_iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for nested in nested_iframes:
                        nested_src = nested.get_attribute("src") or ""
                        if nested_src and nested_src not in results["iframes"]:
                            results["iframes"].append(nested_src)
                            print(f"[NESTED IFRAME] {nested_src[:80]}...")
                            
                except Exception as e:
                    print(f"[ERRO IFRAME] {e}")
        
    except Exception as e:
        print(f"[ERRO] {e}")
    
    return results

def main():
    print("="*80)
    print("ANÁLISE PROFUNDA - PlayerEmbedAPI e MegaEmbed")
    print("="*80)
    
    # URLs para testar
    test_urls = [
        ("PlayerEmbedAPI", "https://playerembedapi.link/?v=tx3jQLbTT"),
        ("MegaEmbed", "https://megaembed.link/#dqd1uk"),
        ("Short.icu (redirect)", "https://short.icu/K8R6OOjS7"),
    ]
    
    driver = setup_driver()
    all_results = []
    
    try:
        for name, url in test_urls:
            result = analyze_url_chain(driver, url, name)
            all_results.append(result)
            time.sleep(1)
    finally:
        driver.quit()
    
    # Salvar resultados
    with open("playerembed_analysis.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    
    for result in all_results:
        print(f"\n{result['name']}:")
        print(f"  Redirecionamentos: {len(result['redirects'])}")
        print(f"  Iframes: {len(result['iframes'])}")
        print(f"  URLs de vídeo: {len(result['video_urls'])}")
        
        if result['video_urls']:
            print("  Vídeos encontrados:")
            for v in result['video_urls'][:3]:
                print(f"    - {v[:80]}...")
        
        if result['iframes']:
            print("  Iframes encontrados:")
            for i in result['iframes'][:3]:
                print(f"    - {i[:80]}...")

if __name__ == "__main__":
    main()
