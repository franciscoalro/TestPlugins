#!/usr/bin/env python3
"""
Análise detalhada das fontes PlayerEmbedAPI e MegaEmbed
Captura requisições de rede para encontrar URLs de vídeo
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Fontes para testar (da análise anterior)
TEST_SOURCES = [
    {
        "name": "PlayerEmbedAPI - Casa do Dragão",
        "url": "https://playerembedapi.link/?v=tx3jQLbTT"
    },
    {
        "name": "MegaEmbed - Casa do Dragão", 
        "url": "https://megaembed.link/#dqd1uk"
    },
    {
        "name": "MyVidPlay - Garota Sequestrada (funciona)",
        "url": "https://myvidplay.com/e/tilgznkxayrx"
    }
]

def setup_driver():
    """Configura Chrome com captura de rede detalhada"""
    options = Options()
    # NÃO usar headless para ver o que acontece
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Habilitar logging de performance
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Habilitar CDP para interceptar requisições
    driver.execute_cdp_cmd("Network.enable", {})
    
    return driver

def get_all_network_requests(driver):
    """Extrai TODAS as requisições de rede"""
    logs = driver.get_log("performance")
    requests = []
    responses = []
    
    for log in logs:
        try:
            message = json.loads(log["message"])["message"]
            method = message["method"]
            
            if method == "Network.requestWillBeSent":
                req = message["params"]["request"]
                requests.append({
                    "url": req["url"],
                    "method": req.get("method", "GET"),
                    "headers": req.get("headers", {}),
                    "type": message["params"].get("type", "Unknown")
                })
            elif method == "Network.responseReceived":
                resp = message["params"]["response"]
                responses.append({
                    "url": resp["url"],
                    "status": resp.get("status", 0),
                    "mimeType": resp.get("mimeType", ""),
                    "headers": resp.get("headers", {})
                })
        except:
            pass
    
    return requests, responses

def analyze_source(driver, name, url):
    """Analisa uma fonte de vídeo específica"""
    print(f"\n{'='*80}")
    print(f"Analisando: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    result = {
        "name": name,
        "url": url,
        "video_urls": [],
        "m3u8_urls": [],
        "mp4_urls": [],
        "interesting_requests": [],
        "page_source_snippets": [],
        "errors": []
    }
    
    try:
        driver.get(url)
        time.sleep(5)  # Esperar carregamento
        
        # Capturar requisições
        requests, responses = get_all_network_requests(driver)
        
        # Filtrar requisições interessantes
        video_patterns = [".m3u8", ".mp4", ".ts", "master.txt", "/hls/", "/video/", "stream", "playlist"]
        
        for req in requests:
            req_url = req["url"].lower()
            if any(p in req_url for p in video_patterns):
                result["interesting_requests"].append(req)
                print(f"[REQ] {req['url'][:100]}...")
                
                if ".m3u8" in req_url or "master" in req_url:
                    result["m3u8_urls"].append(req["url"])
                elif ".mp4" in req_url:
                    result["mp4_urls"].append(req["url"])
        
        # Verificar elementos de vídeo na página
        try:
            videos = driver.find_elements(By.TAG_NAME, "video")
            for video in videos:
                src = video.get_attribute("src")
                if src:
                    result["video_urls"].append(src)
                    print(f"[VIDEO SRC] {src}")
                
                # Verificar sources dentro do video
                sources = video.find_elements(By.TAG_NAME, "source")
                for source in sources:
                    src = source.get_attribute("src")
                    if src:
                        result["video_urls"].append(src)
                        print(f"[SOURCE SRC] {src}")
        except:
            pass
        
        # Verificar iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src:
                print(f"[IFRAME] {src}")
                
                # Se for um iframe de player, entrar nele
                if "player" in src.lower() or "embed" in src.lower():
                    try:
                        driver.switch_to.frame(iframe)
                        time.sleep(2)
                        
                        # Verificar vídeos dentro do iframe
                        videos = driver.find_elements(By.TAG_NAME, "video")
                        for video in videos:
                            src = video.get_attribute("src")
                            if src:
                                result["video_urls"].append(src)
                                print(f"[IFRAME VIDEO] {src}")
                        
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()
        
        # Capturar parte do HTML para análise
        page_source = driver.page_source
        
        # Procurar URLs de vídeo no código fonte
        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', page_source)
        mp4_matches = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', page_source)
        
        for m in m3u8_matches:
            if m not in result["m3u8_urls"]:
                result["m3u8_urls"].append(m)
                print(f"[HTML M3U8] {m[:100]}...")
        
        for m in mp4_matches:
            if m not in result["mp4_urls"]:
                result["mp4_urls"].append(m)
                print(f"[HTML MP4] {m[:100]}...")
        
        # Procurar padrões de JavaScript que podem conter URLs
        js_patterns = [
            r'file:\s*["\']([^"\']+)["\']',
            r'source:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+)["\']',
            r'sources:\s*\[\s*\{\s*file:\s*["\']([^"\']+)["\']',
            r'hls:\s*["\']([^"\']+)["\']',
            r'dash:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, page_source)
            for m in matches:
                if "http" in m and m not in result["video_urls"]:
                    result["video_urls"].append(m)
                    print(f"[JS PATTERN] {m[:100]}...")
        
        # Verificar se há código packed/obfuscado
        if "eval(function(p,a,c,k,e,d)" in page_source:
            print("[INFO] Código JavaScript PACKED detectado - precisa desempacotar")
            result["page_source_snippets"].append("PACKED_JS_DETECTED")
            
            # Extrair o código packed
            packed_match = re.search(r"eval\(function\(p,a,c,k,e,d\)[^}]+\}", page_source)
            if packed_match:
                result["page_source_snippets"].append(packed_match.group()[:500])
        
        # Verificar se há CryptoJS ou decriptação
        if "CryptoJS" in page_source or "decrypt" in page_source.lower():
            print("[INFO] Código de DECRIPTAÇÃO detectado")
            result["page_source_snippets"].append("CRYPTO_DETECTED")
        
        # Esperar mais um pouco e verificar novamente
        time.sleep(5)
        requests2, _ = get_all_network_requests(driver)
        
        for req in requests2:
            req_url = req["url"].lower()
            if any(p in req_url for p in video_patterns):
                if req["url"] not in [r["url"] for r in result["interesting_requests"]]:
                    result["interesting_requests"].append(req)
                    print(f"[REQ DELAYED] {req['url'][:100]}...")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"[ERRO] {e}")
    
    # Resumo
    print(f"\n[RESUMO]")
    print(f"  M3U8 URLs: {len(result['m3u8_urls'])}")
    print(f"  MP4 URLs: {len(result['mp4_urls'])}")
    print(f"  Video URLs: {len(result['video_urls'])}")
    print(f"  Requisições interessantes: {len(result['interesting_requests'])}")
    
    return result

def main():
    print("="*80)
    print("ANÁLISE DETALHADA DE FONTES DE VÍDEO")
    print("PlayerEmbedAPI, MegaEmbed, MyVidPlay")
    print("="*80)
    
    driver = setup_driver()
    all_results = []
    
    try:
        for source in TEST_SOURCES:
            result = analyze_source(driver, source["name"], source["url"])
            all_results.append(result)
            time.sleep(2)
            
    finally:
        driver.quit()
    
    # Salvar resultados
    with open("hard_sources_analysis.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("CONCLUSÕES")
    print("="*80)
    
    for result in all_results:
        print(f"\n{result['name']}:")
        if result['m3u8_urls'] or result['mp4_urls']:
            print("  ✓ URLs de vídeo encontradas!")
            for url in result['m3u8_urls'][:2]:
                print(f"    M3U8: {url[:80]}...")
            for url in result['mp4_urls'][:2]:
                print(f"    MP4: {url[:80]}...")
        else:
            print("  ✗ Nenhuma URL de vídeo encontrada diretamente")
            if "PACKED_JS_DETECTED" in result.get("page_source_snippets", []):
                print("    → Código JavaScript packed detectado")
            if "CRYPTO_DETECTED" in result.get("page_source_snippets", []):
                print("    → Código de decriptação detectado")
    
    print("\nResultados salvos em: hard_sources_analysis.json")

if __name__ == "__main__":
    main()
