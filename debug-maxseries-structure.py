#!/usr/bin/env python3
"""
Debug MaxSeries Structure - Verificar se os seletores CSS estão corretos
"""

import requests
from bs4 import BeautifulSoup

def debug_maxseries_structure():
    """Debug da estrutura HTML do MaxSeries"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    print("🔍 DEBUGGING MAXSERIES STRUCTURE")
    print("=" * 50)
    
    # Testar página principal
    print("\n1. TESTANDO PÁGINA PRINCIPAL")
    print("-" * 30)
    
    try:
        response = session.get("https://www.maxseries.one")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Status: {response.status_code}")
        print(f"Tamanho: {len(response.text)} chars")
        print(f"Title: {soup.title.text if soup.title else 'N/A'}")
        
        # Verificar se há redirecionamento ou JavaScript
        if len(response.text) < 1000:
            print("⚠️ Página muito pequena - possível redirecionamento ou JS")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar página de séries
    print("\n2. TESTANDO PÁGINA DE SÉRIES")
    print("-" * 30)
    
    try:
        response = session.get("https://www.maxseries.one/series/page/1")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Status: {response.status_code}")
        print(f"Tamanho: {len(response.text)} chars")
        
        # Verificar seletores do provider atual
        print("\n📋 VERIFICANDO SELETORES CSS:")
        
        # Seletor atual: "div.item"
        items = soup.select("div.item")
        print(f"div.item: {len(items)} encontrados")
        
        if items:
            item = items[0]
            print(f"Primeiro item HTML: {str(item)[:200]}...")
            
            # Verificar sub-seletores
            title_elem = item.select_first("h3 a")
            print(f"h3 a (título): {'✅' if title_elem else '❌'}")
            if title_elem:
                print(f"  Texto: {title_elem.text.strip()}")
                print(f"  Href: {title_elem.get('href', 'N/A')}")
            
            img_elem = item.select_first("img")
            print(f"img (poster): {'✅' if img_elem else '❌'}")
            if img_elem:
                print(f"  Src: {img_elem.get('src', 'N/A')}")
            
            quality_elem = item.select_first(".quality")
            print(f".quality: {'✅' if quality_elem else '❌'}")
            if quality_elem:
                print(f"  Texto: {quality_elem.text.strip()}")
        
        # Tentar outros seletores possíveis
        print("\n🔍 TESTANDO OUTROS SELETORES:")
        
        alternatives = [
            "article",
            ".post",
            ".movie-item",
            ".serie-item",
            ".content-item",
            "[class*='item']",
            ".entry"
        ]
        
        for selector in alternatives:
            elements = soup.select(selector)
            if elements:
                print(f"{selector}: {len(elements)} encontrados")
                if len(elements) > 0:
                    print(f"  Primeiro: {str(elements[0])[:100]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar página específica de série
    print("\n3. TESTANDO PÁGINA DE EPISÓDIO")
    print("-" * 30)
    
    try:
        # Pegar URL de uma série da página anterior
        response = session.get("https://www.maxseries.one/series/page/1")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar primeiro link de série
        links = soup.select("a[href*='/serie/'], a[href*='/episodio/']")
        if links:
            serie_url = links[0].get('href')
            if not serie_url.startswith('http'):
                serie_url = "https://www.maxseries.one" + serie_url
            
            print(f"Testando: {serie_url}")
            
            response = session.get(serie_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"Status: {response.status_code}")
            print(f"Tamanho: {len(response.text)} chars")
            
            # Verificar seletores de episódio
            print("\n📋 VERIFICANDO SELETORES DE EPISÓDIO:")
            
            title = soup.select_first("h1.entry-title")
            print(f"h1.entry-title: {'✅' if title else '❌'}")
            if title:
                print(f"  Título: {title.text.strip()}")
            
            poster = soup.select_first(".poster img")
            print(f".poster img: {'✅' if poster else '❌'}")
            
            seasons = soup.select(".seasons-lst .season")
            print(f".seasons-lst .season: {len(seasons)} encontrados")
            
            episodes = soup.select(".episode-item")
            print(f".episode-item: {len(episodes)} encontrados")
            
            # Procurar iframes
            iframes = soup.select("iframe[src]")
            print(f"iframe[src]: {len(iframes)} encontrados")
            if iframes:
                for i, iframe in enumerate(iframes[:3]):
                    src = iframe.get('src', '')
                    print(f"  Iframe {i+1}: {src}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DO DEBUG CONCLUÍDO")

if __name__ == "__main__":
    debug_maxseries_structure()