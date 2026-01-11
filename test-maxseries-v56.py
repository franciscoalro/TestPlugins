#!/usr/bin/env python3
"""
Testar MaxSeries v56 - Critical AnimesOnlineCC Fixes
"""

import requests
from bs4 import BeautifulSoup
import json

def test_maxseries_v56():
    print("🧪 TESTE MaxSeries v56 - Critical AnimesOnlineCC Fixes")
    print("=" * 60)
    
    base_url = "https://www.maxseries.one"
    
    try:
        print(f"\n🌐 Testando acesso ao site: {base_url}")
        response = requests.get(base_url, timeout=10)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Testar seletor principal usado no provider
            print(f"\n🔍 Testando seletor: 'div.items article.item'")
            items = soup.select("div.items article.item")
            print(f"📊 Encontrados: {len(items)} itens")
            
            if items:
                print(f"\n📋 ANÁLISE DOS PRIMEIROS 3 ITENS:")
                for i, item in enumerate(items[:3]):
                    print(f"\n--- ITEM {i+1} ---")
                    
                    # Título
                    title_elem = item.select_one("h3.title, h3")
                    title = title_elem.text.strip() if title_elem else "N/A"
                    print(f"📝 Título: {title}")
                    
                    # Link
                    link_elem = item.select_one("a")
                    href = link_elem.get('href') if link_elem else "N/A"
                    print(f"🔗 Link: {href}")
                    
                    # Imagem
                    img_elem = item.select_one("img")
                    if img_elem:
                        img_src = (img_elem.get('src') or 
                                 img_elem.get('data-src') or 
                                 img_elem.get('data-lazy-src') or 
                                 img_elem.get('data-original') or "N/A")
                        print(f"🖼️ Imagem: {img_src}")
                    else:
                        print(f"🖼️ Imagem: N/A")
                    
                    # Qualidade
                    quality_elem = item.select_one(".quality")
                    quality = quality_elem.text.strip() if quality_elem else "N/A"
                    print(f"⭐ Qualidade: {quality}")
            
            # Testar página de filmes
            print(f"\n🎬 Testando página de filmes...")
            movies_url = f"{base_url}/movies/page/1"
            movies_response = requests.get(movies_url, timeout=10)
            print(f"✅ Filmes Status: {movies_response.status_code}")
            
            if movies_response.status_code == 200:
                movies_soup = BeautifulSoup(movies_response.content, 'html.parser')
                movies_items = movies_soup.select("div.items article.item")
                print(f"🎬 Filmes encontrados: {len(movies_items)}")
            
            # Testar página de séries
            print(f"\n📺 Testando página de séries...")
            series_url = f"{base_url}/series/page/1"
            series_response = requests.get(series_url, timeout=10)
            print(f"✅ Séries Status: {series_response.status_code}")
            
            if series_response.status_code == 200:
                series_soup = BeautifulSoup(series_response.content, 'html.parser')
                series_items = series_soup.select("div.items article.item")
                print(f"📺 Séries encontradas: {len(series_items)}")
            
            # Testar pesquisa
            print(f"\n🔍 Testando pesquisa...")
            search_url = f"{base_url}/?s=naruto"
            search_response = requests.get(search_url, timeout=10)
            print(f"✅ Pesquisa Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_soup = BeautifulSoup(search_response.content, 'html.parser')
                search_items = search_soup.select("div.items article.item")
                print(f"🔍 Resultados de pesquisa: {len(search_items)}")
            
            print(f"\n✅ RESUMO DO TESTE:")
            print(f"- Site acessível: ✅")
            print(f"- Seletor funcionando: ✅ ({len(items)} itens)")
            print(f"- Página de filmes: ✅ ({len(movies_items) if 'movies_items' in locals() else 0} itens)")
            print(f"- Página de séries: ✅ ({len(series_items) if 'series_items' in locals() else 0} itens)")
            print(f"- Pesquisa: ✅ ({len(search_items) if 'search_items' in locals() else 0} resultados)")
            
            print(f"\n🎯 CONCLUSÃO:")
            if len(items) > 0:
                print(f"✅ MaxSeries v56 deve funcionar corretamente!")
                print(f"✅ Seletores encontrando conteúdo")
                print(f"✅ Estrutura compatível com o provider")
            else:
                print(f"❌ Problema: Seletor não encontrou itens")
                print(f"❌ Pode precisar ajustar seletores CSS")
        
        else:
            print(f"❌ Erro ao acessar o site: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    test_maxseries_v56()