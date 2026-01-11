#!/usr/bin/env python3
"""
Teste da estrutura real do MaxSeries.one para validar as correções
"""

import requests
from bs4 import BeautifulSoup
import json

def test_maxseries_structure():
    print("🧪 Testando estrutura real do MaxSeries.one")
    print("=" * 50)
    
    base_url = "https://www.maxseries.one"
    
    # Testar URLs corretas baseadas na análise
    test_urls = {
        "filmes": f"{base_url}/filmes/",
        "series": f"{base_url}/series/",
        "search": f"{base_url}/?s=batman"
    }
    
    results = {}
    
    for category, url in test_urls.items():
        print(f"\n📋 Testando: {category}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Testar seletor .item
            items = soup.select('.item')
            print(f"✅ Seletor '.item': {len(items)} items encontrados")
            
            if items:
                # Analisar primeiro item
                first_item = items[0]
                
                # Testar seletores de título
                title_selectors = ['h3', '.title', 'h3.title']
                title_found = None
                for selector in title_selectors:
                    title_elem = first_item.select_one(selector)
                    if title_elem:
                        title_found = title_elem.text.strip()
                        print(f"  📝 Título ('{selector}'): {title_found}")
                        break
                
                # Testar link
                link_elem = first_item.select_one('a')
                if link_elem:
                    href = link_elem.get('href', '')
                    print(f"  🔗 Link: {href}")
                    
                    # Detectar tipo baseado na URL
                    if '/series/' in href:
                        content_type = "TvSeries"
                    elif '/filmes/' in href:
                        content_type = "Movie"
                    else:
                        content_type = "Unknown"
                    print(f"  🎬 Tipo detectado: {content_type}")
                
                # Testar imagem
                img_elem = first_item.select_one('img')
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    print(f"  🖼️ Imagem: {img_src[:50]}..." if img_src else "  ❌ Imagem não encontrada")
                
                results[category] = {
                    "items_count": len(items),
                    "title": title_found,
                    "link": href if 'href' in locals() else None,
                    "type": content_type if 'content_type' in locals() else None,
                    "has_image": img_elem is not None
                }
            else:
                print("  ❌ Nenhum item encontrado")
                results[category] = {"error": "No items found"}
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            results[category] = {"error": str(e)}
    
    # Testar página específica de série
    print(f"\n📺 Testando página específica de série...")
    try:
        series_url = f"{base_url}/series/assistir-terra-de-pecados-online"
        response = requests.get(series_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procurar por elementos de série
        title = soup.select_one('h1')
        title_text = title.text.strip() if title else "Não encontrado"
        print(f"  📝 Título da série: {title_text}")
        
        # Procurar por temporadas
        seasons_text = soup.get_text()
        has_seasons = 'temporada' in seasons_text.lower() or 'season' in seasons_text.lower()
        print(f"  📺 Tem temporadas: {has_seasons}")
        
        # Procurar por gêneros
        genres_found = []
        for text in soup.stripped_strings:
            if any(genre in text.lower() for genre in ['drama', 'crime', 'mistério', 'comédia', 'ação']):
                if len(text) < 50:  # Evitar textos muito longos
                    genres_found.append(text)
        
        print(f"  🎭 Gêneros encontrados: {genres_found[:3]}")
        
        results["series_page"] = {
            "title": title_text,
            "has_seasons": has_seasons,
            "genres": genres_found[:3]
        }
        
    except Exception as e:
        print(f"  ❌ Erro ao testar página de série: {e}")
        results["series_page"] = {"error": str(e)}
    
    # Salvar resultados
    with open("maxseries_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Teste concluído!")
    print(f"📄 Resultados salvos em: maxseries_test_results.json")
    
    # Resumo
    print(f"\n📊 RESUMO DOS TESTES:")
    for category, result in results.items():
        if "error" not in result:
            print(f"✅ {category}: OK")
        else:
            print(f"❌ {category}: {result['error']}")
    
    return results

if __name__ == "__main__":
    test_maxseries_structure()