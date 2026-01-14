#!/usr/bin/env python3
"""
MaxSeries Advanced Deep Analyzer - Análise Avançada Completa
Captura: séries específicas, estrutura de episódios, padrões de URL, cookies, headers
"""

import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, unquote
import time
from datetime import datetime
import base64

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

class AdvancedAnalyzer:
    def __init__(self):
        self.base_url = "https://www.maxseries.one"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "series_analyzed": [],
            "movies_analyzed": [],
            "episodes_structure": [],
            "player_patterns": {},
            "url_patterns": {},
            "api_calls": [],
            "network_requests": []
        }
    
    def find_series_urls(self):
        """Busca URLs de séries na página principal"""
        print("\n🔍 Buscando URLs de séries...")
        
        try:
            response = self.session.get(f"{self.base_url}/series", timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            series_urls = []
            
            # Procurar links de séries
            for article in soup.find_all('article', class_='item'):
                link = article.find('a', href=True)
                if link and '/series/' in link['href']:
                    series_urls.append(link['href'])
            
            print(f"✅ Encontradas {len(series_urls)} séries")
            return series_urls[:5]  # Primeiras 5 para análise
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []
    
    def analyze_series_page(self, url):
        """Analisa página de uma série específica"""
        print(f"\n{'='*80}")
        print(f"📺 Analisando Série: {url}")
        print(f"{'='*80}")
        
        try:
            response = self.session.get(url, timeout=30)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            series_data = {
                "url": url,
                "title": None,
                "year": None,
                "genres": [],
                "plot": None,
                "poster": None,
                "seasons": [],
                "iframe_url": None,
                "playerthree_url": None,
                "episodes_found": 0,
                "raw_html_size": len(html)
            }
            
            # 1. Título
            title_elem = soup.find('h1')
            if title_elem:
                series_data["title"] = title_elem.get_text(strip=True)
                print(f"📌 Título: {series_data['title']}")
            
            # 2. Ano
            year_match = re.search(r'\b(19|20)\d{2}\b', html)
            if year_match:
                series_data["year"] = year_match.group()
                print(f"📅 Ano: {series_data['year']}")
            
            # 3. Gêneros
            genre_links = soup.select('.sgeneros a, .genres a')
            series_data["genres"] = [g.get_text(strip=True) for g in genre_links]
            print(f"🎭 Gêneros: {', '.join(series_data['genres'])}")
            
            # 4. Sinopse
            plot_elem = soup.find('div', class_='wp-content')
            if plot_elem:
                series_data["plot"] = plot_elem.get_text(strip=True)[:200]
                print(f"📝 Sinopse: {series_data['plot'][:80]}...")
            
            # 5. Poster
            poster_elem = soup.select_one('.poster img, meta[property="og:image"]')
            if poster_elem:
                series_data["poster"] = poster_elem.get('src') or poster_elem.get('content')
                print(f"🖼️ Poster: {series_data['poster'][:80]}...")
            
            # 6. Iframe do PlayerThree
            print("\n🎬 Procurando iframe do PlayerThree...")
            iframe = soup.find('iframe', src=re.compile(r'playerthree', re.I))
            if iframe:
                series_data["iframe_url"] = iframe.get('src')
                series_data["playerthree_url"] = series_data["iframe_url"]
                print(f"✅ PlayerThree: {series_data['playerthree_url']}")
                
                # Analisar estrutura de episódios do PlayerThree
                self.analyze_playerthree_structure(series_data["playerthree_url"], series_data)
            else:
                # Procurar no HTML bruto
                iframe_match = re.search(r'https?://playerthree\.online/embed/[^\s"\'<>]+', html)
                if iframe_match:
                    series_data["playerthree_url"] = iframe_match.group()
                    print(f"✅ PlayerThree (regex): {series_data['playerthree_url']}")
                    self.analyze_playerthree_structure(series_data["playerthree_url"], series_data)
            
            # 7. Temporadas (fallback - página MaxSeries)
            print("\n📺 Analisando temporadas...")
            seasons = soup.select('.se-c, .seasons .se-a')
            for i, season in enumerate(seasons):
                season_data = {
                    "number": i + 1,
                    "episodes": []
                }
                
                episodes = season.select('.episodios li, ul.episodios li')
                for j, ep in enumerate(episodes):
                    ep_link = ep.find('a', href=True)
                    if ep_link:
                        episode_data = {
                            "number": j + 1,
                            "title": ep_link.get_text(strip=True),
                            "url": ep_link['href']
                        }
                        season_data["episodes"].append(episode_data)
                
                if season_data["episodes"]:
                    series_data["seasons"].append(season_data)
                    print(f"  ✓ Temporada {i+1}: {len(season_data['episodes'])} episódios")
            
            series_data["episodes_found"] = sum(len(s["episodes"]) for s in series_data["seasons"])
            
            # Salvar HTML
            filename = f"series_{series_data['title'][:30].replace(' ', '_')}_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n💾 HTML salvo: {filename}")
            
            self.results["series_analyzed"].append(series_data)
            return series_data
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def analyze_playerthree_structure(self, playerthree_url, series_data):
        """Analisa estrutura completa do PlayerThree"""
        print(f"\n🎬 Analisando estrutura PlayerThree...")
        
        try:
            response = self.session.get(
                playerthree_url,
                headers={**HEADERS, "Referer": series_data["url"]},
                timeout=30
            )
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            structure = {
                "url": playerthree_url,
                "seasons": [],
                "total_episodes": 0,
                "cards_found": 0
            }
            
            # Procurar temporadas
            season_tabs = soup.select('.header-navigation li[data-season-id]')
            print(f"📊 Temporadas encontradas: {len(season_tabs)}")
            
            for season_tab in season_tabs:
                season_id = season_tab.get('data-season-id')
                season_num = season_tab.get('data-season-number')
                
                season_data = {
                    "id": season_id,
                    "number": int(season_num) if season_num else None,
                    "episodes": []
                }
                
                print(f"\n  📺 Temporada {season_num} (ID: {season_id})")
                
                # Procurar cards de episódios
                cards = soup.select('.card')
                structure["cards_found"] = len(cards)
                
                for card in cards:
                    card_title = card.select_one('.card-title')
                    if card_title:
                        print(f"    📦 Card: {card_title.get_text(strip=True)}")
                    
                    # Episódios dentro do card
                    episodes = card.select('li[data-episode-id]')
                    
                    for ep in episodes:
                        ep_id = ep.get('data-episode-id')
                        ep_season_id = ep.get('data-season-id')
                        
                        if ep_season_id == season_id:
                            link = ep.find('a')
                            ep_title = link.get_text(strip=True) if link else "Sem título"
                            
                            # Extrair número do episódio
                            ep_num_match = re.match(r'^(\d+)', ep_title)
                            ep_num = int(ep_num_match.group(1)) if ep_num_match else None
                            
                            episode_data = {
                                "id": ep_id,
                                "number": ep_num,
                                "title": ep_title,
                                "season_id": ep_season_id,
                                "ajax_url": f"https://playerthree.online/episodio/{ep_id}"
                            }
                            
                            season_data["episodes"].append(episode_data)
                            print(f"      ✓ Ep {ep_num}: {ep_title} (ID: {ep_id})")
                
                if season_data["episodes"]:
                    structure["seasons"].append(season_data)
                    structure["total_episodes"] += len(season_data["episodes"])
            
            print(f"\n📊 Total: {structure['total_episodes']} episódios em {len(structure['seasons'])} temporadas")
            
            series_data["playerthree_structure"] = structure
            self.results["episodes_structure"].append(structure)
            
            # Salvar HTML do PlayerThree
            filename = f"playerthree_structure_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 PlayerThree HTML salvo: {filename}")
            
            # Analisar alguns episódios
            if structure["seasons"]:
                first_season = structure["seasons"][0]
                if first_season["episodes"]:
                    # Analisar primeiro episódio
                    first_ep = first_season["episodes"][0]
                    self.analyze_episode_sources(first_ep["id"], first_ep["ajax_url"])
                    
                    # Analisar último episódio
                    if len(first_season["episodes"]) > 1:
                        last_ep = first_season["episodes"][-1]
                        self.analyze_episode_sources(last_ep["id"], last_ep["ajax_url"])
            
        except Exception as e:
            print(f"❌ Erro ao analisar PlayerThree: {e}")
    
    def analyze_episode_sources(self, episode_id, ajax_url):
        """Analisa sources de um episódio específico"""
        print(f"\n🎯 Analisando episódio {episode_id}...")
        
        try:
            response = self.session.get(
                ajax_url,
                headers={
                    **HEADERS,
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://playerthree.online"
                },
                timeout=30
            )
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            episode_data = {
                "id": episode_id,
                "url": ajax_url,
                "sources": [],
                "buttons": [],
                "player_types": {}
            }
            
            # Extrair botões
            buttons = soup.find_all(['button', 'a'], attrs={'data-source': True})
            
            for btn in buttons:
                source_url = btn.get('data-source')
                btn_text = btn.get_text(strip=True)
                
                if source_url:
                    # Identificar tipo de player
                    player_type = "unknown"
                    if "playerembedapi" in source_url.lower():
                        player_type = "PlayerEmbedAPI"
                    elif "myvidplay" in source_url.lower():
                        player_type = "MyVidPlay"
                    elif "dood" in source_url.lower():
                        player_type = "DoodStream"
                    elif "megaembed" in source_url.lower():
                        player_type = "MegaEmbed"
                    elif "streamtape" in source_url.lower():
                        player_type = "StreamTape"
                    elif "mixdrop" in source_url.lower():
                        player_type = "Mixdrop"
                    
                    button_data = {
                        "text": btn_text,
                        "source": source_url,
                        "type": player_type
                    }
                    
                    episode_data["buttons"].append(button_data)
                    episode_data["sources"].append(source_url)
                    
                    # Contar tipos de player
                    episode_data["player_types"][player_type] = episode_data["player_types"].get(player_type, 0) + 1
                    
                    print(f"  🎬 {player_type}: {source_url[:80]}...")
            
            print(f"  📊 Total: {len(episode_data['sources'])} sources")
            print(f"  📊 Tipos: {episode_data['player_types']}")
            
            # Atualizar padrões globais
            for player_type, count in episode_data["player_types"].items():
                if player_type not in self.results["player_patterns"]:
                    self.results["player_patterns"][player_type] = {
                        "count": 0,
                        "episodes": []
                    }
                self.results["player_patterns"][player_type]["count"] += count
                self.results["player_patterns"][player_type]["episodes"].append(episode_id)
            
            # Salvar HTML do episódio
            filename = f"episode_{episode_id}_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            
            return episode_data
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def analyze_ajax_api(self):
        """Analisa endpoints AJAX do WordPress"""
        print(f"\n{'='*80}")
        print("🌐 Analisando APIs AJAX do WordPress")
        print(f"{'='*80}")
        
        ajax_endpoints = [
            {
                "url": f"{self.base_url}/wp-admin/admin-ajax.php",
                "action": "doo_player_ajax",
                "method": "POST"
            },
            {
                "url": f"{self.base_url}/wp-json/dooplayer/v2/",
                "method": "GET"
            },
            {
                "url": f"{self.base_url}/wp-json/dooplay/search/",
                "method": "GET"
            }
        ]
        
        for endpoint in ajax_endpoints:
            print(f"\n🔍 Testando: {endpoint['url']}")
            try:
                if endpoint["method"] == "GET":
                    response = self.session.get(endpoint["url"], timeout=10)
                else:
                    response = self.session.post(endpoint["url"], timeout=10)
                
                print(f"  Status: {response.status_code}")
                print(f"  Content-Type: {response.headers.get('Content-Type')}")
                
                if response.status_code == 200:
                    content = response.text[:500]
                    print(f"  Resposta: {content}...")
                
                self.results["api_calls"].append({
                    "endpoint": endpoint["url"],
                    "method": endpoint["method"],
                    "status": response.status_code,
                    "content_type": response.headers.get('Content-Type')
                })
                
            except Exception as e:
                print(f"  ❌ Erro: {e}")
    
    def save_results(self):
        """Salva resultados completos"""
        filename = f"maxseries_advanced_analysis_{int(time.time())}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"💾 RESULTADOS SALVOS: {filename}")
        print(f"{'='*80}")
        print(f"📊 Estatísticas Finais:")
        print(f"  - Séries analisadas: {len(self.results['series_analyzed'])}")
        print(f"  - Estruturas de episódios: {len(self.results['episodes_structure'])}")
        print(f"  - Padrões de players:")
        for player, data in self.results["player_patterns"].items():
            print(f"    • {player}: {data['count']} ocorrências")
        
        return filename


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      MaxSeries Advanced Analyzer - Análise Avançada          ║
║                    Janeiro 2026                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = AdvancedAnalyzer()
    
    # 1. Buscar URLs de séries
    series_urls = analyzer.find_series_urls()
    
    # 2. Analisar cada série
    for url in series_urls:
        analyzer.analyze_series_page(url)
        time.sleep(3)  # Delay entre requests
    
    # 3. Analisar APIs AJAX
    analyzer.analyze_ajax_api()
    
    # 4. Salvar resultados
    analyzer.save_results()
    
    print("\n✅ Análise avançada completa!")


if __name__ == "__main__":
    main()
