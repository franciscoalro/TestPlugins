#!/usr/bin/env python3
"""
Testar se os links do MaxSeries estão corretos
"""

import requests
from bs4 import BeautifulSoup

def test_maxseries_links():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("🔗 TESTANDO LINKS MAXSERIES")
    print("=" * 40)
    
    # Testar página de séries
    url = "https://www.maxseries.one/series/page/1"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"📄 Página: {url}")
    print(f"Status: {response.status_code}")
    
    # Analisar articles
    articles = soup.find_all('article', class_='item')
    print(f"\n📋 Articles encontrados: {len(articles)}")
    
    if articles:
        for i, article in enumerate(articles[:5]):  # Primeiros 5
            # Título
            title_elem = article.find('h3', class_='title')
            title = title_elem.text.strip() if title_elem else "N/A"
            
            # Link
            link_elem = article.find('a')
            href = link_elem.get('href') if link_elem else "N/A"
            
            # Verificar se é relativo ou absoluto
            if href.startswith('/'):
                full_url = f"https://www.maxseries.one{href}"
                link_type = "Relativo"
            elif href.startswith('http'):
                full_url = href
                link_type = "Absoluto"
            else:
                full_url = f"https://www.maxseries.one/{href}"
                link_type = "Relativo sem /"
            
            print(f"\n{i+1}. {title}")
            print(f"   Link: {href} ({link_type})")
            print(f"   Full: {full_url}")
            
            # Testar se o link funciona
            try:
                test_response = session.head(full_url, timeout=5)
                status = f"✅ {test_response.status_code}" if test_response.status_code == 200 else f"❌ {test_response.status_code}"
            except:
                status = "❌ Erro"
            
            print(f"   Test: {status}")
    
    print(f"\n🎯 RESUMO:")
    print(f"- Site base: https://www.maxseries.one")
    print(f"- Articles: {len(articles)} encontrados")
    print(f"- Estrutura: article.item > h3.title + a[href]")
    
    # Verificar se precisa de correção no provider
    if articles and articles[0].find('a'):
        first_link = articles[0].find('a').get('href')
        if first_link.startswith('/'):
            print(f"✅ Links são relativos - Provider deve usar mainUrl + href")
        else:
            print(f"⚠️ Links são absolutos - Provider pode usar href direto")

if __name__ == "__main__":
    test_maxseries_links()