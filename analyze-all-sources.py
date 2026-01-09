#!/usr/bin/env python3
"""
Análise completa de todas as fontes de vídeo disponíveis
Foca em encontrar fontes que funcionam (DoodStream clones)
"""

import json
import time
import re
import requests
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

def identify_source(url):
    """Identifica o tipo de fonte"""
    url_lower = url.lower()
    
    # DoodStream clones (FUNCIONAM)
    dood_domains = ["myvidplay", "bysebuho", "g9r6", "doodstream", "dood.to", "dood.watch", 
                    "dood.pm", "dood.wf", "dood.re", "dood.so", "dood.cx", "dood.la", 
                    "dood.ws", "dood.sh", "d0000d", "d000d", "dooood", "ds2play"]
    
    for domain in dood_domains:
        if domain in url_lower:
            return "DoodStream", True
    
    # YouTube (IGNORAR - trailers)
    if "youtube" in url_lower or "youtu.be" in url_lower:
        return "YouTube", False
    
    # Outros players
    if "playerembedapi" in url_lower:
        return "PlayerEmbedAPI", False  # Não funciona bem
    if "megaembed" in url_lower:
        return "MegaEmbed", False  # Não funciona bem
    if "streamwish" in url_lower:
        return "StreamWish", True
    if "filemoon" in url_lower:
        return "FileMoon", True
    if "voe" in url_lower:
        return "Voe", True
    if "mixdrop" in url_lower:
        return "MixDrop", True
    if "streamtape" in url_lower:
        return "StreamTape", True
    if "vidoza" in url_lower:
        return "Vidoza", True
    if "upstream" in url_lower:
        return "Upstream", True
    
    return "Desconhecido", False

def get_episode_sources(driver, series_url):
    """Obtém todas as fontes de um episódio"""
    print(f"\n{'='*80}")
    print(f"Analisando série: {series_url}")
    print('='*80)
    
    results = {
        "series_url": series_url,
        "episodes": [],
        "all_sources": [],
        "working_sources": [],
        "youtube_sources": [],
        "unknown_sources": []
    }
    
    try:
        driver.get(series_url)
        time.sleep(3)
        
        # Encontrar iframe do player
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        player_url = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "playerthree" in src or "player" in src:
                player_url = src if src.startswith("http") else f"https:{src}"
                break
        
        if not player_url:
            print("[ERRO] Iframe do player não encontrado")
            return results
        
        print(f"[PLAYER] {player_url}")
        
        # Navegar para o player
        driver.get(player_url)
        time.sleep(3)
        
        # Encontrar episódios
        episodes = driver.find_elements(By.CSS_SELECTOR, "li[data-episode-id]")
        print(f"[EPISÓDIOS] {len(episodes)} encontrados")
        
        # Analisar os primeiros 3 episódios
        for i, ep in enumerate(episodes[:3]):
            ep_id = ep.get_attribute("data-episode-id")
            print(f"\n[EPISÓDIO {i+1}] ID: {ep_id}")
            
            # Fazer requisição AJAX
            ajax_url = f"https://playerthree.online/episodio/{ep_id}"
            
            try:
                # Usar requests para fazer a chamada AJAX
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": player_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(ajax_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    html = response.text
                    
                    # Extrair fontes
                    sources = re.findall(r'data-source=["\']([^"\']+)["\']', html)
                    
                    ep_data = {
                        "episode_id": ep_id,
                        "sources": []
                    }
                    
                    for src in sources:
                        source_type, works = identify_source(src)
                        source_info = {
                            "url": src,
                            "type": source_type,
                            "likely_works": works
                        }
                        
                        ep_data["sources"].append(source_info)
                        results["all_sources"].append(source_info)
                        
                        if source_type == "YouTube":
                            results["youtube_sources"].append(src)
                            print(f"  ⚠️ {source_type}: {src[:60]}... (IGNORAR)")
                        elif works:
                            results["working_sources"].append(src)
                            print(f"  ✓ {source_type}: {src[:60]}... (FUNCIONA)")
                        else:
                            results["unknown_sources"].append(src)
                            print(f"  ? {source_type}: {src[:60]}... (VERIFICAR)")
                    
                    results["episodes"].append(ep_data)
                    
            except Exception as e:
                print(f"  [ERRO] {e}")
        
    except Exception as e:
        print(f"[ERRO] {e}")
    
    return results

def main():
    print("="*80)
    print("ANÁLISE COMPLETA DE FONTES DE VÍDEO")
    print("="*80)
    
    # Séries para testar
    test_series = [
        "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/",
        "https://www.maxseries.one/series/assistir-garota-sequestrada-online/",
        # Adicionar mais séries para testar
        "https://www.maxseries.one/series/assistir-the-last-of-us-online/",
    ]
    
    driver = setup_driver()
    all_results = []
    
    try:
        for series_url in test_series:
            result = get_episode_sources(driver, series_url)
            all_results.append(result)
            time.sleep(2)
    finally:
        driver.quit()
    
    # Salvar resultados
    with open("all_sources_analysis.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("RESUMO GERAL")
    print("="*80)
    
    total_working = 0
    total_youtube = 0
    total_unknown = 0
    
    source_types = {}
    
    for result in all_results:
        total_working += len(result["working_sources"])
        total_youtube += len(result["youtube_sources"])
        total_unknown += len(result["unknown_sources"])
        
        for src in result["all_sources"]:
            src_type = src["type"]
            if src_type not in source_types:
                source_types[src_type] = {"count": 0, "works": src["likely_works"]}
            source_types[src_type]["count"] += 1
    
    print(f"\nFontes que FUNCIONAM: {total_working}")
    print(f"Fontes YouTube (IGNORAR): {total_youtube}")
    print(f"Fontes desconhecidas: {total_unknown}")
    
    print("\nTipos de fonte encontrados:")
    for src_type, info in sorted(source_types.items(), key=lambda x: -x[1]["count"]):
        status = "✓ FUNCIONA" if info["works"] else "✗ NÃO FUNCIONA" if src_type == "YouTube" else "? VERIFICAR"
        print(f"  {src_type}: {info['count']} ({status})")
    
    print("\n" + "="*80)
    print("RECOMENDAÇÕES PARA O PLUGIN")
    print("="*80)
    
    print("""
1. FONTES QUE FUNCIONAM (DoodStream clones):
   - myvidplay.com
   - bysebuho.com
   - g9r6.com
   - doodstream.com e variantes

2. FONTES A IGNORAR:
   - YouTube (são trailers)
   
3. FONTES PROBLEMÁTICAS:
   - playerembedapi.link (redireciona para abyss.to)
   - megaembed.link (usa ads/tracking)
   
4. SOLUÇÃO:
   - Priorizar fontes DoodStream
   - Ignorar completamente YouTube
   - Tentar WebView para playerembedapi/megaembed como fallback
""")

if __name__ == "__main__":
    main()
