#!/usr/bin/env python3
"""
Análise Direcionada - MaxSeries
Análise específica de uma série para entender estrutura de episódios
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

class TargetedMaxSeriesAnalyzer:
    def __init__(self, geckodriver_path="D:\\geckodriver.exe"):
        self.geckodriver_path = geckodriver_path
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configurar Firefox com GeckoDriver"""
        logger.info("🦎 Configurando GeckoDriver...")
        
        service = Service(executable_path=self.geckodriver_path)
        options = Options()
        
        # Configurar Firefox
        firefox_binary = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        if os.path.exists(firefox_binary):
            options.binary_location = firefox_binary
            logger.info(f"🔍 Firefox encontrado: {firefox_binary}")
        else:
            logger.error(f"❌ Firefox não encontrado")
            return False
        
        # Configurações
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
    
    def analyze_specific_series(self, series_url):
        """Analisar série específica"""
        logger.info(f"📺 Analisando série: {series_url}")
        
        try:
            self.driver.get(series_url)
            time.sleep(5)
            
            analysis = {
                'url': series_url,
                'title': self.get_title(),
                'description': self.get_description(),
                'poster': self.get_poster(),
                'seasons': self.analyze_seasons(),
                'episodes': self.analyze_episodes(),
                'players': self.analyze_players(),
                'iframes': self.analyze_iframes()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return None
    
    def get_title(self):
        """Extrair título"""
        selectors = ['.data h1', 'h1', '.entry-title', '.post-title']
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return element.text.strip()
            except:
                continue
        
        return self.driver.title
    
    def get_description(self):
        """Extrair descrição"""
        selectors = ['.sinopse', '.entry-content', '.wp-content', '.description']
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return element.text.strip()[:500]
            except:
                continue
        
        return 'Descrição não encontrada'
    
    def get_poster(self):
        """Extrair poster"""
        selectors = ['.poster img', '.wp-post-image', '.movie-poster img']
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                src = element.get_attribute('src') or element.get_attribute('data-src')
                if src:
                    return src
            except:
                continue
        
        return None
    
    def analyze_seasons(self):
        """Analisar temporadas"""
        logger.info("🎬 Analisando temporadas...")
        
        seasons_data = {
            'dooplay_seasons': [],
            'season_tabs': [],
            'total_seasons': 0
        }
        
        try:
            # Método 1: DooPlay padrão
            seasons = self.driver.find_elements(By.CSS_SELECTOR, 'div.se-c')
            logger.info(f"🔍 Encontradas {len(seasons)} temporadas (div.se-c)")
            
            for i, season in enumerate(seasons):
                season_info = {
                    'index': i,
                    'id': season.get_attribute('id'),
                    'class': season.get_attribute('class'),
                    'visible': season.is_displayed(),
                    'episodes_in_season': len(season.find_elements(By.CSS_SELECTOR, 'ul.episodios li'))
                }
                seasons_data['dooplay_seasons'].append(season_info)
                logger.info(f"  Temporada {i}: {season_info['episodes_in_season']} episódios")
            
            seasons_data['total_seasons'] = len(seasons)
            
            # Método 2: Tabs de temporadas
            season_tabs = self.driver.find_elements(By.CSS_SELECTOR, '.season-tab, [data-season]')
            for tab in season_tabs:
                seasons_data['season_tabs'].append({
                    'text': tab.text.strip(),
                    'data_season': tab.get_attribute('data-season'),
                    'visible': tab.is_displayed()
                })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de temporadas: {e}")
        
        return seasons_data
    
    def analyze_episodes(self):
        """Analisar episódios"""
        logger.info("📺 Analisando episódios...")
        
        episodes_data = {
            'episode_links': [],
            'total_episodes': 0,
            'selectors_tested': []
        }
        
        # Múltiplos seletores para testar
        episode_selectors = [
            'ul.episodios li a',
            '.episodios a',
            '.episode-list a',
            'li[data-episode] a',
            'a[href*="episodio"]',
            'a[href*="episode"]',
            '.se-c ul.episodios li a'
        ]
        
        for selector in episode_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                episodes_data['selectors_tested'].append({
                    'selector': selector,
                    'count': len(elements)
                })
                
                if elements:
                    logger.info(f"🔍 Seletor '{selector}': {len(elements)} episódios")
                    
                    for i, element in enumerate(elements[:20]):  # Primeiros 20
                        try:
                            episode_info = {
                                'index': i,
                                'title': element.text.strip(),
                                'href': element.get_attribute('href'),
                                'visible': element.is_displayed(),
                                'selector_used': selector
                            }
                            
                            # Tentar extrair número do episódio
                            episode_info['episode_number'] = self.extract_episode_number(element)
                            episode_info['season_number'] = self.extract_season_number(element)
                            
                            episodes_data['episode_links'].append(episode_info)
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Erro no episódio {i}: {e}")
                    
                    episodes_data['total_episodes'] = len(elements)
                    break  # Usar primeiro seletor que funcionar
                    
            except Exception as e:
                logger.warning(f"⚠️ Seletor '{selector}' falhou: {e}")
        
        return episodes_data
    
    def extract_episode_number(self, element):
        """Extrair número do episódio"""
        try:
            # Método 1: .numerando
            try:
                parent = element.find_element(By.XPATH, '..')
                numerando = parent.find_element(By.CSS_SELECTOR, '.numerando')
                numerando_text = numerando.text
                match = re.search(r'(\d+)\s*-\s*(\d+)|E(\d+)', numerando_text)
                if match:
                    return int(match.group(2) or match.group(3))
            except:
                pass
            
            # Método 2: Texto do elemento
            text = element.text
            ep_match = re.search(r'episódio\s*(\d+)|episode\s*(\d+)|ep\s*(\d+)', text, re.IGNORECASE)
            if ep_match:
                return int(ep_match.group(1) or ep_match.group(2) or ep_match.group(3))
            
            # Método 3: URL
            href = element.get_attribute('href') or ''
            url_match = re.search(r'episodio-(\d+)|episode-(\d+)', href)
            if url_match:
                return int(url_match.group(1) or url_match.group(2))
            
        except:
            pass
        
        return None
    
    def extract_season_number(self, element):
        """Extrair número da temporada"""
        try:
            # Procurar elemento pai de temporada
            season_parent = element.find_element(By.XPATH, './ancestor::*[@class="se-c"]')
            season_id = season_parent.get_attribute('id')
            if 'season-' in season_id:
                return int(season_id.replace('season-', ''))
        except:
            pass
        
        return 1
    
    def analyze_players(self):
        """Analisar players"""
        logger.info("🎮 Analisando players...")
        
        players_data = {
            'data_source_buttons': [],
            'ajax_options': [],
            'player_buttons': []
        }
        
        try:
            # Botões com data-source
            data_source_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-source], .btn[data-source]')
            logger.info(f"🔍 Botões data-source: {len(data_source_buttons)}")
            
            for button in data_source_buttons:
                players_data['data_source_buttons'].append({
                    'text': button.text.strip(),
                    'data_source': button.get_attribute('data-source'),
                    'data_type': button.get_attribute('data-type'),
                    'visible': button.is_displayed(),
                    'enabled': button.is_enabled()
                })
            
            # Opções AJAX DooPlay
            ajax_options = self.driver.find_elements(By.CSS_SELECTOR, '#playeroptionsul li, .playeroptionsul li')
            logger.info(f"🔍 Opções AJAX: {len(ajax_options)}")
            
            for option in ajax_options:
                players_data['ajax_options'].append({
                    'text': option.text.strip(),
                    'data_post': option.get_attribute('data-post'),
                    'data_nume': option.get_attribute('data-nume'),
                    'data_type': option.get_attribute('data-type')
                })
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de players: {e}")
        
        return players_data
    
    def analyze_iframes(self):
        """Analisar iframes"""
        logger.info("🖼️ Analisando iframes...")
        
        iframes_data = {
            'iframes': [],
            'total_iframes': 0
        }
        
        try:
            iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
            logger.info(f"🔍 Iframes encontrados: {len(iframes)}")
            
            for i, iframe in enumerate(iframes):
                iframe_info = {
                    'index': i,
                    'src': iframe.get_attribute('src'),
                    'class': iframe.get_attribute('class'),
                    'id': iframe.get_attribute('id'),
                    'visible': iframe.is_displayed(),
                    'size': iframe.size
                }
                iframes_data['iframes'].append(iframe_info)
                logger.info(f"  Iframe {i}: {iframe_info['src']}")
            
            iframes_data['total_iframes'] = len(iframes)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de iframes: {e}")
        
        return iframes_data
    
    def close_driver(self):
        """Fechar driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 GeckoDriver fechado")

def main():
    print("🎯 ANÁLISE DIRECIONADA MAXSERIES")
    print("=" * 50)
    
    # Séries encontradas na análise anterior
    series_urls = [
        "https://www.maxseries.one/series/assistir-terra-de-pecados-online",
        "https://www.maxseries.one/series/assistir-meu-namorado-coreano-online",
        "https://www.maxseries.one/series/assistir-o-tempo-das-moscas-online"
    ]
    
    analyzer = TargetedMaxSeriesAnalyzer()
    
    if not analyzer.setup_driver():
        print("❌ Falha ao configurar GeckoDriver")
        return
    
    try:
        all_results = {}
        
        for i, series_url in enumerate(series_urls[:2]):  # Analisar primeiras 2
            print(f"\n📺 ANALISANDO SÉRIE {i+1}: {series_url}")
            
            result = analyzer.analyze_specific_series(series_url)
            if result:
                all_results[f'series_{i+1}'] = result
                
                print(f"✅ Título: {result['title']}")
                print(f"🎬 Temporadas: {result['seasons']['total_seasons']}")
                print(f"📺 Episódios: {result['episodes']['total_episodes']}")
                print(f"🎮 Players data-source: {len(result['players']['data_source_buttons'])}")
                print(f"🖼️ Iframes: {result['iframes']['total_iframes']}")
        
        # Salvar resultados
        with open('targeted_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análise salva em: targeted_analysis.json")
        
        # Gerar código Kotlin baseado nos resultados
        if all_results:
            generate_improved_kotlin(all_results)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        analyzer.close_driver()

def generate_improved_kotlin(analysis_results):
    """Gerar código Kotlin melhorado baseado na análise direcionada"""
    print("\n🔧 Gerando código Kotlin melhorado...")
    
    # Analisar dados coletados
    total_episodes = 0
    total_players = 0
    episode_selectors = []
    
    for series_key, series_data in analysis_results.items():
        total_episodes += series_data['episodes']['total_episodes']
        total_players += len(series_data['players']['data_source_buttons'])
        
        for selector_info in series_data['episodes']['selectors_tested']:
            if selector_info['count'] > 0:
                episode_selectors.append(selector_info['selector'])
    
    # Seletor mais eficaz
    best_selector = episode_selectors[0] if episode_selectors else 'ul.episodios li a'
    
    kotlin_code = f'''package com.franciscoalro.maxseries

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.ExtractorLink
import com.lagradost.cloudstream3.utils.loadExtractor
import com.lagradost.cloudstream3.utils.Qualities
import android.util.Log

// Gerado por análise direcionada GeckoDriver
// Séries analisadas: {len(analysis_results)}
// Total episódios detectados: {total_episodes}
// Total players detectados: {total_players}
// Melhor seletor: {best_selector}

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
            
            Log.d("MaxSeries", "📺 Processando série (Análise Direcionada): $title")
            
            // Método baseado na análise direcionada
            doc.select("{best_selector}").forEachIndexed {{ index, element ->
                val epTitle = element.text().trim()
                val epHref = element.attr("href")
                
                if (epHref.isNotEmpty()) {{
                    // Extrair número do episódio
                    val epNum = extractEpisodeNumberAdvanced(element, index + 1)
                    val seasonNum = extractSeasonNumberAdvanced(element, 1)
                    
                    episodes.add(newEpisode(epHref) {{
                        this.name = if (epTitle.isNotEmpty()) epTitle else "Episódio $epNum"
                        this.episode = epNum
                        this.season = seasonNum
                    }})
                    
                    Log.d("MaxSeries", "✅ Episódio: T${{seasonNum}}E${{epNum}} - $epTitle")
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
            
            Log.d("MaxSeries", "✅ Total: ${{episodes.size}} episódios")

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

    private fun extractEpisodeNumberAdvanced(element: Element, fallback: Int): Int {{
        // Método 1: .numerando
        try {{
            val numerando = element.parent()?.selectFirst(".numerando")?.text()
            if (numerando != null) {{
                val match = Regex("""(\\d+)\\s*-\\s*(\\d+)|E(\\d+)""").find(numerando)
                if (match != null) {{
                    return (match.groupValues[2].ifEmpty {{ match.groupValues[3] }}).toInt()
                }}
            }}
        }} catch (e: Exception) {{ }}
        
        // Método 2: Texto do elemento
        try {{
            val text = element.text()
            val match = Regex("""episódio\\s*(\\d+)|episode\\s*(\\d+)|ep\\s*(\\d+)""", RegexOption.IGNORE_CASE).find(text)
            if (match != null) {{
                return (match.groupValues[1].ifEmpty {{ match.groupValues[2].ifEmpty {{ match.groupValues[3] }} }}).toInt()
            }}
        }} catch (e: Exception) {{ }}
        
        // Método 3: URL
        try {{
            val href = element.attr("href")
            val match = Regex("""episodio-(\\d+)|episode-(\\d+)""").find(href)
            if (match != null) {{
                return (match.groupValues[1].ifEmpty {{ match.groupValues[2] }}).toInt()
            }}
        }} catch (e: Exception) {{ }}
        
        return fallback
    }}

    private fun extractSeasonNumberAdvanced(element: Element, fallback: Int): Int {{
        try {{
            val seasonParent = element.parents().find {{ it.hasClass("se-c") }}
            if (seasonParent != null) {{
                val seasonId = seasonParent.id()
                if (seasonId.startsWith("season-")) {{
                    return seasonId.replace("season-", "").toInt()
                }}
            }}
        }} catch (e: Exception) {{ }}
        
        return fallback
    }}

    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {{
        Log.d("MaxSeries", "📺 Processando links (Análise Direcionada): $data")
        
        var linksFound = 0
        val doc = app.get(data).document
        
        // Método 1: Botões data-source (confirmado pela análise)
        doc.select("button[data-source], .btn[data-source]").forEach {{ button ->
            val source = button.attr("data-source")
            val playerName = button.text().trim()
            
            if (source.isNotEmpty() && source.startsWith("http")) {{
                Log.d("MaxSeries", "🎯 Player detectado: $playerName -> $source")
                
                try {{
                    if (loadExtractor(source, data, subtitleCallback, callback)) {{
                        linksFound++
                        Log.d("MaxSeries", "✅ Sucesso: $playerName")
                    }}
                }} catch (e: Exception) {{
                    Log.e("MaxSeries", "❌ Erro player $playerName: ${{e.message}}")
                }}
            }}
        }}
        
        // Método 2: Iframe principal
        if (linksFound == 0) {{
            Log.d("MaxSeries", "🔄 Tentando iframe principal")
            
            val mainIframe = doc.selectFirst("iframe.metaframe, iframe[src*=viewplayer], iframe[src*=embed]")?.attr("src")
            if (!mainIframe.isNullOrEmpty()) {{
                val iframeSrc = if (mainIframe.startsWith("//")) "https:$mainIframe" else mainIframe
                
                try {{
                    if (loadExtractor(iframeSrc, data, subtitleCallback, callback)) {{
                        linksFound++
                    }}
                }} catch (e: Exception) {{
                    Log.e("MaxSeries", "❌ Erro iframe: ${{e.message}}")
                }}
            }}
        }}
        
        // Método 3: AJAX DooPlay (fallback)
        if (linksFound == 0) {{
            Log.d("MaxSeries", "🔄 Tentando AJAX DooPlay")
            
            doc.select("#playeroptionsul li, .playeroptionsul li").forEach {{ option ->
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
                        val iframeRegex = Regex(\"\"\"src=["']([^"']+)["']\"\"\")
                        val iframeMatch = iframeRegex.find(ajaxResponse)
                        
                        if (iframeMatch != null) {{
                            val iframeUrl = iframeMatch.groupValues[1]
                            val cleanUrl = if (iframeUrl.startsWith("//")) "https:$iframeUrl" else iframeUrl
                            
                            if (loadExtractor(cleanUrl, data, subtitleCallback, callback)) {{
                                linksFound++
                            }}
                        }}
                    }} catch (e: Exception) {{
                        Log.e("MaxSeries", "❌ Erro AJAX: ${{e.message}}")
                    }}
                }}
            }}
        }}
        
        Log.d("MaxSeries", "✅ Total links encontrados: $linksFound")
        return linksFound > 0
    }}
}}'''
    
    with open('MaxSeriesTargetedAnalysis.kt', 'w', encoding='utf-8') as f:
        f.write(kotlin_code)
    
    print("✅ Código Kotlin salvo em: MaxSeriesTargetedAnalysis.kt")

if __name__ == "__main__":
    main()