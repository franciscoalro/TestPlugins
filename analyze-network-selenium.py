#!/usr/bin/env python3
"""
Script para analisar requisições de rede do MaxSeries usando Selenium
Identifica fontes de vídeo e filtra YouTube (trailers)
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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

# URLs para testar
TEST_URLS = [
    # Série que NÃO funciona - precisa investigar
    "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/",
    # Série que funciona (referência)
    "https://www.maxseries.one/series/assistir-garota-sequestrada-online/",
]

def setup_driver():
    """Configura o Chrome com captura de rede"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Habilitar logging de performance para capturar requisições
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def get_network_requests(driver):
    """Extrai requisições de rede dos logs de performance"""
    logs = driver.get_log("performance")
    requests = []
    
    for log in logs:
        try:
            message = json.loads(log["message"])["message"]
            if message["method"] == "Network.requestWillBeSent":
                url = message["params"]["request"]["url"]
                requests.append({
                    "url": url,
                    "type": message["params"].get("type", "Unknown"),
                    "initiator": message["params"].get("initiator", {}).get("type", "Unknown")
                })
        except:
            pass
    
    return requests

def analyze_page(driver, url):
    """Analisa uma página e extrai informações de vídeo"""
    print(f"\n{'='*80}")
    print(f"Analisando: {url}")
    print('='*80)
    
    result = {
        "url": url,
        "iframes": [],
        "video_sources": [],
        "youtube_sources": [],
        "player_buttons": [],
        "network_requests": [],
        "errors": []
    }
    
    try:
        driver.get(url)
        time.sleep(3)
        
        # Capturar iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if src:
                result["iframes"].append(src)
                print(f"[IFRAME] {src}")
                
                # Verificar se é YouTube
                if "youtube" in src.lower() or "youtu.be" in src.lower():
                    result["youtube_sources"].append(src)
                    print(f"  ⚠️  YOUTUBE DETECTADO (trailer)")
        
        # Tentar entrar no iframe principal (player)
        main_iframe = None
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "playerthree" in src or "player" in src:
                main_iframe = iframe
                break
        
        if main_iframe:
            iframe_src = main_iframe.get_attribute("src")
            print(f"\n[ENTRANDO NO IFRAME] {iframe_src}")
            
            # Navegar diretamente para o iframe
            driver.get(iframe_src if iframe_src.startswith("http") else f"https:{iframe_src}")
            time.sleep(3)
            
            # Procurar botões de fonte
            buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-source], li[data-source], a[data-source]")
            for btn in buttons:
                source = btn.get_attribute("data-source") or ""
                text = btn.text.strip()
                if source:
                    is_youtube = "youtube" in source.lower() or "youtu.be" in source.lower()
                    result["player_buttons"].append({
                        "text": text,
                        "source": source,
                        "is_youtube": is_youtube
                    })
                    status = "⚠️ YOUTUBE" if is_youtube else "✓"
                    print(f"[BOTÃO] {text}: {source} {status}")
            
            # Procurar episódios
            episodes = driver.find_elements(By.CSS_SELECTOR, "li[data-episode-id] a")
            if episodes:
                print(f"\n[EPISÓDIOS ENCONTRADOS] {len(episodes)}")
                
                # Clicar no primeiro episódio para ver as fontes
                if episodes:
                    try:
                        episodes[0].click()
                        time.sleep(2)
                        
                        # Verificar botões de fonte novamente
                        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-source], li[data-source]")
                        print(f"\n[FONTES DO EPISÓDIO 1]")
                        for btn in buttons:
                            source = btn.get_attribute("data-source") or ""
                            text = btn.text.strip()
                            if source:
                                is_youtube = "youtube" in source.lower() or "youtu.be" in source.lower()
                                status = "⚠️ YOUTUBE (IGNORAR)" if is_youtube else "✓ VÁLIDO"
                                print(f"  - {text}: {source[:80]}... {status}")
                                
                                if not is_youtube:
                                    result["video_sources"].append({
                                        "name": text,
                                        "url": source
                                    })
                    except Exception as e:
                        result["errors"].append(f"Erro ao clicar episódio: {e}")
        
        # Capturar requisições de rede
        requests = get_network_requests(driver)
        video_requests = [r for r in requests if any(ext in r["url"].lower() for ext in [".m3u8", ".mp4", ".ts", "video", "stream"])]
        result["network_requests"] = video_requests[:20]  # Limitar
        
        if video_requests:
            print(f"\n[REQUISIÇÕES DE VÍDEO]")
            for req in video_requests[:10]:
                print(f"  - {req['url'][:100]}...")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"[ERRO] {e}")
    
    return result

def analyze_specific_episode(driver, series_url):
    """Analisa um episódio específico para encontrar fontes de vídeo"""
    print(f"\n{'='*80}")
    print(f"Análise detalhada de episódio: {series_url}")
    print('='*80)
    
    result = {
        "series_url": series_url,
        "episode_sources": [],
        "ajax_responses": []
    }
    
    try:
        driver.get(series_url)
        time.sleep(3)
        
        # Encontrar iframe do player
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        player_iframe = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "playerthree" in src or "player" in src:
                player_iframe = src
                break
        
        if player_iframe:
            player_url = player_iframe if player_iframe.startswith("http") else f"https:{player_iframe}"
            print(f"[PLAYER URL] {player_url}")
            
            driver.get(player_url)
            time.sleep(3)
            
            # Encontrar episódios
            episodes = driver.find_elements(By.CSS_SELECTOR, "li[data-episode-id]")
            
            if episodes:
                # Pegar ID do primeiro episódio
                ep_id = episodes[0].get_attribute("data-episode-id")
                print(f"[EPISÓDIO ID] {ep_id}")
                
                # Fazer requisição AJAX diretamente
                ajax_url = f"https://playerthree.online/episodio/{ep_id}"
                print(f"[AJAX URL] {ajax_url}")
                
                # Usar JavaScript para fazer a requisição
                script = f"""
                return fetch('{ajax_url}', {{
                    headers: {{
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': '{player_url}'
                    }}
                }}).then(r => r.text());
                """
                
                try:
                    ajax_response = driver.execute_script(script)
                    result["ajax_responses"].append({
                        "url": ajax_url,
                        "response": ajax_response[:2000] if ajax_response else None
                    })
                    
                    # Parsear resposta para encontrar fontes
                    if ajax_response:
                        # Procurar data-source
                        sources = re.findall(r'data-source=["\']([^"\']+)["\']', ajax_response)
                        for src in sources:
                            is_youtube = "youtube" in src.lower() or "youtu.be" in src.lower()
                            result["episode_sources"].append({
                                "url": src,
                                "is_youtube": is_youtube,
                                "type": identify_source_type(src)
                            })
                            status = "⚠️ YOUTUBE" if is_youtube else "✓"
                            print(f"[FONTE] {identify_source_type(src)}: {src[:80]}... {status}")
                            
                except Exception as e:
                    print(f"[ERRO AJAX] {e}")
                    
                # Clicar no episódio e capturar
                try:
                    episodes[0].click()
                    time.sleep(2)
                    
                    # Verificar botões
                    buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-source]")
                    for btn in buttons:
                        source = btn.get_attribute("data-source")
                        if source:
                            is_youtube = "youtube" in source.lower()
                            result["episode_sources"].append({
                                "url": source,
                                "is_youtube": is_youtube,
                                "type": identify_source_type(source)
                            })
                except:
                    pass
                    
    except Exception as e:
        print(f"[ERRO] {e}")
    
    return result

def identify_source_type(url):
    """Identifica o tipo de fonte de vídeo"""
    url_lower = url.lower()
    
    if "youtube" in url_lower or "youtu.be" in url_lower:
        return "YouTube (TRAILER - IGNORAR)"
    elif "myvidplay" in url_lower:
        return "MyVidPlay (DoodStream)"
    elif "bysebuho" in url_lower:
        return "Bysebuho (DoodStream)"
    elif "g9r6" in url_lower:
        return "G9R6 (DoodStream)"
    elif "dood" in url_lower:
        return "DoodStream"
    elif "megaembed" in url_lower:
        return "MegaEmbed"
    elif "playerembedapi" in url_lower:
        return "PlayerEmbedAPI"
    elif "streamwish" in url_lower:
        return "StreamWish"
    elif "filemoon" in url_lower:
        return "FileMoon"
    elif "voe" in url_lower:
        return "Voe"
    elif "mixdrop" in url_lower:
        return "MixDrop"
    elif "streamtape" in url_lower:
        return "StreamTape"
    else:
        return "Desconhecido"

def main():
    print("="*80)
    print("ANÁLISE DE REDE - MAXSERIES")
    print("Identificando fontes de vídeo e filtrando YouTube")
    print("="*80)
    
    driver = setup_driver()
    all_results = []
    
    try:
        for url in TEST_URLS:
            # Análise básica
            result = analyze_page(driver, url)
            all_results.append(result)
            
            # Análise detalhada de episódio
            ep_result = analyze_specific_episode(driver, url)
            all_results.append(ep_result)
            
    finally:
        driver.quit()
    
    # Salvar resultados
    with open("network_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    
    # Coletar todas as fontes únicas
    all_sources = {}
    youtube_count = 0
    valid_count = 0
    
    for result in all_results:
        sources = result.get("episode_sources", []) + result.get("video_sources", [])
        for src in sources:
            url = src.get("url", "")
            src_type = src.get("type", identify_source_type(url))
            is_youtube = src.get("is_youtube", "youtube" in url.lower())
            
            if is_youtube:
                youtube_count += 1
            else:
                valid_count += 1
                if src_type not in all_sources:
                    all_sources[src_type] = []
                all_sources[src_type].append(url)
    
    print(f"\nFontes YouTube (trailers - IGNORAR): {youtube_count}")
    print(f"Fontes válidas encontradas: {valid_count}")
    
    print("\nTipos de fonte encontrados:")
    for src_type, urls in all_sources.items():
        print(f"  - {src_type}: {len(urls)} fonte(s)")
        for url in urls[:2]:
            print(f"      {url[:80]}...")
    
    print("\nResultados salvos em: network_analysis_results.json")

if __name__ == "__main__":
    main()
