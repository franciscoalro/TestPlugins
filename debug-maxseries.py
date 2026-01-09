#!/usr/bin/env python3
"""
Debug do MaxSeries - verificar estrutura HTML
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SERIES_URL = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def test_with_requests():
    """Testa com requests simples"""
    print("="*60)
    print("TESTE COM REQUESTS")
    print("="*60)
    
    try:
        resp = requests.get(SERIES_URL, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"URL final: {resp.url}")
        print(f"Tamanho: {len(resp.text)} bytes")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Título da página
        title = soup.find('title')
        print(f"Título: {title.text if title else 'N/A'}")
        
        # Procurar links
        all_links = soup.find_all('a', href=True)
        print(f"Total de links: {len(all_links)}")
        
        # Links de episódio
        ep_links = [a for a in all_links if '/episodio/' in a.get('href', '')]
        print(f"Links de episódio: {len(ep_links)}")
        
        for link in ep_links[:5]:
            print(f"  - {link.get('href')}")
        
        # Procurar por padrões de temporada/episódio
        season_divs = soup.select('.temporada, .season, [class*="season"], [class*="temporada"]')
        print(f"Divs de temporada: {len(season_divs)}")
        
        # Salvar HTML para análise
        with open('maxseries_debug.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("HTML salvo em: maxseries_debug.html")
        
    except Exception as e:
        print(f"Erro: {e}")

def test_with_selenium():
    """Testa com Selenium"""
    print("\n" + "="*60)
    print("TESTE COM SELENIUM")
    print("="*60)
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(SERIES_URL)
        print(f"Título: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        time.sleep(5)
        
        # Procurar episódios
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/episodio/"]')
        print(f"Links de episódio: {len(ep_links)}")
        
        for link in ep_links[:5]:
            print(f"  - {link.get_attribute('href')}")
        
        # Procurar botões de temporada
        season_btns = driver.find_elements(By.CSS_SELECTOR, 
            '[class*="season"], [class*="temporada"], .accordion-button, [data-bs-toggle]')
        print(f"Botões de temporada: {len(season_btns)}")
        
        # Clicar em botões de temporada para expandir
        for btn in season_btns[:3]:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)
            except:
                pass
        
        time.sleep(2)
        
        # Verificar novamente
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/episodio/"]')
        print(f"Links de episódio após expandir: {len(ep_links)}")
        
        for link in ep_links[:10]:
            href = link.get_attribute('href')
            text = link.text[:50] if link.text else 'sem texto'
            print(f"  - {text}: {href}")
        
        # Salvar HTML renderizado
        with open('maxseries_selenium.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("HTML salvo em: maxseries_selenium.html")
        
        # Se não encontrou episódios, procurar estrutura alternativa
        if len(ep_links) == 0:
            print("\nProcurando estrutura alternativa...")
            
            # Procurar qualquer link com número de episódio
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            for link in all_links:
                href = link.get_attribute('href') or ''
                text = link.text or ''
                if any(x in href.lower() or x in text.lower() for x in ['episod', 'ep ', 'cap', 'capitulo']):
                    print(f"  Possível: {text[:30]} -> {href[:60]}")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_with_requests()
    test_with_selenium()
