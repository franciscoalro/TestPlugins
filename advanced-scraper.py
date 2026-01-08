#!/usr/bin/env python3
"""
Scraper Avançado MaxSeries - Simula navegador real
Analisa estrutura completa e gera código Kotlin otimizado
"""

import json
import time
import re
import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedMaxSeriesScraper:
    def __init__(self):
        """Inicializar scraper avançado"""
        self.session = requests.Session()
        self.setup_session()
        self.base_url = "https://www.maxseries.one"
        self.results = {}
        
    def setup_session(self):
        """Configurar sessão para simular navegador real"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
        
    def analyze_homepage(self):
        """Analisar página inicial para entender estrutura"""
        logger.info("🏠 Analisando página inicial...")
        
        try:
            response = self.session.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': self.base_url,
                'title': soup.title.text if soup.title else 'N/A',
                'series_links': [],
                'movie_links': [],
                'navigation_structure': {},
                'content_structure': {}
            }
            
            # Encontrar links de séries e filmes
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if '/series/' in href:
                    analysis['series_links'].append({
                        'title': text,
                        'url': urljoin(self.base_url, href)
                    })
                elif '/filme/' in href or '/movie/' in href:
                    analysis['movie_links'].append({
                        'title': text,
                        'url': urljoin(self.base_url, href)
                    })
            
            # Analisar estrutura de navegação
            nav_elements = soup.find_all(['nav', '.menu', '.navigation'])
            for nav in nav_elements:
                nav_links = nav.find_all('a') if nav else []
                analysis['navigation_structure'][nav.get('class', 'unknown')] = [
                    {'text': a.get_text(strip=True), 'href': a.get('href')} 
                    for a in nav_links
                ]
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar homepage: {e}")
            return None
    
    def deep_analyze_series(self, series_url):
        """Análise profunda de uma página de série"""
        logger.info(f"📺 Análise profunda da série: {series_url}")
        
        try:
            response = self.session.get(series_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': series_url,
                'title': self.extract_title(soup),
                'description': self.extract_description(soup),
                'poster': self.extract_poster(soup),
                'seasons_structure': self.analyze_seasons_structure(soup),
                'episodes_structure': self.analyze_episodes_structure(soup),
                'player_structure': self.analyze_player_structure(soup),
                'javascript_analysis': self.analyze_javascript(soup),
                'ajax_endpoints': self.discover_ajax_endpoints(soup),
                'iframe_analysis': self.analyze_iframes(soup),
                'raw_html_sections': self.capture_raw_html(soup)
            }
            
            # Tentar acessar alguns episódios para análise mais profunda
            if analysis['episodes_structure']['episode_links']:
                sample_episodes = analysis['episodes_structure']['episode_links'][:3]
                analysis['episode_deep_analysis'] = []
                
                for ep in sample_episodes:
                    ep_analysis = self.analyze_episode_page(ep['url'])
                    if ep_analysis:
                        analysis['episode_deep_analysis'].append(ep_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise profunda: {e}")
            return None
    
    def extract_title(self, soup):
        """Extrair título da página"""
        selectors = [
            '.data h1',
            'h1',
            '.entry-title',
            '.post-title',
            '.movie-title',
            '.series-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return soup.title.text if soup.title else 'Título não encontrado'
    
    def extract_description(self, soup):
        """Extrair descrição"""
        selectors = [
            '.sinopse',
            '.entry-content',
            '.wp-content',
            '.description',
            '.plot',
            '.overview'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)[:500]
        
        return 'Descrição não encontrada'
    
    def extract_poster(self, soup):
        """Extrair URL do poster"""
        selectors = [
            '.poster img',
            '.wp-post-image',
            '.movie-poster img',
            '.series-poster img'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get('src') or element.get('data-src')
        
        return None
    
    def analyze_seasons_structure(self, soup):
        """Analisar estrutura de temporadas"""
        logger.info("🎬 Analisando estrutura de temporadas...")
        
        structure = {
            'dooplay_seasons': [],
            'season_count': 0,
            'season_selectors_found': []
        }
        
        # Método 1: DooPlay padrão
        seasons = soup.select('div.se-c')
        for i, season in enumerate(seasons):
            season_info = {
                'index': i,
                'id': season.get('id', ''),
                'class': season.get('class', []),
                'episodes_count': len(season.select('ul.episodios li')),
                'season_number': self.extract_season_number(season)
            }
            structure['dooplay_seasons'].append(season_info)
        
        structure['season_count'] = len(seasons)
        
        # Procurar outros padrões de temporadas
        alternative_selectors = [
            '.seasons .season',
            '.season-list .season',
            '[data-season]',
            '.temporada'
        ]
        
        for selector in alternative_selectors:
            elements = soup.select(selector)
            if elements:
                structure['season_selectors_found'].append({
                    'selector': selector,
                    'count': len(elements)
                })
        
        return structure
    
    def analyze_episodes_structure(self, soup):
        """Analisar estrutura de episódios detalhadamente"""
        logger.info("📺 Analisando estrutura de episódios...")
        
        structure = {
            'episode_links': [],
            'episode_patterns': [],
            'numbering_patterns': [],
            'selectors_analysis': {}
        }
        
        # Múltiplos seletores para episódios
        episode_selectors = [
            'ul.episodios li a',
            '.episodios a',
            '.episode-list a',
            '.episodes a',
            'li[data-episode] a',
            'a[href*="episodio"]',
            'a[href*="episode"]'
        ]
        
        for selector in episode_selectors:
            elements = soup.select(selector)
            if elements:
                structure['selectors_analysis'][selector] = {
                    'count': len(elements),
                    'sample_links': []
                }
                
                for i, element in enumerate(elements[:5]):  # Primeiros 5 para análise
                    link_info = {
                        'text': element.get_text(strip=True),
                        'href': element.get('href'),
                        'parent_class': element.parent.get('class', []) if element.parent else [],
                        'data_attributes': {k: v for k, v in element.attrs.items() if k.startswith('data-')}
                    }
                    structure['selectors_analysis'][selector]['sample_links'].append(link_info)
                    
                    if selector == 'ul.episodios li a':  # Priorizar DooPlay
                        structure['episode_links'].append({
                            'index': i,
                            'title': link_info['text'],
                            'url': urljoin(self.base_url, link_info['href']) if link_info['href'] else None,
                            'episode_number': self.extract_episode_number(element),
                            'season_number': self.extract_season_from_episode(element)
                        })
        
        # Analisar padrões de numeração
        structure['numbering_patterns'] = self.analyze_numbering_patterns(soup)
        
        return structure
    
    def extract_season_number(self, season_element):
        """Extrair número da temporada"""
        season_id = season_element.get('id', '')
        if 'season-' in season_id:
            try:
                return int(season_id.replace('season-', ''))
            except:
                pass
        
        season_text = season_element.get_text()
        season_match = re.search(r'temporada\s*(\d+)|season\s*(\d+)', season_text, re.IGNORECASE)
        if season_match:
            return int(season_match.group(1) or season_match.group(2))
        
        return 1
    
    def extract_episode_number(self, episode_element):
        """Extrair número do episódio"""
        # Procurar em .numerando
        numerando = episode_element.find_previous('.numerando') or episode_element.find_next('.numerando')
        if numerando:
            numerando_text = numerando.get_text()
            # Formato: "1 - 1" ou "S1E1"
            match = re.search(r'(\d+)\s*-\s*(\d+)|E(\d+)', numerando_text)
            if match:
                return int(match.group(2) or match.group(3))
        
        # Procurar no texto do link
        text = episode_element.get_text()
        ep_match = re.search(r'episódio\s*(\d+)|episode\s*(\d+)|ep\s*(\d+)', text, re.IGNORECASE)
        if ep_match:
            return int(ep_match.group(1) or ep_match.group(2) or ep_match.group(3))
        
        # Procurar na URL
        href = episode_element.get('href', '')
        url_match = re.search(r'episodio-(\d+)|episode-(\d+)', href)
        if url_match:
            return int(url_match.group(1) or url_match.group(2))
        
        return None
    
    def extract_season_from_episode(self, episode_element):
        """Extrair temporada do contexto do episódio"""
        # Procurar elemento pai de temporada
        season_parent = episode_element.find_parent('.se-c')
        if season_parent:
            return self.extract_season_number(season_parent)
        
        return 1
    
    def analyze_numbering_patterns(self, soup):
        """Analisar padrões de numeração encontrados"""
        patterns = []
        
        # Procurar elementos .numerando
        numerando_elements = soup.select('.numerando')
        for elem in numerando_elements[:10]:  # Primeiros 10
            text = elem.get_text(strip=True)
            patterns.append({
                'type': 'numerando',
                'text': text,
                'pattern': self.identify_numbering_pattern(text)
            })
        
        return patterns
    
    def identify_numbering_pattern(self, text):
        """Identificar padrão de numeração"""
        if re.match(r'\d+\s*-\s*\d+', text):
            return 'season-episode'
        elif re.match(r'S\d+E\d+', text, re.IGNORECASE):
            return 'sXeY'
        elif re.match(r'\d+', text):
            return 'simple_number'
        else:
            return 'unknown'
    
    def analyze_player_structure(self, soup):
        """Analisar estrutura de players"""
        logger.info("🎬 Analisando estrutura de players...")
        
        structure = {
            'iframes': [],
            'player_buttons': [],
            'ajax_options': [],
            'data_source_buttons': []
        }
        
        # Analisar iframes
        iframes = soup.select('iframe')
        for iframe in iframes:
            structure['iframes'].append({
                'src': iframe.get('src'),
                'class': iframe.get('class', []),
                'id': iframe.get('id'),
                'data_attributes': {k: v for k, v in iframe.attrs.items() if k.startswith('data-')}
            })
        
        # Botões com data-source
        data_source_buttons = soup.select('button[data-source], .btn[data-source]')
        for button in data_source_buttons:
            structure['data_source_buttons'].append({
                'text': button.get_text(strip=True),
                'data_source': button.get('data-source'),
                'data_type': button.get('data-type'),
                'class': button.get('class', [])
            })
        
        # Opções AJAX DooPlay
        ajax_options = soup.select('#playeroptionsul li, .playeroptionsul li')
        for option in ajax_options:
            structure['ajax_options'].append({
                'text': option.get_text(strip=True),
                'data_post': option.get('data-post'),
                'data_nume': option.get('data-nume'),
                'data_type': option.get('data-type')
            })
        
        return structure
    
    def analyze_javascript(self, soup):
        """Analisar JavaScript relevante"""
        logger.info("📜 Analisando JavaScript...")
        
        analysis = {
            'jwplayer_configs': [],
            'gleam_configs': [],
            'ajax_patterns': [],
            'video_url_patterns': [],
            'player_initialization': []
        }
        
        scripts = soup.find_all('script')
        for script in scripts:
            content = script.string or ''
            
            # Configurações jwplayer
            if 'jwplayer' in content.lower():
                analysis['jwplayer_configs'].append(content[:500])
            
            # Configurações gleam
            if 'gleam' in content.lower():
                analysis['gleam_configs'].append(content[:500])
            
            # Padrões AJAX
            if 'ajax' in content.lower() or 'XMLHttpRequest' in content:
                analysis['ajax_patterns'].append(content[:300])
            
            # URLs de vídeo
            video_patterns = [
                r'https?://[^"\s]+\.(?:m3u8|mp4|mkv|avi)',
                r'"url"\s*:\s*"([^"]+)"',
                r'"file"\s*:\s*"([^"]+)"',
                r'"source"\s*:\s*"([^"]+)"'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, content)
                analysis['video_url_patterns'].extend(matches)
        
        return analysis
    
    def discover_ajax_endpoints(self, soup):
        """Descobrir endpoints AJAX"""
        logger.info("🔍 Descobrindo endpoints AJAX...")
        
        endpoints = {
            'dooplay_ajax': None,
            'custom_endpoints': [],
            'form_actions': []
        }
        
        # Endpoint DooPlay padrão
        if soup.select('#playeroptionsul li'):
            endpoints['dooplay_ajax'] = '/wp-admin/admin-ajax.php'
        
        # Procurar outros endpoints em scripts
        scripts = soup.find_all('script')
        for script in scripts:
            content = script.string or ''
            
            # Procurar URLs de API
            api_patterns = [
                r'["\']([^"\']*(?:api|ajax|player|stream)[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                endpoints['custom_endpoints'].extend(matches)
        
        # Ações de formulários
        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action')
            if action:
                endpoints['form_actions'].append(action)
        
        return endpoints
    
    def analyze_iframes(self, soup):
        """Análise detalhada de iframes"""
        logger.info("🖼️ Analisando iframes...")
        
        iframe_analysis = []
        iframes = soup.select('iframe')
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src')
            if src:
                try:
                    # Tentar acessar o iframe
                    iframe_response = self.session.get(urljoin(self.base_url, src))
                    iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                    
                    analysis = {
                        'index': i,
                        'src': src,
                        'class': iframe.get('class', []),
                        'content_analysis': {
                            'title': iframe_soup.title.text if iframe_soup.title else None,
                            'player_buttons': len(iframe_soup.select('button[data-source]')),
                            'scripts_count': len(iframe_soup.select('script')),
                            'forms_count': len(iframe_soup.select('form'))
                        }
                    }
                    
                    iframe_analysis.append(analysis)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao analisar iframe {i}: {e}")
        
        return iframe_analysis
    
    def capture_raw_html(self, soup):
        """Capturar seções HTML relevantes"""
        sections = {}
        
        selectors = {
            'seasons_section': '.seasons, .se-list, div.se-c',
            'episodes_section': '.episodios, ul.episodios',
            'players_section': '#playeroptionsul, .player-options, #players',
            'main_content': '.wp-content, .entry-content, .content'
        }
        
        for name, selector in selectors.items():
            element = soup.select_one(selector)
            if element:
                sections[name] = str(element)[:1000]  # Primeiros 1000 chars
            else:
                sections[name] = 'não encontrado'
        
        return sections
    
    def analyze_episode_page(self, episode_url):
        """Analisar página individual de episódio"""
        logger.info(f"📺 Analisando episódio: {episode_url}")
        
        try:
            response = self.session.get(episode_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': episode_url,
                'title': self.extract_title(soup),
                'players': self.analyze_player_structure(soup),
                'iframes': self.analyze_iframes(soup),
                'javascript': self.analyze_javascript(soup)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar episódio: {e}")
            return None
    
    def generate_kotlin_scraper(self, analysis_data):
        """Gerar código Kotlin baseado na análise"""
        logger.info("🔧 Gerando código Kotlin otimizado...")
        
        # Analisar dados e gerar código
        kotlin_code = self.build_kotlin_provider(analysis_data)
        
        return kotlin_code
    
    def build_kotlin_provider(self, data):
        """Construir código do provider Kotlin"""
        
        # Extrair informações da análise
        series_data = data.get('series_analysis', {})
        episodes_structure = series_data.get('episodes_structure', {})
        players_structure = series_data.get('player_structure', {})
        
        # Gerar seletores baseados na análise
        episode_selectors = []
        for selector, info in episodes_structure.get('selectors_analysis', {}).items():
            if info['count'] > 0:
                episode_selectors.append(selector)
        
        player_selectors = []
        if players_structure.get('data_source_buttons'):
            player_selectors.append('button[data-source], .btn[data-source]')
        if players_structure.get('ajax_options'):
            player_selectors.append('#playeroptionsul li, .playeroptionsul li')
        
        kotlin_template = f'''
// Código gerado automaticamente baseado na análise do site
class MaxSeriesProvider : MainAPI() {{
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    override suspend fun load(url: String): LoadResponse? {{
        val doc = app.get(url).document
        val title = doc.selectFirst(".data h1")?.text() 
            ?: doc.selectFirst("h1")?.text() ?: "Unknown"
        val desc = doc.selectFirst(".sinopse")?.text() 
            ?: doc.selectFirst(".entry-content")?.text()
        val poster = doc.selectFirst(".poster img")?.attr("src")
        
        val isSeries = url.contains("/series/")

        if (isSeries) {{
            val episodes = mutableListOf<Episode>()
            
            // Método baseado na análise: {len(episode_selectors)} seletores encontrados
            {self.generate_episode_extraction_code(episode_selectors)}
            
            return newTvSeriesLoadResponse(title, url, TvType.TvSeries, episodes) {{
                this.posterUrl = poster
                this.plot = desc
            }}
        }} else {{
            return newMovieLoadResponse(title, url, TvType.Movie, url) {{
                this.posterUrl = poster
                this.plot = desc
            }}
        }}
    }}

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {{
        val doc = app.get(data).document
        var linksFound = 0
        
        // Método baseado na análise: {len(player_selectors)} tipos de players encontrados
        {self.generate_player_extraction_code(player_selectors)}
        
        return linksFound > 0
    }}
}}
'''
        
        return kotlin_template
    
    def generate_episode_extraction_code(self, selectors):
        """Gerar código de extração de episódios"""
        code_parts = []
        
        for i, selector in enumerate(selectors):
            code_parts.append(f'''
            // Método {i+1}: {selector}
            if (episodes.isEmpty()) {{
                doc.select("{selector}").forEachIndexed {{ index, element ->
                    val epTitle = element.text().trim()
                    val epHref = element.attr("href")
                    
                    if (epHref.isNotEmpty()) {{
                        val epNum = extractEpisodeNumber(element, index + 1)
                        val seasonNum = extractSeasonNumber(element, 1)
                        
                        episodes.add(newEpisode(epHref) {{
                            this.name = epTitle
                            this.episode = epNum
                            this.season = seasonNum
                        }})
                    }}
                }}
            }}''')
        
        return '\n'.join(code_parts)
    
    def generate_player_extraction_code(self, selectors):
        """Gerar código de extração de players"""
        code_parts = []
        
        for i, selector in enumerate(selectors):
            if 'data-source' in selector:
                code_parts.append(f'''
            // Método {i+1}: Botões com data-source
            doc.select("{selector}").forEach {{ button ->
                val source = button.attr("data-source")
                if (source.isNotEmpty() && source.startsWith("http")) {{
                    if (loadExtractor(source, data, subtitleCallback, callback)) {{
                        linksFound++
                    }}
                }}
            }}''')
            elif 'playeroptionsul' in selector:
                code_parts.append(f'''
            // Método {i+1}: AJAX DooPlay
            doc.select("{selector}").forEach {{ option ->
                val playerId = option.attr("data-post")
                val playerNum = option.attr("data-nume")
                val playerType = option.attr("data-type").ifEmpty {{ "movie" }}
                
                if (playerId.isNotEmpty() && playerNum.isNotEmpty()) {{
                    try {{
                        val ajaxUrl = "$mainUrl/wp-admin/admin-ajax.php"
                        val ajaxData = mapOf(
                            "action" to "doo_player_ajax",
                            "post" to playerId,
                            "nume" to playerNum,
                            "type" to playerType
                        )
                        
                        val ajaxResponse = app.post(ajaxUrl, data = ajaxData).text
                        val iframeRegex = Regex("""src=["']([^"']+)["']""")
                        val iframeMatch = iframeRegex.find(ajaxResponse)
                        
                        if (iframeMatch != null) {{
                            val iframeUrl = iframeMatch.groupValues[1]
                            val cleanUrl = if (iframeUrl.startsWith("//")) "https:$iframeUrl" else iframeUrl
                            
                            if (loadExtractor(cleanUrl, data, subtitleCallback, callback)) {{
                                linksFound++
                            }}
                        }}
                    }} catch (e: Exception) {{
                        Log.e("MaxSeries", "Erro no AJAX: ${{e.message}}")
                    }}
                }}
            }}''')
        
        return '\n'.join(code_parts)
    
    def save_analysis(self, data, filename='advanced_analysis.json'):
        """Salvar análise completa"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Análise salva em {filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
    
    def run_complete_analysis(self):
        """Executar análise completa"""
        logger.info("🚀 Iniciando análise completa do MaxSeries...")
        
        results = {
            'analysis_timestamp': time.time(),
            'base_url': self.base_url
        }
        
        # 1. Analisar homepage
        homepage_analysis = self.analyze_homepage()
        if homepage_analysis:
            results['homepage_analysis'] = homepage_analysis
            
            # 2. Analisar série de exemplo
            if homepage_analysis['series_links']:
                sample_series = homepage_analysis['series_links'][0]['url']
                series_analysis = self.deep_analyze_series(sample_series)
                if series_analysis:
                    results['series_analysis'] = series_analysis
        
        # 3. Gerar código Kotlin
        kotlin_code = self.generate_kotlin_scraper(results)
        results['generated_kotlin'] = kotlin_code
        
        # 4. Salvar resultados
        self.save_analysis(results)
        
        # 5. Salvar código Kotlin separadamente
        with open('MaxSeriesGenerated.kt', 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        
        logger.info("✅ Análise completa concluída!")
        return results

def main():
    """Função principal"""
    print("🔍 SCRAPER AVANÇADO MAXSERIES")
    print("=" * 50)
    
    scraper = AdvancedMaxSeriesScraper()
    
    try:
        results = scraper.run_complete_analysis()
        
        print("\n📊 RESUMO DA ANÁLISE:")
        if 'homepage_analysis' in results:
            homepage = results['homepage_analysis']
            print(f"📺 Séries encontradas: {len(homepage['series_links'])}")
            print(f"🎬 Filmes encontrados: {len(homepage['movie_links'])}")
        
        if 'series_analysis' in results:
            series = results['series_analysis']
            print(f"📺 Série analisada: {series['title']}")
            print(f"🎬 Temporadas: {series['seasons_structure']['season_count']}")
            print(f"📺 Episódios: {len(series['episodes_structure']['episode_links'])}")
            print(f"🎮 Players: {len(series['player_structure']['data_source_buttons'])}")
        
        print("\n📄 ARQUIVOS GERADOS:")
        print("  - advanced_analysis.json (análise completa)")
        print("  - MaxSeriesGenerated.kt (código Kotlin)")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Revise o código gerado em MaxSeriesGenerated.kt")
        print("2. Integre as melhorias no MaxSeries atual")
        print("3. Teste com o CloudStream")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    main()