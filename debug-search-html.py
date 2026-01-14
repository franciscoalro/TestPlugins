#!/usr/bin/env python3
"""
Debug da página de busca - salvar HTML para análise
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

query = "gerente"
url = f"https://www.maxseries.one/?s={query}"

print(f"🔍 Buscando: {url}")

response = requests.get(url, headers=HEADERS, timeout=15)
html = response.text

# Salvar HTML
filename = f"search_result_{query}.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html)

print(f"💾 HTML salvo: {filename}")
print(f"📊 Tamanho: {len(html)} bytes")

# Analisar estrutura
soup = BeautifulSoup(html, 'html.parser')

print("\n🔍 Análise da estrutura:")
print(f"  - <article>: {len(soup.select('article'))}")
print(f"  - <article.item>: {len(soup.select('article.item'))}")
print(f"  - <div.result-item>: {len(soup.select('div.result-item'))}")
print(f"  - <div.search-item>: {len(soup.select('div.search-item'))}")
print(f"  - <div.item>: {len(soup.select('div.item'))}")
print(f"  - <li>: {len(soup.select('li'))}")

# Procurar por "no results" ou mensagens
no_results = soup.find(text=lambda t: t and ('no result' in t.lower() or 'nenhum resultado' in t.lower() or 'não encontrado' in t.lower()))
if no_results:
    print(f"\n⚠️ Mensagem encontrada: {no_results.strip()}")

# Procurar título da página
title = soup.find('title')
if title:
    print(f"\n📄 Título da página: {title.get_text(strip=True)}")

# Procurar h1
h1 = soup.find('h1')
if h1:
    print(f"📌 H1: {h1.get_text(strip=True)}")

# Verificar se tem conteúdo de busca
search_content = soup.select('.content, #content, main')
if search_content:
    print(f"\n📦 Área de conteúdo encontrada: {len(search_content)} elementos")
    for i, content in enumerate(search_content[:2], 1):
        print(f"  {i}. Classes: {content.get('class')}")
        print(f"     Filhos: {len(list(content.children))}")
