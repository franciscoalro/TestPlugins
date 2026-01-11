#!/usr/bin/env python3
"""
Parse da estrutura real do site maxseries.one
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def parse_maxseries_structure():
    print("🔍 Analisando estrutura do MaxSeries.one")
    print("=" * 50)
    
    base_url = "https://www.maxseries.one"
    
    # Analisar páginas principais
    pages_to_analyze = {
        "home": f"{base_url}",
        "movies": f"{base_url}/movies",
        "series": f"{base_url}/series"
    }
    
    structure = {
        "site_info": {
            "base_url": base_url,
            "title": "",
            "description": ""
        },
        "categories": {},
        "content_structure": {},
        "selectors": {}
    }
    
    for page_name, url in pages_to_analyze.items():
        print(f"\n📄 Analisando: {page_name} ({url})")
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if page_name == "home":
                # Extrair informações do site
                title = soup.find('title')
                structure["site_info"]["title"] = title.text.strip() if title else ""
                
                # Procurar por navegação/menu
                nav_links = soup.find_all('a')
                categories = []
                for link in nav_links:
                    href = link.get('href', '')
                    text = link.text.strip()
                    if href and text and ('series' in href.lower() or 'movies' in href.lower() or 'filmes' in href.lower()):
                        categories.append({"text": text, "href": href})
                
                structure["categories"]["navigation"] = categories
            
            elif page_name in ["movies", "series"]:
                # Analisar estrutura de conteúdo
                content_items = []
                
                # Procurar por diferentes padrões de cards/items
                possible_selectors = [
                    '.item', '.movie-item', '.series-item', '.card',
                    '[class*="item"]', '[class*="movie"]', '[class*="series"]',
                    'article', '.post', '.content-item'
                ]
                
                for selector in possible_selectors:
                    items = soup.select(selector)
                    if items and len(items) > 2:  # Se encontrou vários items
                        print(f"  ✅ Encontrado padrão: {selector} ({len(items)} items)")
                        
                        # Analisar estrutura do primeiro item
                        first_item = items[0]
                        item_structure = analyze_item_structure(first_item)
                        
                        structure["content_structure"][page_name] = {
                            "selector": selector,
                            "count": len(items),
                            "item_structure": item_structure
                        }
                        break
                
                # Se não encontrou com seletores, tentar análise de texto
                if page_name not in structure["content_structure"]:
                    text_content = soup.get_text()
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    
                    # Procurar por padrões de títulos e anos
                    content_patterns = []
                    for line in lines:
                        if any(year in line for year in ['2024', '2025', '2026', '2023', '2022']):
                            content_patterns.append(line)
                    
                    structure["content_structure"][page_name] = {
                        "method": "text_analysis",
                        "patterns_found": content_patterns[:10]  # Primeiros 10
                    }
        
        except Exception as e:
            print(f"  ❌ Erro ao analisar {page_name}: {e}")
            structure["content_structure"][page_name] = {"error": str(e)}
        
        time.sleep(1)  # Pausa entre requests
    
    # Analisar uma página específica de conteúdo
    print(f"\n📺 Analisando página específica de série...")
    try:
        series_url = f"{base_url}/series/terra-de-pecados"
        response = requests.get(series_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrair informações da página de série
        series_info = {
            "title": extract_text(soup, ['h1', '.title', '[class*="title"]']),
            "original_title": extract_text(soup, ['[class*="original"]', '.original-title']),
            "genres": extract_text(soup, ['[class*="genre"]', '.genres']),
            "seasons": extract_text(soup, ['[class*="season"]', '.seasons', '[class*="temporada"]']),
            "synopsis": extract_text(soup, ['[class*="synopsis"]', '[class*="sinopse"]', '.description']),
            "rating": extract_text(soup, ['[class*="rating"]', '.rating', '[class*="imdb"]']),
        }
        
        structure["content_structure"]["series_page"] = series_info
        
    except Exception as e:
        print(f"  ❌ Erro ao analisar página de série: {e}")
    
    return structure

def analyze_item_structure(item):
    """Analisa a estrutura de um item de conteúdo"""
    structure = {}
    
    # Procurar por diferentes elementos
    elements_to_find = {
        "title": ['h1', 'h2', 'h3', '.title', '[class*="title"]', 'a'],
        "link": ['a'],
        "image": ['img'],
        "year": ['[class*="year"]', '.year', 'span'],
        "genre": ['[class*="genre"]', '.genre'],
        "rating": ['[class*="rating"]', '.rating', '[class*="imdb"]']
    }
    
    for element_type, selectors in elements_to_find.items():
        for selector in selectors:
            found = item.select_one(selector)
            if found:
                if element_type == "link":
                    structure[element_type] = found.get('href', '')
                elif element_type == "image":
                    structure[element_type] = found.get('src', '') or found.get('data-src', '')
                else:
                    structure[element_type] = found.text.strip()
                break
    
    return structure

def extract_text(soup, selectors):
    """Extrai texto usando uma lista de seletores"""
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.text.strip()
    return ""

if __name__ == "__main__":
    try:
        structure = parse_maxseries_structure()
        
        # Salvar resultado
        with open("maxseries_structure_analysis.json", "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Análise concluída!")
        print(f"📄 Resultado salvo em: maxseries_structure_analysis.json")
        
        # Mostrar resumo
        print(f"\n📊 RESUMO DA ANÁLISE:")
        print(f"Site: {structure['site_info']['title']}")
        print(f"Categorias encontradas: {len(structure.get('categories', {}).get('navigation', []))}")
        print(f"Estruturas analisadas: {list(structure['content_structure'].keys())}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")