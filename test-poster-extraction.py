#!/usr/bin/env python3
"""
Testa extração de posters do MaxSeries
"""

import requests
from bs4 import BeautifulSoup

def test_poster_extraction():
    url = "https://www.maxseries.pics/filmes"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
    }
    
    print("🔍 Testando extração de posters...")
    print(f"URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = soup.select('article.item')
    print(f"📦 Total de items encontrados: {len(items)}\n")
    
    for i, item in enumerate(items[:5], 1):  # Apenas primeiros 5
        print(f"{'='*60}")
        print(f"ITEM {i}")
        print(f"{'='*60}")
        
        # Título
        title_elem = item.select_one('h3.title, .title, h3')
        title = title_elem.text.strip() if title_elem else "N/A"
        print(f"📌 Título: {title}")
        
        # Link
        link_elem = item.select_one('a')
        href = link_elem.get('href') if link_elem else "N/A"
        print(f"🔗 Link: {href}")
        
        # Imagem
        img = item.select_one('.image img, img')
        if img:
            src = img.get('src', '')
            data_src = img.get('data-src', '')
            alt = img.get('alt', '')
            
            print(f"🖼️ Poster:")
            print(f"   src: {src}")
            print(f"   data-src: {data_src}")
            print(f"   alt: {alt}")
            
            # Verificar se é TMDB
            poster_url = src or data_src
            if 'tmdb.org' in poster_url:
                print(f"   ✅ É do TMDB!")
                
                # Verificar tamanho
                if '/w500/' in poster_url:
                    print(f"   📏 Tamanho: w500 (500px)")
                    upgraded = poster_url.replace('/w500/', '/original/')
                    print(f"   ⬆️ Upgraded: {upgraded}")
                elif '/w1280/' in poster_url:
                    print(f"   📏 Tamanho: w1280 (1280px)")
                elif '/original/' in poster_url:
                    print(f"   📏 Tamanho: original (máxima qualidade)")
            else:
                print(f"   ⚠️ NÃO é do TMDB")
        else:
            print(f"❌ Nenhuma imagem encontrada")
        
        # Ano
        year_elem = item.select_one('.data span, span')
        year_text = year_elem.text if year_elem else ""
        print(f"📅 Ano: {year_text}")
        
        # Tipo
        is_series = '/series/' in href
        content_type = "Série" if is_series else "Filme"
        print(f"🎬 Tipo: {content_type}")
        
        print()

if __name__ == "__main__":
    test_poster_extraction()
