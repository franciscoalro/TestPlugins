#!/usr/bin/env python3
"""
Scraper Avançado MaxSeries com GeckoDriver
Simula navegador real para análise completa e interativa
"""

import json
import time
import re
import logging
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeckoAdvancedScraper:
    def __init__(self, geckodriver_path="D:\\geckodriver.exe", headless=False):
        """Inicializar scraper com GeckoDriver"""
        self.geckodriver_path = geckodriver_path
        self.headless = headless
        self.driver = None
        self.wait = None
        self.base_url = "https://www.maxseries.one"
        self.results = {}
        
    def setup_driver(self):
        """Configurar Firefox com GeckoDriver"""
        logger.info("🦎 Configurando GeckoDriver...")
        
        # Verificar se GeckoDriver existe
        if not os.path.exists(self.geckodriver_path):
            logger.error(f"❌ GeckoDriver não encontrado: {self.geckodriver_path}")
            return False
        
        # Configurar serviço
        service = Service(executable_path=self.geckodriver_path)
        
        # Configurar opções do Firefox
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        # Configurações para melhor scraping
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Configurar caminho do Firefox (fornecido pelo usuário)
        firefox_binary = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        
        if os.path.exists(firefox_binary):
            options.binary_location = firefox_binary
            logger.info(f"🔍 Firefox encontrado: {firefox_binary}")
        else:
            logger.error(f"❌ Firefox não encontrado em: {firefox_binary}")
            return False
        
        # Configurações de preferências
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference('general.useragent.override', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Desabilitar imagens para velocidade (opcional)
        options.set_preference('permissions.default.image', 2)
        
        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("✅ GeckoDriver iniciado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar GeckoDriver: {e}")
            logger.info("🔧 Soluções possíveis:")
            logger.info("1. Execute: setup-firefox-geckodriver.ps1")
            logger.info("2. Instale Firefox manualmente")
            logger.info("3. Use gecko-simulation-scraper.py (sem Firefox)")
            return False
    
    def analyze_homepage_interactive(self):
        """Análise interativa da homepage"""
        logger.info("🏠 Analisando homepage interativamente...")
        
        try:
            self.driver.get(self.base_url)
            time.sleep(3)  # Aguardar carregamento
            
            analysis = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_source_length': len(self.driver.page_source),
                'series_links': [],
                'movie_links': [],
                'navigation_elements': [],
                'interactive_elements': []
            }
            
            # Procurar links de séries e filmes
            try:
                series_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/series/"]')
                for link in series_links[:10]:  # Primeiros 10
                    try:
                        analysis['series_links'].append({
                            'text': link.text.strip(),
                            'href': link.get_attribute('href'),
                            'visible': link.is_displayed()
                        })
                    except:
                        continue
                
                movie_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/filme/"], a[href*="/movie/"]')
                for link in movie_links[:10]:  # Primeiros 10
                    try:
                        analysis['movie_links'].append({
                            'text': link.text.strip(),
                            'href': link.get_attribute('href'),
                            'visible': link.is_displayed()
                        })
                    except:
                        continue
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar links: {e}")
            
            # Analisar elementos de navegação
            try:
                nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 'nav, .menu, .navigation')
                for nav in nav_elements:
                    nav_links = nav.find_elements(By.TAG_NAME, 'a')
                    analysis['navigation_elements'].append({
                        'class': nav.get_attribute('class'),
                        'links_count': len(nav_links),
                        'links': [{'text': a.text.strip(), 'href': a.get_attribute('href')} 
                                for a in nav_links[:5]]  # Primeiros 5
                    })
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar navegação: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise da homepage: {e}")
            return None
    
    def deep_analyze_series_page(self, series_url):
        """Análise profunda e interativa de uma página de série"""
        logger.info(f"📺 Análise profunda da série: {series_url}")
        
        try:
            self.driver.get(series_url)
            time.sleep(5)  # Aguardar carregamento completo
            
            analysis = {
                'url': series_url,
                'title': self.extract_title_interactive(),
                'description': self.extract_description_interactive(),
                'poster': self.extract_poster_interactive(),
                'seasons_analysis': self.analyze_seasons_interactive(),
                'episodes_analysis': self.analyze_episodes_interactive(),
                'player_analysis': self.analyze_players_interactive(),
                'javascript_analysis': self.analyze_javascript_interactive(),
                'network_analysis': self.monitor_network_requests(),
                'interaction_results': self.simulate_user_interactions()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise profunda: {e}")
            return None
    
    def extract_title_interactive(self):
        """Extrair título usando Selenium"""
        selectors = [
            '.data h1',
            'h1',
            '.entry-title',
            '.post-title',
            '.movie-title',
            '.series-title'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return element.text.strip()
            except:
                continue
        
        return self.driver.title
    
    def extract_description_interactive(self):
        """Extrair descrição usando Selenium"""
        selectors = [
            '.sinopse',
            '.entry-content',
            '.wp-content',
            '.description',
            '.plot',
            '.overview'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return element.text.strip()[:500]
            except:
                continue
        
        return 'Descrição não encontrada'
    
    def extract_poster_interactive(self):
        """Extrair poster usando Selenium"""
        selectors = [
            '.poster img',
            '.wp-post-image',
            '.movie-poster img',
            '.series-poster img'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                src = element.get_attribute('src') or element.get_attribute('data-src')
                if src:
                    return src
            except:
                continue
        
        return None
    
    def analyze_seasons_interactive(self):
        """Análise interativa de temporadas"""
        logger.info("🎬 Analisando temporadas interativamente...")
        
        analysis = {
            'dooplay_seasons': [],
            'season_tabs': [],
            'season_buttons': [],
            'total_seasons': 0
        }
        
        try:
            # Método 1: DooPlay padrão
            seasons = self.driver.find_elements(By.CSS_SELECTOR, 'div.se-c')
            for i, season in enumerate(seasons):
                season_info = {
                    'index': i,
                    'id': season.get_attribute('id'),
                    'class': season.get_attribute('class'),
                    'visible': season.is_displayed(),
                    'episodes_count': len(season.find_elements(By.CSS_SELECTOR, 'ul.episodios li'))
                }
                analysis['dooplay_seasons'].append(season_info)
            
            analysis['total_seasons'] = len(seasons)
            
            # Método 2: Tabs de temporadas
            season_tabs = self.driver.find_elements(By.CSS_SELECTOR, '.season-tab, [data-season], .temporada')
            for tab in season_tabs:
                analysis['season_tabs'].append({
                    'text': tab.text.strip(),
                    'data_season': tab.get_attribute('data-season'),
                    'clickable': tab.is_enabled()
                })
            
            # Método 3: Botões de temporadas
            season_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-season], .season-button')
            for button in season_buttons:
                analysis['season_buttons'].append({
                    'text': button.text.strip(),
                    'data_season': button.get_attribute('data-season'),
                    'enabled': button.is_enabled()
                })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de temporadas: {e}")
        
        return analysis
    
    def analyze_episodes_interactive(self):
        """Análise interativa de episódios"""
        logger.info("📺 Analisando episódios interativamente...")
        
        analysis = {
            'episode_links': [],
            'episode_elements': [],
            'numbering_analysis': [],
            'clickable_episodes': []
        }
        
        try:
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
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"🔍 Encontrados {len(elements)} episódios com seletor: {selector}")
                        
                        for i, element in enumerate(elements[:10]):  # Primeiros 10
                            try:
                                episode_info = {
                                    'selector': selector,
                                    'index': i,
                                    'text': element.text.strip(),
                                    'href': element.get_attribute('href'),
                                    'visible': element.is_displayed(),
                                    'clickable': element.is_enabled(),
                                    'parent_class': element.find_element(By.XPATH, '..').get_attribute('class') if element else None
                                }
                                
                                # Tentar extrair número do episódio
                                episode_info['episode_number'] = self.extract_episode_number_interactive(element)
                                episode_info['season_number'] = self.extract_season_number_interactive(element)
                                
                                analysis['episode_elements'].append(episode_info)
                                
                                if element.get_attribute('href'):
                                    analysis['episode_links'].append({
                                        'title': episode_info['text'],
                                        'url': element.get_attribute('href'),
                                        'episode': episode_info['episode_number'],
                                        'season': episode_info['season_number']
                                    })
                                
                            except Exception as e:
                                logger.warning(f"⚠️ Erro ao processar episódio {i}: {e}")
                                continue
                        
                        break  # Usar primeiro seletor que funcionar
                        
                except Exception as e:
                    logger.warning(f"⚠️ Seletor {selector} falhou: {e}")
                    continue
            
            # Analisar elementos de numeração
            try:
                numerando_elements = self.driver.find_elements(By.CSS_SELECTOR, '.numerando')
                for elem in numerando_elements[:5]:  # Primeiros 5
                    analysis['numbering_analysis'].append({
                        'text': elem.text.strip(),
                        'pattern': self.identify_numbering_pattern(elem.text.strip())
                    })
            except Exception as e:
                logger.warning(f"⚠️ Erro na análise de numeração: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de episódios: {e}")
        
        return analysis
    
    def extract_episode_number_interactive(self, element):
        """Extrair número do episódio usando Selenium"""
        try:
            # Procurar em .numerando próximo
            try:
                numerando = element.find_element(By.XPATH, './/*[@class="numerando"]')
                numerando_text = numerando.text
                match = re.search(r'(\d+)\s*-\s*(\d+)|E(\d+)', numerando_text)
                if match:
                    return int(match.group(2) or match.group(3))
            except:
                pass
            
            # Procurar no texto do elemento
            text = element.text
            ep_match = re.search(r'episódio\s*(\d+)|episode\s*(\d+)|ep\s*(\d+)', text, re.IGNORECASE)
            if ep_match:
                return int(ep_match.group(1) or ep_match.group(2) or ep_match.group(3))
            
            # Procurar na URL
            href = element.get_attribute('href') or ''
            url_match = re.search(r'episodio-(\d+)|episode-(\d+)', href)
            if url_match:
                return int(url_match.group(1) or url_match.group(2))
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair número do episódio: {e}")
        
        return None
    
    def extract_season_number_interactive(self, element):
        """Extrair número da temporada usando Selenium"""
        try:
            # Procurar elemento pai de temporada
            try:
                season_parent = element.find_element(By.XPATH, './ancestor::*[@class="se-c"]')
                season_id = season_parent.get_attribute('id')
                if 'season-' in season_id:
                    return int(season_id.replace('season-', ''))
            except:
                pass
            
            # Procurar em data attributes
            season_data = element.get_attribute('data-season')
            if season_data:
                try:
                    return int(season_data)
                except:
                    pass
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair temporada: {e}")
        
        return 1
    
    def identify_numbering_pattern(self, text):
        """Identificar padrão de numeração"""
        if re.match(r'\d+\s*-\s*\d+', text):
            return 'season-episode'
        elif re.match(r'S\d+E\d+', text, re.IGNORECASE):
            return 'sXeY'
        elif re.match(r'\d+x\d+', text):
            return 'seasonXepisode'
        elif re.match(r'\d+', text):
            return 'simple_number'
        else:
            return 'unknown'
    
    def analyze_players_interactive(self):
        """Análise interativa de players"""
        logger.info("🎬 Analisando players interativamente...")
        
        analysis = {
            'iframes': [],
            'player_buttons': [],
            'data_source_buttons': [],
            'ajax_options': [],
            'interactive_elements': []
        }
        
        try:
            # Analisar iframes
            iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
            for i, iframe in enumerate(iframes):
                iframe_info = {
                    'index': i,
                    'src': iframe.get_attribute('src'),
                    'class': iframe.get_attribute('class'),
                    'id': iframe.get_attribute('id'),
                    'visible': iframe.is_displayed(),
                    'size': {
                        'width': iframe.size['width'],
                        'height': iframe.size['height']
                    }
                }
                analysis['iframes'].append(iframe_info)
            
            # Botões com data-source
            data_source_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-source], .btn[data-source]')
            for button in data_source_buttons:
                analysis['data_source_buttons'].append({
                    'text': button.text.strip(),
                    'data_source': button.get_attribute('data-source'),
                    'data_type': button.get_attribute('data-type'),
                    'enabled': button.is_enabled(),
                    'visible': button.is_displayed()
                })
            
            # Opções AJAX DooPlay
            ajax_options = self.driver.find_elements(By.CSS_SELECTOR, '#playeroptionsul li, .playeroptionsul li')
            for option in ajax_options:
                analysis['ajax_options'].append({
                    'text': option.text.strip(),
                    'data_post': option.get_attribute('data-post'),
                    'data_nume': option.get_attribute('data-nume'),
                    'data_type': option.get_attribute('data-type'),
                    'clickable': option.is_enabled()
                })
            
            # Elementos interativos gerais
            interactive_elements = self.driver.find_elements(By.CSS_SELECTOR, 'button, .btn, [onclick], [data-toggle]')
            for elem in interactive_elements[:10]:  # Primeiros 10
                if elem.is_displayed() and elem.is_enabled():
                    analysis['interactive_elements'].append({
                        'tag': elem.tag_name,
                        'text': elem.text.strip()[:50],
                        'class': elem.get_attribute('class'),
                        'onclick': elem.get_attribute('onclick')
                    })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de players: {e}")
        
        return analysis
    
    def analyze_javascript_interactive(self):
        """Análise de JavaScript usando Selenium"""
        logger.info("📜 Analisando JavaScript interativamente...")
        
        analysis = {
            'script_count': 0,
            'external_scripts': [],
            'inline_scripts': [],
            'jwplayer_detected': False,
            'gleam_detected': False,
            'ajax_patterns': [],
            'video_urls': []
        }
        
        try:
            # Contar scripts
            scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script')
            analysis['script_count'] = len(scripts)
            
            # Analisar scripts externos
            for script in scripts:
                src = script.get_attribute('src')
                if src:
                    analysis['external_scripts'].append(src)
                    
                    # Detectar bibliotecas conhecidas
                    if 'jwplayer' in src.lower():
                        analysis['jwplayer_detected'] = True
                    if 'gleam' in src.lower() or 'app.js' in src.lower():
                        analysis['gleam_detected'] = True
            
            # Executar JavaScript para obter configurações
            try:
                # Tentar obter configurações gleam
                gleam_config = self.driver.execute_script("return typeof gleam !== 'undefined' ? gleam.config : null;")
                if gleam_config:
                    analysis['gleam_config'] = gleam_config
                
                # Tentar obter configurações jwplayer
                jwplayer_instances = self.driver.execute_script("return typeof jwplayer !== 'undefined' ? jwplayer().getConfig() : null;")
                if jwplayer_instances:
                    analysis['jwplayer_config'] = jwplayer_instances
                
                # Procurar URLs de vídeo em variáveis JavaScript
                video_vars = self.driver.execute_script("""
                    var videoUrls = [];
                    for (var prop in window) {
                        try {
                            if (typeof window[prop] === 'string' && 
                                (window[prop].includes('.m3u8') || 
                                 window[prop].includes('.mp4') || 
                                 window[prop].includes('embed'))) {
                                videoUrls.push(window[prop]);
                            }
                        } catch(e) {}
                    }
                    return videoUrls;
                """)
                
                if video_vars:
                    analysis['video_urls'].extend(video_vars)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao executar JavaScript: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de JavaScript: {e}")
        
        return analysis
    
    def monitor_network_requests(self):
        """Monitorar requests de rede (simulado)"""
        logger.info("🌐 Monitorando requests de rede...")
        
        # Nota: Para monitoramento real de rede, seria necessário usar 
        # selenium-wire ou configurar proxy. Por enquanto, simulamos.
        
        analysis = {
            'ajax_endpoints_detected': [],
            'video_requests': [],
            'api_calls': []
        }
        
        try:
            # Procurar por padrões de AJAX no código fonte
            page_source = self.driver.page_source
            
            # Procurar endpoints AJAX
            ajax_patterns = [
                r'["\']([^"\']*(?:ajax|api|player|stream)[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in ajax_patterns:
                matches = re.findall(pattern, page_source)
                analysis['ajax_endpoints_detected'].extend(matches)
            
            # Procurar URLs de vídeo
            video_patterns = [
                r'https?://[^"\s]+\.(?:m3u8|mp4|mkv|avi)',
                r'"file"\s*:\s*"([^"]+)"',
                r'"source"\s*:\s*"([^"]+)"'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, page_source)
                analysis['video_requests'].extend(matches)
            
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento de rede: {e}")
        
        return analysis
    
    def simulate_user_interactions(self):
        """Simular interações do usuário"""
        logger.info("🖱️ Simulando interações do usuário...")
        
        interactions = {
            'clicked_elements': [],
            'hover_effects': [],
            'form_interactions': [],
            'dynamic_content': []
        }
        
        try:
            # Simular cliques em botões de player
            player_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-source], .btn[data-source]')
            
            for i, button in enumerate(player_buttons[:3]):  # Testar primeiros 3
                try:
                    if button.is_displayed() and button.is_enabled():
                        # Scroll até o elemento
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # Hover sobre o elemento
                        ActionChains(self.driver).move_to_element(button).perform()
                        time.sleep(1)
                        
                        # Capturar estado antes do clique
                        before_iframes = len(self.driver.find_elements(By.CSS_SELECTOR, 'iframe'))
                        
                        # Clicar
                        button.click()
                        time.sleep(3)  # Aguardar resposta
                        
                        # Capturar estado depois do clique
                        after_iframes = len(self.driver.find_elements(By.CSS_SELECTOR, 'iframe'))
                        
                        interaction_result = {
                            'button_index': i,
                            'button_text': button.text.strip(),
                            'data_source': button.get_attribute('data-source'),
                            'iframes_before': before_iframes,
                            'iframes_after': after_iframes,
                            'iframe_changed': before_iframes != after_iframes
                        }
                        
                        # Verificar se novos iframes apareceram
                        if after_iframes > before_iframes:
                            new_iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
                            for iframe in new_iframes[before_iframes:]:
                                interaction_result['new_iframe_src'] = iframe.get_attribute('src')
                        
                        interactions['clicked_elements'].append(interaction_result)
                        
                        logger.info(f"✅ Clique simulado no botão {i}: {button.text.strip()}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao clicar no botão {i}: {e}")
            
            # Simular hover em elementos
            hover_elements = self.driver.find_elements(By.CSS_SELECTOR, '.episode, .player-option, .season')
            for elem in hover_elements[:5]:  # Primeiros 5
                try:
                    if elem.is_displayed():
                        ActionChains(self.driver).move_to_element(elem).perform()
                        time.sleep(0.5)
                        
                        interactions['hover_effects'].append({
                            'element_class': elem.get_attribute('class'),
                            'text': elem.text.strip()[:30]
                        })
                except:
                    continue
            
        except Exception as e:
            logger.error(f"❌ Erro nas interações: {e}")
        
        return interactions
    
    def analyze_episode_page_interactive(self, episode_url):
        """Análise interativa de página de episódio"""
        logger.info(f"📺 Analisando episódio interativamente: {episode_url}")
        
        try:
            self.driver.get(episode_url)
            time.sleep(5)
            
            analysis = {
                'url': episode_url,
                'title': self.extract_title_interactive(),
                'players': self.analyze_players_interactive(),
                'javascript': self.analyze_javascript_interactive(),
                'interactions': self.simulate_user_interactions(),
                'network': self.monitor_network_requests()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar episódio: {e}")
            return None
    
    def generate_advanced_kotlin_code(self, analysis_data):
        """Gerar código Kotlin avançado baseado na análise completa"""
        logger.info("🔧 Gerando código Kotlin avançado...")
        
        # Extrair informações da análise
        series_data = analysis_data.get('series_analysis', {})
        episodes_data = series_data.get('episodes_analysis', {})
        players_data = series_data.get('player_analysis', {})
        interactions_data = series_data.get('interaction_results', {})
        
        # Gerar código baseado nos dados reais coletados
        kotlin_template = f'''package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

class MaxSeriesProvider : MainAPI() {{
    override var mainUrl = "https://www.maxseries.one"
    override var name = "MaxSeries"
    override val hasMainPage = true
    override var lang = "pt"
    override val supportedTypes = setOf(TvType.TvSeries, TvType.Movie)

    // Baseado na análise GeckoDriver: {len(episodes_data.get('episode_links', []))} episódios detectados
    // Players encontrados: {len(players_data.get('data_source_buttons', []))} botões data-source
    // Interações testadas: {len(interactions_data.get('clicked_elements', []))} cliques simulados

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
            
            Log.d("MaxSeries", "📺 Analisando série (GeckoDriver): $title")
            
            // Método 1: Estrutura detectada pelo GeckoDriver
            {self.generate_episode_code_from_analysis(episodes_data)}
            
            Log.d("MaxSeries", "✅ Total episódios: ${{episodes.size}}")

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
        Log.d("MaxSeries", "📺 Processando links (GeckoDriver): $data")
        
        var linksFound = 0
        val doc = app.get(data).document
        
        // Método baseado nas interações GeckoDriver
        {self.generate_player_code_from_analysis(players_data, interactions_data)}
        
        Log.d("MaxSeries", "✅ Links encontrados: $linksFound")
        return linksFound > 0
    }}
}}'''
        
        return kotlin_template
    
    def generate_episode_code_from_analysis(self, episodes_data):
        """Gerar código de episódios baseado na análise"""
        episode_links = episodes_data.get('episode_links', [])
        
        if not episode_links:
            return '''
            // Nenhum episódio detectado pelo GeckoDriver - usando fallback
            episodes.add(newEpisode(url) {
                this.name = "Episódio 1"
                this.episode = 1
                this.season = 1
            })'''
        
        # Analisar padrões encontrados
        has_seasons = any(ep.get('season', 1) > 1 for ep in episode_links)
        
        code = '''
            // Estrutura detectada pelo GeckoDriver
            doc.select("ul.episodios li a").forEachIndexed { index, element ->
                val epTitle = element.text().trim()
                val epHref = element.attr("href")
                
                if (epHref.isNotEmpty()) {
                    val epNum = extractEpisodeNumber(element, index + 1)
                    val seasonNum = extractSeasonNumber(element, 1)
                    
                    episodes.add(newEpisode(epHref) {
                        this.name = epTitle
                        this.episode = epNum
                        this.season = seasonNum
                    })
                }
            }'''
        
        return code
    
    def generate_player_code_from_analysis(self, players_data, interactions_data):
        """Gerar código de players baseado na análise"""
        data_source_buttons = players_data.get('data_source_buttons', [])
        clicked_elements = interactions_data.get('clicked_elements', [])
        
        if not data_source_buttons:
            return '''
            // Nenhum player data-source detectado - usando método padrão
            doc.select("iframe").forEach { iframe ->
                val src = iframe.attr("src")
                if (src.isNotEmpty() && src.startsWith("http")) {
                    if (loadExtractor(src, data, subtitleCallback, callback)) {
                        linksFound++
                    }
                }
            }'''
        
        code = '''
        // Players detectados pelo GeckoDriver
        doc.select("button[data-source], .btn[data-source]").forEach { button ->
            val source = button.attr("data-source")
            val playerName = button.text().trim()
            
            if (source.isNotEmpty() && source.startsWith("http")) {
                Log.d("MaxSeries", "🎯 Player GeckoDriver: $playerName -> $source")
                
                if (loadExtractor(source, data, subtitleCallback, callback)) {
                    linksFound++
                }
            }
        }
        
        // Fallback: iframe principal
        if (linksFound == 0) {
            val mainIframe = doc.selectFirst("iframe.metaframe, iframe[src*=viewplayer]")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                
                try {
                    val iframeDoc = app.get(iframeSrc).document
                    iframeDoc.select("button[data-source]").forEach { button ->
                        val source = button.attr("data-source")
                        if (source.isNotEmpty() && loadExtractor(source, data, subtitleCallback, callback)) {
                            linksFound++
                        }
                    }
                } catch (e: Exception) {
                    Log.e("MaxSeries", "Erro no iframe: ${e.message}")
                }
            }
        }'''
        
        return code
    
    def save_analysis_results(self, results, filename='gecko_analysis.json'):
        """Salvar resultados da análise"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Análise salva em {filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
    
    def run_complete_gecko_analysis(self):
        """Executar análise completa com GeckoDriver"""
        logger.info("🚀 Iniciando análise completa com GeckoDriver...")
        
        if not self.setup_driver():
            logger.error("❌ Falha ao configurar GeckoDriver")
            return None
        
        try:
            results = {
                'analysis_timestamp': time.time(),
                'geckodriver_version': 'v0.34.0',
                'base_url': self.base_url
            }
            
            # 1. Analisar homepage
            homepage_analysis = self.analyze_homepage_interactive()
            if homepage_analysis:
                results['homepage_analysis'] = homepage_analysis
                
                # 2. Analisar série de exemplo
                if homepage_analysis['series_links']:
                    sample_series = homepage_analysis['series_links'][0]['href']
                    series_analysis = self.deep_analyze_series_page(sample_series)
                    if series_analysis:
                        results['series_analysis'] = series_analysis
                        
                        # 3. Analisar episódio de exemplo
                        if series_analysis['episodes_analysis']['episode_links']:
                            sample_episode = series_analysis['episodes_analysis']['episode_links'][0]['url']
                            episode_analysis = self.analyze_episode_page_interactive(sample_episode)
                            if episode_analysis:
                                results['episode_analysis'] = episode_analysis
            
            # 4. Gerar código Kotlin avançado
            kotlin_code = self.generate_advanced_kotlin_code(results)
            results['generated_kotlin'] = kotlin_code
            
            # 5. Salvar resultados
            self.save_analysis_results(results)
            
            # 6. Salvar código Kotlin
            with open('MaxSeriesGeckoAdvanced.kt', 'w', encoding='utf-8') as f:
                f.write(kotlin_code)
            
            logger.info("✅ Análise completa com GeckoDriver concluída!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return None
        
        finally:
            self.close_driver()
    
    def close_driver(self):
        """Fechar GeckoDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 GeckoDriver fechado")

def main():
    """Função principal"""
    print("🦎 SCRAPER AVANÇADO MAXSERIES COM GECKODRIVER")
    print("=" * 60)
    
    # Verificar se GeckoDriver existe
    import os
    if not os.path.exists("D:\\geckodriver.exe"):
        print("❌ GeckoDriver não encontrado em D:\\geckodriver.exe")
        print("📥 Baixe em: https://github.com/mozilla/geckodriver/releases")
        print("🔧 Ou execute: setup-firefox-geckodriver.ps1")
        return
    
    # Verificar se Firefox está instalado
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Mozilla Firefox\firefox.exe")
    ]
    
    firefox_found = any(os.path.exists(path) for path in firefox_paths)
    
    if not firefox_found:
        print("❌ Firefox não encontrado")
        print("🔧 Execute: setup-firefox-geckodriver.ps1 para instalar")
        print("📥 Ou baixe manualmente: https://www.mozilla.org/firefox/")
        print("🔄 Alternativa: use gecko-simulation-scraper.py (sem Firefox)")
        
        # Oferecer opção de usar simulação
        try:
            choice = input("\n🤔 Usar simulação sem Firefox? (s/n): ").lower()
            if choice in ['s', 'sim', 'y', 'yes']:
                print("🔄 Executando simulação...")
                os.system("python gecko-simulation-scraper.py")
                return
        except KeyboardInterrupt:
            print("\n⚠️ Cancelado pelo usuário")
            return
        
        return
    
    scraper = GeckoAdvancedScraper(headless=False)  # Modo visual para debug
    
    try:
        results = scraper.run_complete_gecko_analysis()
        
        if results:
            print("\n📊 RESUMO DA ANÁLISE GECKODRIVER:")
            
            if 'homepage_analysis' in results:
                homepage = results['homepage_analysis']
                print(f"🏠 Homepage: {homepage['title']}")
                print(f"📺 Séries encontradas: {len(homepage['series_links'])}")
                print(f"🎬 Filmes encontrados: {len(homepage['movie_links'])}")
            
            if 'series_analysis' in results:
                series = results['series_analysis']
                print(f"📺 Série analisada: {series['title']}")
                print(f"🎬 Temporadas: {len(series['seasons_analysis']['dooplay_seasons'])}")
                print(f"📺 Episódios: {len(series['episodes_analysis']['episode_links'])}")
                print(f"🎮 Players: {len(series['player_analysis']['data_source_buttons'])}")
                print(f"🖱️ Interações: {len(series['interaction_results']['clicked_elements'])}")
            
            print("\n📄 ARQUIVOS GERADOS:")
            print("  - gecko_analysis.json (análise completa)")
            print("  - MaxSeriesGeckoAdvanced.kt (código Kotlin)")
            
            print("\n🎯 PRÓXIMOS PASSOS:")
            print("1. Revise o código em MaxSeriesGeckoAdvanced.kt")
            print("2. Substitua o código atual do MaxSeries")
            print("3. Teste no CloudStream")
            
        else:
            print("❌ Análise falhou")
            print("🔄 Tente a simulação: python gecko-simulation-scraper.py")
            
    except KeyboardInterrupt:
        print("\n⚠️ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔄 Tente a simulação: python gecko-simulation-scraper.py")
    
    finally:
        if scraper.driver:
            scraper.close_driver()

if __name__ == "__main__":
    main()