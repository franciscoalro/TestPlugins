#!/usr/bin/env python3
"""
Testa as novas categorias adicionadas ao MaxSeries v208
"""

import requests
from bs4 import BeautifulSoup

def test_category(url, name):
    """Testa uma categoria"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('article.item')
            return f"✅ {len(items):3d} items"
        else:
            return f"❌ HTTP {response.status_code}"
    except Exception as e:
        return f"❌ {str(e)[:30]}"

def main():
    print("🧪 TESTE DAS NOVAS CATEGORIAS - MaxSeries v208")
    print("="*80)
    
    base_url = "https://www.maxseries.pics"
    
    # Categorias NOVAS (v208)
    new_categories = [
        ("trending", "Em Alta"),
        ("generos/aventura", "Aventura"),
        ("generos/crime", "Crime"),
        ("generos/documentario", "Documentário"),
        ("generos/familia", "Família"),
        ("generos/fantasia", "Fantasia"),
        ("generos/faroeste", "Faroeste"),
        ("generos/ficcao-cientifica", "Ficção Científica"),
        ("generos/guerra", "Guerra"),
        ("generos/historia", "História"),
        ("generos/kids", "Infantil"),
        ("generos/misterio", "Mistério"),
        ("generos/musica", "Música"),
        ("generos/thriller", "Thriller"),
    ]
    
    print("\n🆕 NOVAS CATEGORIAS (v208):")
    print("-"*80)
    
    success = 0
    failed = 0
    
    for path, name in new_categories:
        url = f"{base_url}/{path}"
        result = test_category(url, name)
        print(f"{name:25} → {result}")
        
        if "✅" in result:
            success += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print(f"📊 RESULTADO: {success}/{len(new_categories)} funcionando")
    
    if failed > 0:
        print(f"⚠️ {failed} categorias com problema")
    else:
        print("✅ TODAS as novas categorias funcionando perfeitamente!")

if __name__ == "__main__":
    main()
