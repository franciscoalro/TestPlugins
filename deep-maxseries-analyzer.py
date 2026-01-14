#!/usr/bin/env python3
"""
MaxSeries Deep Analyzer - Análise Profunda do Site
Captura: estrutura, tokens, frames, players, seções, APIs
"""

import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import time
from datetime import datetime

# Headers modernos (Firefox 146 - Jan 2026)
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

class MaxSeriesAnalyzer:
    def __init__(self):
        self.base_url = "https://www.maxseries.one"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "pages_analyzed": [],
            "tokens_found": [],
            "frames_found": [],
            "players_found": [],
            "api_endpoints": [],
            "scripts": [],
            "forms": [],
            "cookies": [],
            "meta_tags": {},
            "css_selectors": {},
            "ajax_calls": []
        }
    
    def analyze_page(self, url, page_type="unknown"):
        """Analisa uma página completa"""
        print(f"\n{'='*80}")
        print(f"🔍 Analisando: {url}")
        print(f"📄 Tipo: {page_type}")
        print(f"{'='*80}")
        
        try:
            response = self.session.get(url, timeout=30)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            page_data = {
                "url": url,
                "type": page_type,
                "status_code": response.status_code,
                "size": len(html),
                "title": soup.title.string if soup.title else None,
                "sections": [],
                "iframes": [],
                "scripts": [],
                "forms": [],
                "data_attributes": [],
                "ajax_endpoints": [],
                "player_urls": [],
                "tokens": [],
                "meta_info": {}
            }
            
            # 1. Analisar Meta Tags
            print("\n📋 Meta Tags:")
            page_data["meta_info"] = self._extract_meta_tags(soup)
            
            # 2. Analisar Seções/Estrutura
            print("\n🏗️ Estrutura da Página:")
            page_data["sections"] = self._extract_sections(soup)
            
            # 3. Analisar Scripts
            print("\n📜 Scripts:")
            page_data["scripts"] = self._extract_scripts(soup, url)
            
            # 4. Analisar iFrames
            print("\n🖼️ iFrames:")
            page_data["iframes"] = self._extract_iframes(soup, url)
            
            # 5. Analisar Formulários
            print("\n📝 Formulários:")
            page_data["forms"] = self._extract_forms(soup)
            
            # 6. Analisar Data Attributes
            print("\n🏷️ Data Attributes:")
            page_data["data_attributes"] = self._extract_data_attributes(soup)
            
            # 7. Procurar Tokens/Keys
            print("\n🔑 Tokens/Keys:")
            page_data["tokens"] = self._extract_tokens(html)
            
            # 8. Procurar Endpoints AJAX
            print("\n🌐 AJAX Endpoints:")
            page_data["ajax_endpoints"] = self._extract_ajax_endpoints(html)
            
            # 9. Procurar URLs de Players
            print("\n🎬 Player URLs:")
            page_data["player_urls"] = self._extract_player_urls(html)
            
            # 10. Analisar Cookies
            print("\n🍪 Cookies:")
            self._extract_cookies(response)
            
            self.results["pages_analyzed"].append(page_data)
            
            # Salvar HTML para análise offline
            filename = f"maxseries_{page_type}_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n💾 HTML salvo: {filename}")
            
            return page_data
            
        except Exception as e:
            print(f"❌ Erro ao analisar {url}: {e}")
            return None
    
    def _extract_meta_tags(self, soup):
        """Extrai todas as meta tags"""
        meta_info = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                meta_info[name] = content
                print(f"  {name}: {content[:80]}...")
        
        return meta_info
    
    def _extract_sections(self, soup):
        """Extrai seções principais da página"""
        sections = []
        
        # Procurar por seções comuns
        section_selectors = [
            ('header', 'Header'),
            ('nav', 'Navigation'),
            ('main', 'Main Content'),
            ('article', 'Article'),
            ('.content', 'Content'),
            ('.movies', 'Movies Section'),
            ('.series', 'Series Section'),
            ('.episodes', 'Episodes Section'),
            ('.seasons', 'Seasons Section'),
            ('footer', 'Footer')
        ]
        
        for selector, name in section_selectors:
            elements = soup.select(selector)
            if elements:
                for i, elem in enumerate(elements):
                    section_data = {
                        "name": f"{name} {i+1}" if len(elements) > 1 else name,
                        "selector": selector,
                        "classes": elem.get('class', []),
                        "id": elem.get('id'),
                        "children_count": len(elem.find_all()),
                        "text_length": len(elem.get_text(strip=True))
                    }
                    sections.append(section_data)
                    print(f"  ✓ {section_data['name']}: {section_data['children_count']} elementos")
        
        return sections
    
    def _extract_scripts(self, soup, base_url):
        """Extrai todos os scripts"""
        scripts = []
        
        for script in soup.find_all('script'):
            script_data = {
                "src": script.get('src'),
                "type": script.get('type'),
                "inline": script.string is not None,
                "size": len(script.string) if script.string else 0
            }
            
            if script_data["src"]:
                full_url = urljoin(base_url, script_data["src"])
                script_data["full_url"] = full_url
                print(f"  📦 Externo: {full_url}")
            elif script.string:
                # Procurar por padrões interessantes no script inline
                content = script.string
                
                # Procurar variáveis importantes
                var_patterns = [
                    r'var\s+(\w+)\s*=',
                    r'const\s+(\w+)\s*=',
                    r'let\s+(\w+)\s*='
                ]
                
                variables = []
                for pattern in var_patterns:
                    variables.extend(re.findall(pattern, content))
                
                script_data["variables"] = list(set(variables))[:20]  # Primeiras 20
                
                # Procurar URLs
                urls = re.findall(r'https?://[^\s\'"<>]+', content)
                script_data["urls"] = list(set(urls))
                
                print(f"  📝 Inline: {len(content)} chars, {len(variables)} vars, {len(urls)} URLs")
            
            scripts.append(script_data)
            self.results["scripts"].append(script_data)
        
        return scripts
    
    def _extract_iframes(self, soup, base_url):
        """Extrai todos os iframes"""
        iframes = []
        
        for iframe in soup.find_all('iframe'):
            iframe_data = {
                "src": iframe.get('src'),
                "data-src": iframe.get('data-src'),
                "id": iframe.get('id'),
                "class": iframe.get('class'),
                "width": iframe.get('width'),
                "height": iframe.get('height'),
                "allowfullscreen": iframe.get('allowfullscreen') is not None
            }
            
            src = iframe_data["src"] or iframe_data["data-src"]
            if src:
                full_url = urljoin(base_url, src)
                iframe_data["full_url"] = full_url
                
                # Identificar tipo de player
                if "playerthree" in full_url.lower():
                    iframe_data["player_type"] = "PlayerThree"
                elif "youtube" in full_url.lower():
                    iframe_data["player_type"] = "YouTube"
                else:
                    iframe_data["player_type"] = "Unknown"
                
                print(f"  🖼️ {iframe_data['player_type']}: {full_url}")
                
                iframes.append(iframe_data)
                self.results["frames_found"].append(iframe_data)
        
        return iframes
    
    def _extract_forms(self, soup):
        """Extrai todos os formulários"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                "action": form.get('action'),
                "method": form.get('method', 'GET').upper(),
                "id": form.get('id'),
                "class": form.get('class'),
                "inputs": []
            }
            
            # Extrair inputs
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    "type": input_elem.get('type', 'text'),
                    "name": input_elem.get('name'),
                    "id": input_elem.get('id'),
                    "value": input_elem.get('value'),
                    "required": input_elem.get('required') is not None
                }
                form_data["inputs"].append(input_data)
            
            forms.append(form_data)
            print(f"  📝 Form: {form_data['method']} {form_data['action']} ({len(form_data['inputs'])} inputs)")
        
        return forms
    
    def _extract_data_attributes(self, soup):
        """Extrai elementos com data-* attributes"""
        data_attrs = []
        
        # Procurar elementos com data-*
        elements_with_data = soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs))
        
        for elem in elements_with_data[:50]:  # Limitar a 50
            elem_data = {
                "tag": elem.name,
                "id": elem.get('id'),
                "class": elem.get('class'),
                "data_attributes": {}
            }
            
            for attr, value in elem.attrs.items():
                if attr.startswith('data-'):
                    elem_data["data_attributes"][attr] = value
            
            if elem_data["data_attributes"]:
                data_attrs.append(elem_data)
                print(f"  🏷️ {elem.name}: {list(elem_data['data_attributes'].keys())}")
        
        return data_attrs
    
    def _extract_tokens(self, html):
        """Procura por tokens, keys, secrets"""
        tokens = []
        
        patterns = [
            (r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']', "token"),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', "api_key"),
            (r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', "secret"),
            (r'auth["\']?\s*[:=]\s*["\']([^"\']+)["\']', "auth"),
            (r'bearer\s+([A-Za-z0-9\-_\.]+)', "bearer"),
            (r'jwt["\']?\s*[:=]\s*["\']([^"\']+)["\']', "jwt"),
            (r'csrf["\']?\s*[:=]\s*["\']([^"\']+)["\']', "csrf"),
            (r'nonce["\']?\s*[:=]\s*["\']([^"\']+)["\']', "nonce")
        ]
        
        for pattern, token_type in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if len(match) > 10:  # Filtrar tokens muito curtos
                    token_data = {
                        "type": token_type,
                        "value": match[:50] + "..." if len(match) > 50 else match,
                        "length": len(match)
                    }
                    tokens.append(token_data)
                    print(f"  🔑 {token_type}: {token_data['value']}")
                    self.results["tokens_found"].append(token_data)
        
        return tokens
    
    def _extract_ajax_endpoints(self, html):
        """Procura por endpoints AJAX"""
        endpoints = []
        
        patterns = [
            r'ajax["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'url["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'api["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match.startswith(('http', '/', './')):
                    endpoint_data = {
                        "url": match,
                        "type": "ajax"
                    }
                    endpoints.append(endpoint_data)
                    print(f"  🌐 {match}")
                    self.results["api_endpoints"].append(endpoint_data)
        
        return list({e["url"]: e for e in endpoints}.values())  # Remove duplicatas
    
    def _extract_player_urls(self, html):
        """Procura por URLs de players"""
        players = []
        
        player_domains = [
            'playerembedapi',
            'myvidplay',
            'dood',
            'streamtape',
            'mixdrop',
            'filemoon',
            'uqload',
            'vidcloud',
            'upstream',
            'megaembed',
            'playerthree'
        ]
        
        # Procurar URLs de players
        for domain in player_domains:
            pattern = rf'https?://[^"\'\s]*{domain}[^"\'\s]*'
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                player_data = {
                    "domain": domain,
                    "url": match,
                    "type": "player"
                }
                players.append(player_data)
                print(f"  🎬 {domain}: {match[:80]}...")
                self.results["players_found"].append(player_data)
        
        return players
    
    def _extract_cookies(self, response):
        """Extrai cookies da resposta"""
        for cookie in response.cookies:
            cookie_data = {
                "name": cookie.name,
                "value": cookie.value[:50] + "..." if len(cookie.value) > 50 else cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
                "httponly": cookie.has_nonstandard_attr('HttpOnly')
            }
            self.results["cookies"].append(cookie_data)
            print(f"  🍪 {cookie.name}: {cookie_data['value']}")
    
    def analyze_playerthree_episode(self, episode_id):
        """Analisa um episódio específico do PlayerThree"""
        print(f"\n{'='*80}")
        print(f"🎬 Analisando Episódio PlayerThree: {episode_id}")
        print(f"{'='*80}")
        
        url = f"https://playerthree.online/episodio/{episode_id}"
        
        try:
            response = self.session.get(
                url,
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
                "episode_id": episode_id,
                "url": url,
                "status_code": response.status_code,
                "size": len(html),
                "buttons": [],
                "sources": [],
                "data_attributes": []
            }
            
            # Procurar botões de player
            print("\n🔘 Botões de Player:")
            buttons = soup.find_all(['button', 'a'], attrs={'data-source': True})
            for btn in buttons:
                btn_data = {
                    "tag": btn.name,
                    "text": btn.get_text(strip=True),
                    "data-source": btn.get('data-source'),
                    "data-src": btn.get('data-src'),
                    "class": btn.get('class'),
                    "id": btn.get('id')
                }
                episode_data["buttons"].append(btn_data)
                print(f"  🔘 {btn_data['text']}: {btn_data['data-source']}")
            
            # Extrair sources via regex
            print("\n🎯 Sources (Regex):")
            source_patterns = [
                r'data-source\s*=\s*["\']([^"\']+)["\']',
                r'data-src\s*=\s*["\']([^"\']+)["\']',
                r'href\s*=\s*["\'](https?://(?:playerembedapi|myvidplay|dood|megaembed)[^"\']+)["\']'
            ]
            
            for pattern in source_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http') and match not in episode_data["sources"]:
                        episode_data["sources"].append(match)
                        print(f"  🎯 {match}")
            
            # Salvar HTML
            filename = f"playerthree_episode_{episode_id}_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n💾 HTML salvo: {filename}")
            
            return episode_data
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def save_results(self):
        """Salva todos os resultados em JSON"""
        filename = f"maxseries_deep_analysis_{int(time.time())}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"💾 Resultados salvos: {filename}")
        print(f"{'='*80}")
        print(f"📊 Estatísticas:")
        print(f"  - Páginas analisadas: {len(self.results['pages_analyzed'])}")
        print(f"  - Tokens encontrados: {len(self.results['tokens_found'])}")
        print(f"  - Frames encontrados: {len(self.results['frames_found'])}")
        print(f"  - Players encontrados: {len(self.results['players_found'])}")
        print(f"  - Scripts encontrados: {len(self.results['scripts'])}")
        print(f"  - API Endpoints: {len(self.results['api_endpoints'])}")
        print(f"  - Cookies: {len(self.results['cookies'])}")
        
        return filename


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         MaxSeries Deep Analyzer - Análise Profunda           ║
║                    Janeiro 2026                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = MaxSeriesAnalyzer()
    
    # 1. Analisar Home
    print("\n🏠 ANALISANDO HOME")
    analyzer.analyze_page("https://www.maxseries.one", "home")
    time.sleep(2)
    
    # 2. Analisar Página de Filmes
    print("\n🎬 ANALISANDO FILMES")
    analyzer.analyze_page("https://www.maxseries.one/filmes", "movies")
    time.sleep(2)
    
    # 3. Analisar Página de Séries
    print("\n📺 ANALISANDO SÉRIES")
    analyzer.analyze_page("https://www.maxseries.one/series", "series")
    time.sleep(2)
    
    # 4. Analisar uma série específica (exemplo)
    print("\n🎯 ANALISANDO SÉRIE ESPECÍFICA")
    # Você pode adicionar uma URL de série específica aqui
    # analyzer.analyze_page("https://www.maxseries.one/series/exemplo", "series_detail")
    
    # 5. Analisar episódio do PlayerThree
    print("\n🎬 ANALISANDO EPISÓDIO PLAYERTHREE")
    # IDs de episódios conhecidos
    episode_ids = ["258444", "219179", "212780"]
    for ep_id in episode_ids:
        analyzer.analyze_playerthree_episode(ep_id)
        time.sleep(2)
    
    # 6. Salvar resultados
    analyzer.save_results()
    
    print("\n✅ Análise completa!")


if __name__ == "__main__":
    main()
