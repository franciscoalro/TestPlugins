#!/usr/bin/env python3
"""
Teste da correção de busca - simula o que o provider faz
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
}

def test_search_kotlin_way(query):
    """Simula o código Kotlin corrigido"""
    print(f"\n{'='*80}")
    print(f"🔍 Testando busca: '{query}'")
    print(f"{'='*80}")
    
    url = f"https://www.maxseries.one/?s={query.replace(' ', '+')}"
    print(f"URL: {url}\n")
    
    response = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Método 1: .result-item article (página de busca)
    search_results = soup.select(".result-item article")
    print(f"📊 Método 1 (.result-item article): {len(search_results)} resultados")
    
    for i, article in enumerate(search_results[:5], 1):
        # Simular toSearchResultFromSearch()
        link_elem = article.select_one(".thumbnail a") or article.select_one("a")
        if link_elem:
            href = link_elem.get('href')
            
            img = article.select_one("img")
            title = img.get('alt') if img else None
            if not title:
                title_elem = article.select_one("h3, .title")
                title = title_elem.get_text(strip=True) if title_elem else "Sem título"
            
            # Verificar tipo
            is_series = "/series/" in href or article.select_one(".tvshows") is not None
            tv_type = "TvSeries" if is_series else "Movie"
            
            print(f"  {i}. {title} ({tv_type})")
            print(f"     {href}")
    
    # Método 2: article.item (fallback)
    normal_results = soup.select("article.item")
    print(f"\n📊 Método 2 (article.item - fallback): {len(normal_results)} resultados")
    
    total = len(search_results) + (len(normal_results) if not search_results else 0)
    print(f"\n✅ Total de resultados: {total}")
    
    return total > 0


# Testar com várias queries
queries = ["gerente", "chapolin", "garota", "mil golpes", "breaking bad"]

print("""
╔═══════════════════════════════════════════════════════════════╗
║        Teste de Correção de Busca - MaxSeries v78            ║
╚═══════════════════════════════════════════════════════════════╝
""")

success_count = 0
for query in queries:
    if test_search_kotlin_way(query):
        success_count += 1

print(f"\n\n{'='*80}")
print(f"📊 RESUMO FINAL")
print(f"{'='*80}")
print(f"✅ Buscas bem-sucedidas: {success_count}/{len(queries)}")
print(f"{'✅ CORREÇÃO FUNCIONA!' if success_count == len(queries) else '⚠️ Algumas buscas falharam'}")
