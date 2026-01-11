#!/usr/bin/env python3
"""
Corrigir seletores MaxSeries - Análise simples
"""

import requests
from bs4 import BeautifulSoup

def fix_maxseries():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("🔧 CORRIGINDO SELETORES MAXSERIES")
    print("=" * 40)
    
    # Testar página de séries
    url = "https://www.maxseries.one/series/page/1"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"Status: {response.status_code}")
    print(f"Tamanho: {len(response.text)} chars")
    
    # Procurar articles (parece ser o correto)
    articles = soup.find_all('article')
    print(f"\n📋 Articles encontrados: {len(articles)}")
    
    if articles:
        # Analisar primeiro article
        first = articles[0]
        print(f"\nPrimeiro article:")
        print(f"Classes: {first.get('class', [])}")
        
        # Procurar título
        h3 = first.find('h3')
        if h3:
            link = h3.find('a')
            if link:
                print(f"Título: {link.text.strip()}")
                print(f"Link: {link.get('href')}")
        
        # Procurar imagem
        img = first.find('img')
        if img:
            print(f"Imagem: {img.get('src')}")
        
        # Mostrar HTML sample
        print(f"\nHTML sample:")
        print(str(first)[:500] + "...")
        
        # Gerar seletor correto
        print(f"\n💻 SELETOR CORRETO:")
        print("document.select(\"article\").mapNotNull { it.toSearchResult() }")
        
        print(f"\n🔧 FUNÇÃO toSearchResult CORRIGIDA:")
        print("""
private fun Element.toSearchResult(): SearchResponse? {
    val title = this.selectFirst("h3 a")?.text()?.trim() ?: return null
    val href = this.selectFirst("h3 a")?.attr("href") ?: return null
    val posterUrl = this.selectFirst("img")?.attr("src")
    val quality = this.selectFirst(".quality")?.text()

    return newMovieSearchResponse(title, href, TvType.Movie) {
        this.posterUrl = posterUrl
        this.quality = getQualityFromString(quality)
    }
}
        """)

if __name__ == "__main__":
    fix_maxseries()