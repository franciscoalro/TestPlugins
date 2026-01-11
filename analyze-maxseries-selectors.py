#!/usr/bin/env python3
"""
Analisar seletores CSS do MaxSeries para corrigir o provider
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_maxseries():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    print("🔍 ANALISANDO ESTRUTURA MAXSERIES")
    print("=" * 50)
    
    # Analisar página de séries
    url = "https://www.maxseries.one/series/page/1"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"📄 Analisando: {url}")
    print(f"Status: {response.status_code}")
    print(f"Tamanho: {len(response.text)} chars")
    
    # Procurar estrutura de itens
    print("\n🔍 PROCURANDO ESTRUTURA DE ITENS:")
    
    # Analisar diferentes possibilidades
    possible_selectors = [
        "article",
        ".post",
        ".movie",
        ".serie", 
        ".item",
        "[class*='item']",
        "[class*='post']",
        "[class*='movie']",
        "[class*='serie']"
    ]
    
    found_items = []
    
    for selector in possible_selectors:
        elements = soup.select(selector)
        if elements and len(elements) > 5:  # Pelo menos 5 itens
            print(f"✅ {selector}: {len(elements)} itens encontrados")
            
            # Analisar primeiro item
            first_item = elements[0]
            
            # Procurar título
            title_selectors = ["h1", "h2", "h3", "h4", ".title", "[class*='title']", "a"]
            title_found = None
            title_selector = None
            
            for ts in title_selectors:
                title_elem = first_item.select_first(ts)
                if title_elem and title_elem.text.strip():
                    title_found = title_elem.text.strip()
                    title_selector = ts
                    break
            
            # Procurar link
            link_elem = first_item.select_first("a[href]")
            link_found = link_elem.get('href') if link_elem else None
            
            # Procurar imagem
            img_elem = first_item.select_first("img")
            img_found = img_elem.get('src') if img_elem else None
            
            if title_found and link_found:
                found_items.append({
                    'container_selector': selector,
                    'title_selector': title_selector,
                    'title': title_found,
                    'link': link_found,
                    'image': img_found,
                    'html_sample': str(first_item)[:300]
                })
                
                print(f"  📝 Título: {title_found}")
                print(f"  🔗 Link: {link_found}")
                print(f"  🖼️ Imagem: {img_found}")
        else:
            print(f"❌ {selector}: {len(elements)} itens")
    
    # Mostrar melhor opção
    if found_items:
        print(f"\n🎯 MELHOR OPÇÃO ENCONTRADA:")
        best = found_items[0]
        print(f"Container: {best['container_selector']}")
        print(f"Título: {best['title_selector']}")
        print(f"Exemplo: {best['title']}")
        
        # Gerar código Kotlin
        print(f"\n💻 CÓDIGO KOTLIN SUGERIDO:")
        print("```kotlin")
        print("private fun Element.toSearchResult(): SearchResponse? {")
        print(f"    val title = this.selectFirst(\"{best['title_selector']}\")?.text()?.trim() ?: return null")
        print(f"    val href = this.selectFirst(\"a\")?.attr(\"href\") ?: return null")
        print("    val posterUrl = this.selectFirst(\"img\")?.attr(\"src\")")
        print("    val quality = this.selectFirst(\".quality\")?.text()")
        print("")
        print("    return newMovieSearchResponse(title, href, TvType.Movie) {")
        print("        this.posterUrl = posterUrl")
        print("        this.quality = getQualityFromString(quality)")
        print("    }")
        print("}")
        print("")
        print("// No getMainPage:")
        print(f"val home = document.select(\"{best['container_selector']}\").mapNotNull {{")
        print("    it.toSearchResult()")
        print("}")
        print("```")
        
        # Salvar análise
        with open('maxseries_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(found_items, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análise salva em: maxseries_analysis.json")
    
    else:
        print("\n❌ NENHUMA ESTRUTURA VÁLIDA ENCONTRADA")
        print("O site pode estar usando JavaScript para carregar conteúdo")
        
        # Salvar HTML para análise manual
        with open('maxseries_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📄 HTML salvo em: maxseries_page.html")

if __name__ == "__main__":
    analyze_maxseries()