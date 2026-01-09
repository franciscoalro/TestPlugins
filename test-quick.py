#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Testar acesso ao site
url = 'https://www.maxseries.one/series/'
print(f'Acessando: {url}')
response = requests.get(url, headers=HEADERS, timeout=30)
print(f'Status: {response.status_code}')

soup = BeautifulSoup(response.text, 'html.parser')

# Ver estrutura
articles = soup.select('article')
print(f'Articles encontrados: {len(articles)}')

# Pegar primeiro article
if articles:
    art = articles[0]
    print(f'\nPrimeiro article:')
    print(f'Classes: {art.get("class")}')
    
    # Buscar links
    links = art.select('a')
    for link in links[:3]:
        href = link.get('href', '')
        text = link.text.strip()[:50] if link.text else ''
        print(f'  Link: {href}')
        print(f'  Text: {text}')
    
    # Buscar imagens
    imgs = art.select('img')
    for img in imgs[:2]:
        src = img.get('src', '')
        print(f'  Img: {src[:80]}')

# Pegar uma série específica
print('\n--- Testando série específica ---')
series_link = None
for art in articles[:5]:
    link = art.select_one('a')
    if link:
        href = link.get('href', '')
        if '/series/' in href:
            series_link = href
            print(f'Série encontrada: {href}')
            break

if series_link:
    print(f'\nCarregando série: {series_link}')
    r2 = requests.get(series_link, headers=HEADERS, timeout=30)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    # Buscar iframe
    iframe = soup2.select_one('iframe')
    if iframe:
        src = iframe.get('src', '')
        if src.startswith('//'):
            src = 'https:' + src
        print(f'Iframe: {src}')
        
        # Carregar iframe
        print(f'\nCarregando iframe...')
        r3 = requests.get(src, headers=HEADERS, timeout=30)
        soup3 = BeautifulSoup(r3.text, 'html.parser')
        
        # Buscar episódios
        eps = soup3.select('li[data-episode-id]')
        print(f'Episódios encontrados: {len(eps)}')
        
        if eps:
            ep = eps[0]
            ep_id = ep.get('data-episode-id', '')
            print(f'Primeiro episódio ID: {ep_id}')
            
            # Fazer AJAX
            if ep_id:
                ajax_url = f'https://playerthree.online/episodio/{ep_id}'
                print(f'\nAJAX: {ajax_url}')
                
                ajax_headers = {
                    **HEADERS,
                    'Referer': src,
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                r4 = requests.get(ajax_url, headers=ajax_headers, timeout=30)
                print(f'AJAX Status: {r4.status_code}')
                
                soup4 = BeautifulSoup(r4.text, 'html.parser')
                
                # Buscar players
                buttons = soup4.select('button[data-source]')
                print(f'Botões de player: {len(buttons)}')
                
                for btn in buttons:
                    name = btn.text.strip()
                    source = btn.get('data-source', '')
                    if source and 'youtube' not in source.lower():
                        print(f'  {name}: {source[:80]}')
    else:
        print('Nenhum iframe encontrado')
