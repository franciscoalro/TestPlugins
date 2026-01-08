#!/usr/bin/env python3
"""
Analisador Automático MaxSeries com GeckoDriver
Analisa estrutura de páginas para criar scraper perfeito
"""

import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaxSeriesAnalyzer:
    def __init__(self, headless=True):
        """Inicializar analisador com GeckoDriver"""
        self.setup_driver(headless)
        self.results = {}
        
    def setup_driver(self, headless):
        """Configurar Firefox com GeckoDriver"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        
        # Configurações para melhor análise
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Firefox(options=options)
            logger.info("✅ GeckoDriver iniciado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar GeckoDriver: {e}")
            raise
    
    def analyze_series_page(self, url):
        """Analisar página de série completa"""
        logger.info(f"📺 Analisando série: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Aguardar carregamento
            
            # Capturar informações básicas
            page_info = {
                'url': url,
                'title': self.driver.title,
                'current_url': self.driver.current_url
            }
            
            # Analisar estrutura de episódios
            episodes_structure = self.analyze_episodes_structure()
            
            # Analisar players
            players_structure = self.analyze_players_structure()
            
            # Analisar scripts JavaScript
            scripts_analysis = self.analyze_javascript()
            
            # Capturar HTML relevante
            html_sections = self.capture_relevant_html()
            
            result = {
                'page_info': page_info,
                'episodes': episodes_structure,
                'players': players_structure,
                'scripts': scripts_analysis,
                'html_sections': html_sections,
                'analysis_timestamp': time.time()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar série: {e}")
            return None
    
    def analyze_episodes_structure(self):
        """Analisar estrutura de episódios detalhadamente"""
        logger.info("🔍 Analisando estrutura de episódios...")
        
        structure = {
            'dooplay_seasons': [],
            'episode_lists': [],
            'alternative_structures': [],
            'episode_links': []
        }
        
        try:
            # Método 1: DooPlay padrão
            seasons = self.driver.find_elements(By.CSS_SELECTOR, 'div.se-c')
            for i, season in enumerate(seasons):
                season_info = {
                    'index': i,
                    'id': season.get_attribute('id'),
                    'class': season.get_attribute('class'),
                    'episodes_count': len(season.find_elements(By.CSS_SELECTOR, 'ul.episodios li'))
                }
                
                # Capturar episódios da temporada
                episodes = season.find_elements(By.CSS_SELECTOR, 'ul.episodios li')
                episode_details = []
                
                for j, ep in enumerate(episodes[:5]):  # Primeiros 5 para análise
                    try:
                        link = ep.find_element(By.CSS_SELECTOR, 'a')
                        numerando = ep.find_elements(By.CSS_SELECTOR, '.numerando')
                        
                        ep_info = {
                            'index': j,
                            'text': ep.text.strip(),
                            'link_href': link.get_attribute('href') if link else None,
                            'numerando': numerando[0].text if numerando else None,
                            'html': ep.get_attribute('outerHTML')[:200]
                        }
                        episode_details.append(ep_info)
                    except:
                        continue
                
                season_info['episodes_sample'] = episode_details
                structure['dooplay_seasons'].append(season_info)
            
            # Método 2: Listas alternativas
            alternative_selectors = [
                'ul.episodios li a',
                '.episodios a',
                '.episode-list a',
                '.episodes a',
                'li[data-episode] a'
            ]
            
            for selector in alternative_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    structure['alternative_structures'].append({
                        'selector': selector,
                        'count': len(elements),
                        'sample': [el.text.strip() for el in elements[:3]]
                    })
            
            # Método 3: Links com padrões de episódio
            all_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="episodio"], a[href*="episode"]')
            for link in all_links[:10]:  # Primeiros 10
                structure['episode_links'].append({
                    'text': link.text.strip(),
                    'href': link.get_attribute('href'),
                    'parent_class': link.find_element(By.XPATH, '..').get_attribute('class')
                })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de episódios: {e}")
        
        return structure
    
    def analyze_players_structure(self):
        """Analisar estrutura de players"""
        logger.info("🎬 Analisando estrutura de players...")
        
        structure = {
            'iframes': [],
            'player_buttons': [],
            'ajax_options': [],
            'scripts_players': []
        }
        
        try:
            # Iframes
            iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
            for iframe in iframes:
                structure['iframes'].append({
                    'src': iframe.get_attribute('src'),
                    'class': iframe.get_attribute('class'),
                    'id': iframe.get_attribute('id')
                })
            
            # Botões com data-source
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-source], .btn[data-source]')
            for button in buttons:
                structure['player_buttons'].append({
                    'text': button.text.strip(),
                    'data_source': button.get_attribute('data-source'),
                    'data_type': button.get_attribute('data-type')
                })
            
            # Opções AJAX
            ajax_options = self.driver.find_elements(By.CSS_SELECTOR, '#playeroptionsul li, .playeroptionsul li')
            for option in ajax_options:
                structure['ajax_options'].append({
                    'text': option.text.strip(),
                    'data_post': option.get_attribute('data-post'),
                    'data_nume': option.get_attribute('data-nume'),
                    'data_type': option.get_attribute('data-type')
                })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de players: {e}")
        
        return structure
    
    def analyze_javascript(self):
        """Analisar scripts JavaScript relevantes"""
        logger.info("📜 Analisando scripts JavaScript...")
        
        scripts = {
            'jwplayer_configs': [],
            'gleam_configs': [],
            'ajax_calls': [],
            'video_urls': []
        }
        
        try:
            # Capturar todos os scripts
            script_elements = self.driver.find_elements(By.CSS_SELECTOR, 'script')
            
            for script in script_elements:
                content = script.get_attribute('innerHTML')
                if not content:
                    continue
                
                # Procurar configurações específicas
                if 'jwplayer' in content.lower():
                    scripts['jwplayer_configs'].append(content[:500])
                
                if 'gleam' in content.lower():
                    scripts['gleam_configs'].append(content[:500])
                
                if 'ajax' in content.lower() or 'XMLHttpRequest' in content:
                    scripts['ajax_calls'].append(content[:300])
                
                # Procurar URLs de vídeo
                import re
                video_patterns = [
                    r'https?://[^"\s]+\.(?:m3u8|mp4|mkv|avi)',
                    r'"url"\s*:\s*"([^"]+)"',
                    r'"file"\s*:\s*"([^"]+)"'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, content)
                    scripts['video_urls'].extend(matches)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de JavaScript: {e}")
        
        return scripts
    
    def capture_relevant_html(self):
        """Capturar seções HTML relevantes"""
        logger.info("📄 Capturando HTML relevante...")
        
        html_sections = {}
        
        try:
            # Seções importantes
            selectors = {
                'seasons_section': '.seasons, .se-list, div.se-c',
                'episodes_section': '.episodios, ul.episodios',
                'players_section': '#playeroptionsul, .player-options, #players',
                'main_content': '.wp-content, .entry-content, .content'
            }
            
            for name, selector in selectors.items():
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    html_sections[name] = element.get_attribute('outerHTML')[:1000]
                except:
                    html_sections[name] = 'não encontrado'
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar HTML: {e}")
        
        return html_sections
    
    def analyze_movie_page(self, url):
        """Analisar página de filme"""
        logger.info(f"🎬 Analisando filme: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Focar na análise de players para filmes
            players_structure = self.analyze_players_structure()
            scripts_analysis = self.analyze_javascript()
            
            # Simular cliques em players se existirem
            player_interactions = self.simulate_player_interactions()
            
            result = {
                'url': url,
                'title': self.driver.title,
                'players': players_structure,
                'scripts': scripts_analysis,
                'interactions': player_interactions,
                'analysis_timestamp': time.time()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar filme: {e}")
            return None
    
    def simulate_player_interactions(self):
        """Simular interações com players"""
        logger.info("🖱️ Simulando interações com players...")
        
        interactions = {
            'clicked_buttons': [],
            'network_requests': [],
            'iframe_changes': []
        }
        
        try:
            # Tentar clicar em botões de player
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-source], .btn[data-source]')
            
            for i, button in enumerate(buttons[:3]):  # Testar primeiros 3
                try:
                    button_info = {
                        'index': i,
                        'text': button.text.strip(),
                        'data_source': button.get_attribute('data-source')
                    }
                    
                    # Clicar e observar mudanças
                    button.click()
                    time.sleep(2)
                    
                    # Verificar se iframe mudou
                    new_iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
                    iframe_sources = [iframe.get_attribute('src') for iframe in new_iframes]
                    
                    button_info['result_iframes'] = iframe_sources
                    interactions['clicked_buttons'].append(button_info)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao clicar no botão {i}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro nas interações: {e}")
        
        return interactions
    
    def generate_scraper_code(self, analysis_results):
        """Gerar código de scraper baseado na análise"""
        logger.info("🔧 Gerando código de scraper...")
        
        # Analisar resultados e gerar código Kotlin otimizado
        # Este seria um sistema mais complexo que analisa os padrões encontrados
        # e gera o código correspondente
        
        scraper_suggestions = {
            'episode_selectors': [],
            'player_methods': [],
            'javascript_handling': [],
            'recommended_approach': ''
        }
        
        # Lógica para gerar sugestões baseadas na análise...
        
        return scraper_suggestions
    
    def save_results(self, results, filename='maxseries_analysis.json'):
        """Salvar resultados da análise"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Resultados salvos em {filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
    
    def close(self):
        """Fechar driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("🔒 GeckoDriver fechado")

def main():
    """Função principal"""
    print("🦎 ANALISADOR AUTOMÁTICO MAXSERIES")
    print("=" * 50)
    
    # URLs para análise
    test_urls = {
        'serie': 'https://www.maxseries.one/series/breaking-bad/',
        'filme': 'https://www.maxseries.one/filme/exemplo/'
    }
    
    analyzer = MaxSeriesAnalyzer(headless=False)  # Modo visual para debug
    
    try:
        all_results = {}
        
        # Analisar série
        print("\n📺 Analisando estrutura de séries...")
        series_result = analyzer.analyze_series_page(test_urls['serie'])
        if series_result:
            all_results['series_analysis'] = series_result
        
        # Analisar filme
        print("\n🎬 Analisando estrutura de filmes...")
        # movie_result = analyzer.analyze_movie_page(test_urls['filme'])
        # if movie_result:
        #     all_results['movie_analysis'] = movie_result
        
        # Salvar resultados
        analyzer.save_results(all_results)
        
        # Gerar sugestões de código
        suggestions = analyzer.generate_scraper_code(all_results)
        analyzer.save_results(suggestions, 'scraper_suggestions.json')
        
        print("\n✅ Análise concluída!")
        print("📄 Verifique os arquivos:")
        print("  - maxseries_analysis.json")
        print("  - scraper_suggestions.json")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()