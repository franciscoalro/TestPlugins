#!/usr/bin/env python3
"""
Debug CloudStream Request - Simular exatamente como o CloudStream faz requests
"""

import requests
from bs4 import BeautifulSoup

def debug_cloudstream_request():
    print("🔍 DEBUG CLOUDSTREAM REQUEST")
    print("=" * 40)
    
    # Headers que o CloudStream usa
    cloudstream_headers = {
        'User-Agent': 'CloudStream/3.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Headers de browser normal
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = "https://www.maxseries.one/series/page/1"
    
    print("1. TESTE COM HEADERS CLOUDSTREAM")
    print("-" * 30)
    
    try:
        session1 = requests.Session()
        session1.headers.update(cloudstream_headers)
        
        response1 = session1.get(url)
        soup1 = BeautifulSoup(response1.text, 'html.parser')
        articles1 = soup1.find_all('article', class_='item')
        
        print(f"Status: {response1.status_code}")
        print(f"Tamanho: {len(response1.text)} chars")
        print(f"Articles: {len(articles1)}")
        
        if articles1:
            first_title = articles1[0].find('h3', class_='title')
            print(f"Primeiro título: {first_title.text.strip() if first_title else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n2. TESTE COM HEADERS BROWSER")
    print("-" * 30)
    
    try:
        session2 = requests.Session()
        session2.headers.update(browser_headers)
        
        response2 = session2.get(url)
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        articles2 = soup2.find_all('article', class_='item')
        
        print(f"Status: {response2.status_code}")
        print(f"Tamanho: {len(response2.text)} chars")
        print(f"Articles: {len(articles2)}")
        
        if articles2:
            first_title = articles2[0].find('h3', class_='title')
            print(f"Primeiro título: {first_title.text.strip() if first_title else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n3. TESTE PÁGINA PRINCIPAL")
    print("-" * 30)
    
    try:
        main_url = "https://www.maxseries.one"
        response3 = session2.get(main_url)
        
        print(f"Status: {response3.status_code}")
        print(f"Tamanho: {len(response3.text)} chars")
        
        if len(response3.text) < 1000:
            print("⚠️ Página principal muito pequena - possível redirecionamento")
            print(f"Conteúdo: {response3.text[:200]}...")
        else:
            print("✅ Página principal OK")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n🎯 DIAGNÓSTICO:")
    if len(articles1) == 0 and len(articles2) > 0:
        print("❌ Site bloqueia User-Agent do CloudStream")
        print("💡 Solução: Adicionar User-Agent customizado no provider")
    elif len(articles1) > 0:
        print("✅ Site aceita requests do CloudStream")
        print("💡 Problema pode estar em outro lugar")
    else:
        print("❌ Site não retorna conteúdo para nenhum User-Agent")
        print("💡 Pode ser problema de JavaScript ou proteção")

if __name__ == "__main__":
    debug_cloudstream_request()