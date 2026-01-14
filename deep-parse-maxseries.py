#!/usr/bin/env python3
"""
Parse profundo do MaxSeries.one para capturar estrutura completa
- Página inicial
- Filmes
- Séries
- Episódios
- Players
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def save_html(content, filename):
    """Salva HTML para análise"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Salvo: {filename}")

def parse_home():
    """Parse da página inicial"""
    print("\n" + "="*60)
    print("🏠 PÁGINA INICIAL")
    print("="*60)
    
    url = "https://www.maxseries.one"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_home.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Estrutura da página
    print("\n📋 Estrutura da Home:")
    
    # Menu principal
    menu = soup.select("nav a, .menu a, header a")
    print(f"\n🔗 Links do Menu ({len(menu)}):")
    for link in menu[:10]:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if text and href:
            print(f"  - {text}: {href}")
    
    # Seções de conteúdo
    sections = soup.select("section, .section, .content-section")
    print(f"\n📦 Seções de Conteúdo: {len(sections)}")
    
    # Cards de filmes/séries
    cards = soup.select("article.item, .item, .movie-item, .serie-item")
    print(f"\n🎬 Cards de Conteúdo: {len(cards)}")
    
    if cards:
        print("\n📝 Estrutura de um Card:")
        card = cards[0]
        print(f"  HTML: {card.prettify()[:500]}...")
        
        # Extrair informações
        title = card.select_one("h3, .title, h2")
        link = card.select_one("a")
        image = card.select_one("img")
        year = card.select_one(".year, .data span")
        
        print(f"\n  Título: {title.get_text(strip=True) if title else 'N/A'}")
        print(f"  Link: {link.get('href') if link else 'N/A'}")
        print(f"  Imagem: {image.get('src') or image.get('data-src') if image else 'N/A'}")
        print(f"  Ano: {year.get_text(strip=True) if year else 'N/A'}")
    
    # Categorias
    categories = soup.select(".genres a, .category a, .sgeneros a")
    print(f"\n🏷️ Categorias: {len(categories)}")
    for cat in categories[:5]:
        print(f"  - {cat.get_text(strip=True)}")
    
    return {
        "url": url,
        "cards_count": len(cards),
        "sections_count": len(sections)
    }

def parse_movies_page():
    """Parse da página de filmes"""
    print("\n" + "="*60)
    print("🎬 PÁGINA DE FILMES")
    print("="*60)
    
    url = "https://www.maxseries.one/filmes"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_filmes.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Cards de filmes
    cards = soup.select("article.item, .item, .movie-item")
    print(f"\n🎬 Total de Filmes: {len(cards)}")
    
    # Paginação
    pagination = soup.select(".pagination a, .nav-links a")
    print(f"\n📄 Paginação: {len(pagination)} links")
    
    # Filtros
    filters = soup.select(".filters select, .filter-select")
    print(f"\n🔍 Filtros: {len(filters)}")
    
    # Analisar 3 filmes
    movies = []
    for i, card in enumerate(cards[:3]):
        print(f"\n📽️ Filme {i+1}:")
        
        title_elem = card.select_one("h3, .title, h2")
        link_elem = card.select_one("a")
        img_elem = card.select_one("img")
        
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        link = link_elem.get('href') if link_elem else None
        img = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
        
        print(f"  Título: {title}")
        print(f"  Link: {link}")
        print(f"  Imagem: {img}")
        
        movie = {
            "title": title,
            "link": link,
            "image": img
        }
        movies.append(movie)
    
    return movies

def parse_series_page():
    """Parse da página de séries"""
    print("\n" + "="*60)
    print("📺 PÁGINA DE SÉRIES")
    print("="*60)
    
    url = "https://www.maxseries.one/series"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_series.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Cards de séries
    cards = soup.select("article.item, .item, .serie-item")
    print(f"\n📺 Total de Séries: {len(cards)}")
    
    # Analisar 3 séries
    series = []
    for i, card in enumerate(cards[:3]):
        print(f"\n📺 Série {i+1}:")
        
        title_elem = card.select_one("h3, .title, h2")
        link_elem = card.select_one("a")
        img_elem = card.select_one("img")
        
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        link = link_elem.get('href') if link_elem else None
        img = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
        
        print(f"  Título: {title}")
        print(f"  Link: {link}")
        
        if link:
            series.append({
                "title": title,
                "link": link,
                "image": img
            })
    
    return series

def parse_movie_detail(movie_url):
    """Parse de uma página de filme"""
    print("\n" + "="*60)
    print(f"🎬 DETALHES DO FILME")
    print("="*60)
    print(f"URL: {movie_url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(movie_url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_movie_detail.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Título
    title = soup.select_one("h1, .title")
    print(f"\n📝 Título: {title.get_text(strip=True) if title else 'N/A'}")
    
    # Poster
    poster = soup.select_one(".poster img, .movie-poster img")
    print(f"🖼️ Poster: {poster.get('src') if poster else 'N/A'}")
    
    # Sinopse
    plot = soup.select_one(".description, .sinopse, .plot")
    print(f"📖 Sinopse: {plot.get_text(strip=True)[:100] if plot else 'N/A'}...")
    
    # Gêneros
    genres = soup.select(".sgeneros a, .genres a")
    print(f"🏷️ Gêneros: {', '.join([g.get_text(strip=True) for g in genres])}")
    
    # Ano
    year_elem = soup.select_one(".year, .data")
    print(f"📅 Ano: {year_elem.get_text(strip=True) if year_elem else 'N/A'}")
    
    # Iframe do player
    iframes = soup.select("iframe")
    print(f"\n🎥 Iframes encontrados: {len(iframes)}")
    for i, iframe in enumerate(iframes):
        src = iframe.get('src', '')
        print(f"  {i+1}. {src}")
    
    # Procurar playerthree
    playerthree_pattern = re.compile(r'https?://playerthree\.online/[^"\']+')
    playerthree_urls = playerthree_pattern.findall(html)
    print(f"\n🎮 URLs do PlayerThree: {len(playerthree_urls)}")
    for url in playerthree_urls[:3]:
        print(f"  - {url}")
    
    return {
        "title": title.get_text(strip=True) if title else None,
        "playerthree_urls": playerthree_urls
    }

def parse_series_detail(series_url):
    """Parse de uma página de série"""
    print("\n" + "="*60)
    print(f"📺 DETALHES DA SÉRIE")
    print("="*60)
    print(f"URL: {series_url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(series_url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_series_detail.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Título
    title = soup.select_one("h1, .title")
    print(f"\n📝 Título: {title.get_text(strip=True) if title else 'N/A'}")
    
    # Temporadas
    seasons = soup.select(".se-c, .seasons .se-a, #seasons .se-c")
    print(f"\n📺 Temporadas: {len(seasons)}")
    
    # Episódios
    episodes_data = []
    for season_idx, season in enumerate(seasons[:2]):  # Analisar 2 temporadas
        print(f"\n🎬 Temporada {season_idx + 1}:")
        
        episodes = season.select(".episodios li, .se-a ul li, ul.episodios li")
        print(f"  Episódios: {len(episodes)}")
        
        for ep_idx, episode in enumerate(episodes[:3]):  # Analisar 3 episódios
            ep_link = episode.select_one("a")
            ep_title = episode.select_one(".episodiotitle a, .epst")
            
            if ep_link:
                ep_url = ep_link.get('href')
                ep_name = ep_title.get_text(strip=True) if ep_title else f"Episódio {ep_idx + 1}"
                
                print(f"    {ep_idx + 1}. {ep_name}: {ep_url}")
                
                episodes_data.append({
                    "season": season_idx + 1,
                    "episode": ep_idx + 1,
                    "title": ep_name,
                    "url": ep_url
                })
    
    # Iframe do player
    iframes = soup.select("iframe")
    print(f"\n🎥 Iframes encontrados: {len(iframes)}")
    for i, iframe in enumerate(iframes):
        src = iframe.get('src', '')
        if 'playerthree' in src:
            print(f"  ✅ PlayerThree: {src}")
    
    # Procurar playerthree no HTML
    playerthree_pattern = re.compile(r'https?://playerthree\.online/[^"\']+')
    playerthree_urls = playerthree_pattern.findall(html)
    print(f"\n🎮 URLs do PlayerThree: {len(playerthree_urls)}")
    for url in set(playerthree_urls)[:3]:
        print(f"  - {url}")
    
    return {
        "title": title.get_text(strip=True) if title else None,
        "seasons": len(seasons),
        "episodes": episodes_data,
        "playerthree_urls": list(set(playerthree_urls))
    }

def parse_playerthree(playerthree_url):
    """Parse da página do PlayerThree"""
    print("\n" + "="*60)
    print(f"🎮 PLAYERTHREE")
    print("="*60)
    print(f"URL: {playerthree_url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.maxseries.one"
    }
    
    response = requests.get(playerthree_url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, "maxseries_playerthree.html")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Temporadas
    seasons = soup.select(".header-navigation li[data-season-id]")
    print(f"\n📺 Temporadas: {len(seasons)}")
    for season in seasons[:3]:
        season_id = season.get('data-season-id')
        season_num = season.get('data-season-number')
        season_name = season.get_text(strip=True)
        print(f"  - ID: {season_id}, Número: {season_num}, Nome: {season_name}")
    
    # Cards de episódios
    cards = soup.select(".card")
    print(f"\n🎬 Cards: {len(cards)}")
    
    for card_idx, card in enumerate(cards[:2]):
        card_title = card.select_one(".card-title")
        print(f"\n📦 Card {card_idx + 1}: {card_title.get_text(strip=True) if card_title else 'N/A'}")
        
        episodes = card.select("li[data-episode-id]")
        print(f"  Episódios: {len(episodes)}")
        
        for ep in episodes[:3]:
            ep_id = ep.get('data-episode-id')
            ep_season = ep.get('data-season-id')
            ep_link = ep.select_one("a")
            ep_text = ep_link.get_text(strip=True) if ep_link else "N/A"
            
            print(f"    - ID: {ep_id}, Season: {ep_season}, Texto: {ep_text}")
    
    return {
        "seasons": len(seasons),
        "cards": len(cards)
    }

def parse_playerthree_episode(playerthree_url, episode_id):
    """Parse de um episódio específico do PlayerThree"""
    print("\n" + "="*60)
    print(f"🎬 EPISÓDIO DO PLAYERTHREE")
    print("="*60)
    
    base_url = playerthree_url.split("/embed/")[0] if "/embed/" in playerthree_url else "https://playerthree.online"
    episode_url = f"{base_url}/episodio/{episode_id}"
    
    print(f"URL: {episode_url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Referer": playerthree_url,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    response = requests.get(episode_url, headers=headers, timeout=15)
    html = response.text
    
    save_html(html, f"maxseries_episode_{episode_id}.html")
    
    print(f"\n📄 Resposta ({len(html)} chars)")
    print(f"Início: {html[:300]}...")
    
    # Extrair sources
    sources = []
    
    # Padrão 1: data-source
    pattern1 = re.compile(r'data-source\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for match in pattern1.findall(html):
        if match.startswith("http"):
            sources.append(match)
    
    # Padrão 2: data-src
    pattern2 = re.compile(r'data-src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for match in pattern2.findall(html):
        if match.startswith("http"):
            sources.append(match)
    
    sources = list(set(sources))
    
    print(f"\n🎯 Sources encontradas: {len(sources)}")
    for src in sources:
        # Identificar tipo
        if "playerembedapi" in src.lower():
            print(f"  🟢 PlayerEmbedAPI: {src}")
        elif "myvidplay" in src.lower():
            print(f"  🟡 MyVidPlay: {src}")
        elif "dood" in src.lower():
            print(f"  🟠 Dood: {src}")
        elif "megaembed" in src.lower():
            print(f"  🔴 MegaEmbed: {src}")
        elif "streamtape" in src.lower():
            print(f"  🟣 StreamTape: {src}")
        elif "mixdrop" in src.lower():
            print(f"  🔵 Mixdrop: {src}")
        else:
            print(f"  ⚪ Outro: {src}")
    
    return sources

def main():
    print("="*60)
    print("🔍 PARSE PROFUNDO DO MAXSERIES.ONE")
    print("="*60)
    
    results = {}
    
    # 1. Home
    results['home'] = parse_home()
    
    # 2. Filmes
    movies = parse_movies_page()
    results['movies'] = movies
    
    # 3. Séries
    series = parse_series_page()
    results['series'] = series
    
    # 4. Detalhes de um filme
    if movies and movies[0]['link']:
        movie_detail = parse_movie_detail(movies[0]['link'])
        results['movie_detail'] = movie_detail
    
    # 5. Detalhes de uma série
    if series and series[0]['link']:
        series_detail = parse_series_detail(series[0]['link'])
        results['series_detail'] = series_detail
        
        # 6. PlayerThree
        if series_detail.get('playerthree_urls'):
            playerthree_url = series_detail['playerthree_urls'][0]
            playerthree_data = parse_playerthree(playerthree_url)
            results['playerthree'] = playerthree_data
            
            # 7. Episódio específico
            # Usar um ID de episódio conhecido
            episode_id = "258444"  # ID que sabemos que funciona
            sources = parse_playerthree_episode(playerthree_url, episode_id)
            results['episode_sources'] = sources
    
    # Salvar resultados
    with open("maxseries_parse_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("✅ PARSE COMPLETO!")
    print("="*60)
    print("\nArquivos gerados:")
    print("  - maxseries_home.html")
    print("  - maxseries_filmes.html")
    print("  - maxseries_series.html")
    print("  - maxseries_movie_detail.html")
    print("  - maxseries_series_detail.html")
    print("  - maxseries_playerthree.html")
    print("  - maxseries_episode_*.html")
    print("  - maxseries_parse_results.json")

if __name__ == "__main__":
    main()
