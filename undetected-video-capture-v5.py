#!/usr/bin/env python3
"""
Captura de URLs de Vídeo - V5 ANTI-DETECÇÃO MÁXIMA
Resolve problema de redirecionamento para abyss.to

Uso: python undetected-video-capture-v5.py [URL]
"""

import json
import time
import random
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@dataclass
class VideoURL:
    url: str
    source_type: str
    quality: Optional[str] = None
    referer: Optional[str] = None


class AntiDetectCapture:
    """Captura com máxima anti-detecção"""
    
    FINAL_VIDEO_PATTERNS = ['.m3u8', '.mp4', '/hls/', 'master', '/video/', '.ts', 
                            'googlevideo', 'akamaized', 'cloudfront', 'storage.googleapis']
    
    IGNORE_PATTERNS = ['google-analytics', 'facebook', '.css', '.js', '.png', '.jpg', 
                       '.gif', '.ico', '.woff', 'mc.yandex', 'cdn-cgi/rum', 'abyss.to']
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        self.headless = headless
        self.verbose = verbose
        self.driver = None
        self.captured_videos: List[VideoURL] = []
        self.current_referer = None
        
    def log(self, msg: str, level: str = "INFO"):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "VIDEO": "🎬", 
                     "WAIT": "⏳", "DEBUG": "🔍", "WARN": "⚠️"}.get(level, "")
            print(f"[{ts}] {emoji} {msg}")
    
    def create_driver(self) -> uc.Chrome:
        """Cria driver com máxima anti-detecção"""
        options = uc.ChromeOptions()
        
        # Configurações básicas
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=pt-BR')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        # Anti-detecção extra
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Logging de rede
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.log("Iniciando Chrome com anti-detecção máxima...")
        
        # Usar versão específica do Chrome se disponível
        driver = uc.Chrome(options=options, version_main=None)
        
        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        # Injetar scripts anti-detecção
        self.inject_anti_detection(driver)
        
        return driver
    
    def inject_anti_detection(self, driver):
        """Injeta scripts para mascarar detecção de Selenium"""
        try:
            # Esconder webdriver
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Esconder navigator.webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Esconder chrome.runtime
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Modificar navigator.plugins para parecer real
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Modificar navigator.languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['pt-BR', 'pt', 'en-US', 'en']
                    });
                    
                    // Esconder automation
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                '''
            })
            self.log("Scripts anti-detecção injetados", "SUCCESS")
        except Exception as e:
            self.log(f"Aviso: Não foi possível injetar scripts: {e}", "WARN")
    
    def human_delay(self, min_s: float = 0.5, max_s: float = 2):
        """Delay humanizado"""
        time.sleep(random.uniform(min_s, max_s))
    
    def human_move_to_element(self, element):
        """Move o mouse para o elemento de forma humanizada"""
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
        except:
            pass
    
    def navigate_with_referer(self, url: str, referer: str = None):
        """Navega mantendo a cadeia de referers"""
        try:
            if referer:
                # Usar CDP para configurar headers
                self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                    'headers': {
                        'Referer': referer,
                        'Origin': referer.split('/')[0] + '//' + referer.split('/')[2] if '//' in referer else referer
                    }
                })
                
            self.driver.get(url)
            self.current_referer = url
            self.human_delay(2, 4)
            
        except Exception as e:
            self.log(f"Erro navegação: {e}", "ERROR")
            self.driver.get(url)
    
    def is_video_url(self, url: str) -> bool:
        url_lower = url.lower()
        if any(p in url_lower for p in self.IGNORE_PATTERNS):
            return False
        return any(p in url_lower for p in self.FINAL_VIDEO_PATTERNS)
    
    def capture_network(self, wait_seconds: int = 15) -> List[VideoURL]:
        """Captura URLs de vídeo das requisições"""
        videos = []
        seen = set()
        
        self.log(f"Aguardando {wait_seconds}s para capturar requisições...", "WAIT")
        time.sleep(wait_seconds)
        
        try:
            logs = self.driver.get_log('performance')
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    
                    if method in ['Network.requestWillBeSent', 'Network.responseReceived']:
                        if method == 'Network.requestWillBeSent':
                            req = msg.get('params', {}).get('request', {})
                            url = req.get('url', '')
                        else:
                            resp = msg.get('params', {}).get('response', {})
                            url = resp.get('url', '')
                        
                        if url and self.is_video_url(url) and url not in seen:
                            seen.add(url)
                            source_type = 'm3u8' if '.m3u8' in url.lower() else 'mp4'
                            
                            video = VideoURL(
                                url=url,
                                source_type=source_type,
                                referer=self.current_referer
                            )
                            videos.append(video)
                            self.log(f"VÍDEO: {url[:100]}", "VIDEO")
                            
                except:
                    pass
                    
        except Exception as e:
            self.log(f"Erro captura: {e}", "ERROR")
            
        return videos
    
    def check_for_abyss_redirect(self) -> bool:
        """Verifica se foi redirecionado para abyss.to"""
        current_url = self.driver.current_url
        if 'abyss.to' in current_url.lower():
            self.log("DETECTADO: Redirecionamento para abyss.to!", "WARN")
            return True
        return False
    
    def get_player_sources_from_playerthree(self) -> List[Dict]:
        """Extrai fontes do playerthree mantendo contexto"""
        sources = []
        
        try:
            # Encontrar episódios
            episode_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='#']")
            
            for link in episode_links:
                href = link.get_attribute('href') or ''
                if '#' in href and '_' in href.split('#')[-1]:
                    text = link.text.strip()
                    self.log(f"Episódio encontrado: {text} - {href}", "DEBUG")
                    
                    # Clicar no episódio
                    self.human_move_to_element(link)
                    self.human_delay(0.3, 0.7)
                    
                    try:
                        self.driver.execute_script("arguments[0].click();", link)
                        self.human_delay(2, 3)
                        
                        # Agora buscar botões de fonte
                        source_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-source], [data-source]")
                        
                        for btn in source_buttons:
                            src = btn.get_attribute('data-source')
                            btn_text = btn.text.strip()
                            
                            if src and src.startswith('http') and 'youtube' not in src.lower():
                                sources.append({
                                    'url': src,
                                    'name': btn_text,
                                    'element': btn
                                })
                                self.log(f"Fonte: {btn_text} - {src[:50]}...", "DEBUG")
                        
                        if sources:
                            break  # Pegamos as fontes do primeiro episódio
                            
                    except Exception as e:
                        self.log(f"Erro ao clicar: {e}", "ERROR")
                        continue
                        
        except Exception as e:
            self.log(f"Erro ao extrair fontes: {e}", "ERROR")
            
        return sources
    
    def navigate_to_source_with_context(self, source: Dict) -> List[VideoURL]:
        """Navega para fonte mantendo contexto/cookies"""
        videos = []
        source_url = source['url']
        
        self.log(f"Navegando para fonte: {source['name']} com contexto correto...")
        
        try:
            # Primeiro, clicar no botão (isso mantém cookies/sessão)
            element = source.get('element')
            if element:
                self.human_move_to_element(element)
                self.human_delay(0.5, 1)
                self.driver.execute_script("arguments[0].click();", element)
                self.human_delay(3, 5)
                
                # Verificar se um iframe foi carregado
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    iframe_src = iframe.get_attribute('src') or ''
                    if iframe_src and ('megaembed' in iframe_src or 'playerembedapi' in iframe_src or 'myvidplay' in iframe_src):
                        self.log(f"Iframe do player carregado: {iframe_src[:60]}...", "SUCCESS")
                        
                        # Entrar no iframe
                        self.driver.switch_to.frame(iframe)
                        self.human_delay(5, 8)
                        
                        # Capturar vídeos
                        videos.extend(self.capture_network(20))
                        
                        # Verificar elemento video
                        try:
                            video_el = self.driver.find_element(By.TAG_NAME, 'video')
                            src = video_el.get_attribute('src') or ''
                            if src and self.is_video_url(src):
                                videos.append(VideoURL(url=src, source_type='element'))
                                self.log(f"Video element: {src[:60]}", "VIDEO")
                        except:
                            pass
                        
                        # Sair do iframe
                        self.driver.switch_to.default_content()
                        
                        if videos:
                            return videos
            
            # Se não funcionou pelo clique, tentar navegação direta com referer
            self.log("Tentando navegação direta com referer correto...")
            
            # Configurar referer como playerthree
            current_url = self.driver.current_url
            self.navigate_with_referer(source_url, current_url)
            
            # Verificar redirecionamento
            if self.check_for_abyss_redirect():
                self.log("Vídeo expirado ou proteção ativa. Tentando outra fonte...", "WARN")
                return videos
            
            # Aguardar e capturar
            videos.extend(self.capture_network(25))
            
        except Exception as e:
            self.log(f"Erro navegando para fonte: {e}", "ERROR")
            
        return videos
    
    def process_maxseries(self, url: str) -> List[VideoURL]:
        """Processa MaxSeries com fluxo completo"""
        all_videos = []
        
        self.log(f"=== Processando MaxSeries: {url} ===")
        
        try:
            # 1. Acessar página da série
            self.driver.get(url)
            self.human_delay(3, 5)
            
            # 2. Encontrar iframe do playerthree
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            playerthree_url = None
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if 'playerthree' in src.lower():
                    playerthree_url = src if src.startswith('http') else 'https:' + src
                    break
            
            if not playerthree_url:
                self.log("Playerthree não encontrado!", "ERROR")
                return all_videos
            
            self.log(f"Playerthree: {playerthree_url[:60]}...")
            
            # 3. Navegar para playerthree
            self.driver.get(playerthree_url)
            self.current_referer = playerthree_url
            self.human_delay(3, 5)
            
            # 4. Extrair fontes
            sources = self.get_player_sources_from_playerthree()
            self.log(f"Encontradas {len(sources)} fontes")
            
            # 5. Testar cada fonte
            for source in sources[:3]:  # Limitar a 3 fontes
                self.log(f"Testando: {source['name']}")
                
                videos = self.navigate_to_source_with_context(source)
                all_videos.extend(videos)
                
                if videos:
                    self.log(f"Vídeos encontrados em {source['name']}!", "SUCCESS")
                    break
                else:
                    # Voltar para playerthree para tentar próxima fonte
                    self.driver.get(playerthree_url)
                    self.human_delay(2, 3)
                    # Re-clicar no episódio
                    sources = self.get_player_sources_from_playerthree()
                    
        except Exception as e:
            self.log(f"Erro: {e}", "ERROR")
            
        return all_videos
    
    def run(self, url: str) -> Dict:
        """Executa captura"""
        print("\n" + "=" * 70)
        print("  ANTI-DETECT VIDEO CAPTURE V5")
        print("  Resolve redirecionamento para abyss.to")
        print("=" * 70)
        print(f"\n  URL: {url}\n")
        
        self.log("=" * 60)
        self.log("INICIANDO CAPTURA V5 - ANTI-DETECÇÃO MÁXIMA")
        self.log("=" * 60)
        
        results = {
            "input_url": url,
            "videos": [],
            "started_at": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            self.driver = self.create_driver()
            self.log("Driver OK!", "SUCCESS")
            
            # Determinar tipo de URL e processar
            if 'maxseries' in url.lower():
                videos = self.process_maxseries(url)
            else:
                # Tentar direto
                self.driver.get(url)
                self.human_delay(3, 5)
                videos = self.capture_network(25)
            
            # Remover duplicatas
            unique = []
            seen = set()
            for v in videos:
                if v.url not in seen:
                    seen.add(v.url)
                    unique.append(v)
            
            self.captured_videos = unique
            results["videos"] = [asdict(v) for v in unique]
            results["success"] = len(unique) > 0
            results["finished_at"] = datetime.now().isoformat()
            
            # Resumo
            self.log("=" * 60)
            self.log("RESULTADOS")
            self.log("=" * 60)
            self.log(f"URLs capturadas: {len(unique)}")
            
            for i, v in enumerate(unique, 1):
                self.log(f"{i}. [{v.source_type}] {v.url}", "VIDEO")
                
        except Exception as e:
            self.log(f"Erro fatal: {e}", "ERROR")
            results["error"] = str(e)
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.log("Driver encerrado")
        
        return results
    
    def save(self, results: Dict, filename: str = None):
        if not filename:
            filename = f"antidetect_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"Salvo: {filename}", "SUCCESS")


def main():
    default_url = "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    capturer = AntiDetectCapture(headless=False, verbose=True)
    results = capturer.run(url)
    capturer.save(results)
    
    if results.get('videos'):
        print("\n" + "=" * 70)
        print("  ✅ VÍDEOS CAPTURADOS")
        print("=" * 70)
        
        for i, v in enumerate(results['videos'], 1):
            print(f"\n  {i}. Tipo: {v['source_type']}")
            print(f"     URL: {v['url']}")
            if v.get('referer'):
                print(f"     Referer: {v['referer']}")
    else:
        print("\n  ❌ Nenhum vídeo capturado.")
        print("\n  💡 Dicas:")
        print("     1. Quando o Chrome abrir, clique MANUALMENTE no botão de play")
        print("     2. O script vai capturar a URL que for requisitada")
        print("     3. Se redirecionar para abyss.to, o vídeo pode estar expirado")
    
    print()
    return results


if __name__ == "__main__":
    main()
