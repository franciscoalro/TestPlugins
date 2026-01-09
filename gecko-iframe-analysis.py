#!/usr/bin/env python3
"""
Análise de Iframes - MaxSeries
Análise específica dos iframes playerthree.online para encontrar episódios
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IframeAnalyzer:
    def __init__(self, geckodriver_path="D:\\geckodriver.exe"):
        self.geckodriver_path = geckodriver_path
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configurar Firefox com GeckoDriver"""
        logger.info("🦎 Configurando GeckoDriver...")
        
        service = Service(executable_path=self.geckodriver_path)
        options = Options()
        
        firefox_binary = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        if os.path.exists(firefox_binary):
            options.binary_location = firefox_binary
            logger.info(f"🔍 Firefox encontrado: {firefox_binary}")
        else:
            logger.error(f"❌ Firefox não encontrado")
            return False
        
        options.add_argument('--window-size=1920,1080')
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("✅ GeckoDriver iniciado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def analyze_iframe_content(self, iframe_url):
        """Analisar conteúdo do iframe"""
        logger.info(f"🖼️ Analisando iframe: {iframe_url}")
        
        try:
            self.driver.get(iframe_url)
            time.sleep(5)
            
            analysis = {
                'url': iframe_url,
                'title': self.driver.title,
                'page_source_length': len(self.driver.page_source),
                'episodes': self.find_episodes_in_iframe(),
                'seasons': self.find_seasons_in_iframe(),
                'players': self.find_players_in_iframe(),
                'navigation': self.find_navigation_in_iframe(),
                'javascript': self.analyze_javascript_in_iframe()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise do iframe: {e}")
            return None
    
    def find_episodes_in_iframe(self):
        """Encontrar episódios no iframe"""
        logger.info("📺 Procurando episódios no iframe...")
        
        episodes_data = {
            'episode_links': [],
            'episode_buttons': [],
            'episode_navigation': [],
            'selectors_tested': []
        }
        
        # Seletores específicos para playerthree.online
        episode_selectors = [
            'li[data-season-id][data-episode-id] a',
            'li[data-episode-id] a',
            '.header-navigation li a',
            '.episode-list li a',
            'ul li[data-season-id] a',
            'a[href*="#"]',
            '.navigation li a',
            'button[data-episode]',
            '.episode-item a'
        ]
        
        for selector in episode_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                episodes_data['selectors_tested'].append({
                    'selector': selector,
                    'count': len(elements)
                })
                
                if elements:
                    logger.info(f"🔍 Seletor '{selector}': {len(elements)} elementos")
                    
                    for i, element in enumerate(elements[:20]):  # Primeiros 20
                        try:
                            episode_info = {
                                'index': i,
                                'text': element.text.strip(),
                                'href': element.get_attribute('href'),
                                'data_season_id': element.get_attribute('data-season-id'),
                                'data_episode_id': element.get_attribute('data-episode-id'),
                                'data_season_number': element.get_attribute('data-season-number'),
                                'visible': element.is_displayed(),
                                'selector_used': selector
                            }
                            
                            episodes_data['episode_links'].append(episode_info)
                            logger.info(f"  Episódio {i}: {episode_info['text']} (Season: {episode_info['data_season_id']}, Episode: {episode_info['data_episode_id']})")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Erro no elemento {i}: {e}")
                    
                    break  # Usar primeiro seletor que funcionar
                    
            except Exception as e:
                logger.warning(f"⚠️ Seletor '{selector}' falhou: {e}")
        
        return episodes_data
    
    def find_seasons_in_iframe(self):
        """Encontrar temporadas no iframe"""
        logger.info("🎬 Procurando temporadas no iframe...")
        
        seasons_data = {
            'season_navigation': [],
            'season_buttons': [],
            'selectors_tested': []
        }
        
        season_selectors = [
            'ul.header-navigation li[data-season-id]',
            '.season-navigation li',
            'button[data-season]',
            '.season-tab',
            'li[data-season-number]'
        ]
        
        for selector in season_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                seasons_data['selectors_tested'].append({
                    'selector': selector,
                    'count': len(elements)
                })
                
                if elements:
                    logger.info(f"🔍 Temporadas '{selector}': {len(elements)} elementos")
                    
                    for i, element in enumerate(elements):
                        try:
                            season_info = {
                                'index': i,
                                'text': element.text.strip(),
                                'data_season_id': element.get_attribute('data-season-id'),
                                'data_season_number': element.get_attribute('data-season-number'),
                                'visible': element.is_displayed()
                            }
                            
                            seasons_data['season_navigation'].append(season_info)
                            logger.info(f"  Temporada {i}: {season_info['text']} (ID: {season_info['data_season_id']}, Num: {season_info['data_season_number']})")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Erro na temporada {i}: {e}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Seletor temporadas '{selector}' falhou: {e}")
        
        return seasons_data
    
    def find_players_in_iframe(self):
        """Encontrar players no iframe"""
        logger.info("🎮 Procurando players no iframe...")
        
        players_data = {
            'player_buttons': [],
            'data_source_buttons': [],
            'selectors_tested': []
        }
        
        player_selectors = [
            'button[data-source]',
            '.btn[data-source]',
            'button[data-show-player]',
            '.player-option',
            '#players button',
            '.choose-player button'
        ]
        
        for selector in player_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                players_data['selectors_tested'].append({
                    'selector': selector,
                    'count': len(elements)
                })
                
                if elements:
                    logger.info(f"🔍 Players '{selector}': {len(elements)} elementos")
                    
                    for i, element in enumerate(elements):
                        try:
                            player_info = {
                                'index': i,
                                'text': element.text.strip(),
                                'data_source': element.get_attribute('data-source'),
                                'data_show_player': element.get_attribute('data-show-player'),
                                'data_type': element.get_attribute('data-type'),
                                'visible': element.is_displayed(),
                                'enabled': element.is_enabled()
                            }
                            
                            players_data['player_buttons'].append(player_info)
                            logger.info(f"  Player {i}: {player_info['text']} -> {player_info['data_source']}")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Erro no player {i}: {e}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Seletor players '{selector}' falhou: {e}")
        
        return players_data
    
    def find_navigation_in_iframe(self):
        """Encontrar navegação no iframe"""
        logger.info("🧭 Procurando navegação no iframe...")
        
        nav_data = {
            'navigation_elements': [],
            'clickable_elements': []
        }
        
        try:
            # Procurar elementos de navegação
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 'nav, .navigation, .header-navigation, ul.header-navigation')
            
            for i, nav in enumerate(nav_elements):
                nav_links = nav.find_elements(By.TAG_NAME, 'a')
                nav_buttons = nav.find_elements(By.TAG_NAME, 'button')
                nav_lis = nav.find_elements(By.TAG_NAME, 'li')
                
                nav_info = {
                    'index': i,
                    'class': nav.get_attribute('class'),
                    'id': nav.get_attribute('id'),
                    'links_count': len(nav_links),
                    'buttons_count': len(nav_buttons),
                    'list_items_count': len(nav_lis)
                }
                
                nav_data['navigation_elements'].append(nav_info)
                logger.info(f"  Nav {i}: {nav_info['links_count']} links, {nav_info['buttons_count']} botões, {nav_info['list_items_count']} itens")
            
            # Procurar elementos clicáveis
            clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a, button, [onclick], [data-toggle]')
            nav_data['clickable_elements'] = len(clickable_elements)
            logger.info(f"🖱️ Total elementos clicáveis: {len(clickable_elements)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de navegação: {e}")
        
        return nav_data
    
    def analyze_javascript_in_iframe(self):
        """Analisar JavaScript no iframe"""
        logger.info("📜 Analisando JavaScript no iframe...")
        
        js_data = {
            'scripts_count': 0,
            'external_scripts': [],
            'gleam_detected': False,
            'video_urls': [],
            'config_objects': []
        }
        
        try:
            scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script')
            js_data['scripts_count'] = len(scripts)
            
            for script in scripts:
                src = script.get_attribute('src')
                if src:
                    js_data['external_scripts'].append(src)
                
                content = script.get_attribute('innerHTML') or ''
                
                # Procurar gleam.config
                if 'gleam.config' in content:
                    js_data['gleam_detected'] = True
                    logger.info("🎯 gleam.config detectado!")
                
                # Procurar URLs de vídeo
                video_patterns = [
                    r'https?://[^"\s]+\.(?:m3u8|mp4|mkv|avi)',
                    r'"file"\s*:\s*"([^"]+)"',
                    r'"source"\s*:\s*"([^"]+)"'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, content)
                    js_data['video_urls'].extend(matches)
            
            # Tentar executar JavaScript para obter configurações
            try:
                gleam_config = self.driver.execute_script("return typeof gleam !== 'undefined' ? gleam.config : null;")
                if gleam_config:
                    js_data['config_objects'].append({'type': 'gleam', 'config': gleam_config})
                    logger.info("✅ Configuração gleam obtida via JavaScript")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao executar JavaScript: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de JavaScript: {e}")
        
        return js_data
    
    def close_driver(self):
        """Fechar driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 GeckoDriver fechado")

def main():
    print("🖼️ ANÁLISE DE IFRAMES MAXSERIES")
    print("=" * 50)
    
    # URLs dos iframes encontrados na análise anterior
    iframe_urls = [
        "https://playerthree.online/embed/synden/",
        "https://playerthree.online/embed/meu-namorado-coreano/"
    ]
    
    analyzer = IframeAnalyzer()
    
    if not analyzer.setup_driver():
        print("❌ Falha ao configurar GeckoDriver")
        return
    
    try:
        all_results = {}
        
        for i, iframe_url in enumerate(iframe_urls):
            print(f"\n🖼️ ANALISANDO IFRAME {i+1}: {iframe_url}")
            
            result = analyzer.analyze_iframe_content(iframe_url)
            if result:
                all_results[f'iframe_{i+1}'] = result
                
                print(f"✅ Título: {result['title']}")
                print(f"📺 Episódios encontrados: {len(result['episodes']['episode_links'])}")
                print(f"🎬 Temporadas encontradas: {len(result['seasons']['season_navigation'])}")
                print(f"🎮 Players encontrados: {len(result['players']['player_buttons'])}")
                print(f"📜 Scripts: {result['javascript']['scripts_count']}")
                print(f"🎯 Gleam detectado: {result['javascript']['gleam_detected']}")
        
        # Salvar resultados
        with open('iframe_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análise salva em: iframe_analysis.json")
        
        # Gerar código Kotlin baseado nos resultados dos iframes
        if all_results:
            generate_iframe_based_kotlin(all_results)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        analyzer.close_driver()

def generate_iframe_based_kotlin(iframe_results):
    """Gerar código Kotlin baseado na análise dos iframes"""
    print("\n🔧 Gerando código Kotlin baseado nos iframes...")
    
    # Analisar dados dos iframes
    total_episodes = 0
    total_players = 0
    episode_selectors = []
    player_selectors = []
    
    for iframe_key, iframe_data in iframe_results.items():
        total_episodes += len(iframe_data['episodes']['episode_links'])
        total_players += len(iframe_data['players']['player_buttons'])
        
        # Encontrar seletores que funcionaram
        for selector_info in iframe_data['episodes']['selectors_tested']:
            if selector_info['count'] > 0:
                episode_selectors.append(selector_info['selector'])
        
        for selector_info in iframe_data['players']['selectors_tested']:
            if selector_info['count'] > 0:
                player_selectors.append(selector_info['selector'])
    
    # Seletores mais eficazes
    best_episode_selector = episode_selectors[0] if episode_selectors else 'li[data-season-id][data-episode-id] a'
    best_player_selector = player_selectors[0] if player_selectors else 'button[data-source]'
    
    kotlin_code = f'''package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// Gerado por análise de iframes GeckoDriver
// Iframes analisados: {len(iframe_results)}
// Total episódios detectados: {total_episodes}
// Total players detectados: {total_players}
// Melhor seletor episódios: {best_episode_selector}
// Melhor seletor players: {best_player_selector}

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
            
            Log.d("MaxSeries", "📺 Processando série (Análise Iframe): $title")
            
            // Método baseado na análise de iframes
            val mainIframe = doc.selectFirst("iframe")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {{
                try {{
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "🖼️ Carregando iframe: $iframeSrc")
                    
                    val iframeDoc = app.get(iframeSrc).document
                    
                    // Extrair temporadas da navegação
                    val seasons = mutableMapOf<String, Int>()
                    iframeDoc.select("ul.header-navigation li[data-season-id]").forEach {{ seasonLi ->
                        val seasonId = seasonLi.attr("data-season-id")
                        val seasonNumber = seasonLi.attr("data-season-number").toIntOrNull() ?: 1
                        if (seasonId.isNotEmpty()) {{
                            seasons[seasonId] = seasonNumber
                            Log.d("MaxSeries", "🎬 Temporada: $seasonNumber (ID: $seasonId)")
                        }}
                    }}
                    
                    // Extrair episódios com dados reais de temporada/episódio
                    iframeDoc.select("{best_episode_selector}").forEach {{ epLi ->
                        val seasonId = epLi.attr("data-season-id")
                        val episodeId = epLi.attr("data-episode-id")
                        val epLink = epLi.selectFirst("a") ?: epLi
                        
                        if (seasonId.isNotEmpty() && episodeId.isNotEmpty()) {{
                            val epTitle = epLink.text().trim()
                            val epHref = epLink.attr("href") // Formato: #12956_255628
                            
                            // Extrair número do episódio do título (formato: "1 - Título do Episódio")
                            val epNum = epTitle.split(" - ").firstOrNull()?.trim()?.toIntOrNull() ?: 1
                            val seasonNum = seasons[seasonId] ?: 1
                            
                            // Criar URL do episódio que inclui o iframe URL e referência do episódio
                            val episodeUrl = "$iframeSrc$epHref"
                            
                            episodes.add(newEpisode(episodeUrl) {{
                                this.name = epTitle
                                this.episode = epNum
                                this.season = seasonNum
                            }})
                            
                            Log.d("MaxSeries", "✅ Episódio: T${{seasonNum}}E${{epNum}} - $epTitle")
                        }}
                    }}
                    
                }} catch (e: Exception) {{
                    Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${{e.message}}")
                }}
            }}
            
            // Fallback se nenhum episódio for encontrado
            if (episodes.isEmpty()) {{
                Log.d("MaxSeries", "⚠️ Fallback: criando episódio único")
                episodes.add(newEpisode(url) {{
                    this.name = "Episódio 1"
                    this.episode = 1
                    this.season = 1
                }})
            }}
            
            Log.d("MaxSeries", "✅ Total: ${{episodes.size}} episódios em ${{episodes.map {{ it.season }}.distinct().size}} temporadas")

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
        Log.d("MaxSeries", "📺 Processando links (Análise Iframe): $data")
        
        var linksFound = 0
        
        try {{
            // Verificar se é uma URL de episódio do iframe (contém #)
            if (data.contains("#")) {{
                Log.d("MaxSeries", "🎯 Processando episódio do iframe")
                
                // Carregar a página do iframe com o fragmento do episódio
                val doc = app.get(data).document
                
                // Procurar botões de seleção de player (como "Player #1", "Player #2")
                val playerButtons = doc.select("{best_player_selector}")
                
                if (playerButtons.isNotEmpty()) {{
                    Log.d("MaxSeries", "🎮 Encontrados ${{playerButtons.size}} players")
                    
                    playerButtons.forEach {{ button ->
                        val playerName = button.text().trim()
                        Log.d("MaxSeries", "🔄 Testando player: $playerName")
                        
                        try {{
                            // Procurar atributos de dados que podem conter informações do vídeo
                            val dataSource = button.attr("data-source")
                            val dataUrl = button.attr("data-url")
                            val dataPlayer = button.attr("data-player")
                            
                            val videoUrl = dataSource.ifEmpty {{ dataUrl.ifEmpty {{ dataPlayer }} }}
                            
                            if (videoUrl.isNotEmpty() && videoUrl.startsWith("http")) {{
                                Log.d("MaxSeries", "🎯 URL encontrada no botão: $videoUrl")
                                
                                if (loadExtractor(videoUrl, data, subtitleCallback, callback)) {{
                                    linksFound++
                                }}
                            }}
                            
                        }} catch (e: Exception) {{
                            Log.e("MaxSeries", "❌ Erro ao processar player $playerName: ${{e.message}}")
                        }}
                    }}
                }}
                
                // Procurar gleam.config nos scripts (como mostrado no HTML)
                doc.select("script").forEach {{ script ->
                    val scriptContent = script.html()
                    
                    if (scriptContent.contains("gleam.config", ignoreCase = true)) {{
                        Log.d("MaxSeries", "🎬 Script gleam.config encontrado")
                        
                        // Extrair URL do gleam.config
                        val gleamUrlRegex = Regex(\"\"\"\"url\"\\s*:\\s*\"([^\"]+)\"\"\")
                        val gleamMatch = gleamUrlRegex.find(scriptContent)
                        
                        if (gleamMatch != null) {{
                            val gleamUrl = gleamMatch.groupValues[1].replace("\\\\/", "/")
                            Log.d("MaxSeries", "🎯 Gleam URL: $gleamUrl")
                            
                            if (gleamUrl.startsWith("http")) {{
                                try {{
                                    if (loadExtractor(gleamUrl, data, subtitleCallback, callback)) {{
                                        linksFound++
                                    }}
                                }} catch (e: Exception) {{
                                    Log.e("MaxSeries", "❌ Erro ao processar gleam URL: ${{e.message}}")
                                }}
                            }}
                        }}
                    }}
                }}
                
            }} else {{
                // Processamento padrão para URLs que não são de iframe
                Log.d("MaxSeries", "🔄 Processamento padrão")
                val doc = app.get(data).document
                
                val mainIframe = doc.selectFirst("iframe")?.attr("src")
                if (!mainIframe.isNullOrEmpty()) {{
                    val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                    Log.d("MaxSeries", "📺 Carregando iframe principal: $iframeSrc")
                    
                    try {{
                        if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {{
                            linksFound++
                        }}
                    }} catch (e: Exception) {{
                        Log.e("MaxSeries", "❌ Erro ao carregar iframe: ${{e.message}}")
                    }}
                }}
            }}
            
        }} catch (e: Exception) {{
            Log.e("MaxSeries", "❌ Erro geral no loadLinks: ${{e.message}}")
        }}
        
        Log.d("MaxSeries", "✅ Total de links encontrados: $linksFound")
        return linksFound > 0
    }}
}}'''
    
    with open('MaxSeriesIframeAnalysis.kt', 'w', encoding='utf-8') as f:
        f.write(kotlin_code)
    
    print("✅ Código Kotlin salvo em: MaxSeriesIframeAnalysis.kt")

if __name__ == "__main__":
    main()