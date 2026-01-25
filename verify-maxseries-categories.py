#!/usr/bin/env python3
"""
Verifica se as categorias do MaxSeries estão corretas
"""

import requests
from bs4 import BeautifulSoup

def check_url(url, name):
    """Verifica se uma URL está acessível e retorna informações"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Contar items
            items = soup.select('article.item')
            
            # Verificar título da página
            page_title = soup.select_one('h1, .page-title, title')
            title_text = page_title.text.strip() if page_title else "N/A"
            
            return {
                'status': '✅ OK',
                'code': response.status_code,
                'items': len(items),
                'title': title_text[:50]
            }
        else:
            return {
                'status': '⚠️ ERRO',
                'code': response.status_code,
                'items': 0,
                'title': 'N/A'
            }
    except Exception as e:
        return {
            'status': '❌ FALHA',
            'code': 'N/A',
            'items': 0,
            'title': str(e)[:50]
        }

def main():
    print("🔍 VERIFICAÇÃO DE CATEGORIAS DO MAXSERIES")
    print("="*80)
    
    base_url = "https://www.maxseries.pics"
    
    categories = [
        (f"{base_url}/", "Início"),
        (f"{base_url}/filmes", "Filmes"),
        (f"{base_url}/series", "Séries"),
        (f"{base_url}/generos/acao", "Ação"),
        (f"{base_url}/generos/comedia", "Comédia"),
        (f"{base_url}/generos/drama", "Drama"),
        (f"{base_url}/generos/terror", "Terror"),
        (f"{base_url}/generos/romance", "Romance"),
        (f"{base_url}/generos/animacao", "Animação"),
    ]
    
    print(f"\n📍 Base URL: {base_url}\n")
    
    results = []
    
    for url, name in categories:
        print(f"🔎 Testando: {name:15} → {url}")
        result = check_url(url, name)
        results.append((name, url, result))
        
        print(f"   {result['status']} | HTTP {result['code']} | {result['items']} items | {result['title']}")
        print()
    
    # Resumo
    print("="*80)
    print("📊 RESUMO")
    print("="*80)
    
    ok_count = sum(1 for _, _, r in results if r['status'] == '✅ OK')
    error_count = sum(1 for _, _, r in results if r['status'] != '✅ OK')
    
    print(f"\n✅ Funcionando: {ok_count}/{len(results)}")
    print(f"❌ Com erro: {error_count}/{len(results)}")
    
    if error_count > 0:
        print("\n⚠️ URLs COM PROBLEMA:")
        for name, url, result in results:
            if result['status'] != '✅ OK':
                print(f"  - {name}: {url}")
                print(f"    Erro: {result['title']}")
    
    # Sugestões de categorias reais
    print("\n" + "="*80)
    print("🔍 DESCOBRINDO CATEGORIAS REAIS DO SITE...")
    print("="*80)
    
    try:
        response = requests.get(base_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
        }, timeout=10)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar links de menu/navegação
        nav_links = soup.select('nav a, .menu a, header a, .navigation a')
        
        print("\n📋 Links encontrados no menu:")
        found_categories = set()
        
        for link in nav_links:
            href = link.get('href', '')
            text = link.text.strip()
            
            if href and text and len(text) > 2:
                # Filtrar apenas links relevantes
                if any(x in href.lower() for x in ['filme', 'serie', 'genero', 'categoria', 'lancamento']):
                    if href.startswith('/'):
                        href = base_url + href
                    
                    if href not in found_categories:
                        found_categories.add(href)
                        print(f"  • {text:20} → {href}")
        
        # Procurar gêneros específicos
        print("\n🎭 Gêneros encontrados:")
        genre_links = soup.select('a[href*="genero"], a[href*="genre"], .genres a, .genre a')
        
        for link in genre_links:
            href = link.get('href', '')
            text = link.text.strip()
            
            if href and text:
                if href.startswith('/'):
                    href = base_url + href
                print(f"  • {text:20} → {href}")
        
    except Exception as e:
        print(f"❌ Erro ao descobrir categorias: {e}")

if __name__ == "__main__":
    main()
