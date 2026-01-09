#!/usr/bin/env python3
"""
Captura de URLs de Vídeo - V3 (Específico para PlayerthreeOnline)
Clica nos episódios e captura as requisições quando o iframe carrega

Uso: python undetected-video-capture-v3.py [URL]
"""

import json
import time
import random
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class VideoSource:
    url: str
    source_type: str
    host: str
    headers: Dict[str, str]
    found_at: str
    episode_id: Optional[str] = None
    quality: Optional[str] = None


class PlayerthreeCaptureV3:
    """Captura específica para playerthree.online e similares"""
    
    DOOD_DOMAINS = ['myvidplay', 'bysebuho', 'g9r6', 'dood', 'ds2play', 'd0000d']
    VIDEO_PATTERNS = ['.m3u8', '.mp4', '/hls/', 'master', '/video/', '/e/', '/d/']
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        self.headless = headless
        self.verbose = verbose
        self.driver = None
        self.found_videos: List[VideoSource] = []
        
    def log(self, msg: str, level: str = "INFO"):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "VIDEO": "🎬", 
                     "DEBUG": "🔍", "CLICK": "👆", "WAIT": "⏳"}.get(level, "")
            print(f"[{ts}] {emoji} {msg}")
    
    def create_driver(self) -> uc.Chrome:
        options = uc.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=pt-BR')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--ignore-certificate-errors')
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Logging de rede
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.log("Iniciando Chrome indetectável...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_page_load_timeout(60)
        
        return driver
    
    def human_delay(self, min_s: float = 1, max_s: float = 3):
        time.sleep(random.uniform(min_s, max_s))
    
    def capture_network(self) -> List[Dict]:
        """Captura logs de rede"""
        requests = []
        try:
            logs = self.driver.get_log('performance')
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    
                    if method == 'Network.requestWillBeSent':
                        req = msg.get('params', {}).get('request', {})
                        url = req.get('url', '')
                        if url:
                            requests.append({
                                'url': url,
                                'headers': req.get('headers', {}),
                            })
                except:
                    pass
        except:
            pass
        return requests
    
    def is_video_url(self, url: str) -> bool:
        """Verifica se é URL de vídeo/extrator"""
        url_lower = url.lower()
        
        # Ignorar recursos estáticos
        if any(x in url_lower for x in ['google', 'analytics', 'facebook', 'adsense', '.css', '.js', '.png', '.jpg', '.gif', '.ico']):
            return False
        
        # Verificar padrões de vídeo
        is_video_pattern = any(p in url_lower for p in self.VIDEO_PATTERNS)
        
        # Verificar domínios de streaming
        is_streaming_domain = any(d in url_lower for d in self.DOOD_DOMAINS)
        
        # Verificar outros extractores
        is_extractor = any(e in url_lower for e in ['megaembed', 'playerembedapi', 'streamwish', 'filemoon', 'mixdrop', 'streamtape', 'voe.sx'])
        
        return is_video_pattern or is_streaming_domain or is_extractor
    
    def get_host(self, url: str) -> str:
        url_lower = url.lower()
        if any(d in url_lower for d in self.DOOD_DOMAINS):
            return "doodstream"
        elif "megaembed" in url_lower:
            return "megaembed"
        elif "playerembedapi" in url_lower:
            return "playerembedapi"
        elif "streamwish" in url_lower:
            return "streamwish"
        elif "filemoon" in url_lower:
            return "filemoon"
        elif "storage.googleapis" in url_lower:
            return "google_storage"
        else:
            try:
                from urllib.parse import urlparse
                return urlparse(url).netloc
            except:
                return "unknown"
    
    def find_episode_links(self) -> List[Dict]:
        """Encontra links de episódios no formato #SERIE_EPISODIO"""
        episodes = []
        try:
            # Tentar diferentes seletores
            selectors = [
                "a[href^='#']",  # Links com hash
                "li[data-episode-id] a",
                ".episode-link",
                ".ep-item a",
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    href = el.get_attribute('href') or ''
                    text = el.text.strip() or el.get_attribute('title') or ''
                    
                    # Verificar se é formato de episódio (#ID_EPID)
                    if '#' in href and ('_' in href or href.replace('#', '').isdigit()):
                        # Extrair ID do episódio
                        hash_value = href.split('#')[-1] if '#' in href else href
                        
                        episodes.append({
                            'element': el,
                            'href': href,
                            'hash': hash_value,
                            'text': text
                        })
                        
            self.log(f"Encontrados {len(episodes)} links de episódios")
            
        except Exception as e:
            self.log(f"Erro ao buscar episódios: {e}", "ERROR")
            
        return episodes
    
    def find_source_buttons(self) -> List[Dict]:
        """Encontra botões de fonte (após clicar no episódio)"""
        sources = []
        try:
            selectors = [
                "button[data-source]",
                "li[data-source]",
                "[data-source]",
                ".server-btn",
                ".source-btn",
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    src = el.get_attribute('data-source') or ''
                    text = el.text.strip() or ''
                    
                    if src and src.startswith('http') and 'youtube' not in src.lower():
                        sources.append({
                            'element': el,
                            'url': src,
                            'name': text
                        })
                        self.log(f"Fonte: {text} - {src[:50]}...", "DEBUG")
                        
        except Exception as e:
            self.log(f"Erro ao buscar fontes: {e}", "ERROR")
            
        return sources
    
    def click_element_safe(self, element, description: str = "") -> bool:
        """Clica em elemento de forma segura com JS"""
        try:
            self.log(f"Clicando: {description}", "CLICK")
            
            # Scroll para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.human_delay(0.3, 0.7)
            
            # Clicar via JS para evitar detecção
            self.driver.execute_script("arguments[0].click();", element)
            
            self.human_delay(1, 2)
            return True
            
        except Exception as e:
            self.log(f"Erro ao clicar: {e}", "ERROR")
            return False
    
    def wait_for_iframe(self, timeout: int = 10) -> Optional[str]:
        """Aguarda iframe aparecer e retorna sua URL"""
        try:
            self.log(f"Aguardando iframe aparecer...", "WAIT")
            
            for _ in range(timeout * 2):
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if src and any(d in src.lower() for d in self.DOOD_DOMAINS + ['megaembed', 'playerembedapi', 'player']):
                        self.log(f"Iframe detectado: {src[:60]}...", "SUCCESS")
                        return src
                time.sleep(0.5)
                
        except Exception as e:
            self.log(f"Erro aguardando iframe: {e}", "ERROR")
            
        return None
    
    def capture_from_iframe(self, iframe_url: str, episode_id: str = None) -> List[VideoSource]:
        """Navega para iframe e captura URLs de vídeo"""
        videos = []
        
        try:
            self.log(f"Navegando para iframe: {iframe_url[:60]}...")
            self.driver.get(iframe_url)
            self.human_delay(3, 5)
            
            # Aguardar e capturar requisições
            self.log("Aguardando 10s para capturar requisições...", "WAIT")
            time.sleep(10)
            
            # Capturar rede
            requests = self.capture_network()
            
            # Filtrar vídeos
            seen = set()
            for req in requests:
                url = req.get('url', '')
                if url and self.is_video_url(url) and url not in seen:
                    seen.add(url)
                    
                    video = VideoSource(
                        url=url,
                        source_type='m3u8' if '.m3u8' in url.lower() else 'mp4',
                        host=self.get_host(url),
                        headers=req.get('headers', {}),
                        found_at=datetime.now().isoformat(),
                        episode_id=episode_id
                    )
                    videos.append(video)
                    self.log(f"URL capturada: {url[:80]}...", "VIDEO")
            
            # Verificar elemento <video>
            try:
                video_els = self.driver.find_elements(By.TAG_NAME, 'video')
                for vel in video_els:
                    src = vel.get_attribute('src') or ''
                    if src and src not in seen:
                        seen.add(src)
                        videos.append(VideoSource(
                            url=src,
                            source_type='m3u8' if '.m3u8' in src else 'mp4',
                            host=self.get_host(src),
                            headers={},
                            found_at=datetime.now().isoformat()
                        ))
                        self.log(f"Video element: {src[:60]}...", "VIDEO")
            except:
                pass
                
            # Verificar iframes aninhados
            try:
                inner_iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for inner in inner_iframes:
                    inner_src = inner.get_attribute('src') or ''
                    if inner_src and any(d in inner_src.lower() for d in self.DOOD_DOMAINS):
                        self.log(f"Iframe aninhado DoodStream: {inner_src[:60]}...")
                        # Navegar para o doodstream
                        self.driver.get(inner_src)
                        self.human_delay(3, 5)
                        time.sleep(8)
                        
                        inner_reqs = self.capture_network()
                        for req in inner_reqs:
                            url = req.get('url', '')
                            if url and self.is_video_url(url) and url not in seen:
                                seen.add(url)
                                videos.append(VideoSource(
                                    url=url,
                                    source_type='m3u8' if '.m3u8' in url else 'mp4',
                                    host=self.get_host(url),
                                    headers=req.get('headers', {}),
                                    found_at=datetime.now().isoformat()
                                ))
                                self.log(f"URL do DoodStream: {url[:80]}...", "VIDEO")
            except:
                pass
                
        except Exception as e:
            self.log(f"Erro captura iframe: {e}", "ERROR")
            
        return videos
    
    def process_player_page(self, player_url: str) -> List[VideoSource]:
        """Processa página do playerthree (ou similar)"""
        all_videos = []
        
        try:
            self.log(f"=== Processando player: {player_url} ===")
            self.driver.get(player_url)
            self.human_delay(3, 5)
            
            # 1. Buscar links de episódios
            episodes = self.find_episode_links()
            
            if not episodes:
                self.log("Nenhum episódio encontrado, tentando fontes diretas...")
                # Tentar fontes diretas
                sources = self.find_source_buttons()
                for src in sources[:5]:
                    videos = self.capture_from_iframe(src['url'])
                    all_videos.extend(videos)
                return all_videos
            
            # 2. Clicar no primeiro episódio
            first_ep = episodes[0]
            self.log(f"Clicando no episódio: {first_ep['text']} ({first_ep['hash']})")
            
            if self.click_element_safe(first_ep['element'], first_ep['text']):
                # 3. Aguardar iframe ou botões de fonte aparecerem
                self.human_delay(2, 3)
                
                # 4. Verificar se apareceram botões de fonte
                sources = self.find_source_buttons()
                
                if sources:
                    self.log(f"Encontradas {len(sources)} fontes após clique")
                    
                    # Clicar em cada fonte e capturar
                    for src in sources[:5]:
                        self.log(f"Testando fonte: {src['name']}")
                        
                        if self.click_element_safe(src['element'], src['name']):
                            # Aguardar iframe carregar
                            iframe_url = self.wait_for_iframe(timeout=8)
                            
                            if iframe_url:
                                videos = self.capture_from_iframe(iframe_url, first_ep['hash'])
                                all_videos.extend(videos)
                                
                                # Voltar para o player
                                self.driver.get(player_url)
                                self.human_delay(2, 3)
                                
                                # Clicar no episódio novamente
                                episodes = self.find_episode_links()
                                if episodes:
                                    self.click_element_safe(episodes[0]['element'], episodes[0]['text'])
                                    self.human_delay(1, 2)
                        else:
                            # Tentar navegar direto para a URL da fonte
                            videos = self.capture_from_iframe(src['url'], first_ep['hash'])
                            all_videos.extend(videos)
                else:
                    # Verificar se tem iframe direto
                    iframe_url = self.wait_for_iframe(timeout=10)
                    if iframe_url:
                        videos = self.capture_from_iframe(iframe_url, first_ep['hash'])
                        all_videos.extend(videos)
            
        except Exception as e:
            self.log(f"Erro processando player: {e}", "ERROR")
            
        return all_videos
    
    def capture_from_maxseries(self, url: str) -> List[VideoSource]:
        """Captura de página MaxSeries"""
        all_videos = []
        
        try:
            self.log(f"=== MaxSeries: {url} ===")
            self.driver.get(url)
            self.human_delay(3, 5)
            
            # Encontrar iframe do player
            player_iframes = []
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if 'playerthree' in src.lower() or 'player' in src.lower():
                    if src.startswith('//'):
                        src = 'https:' + src
                    player_iframes.append(src)
                    self.log(f"Player iframe: {src[:60]}...", "DEBUG")
            
            if not player_iframes:
                self.log("Nenhum player encontrado!", "ERROR")
                return all_videos
            
            # Processar cada player
            for player_url in player_iframes[:1]:  # Apenas o primeiro
                videos = self.process_player_page(player_url)
                all_videos.extend(videos)
                
        except Exception as e:
            self.log(f"Erro MaxSeries: {e}", "ERROR")
            
        return all_videos
    
    def run(self, url: str) -> Dict:
        """Executa captura completa"""
        print("\n" + "=" * 70)
        print("  UNDETECTED VIDEO CAPTURE V3")
        print("  Específico para playerthree.online e similares")
        print("=" * 70)
        print(f"\n  URL: {url}\n")
        
        self.log("=" * 60)
        self.log("INICIANDO CAPTURA V3")
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
            
            if 'maxseries' in url.lower():
                videos = self.capture_from_maxseries(url)
            elif 'playerthree' in url.lower():
                videos = self.process_player_page(url)
            else:
                # Tentar como player genérico
                videos = self.process_player_page(url)
            
            # Remover duplicatas
            unique = []
            seen = set()
            for v in videos:
                if v.url not in seen:
                    seen.add(v.url)
                    unique.append(v)
            
            self.found_videos = unique
            results["videos"] = [asdict(v) for v in unique]
            results["success"] = len(unique) > 0
            results["finished_at"] = datetime.now().isoformat()
            
            # Resumo
            self.log("=" * 60)
            self.log("RESULTADOS")
            self.log("=" * 60)
            self.log(f"Vídeos encontrados: {len(unique)}")
            
            for i, v in enumerate(unique, 1):
                self.log(f"{i}. [{v.host}] {v.url}", "VIDEO")
                
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
            filename = f"video_capture_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"Salvo: {filename}", "SUCCESS")


def main():
    default_url = "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    capturer = PlayerthreeCaptureV3(headless=False, verbose=True)
    results = capturer.run(url)
    capturer.save(results)
    
    if results.get('videos'):
        print("\n" + "=" * 70)
        print("  ✅ VÍDEOS/FONTES ENCONTRADOS")
        print("=" * 70)
        
        for i, v in enumerate(results['videos'], 1):
            print(f"\n  {i}. Host: {v['host']}")
            print(f"     Tipo: {v['source_type']}")
            print(f"     URL:  {v['url']}")
    else:
        print("\n  ❌ Nenhum vídeo encontrado.")
        print("     Verifique se o site está online e tente novamente.")
    
    print()
    return results


if __name__ == "__main__":
    main()
