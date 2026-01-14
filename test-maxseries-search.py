#!/usr/bin/env python3
"""
Teste de Busca do MaxSeries
Testa diferentes endpoints de busca para identificar o problema
"""

import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def test_search_method_1(query):
    """Método 1: GET /?s=query"""
    print(f"\n{'='*80}")
    print(f"🔍 MÉTODO 1: GET /?s={query}")
    print(f"{'='*80}")
    
    url = f"https://www.maxseries.one/?s={query.replace(' ', '+')}"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Size: {len(response.text)} bytes")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar resultados
        articles = soup.select('article.item')
        print(f"\n📊 Resultados encontrados: {len(articles)}")
        
        for i, article in enumerate(articles[:5], 1):
            title_elem = article.select_one('h3.title, .title, h3')
            link_elem = article.select_one('a')
            
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href')
                print(f"  {i}. {title}")
                print(f"     {link}")
        
        return len(articles) > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_search_method_2(query):
    """Método 2: WordPress REST API Search"""
    print(f"\n{'='*80}")
    print(f"🔍 MÉTODO 2: WordPress REST API /wp-json/dooplay/search/")
    print(f"{'='*80}")
    
    url = f"https://www.maxseries.one/wp-json/dooplay/search/"
    print(f"URL: {url}")
    
    try:
        # Primeiro, tentar GET para ver estrutura
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2)[:500]}")
        
        # Tentar POST com query
        print(f"\n🔄 Tentando POST com query...")
        response = requests.post(
            url,
            headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            data={"s": query},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resultados: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"Resposta: {json.dumps(data, indent=2)[:500]}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_search_method_3(query):
    """Método 3: AJAX Search"""
    print(f"\n{'='*80}")
    print(f"🔍 MÉTODO 3: AJAX Live Search")
    print(f"{'='*80}")
    
    url = "https://www.maxseries.one/wp-admin/admin-ajax.php"
    print(f"URL: {url}")
    
    try:
        response = requests.post(
            url,
            headers={
                **HEADERS,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            },
            data={
                "action": "doo_search",
                "s": query
            },
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Size: {len(response.text)} bytes")
        
        if response.status_code == 200:
            print(f"Resposta: {response.text[:500]}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_search_method_4(query):
    """Método 4: Busca na página de séries/filmes"""
    print(f"\n{'='*80}")
    print(f"🔍 MÉTODO 4: Busca manual em /series e /filmes")
    print(f"{'='*80}")
    
    results = []
    
    for section in ['/series', '/filmes']:
        url = f"https://www.maxseries.one{section}"
        print(f"\n📂 Buscando em: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.select('article.item')
            print(f"   Total de items: {len(articles)}")
            
            # Filtrar por query
            for article in articles:
                title_elem = article.select_one('h3.title, .title, h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if query.lower() in title.lower():
                        link_elem = article.select_one('a')
                        if link_elem:
                            results.append({
                                'title': title,
                                'url': link_elem.get('href')
                            })
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n📊 Resultados filtrados: {len(results)}")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result['title']}")
        print(f"     {result['url']}")
    
    return len(results) > 0


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           Teste de Busca MaxSeries - Janeiro 2026            ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Queries de teste
    queries = [
        "gerente",
        "chapolin",
        "garota",
        "mil golpes"
    ]
    
    for query in queries:
        print(f"\n\n{'#'*80}")
        print(f"# TESTANDO QUERY: '{query}'")
        print(f"{'#'*80}")
        
        # Testar todos os métodos
        method1 = test_search_method_1(query)
        method2 = test_search_method_2(query)
        method3 = test_search_method_3(query)
        method4 = test_search_method_4(query)
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMO PARA '{query}':")
        print(f"{'='*80}")
        print(f"  Método 1 (GET /?s=): {'✅ Funciona' if method1 else '❌ Falhou'}")
        print(f"  Método 2 (REST API): {'✅ Funciona' if method2 else '❌ Falhou'}")
        print(f"  Método 3 (AJAX): {'✅ Funciona' if method3 else '❌ Falhou'}")
        print(f"  Método 4 (Manual): {'✅ Funciona' if method4 else '❌ Falhou'}")
        
        # Parar após primeiro teste para não sobrecarregar
        break
    
    print("\n\n✅ Teste completo!")


if __name__ == "__main__":
    main()
