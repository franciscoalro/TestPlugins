#!/usr/bin/env python3
"""
Captura de URLs de Vídeo com Selenium Indetectável - V2
Versão melhorada com clique em botões de fonte e iframes aninhados

Uso: python undetected-video-capture-v2.py [URL_DO_EPISODIO_OU_FILME]
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
    quality: Optional[str] = None
    source_name: Optional[str] = None


class UndetectedVideoCaptureV2:
    """Captura URLs de vídeo - Versão 2 com suporte a cliques"""
    
    DOODSTREAM_DOMAINS = [
        'myvidplay.com', 'bysebuho.com', 'g9r6.com',
        'doodstream.com', 'dood.to', 'dood.watch', 'dood.pm',
        'dood.wf', 'dood.re', 'dood.so', 'dood.cx',
        'ds2play.com', 'd0000d.com', 'd000d.com'
    ]
    
    HARD_HOSTS = ['playerthree.online', 'megaembed.link', 'playerembedapi.link']
    VIDEO_PATTERNS = ['.m3u8', '.mp4', '/hls/', 'master', '/video/', 'stream', '.ts']
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        self.headless = headless
        self.verbose = verbose
        self.driver = None
        self.found_videos: List[VideoSource] = []
        self.all_network: List[Dict] = []
        
    def log(self, msg: str, level: str = "INFO"):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "VIDEO": "🎬", "DEBUG": "🔍", "CLICK": "👆"}.get(level, "")
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
        
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.log("Iniciando Chrome indetectável...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(5)
        
        return driver
    
    def human_delay(self, min_sec: float = 1, max_sec: float = 3):
        time.sleep(random.uniform(min_sec, max_sec))
    
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
                        requests.append({
                            'url': req.get('url', ''),
                            'headers': req.get('headers', {}),
                            'type': 'request'
                        })
                    elif method == 'Network.responseReceived':
                        resp = msg.get('params', {}).get('response', {})
                        requests.append({
                            'url': resp.get('url', ''),
                            'headers': resp.get('headers', {}),
                            'type': 'response'
                        })
                except:
                    pass
        except Exception as e:
            self.log(f"Erro captura rede: {e}", "ERROR")
        return requests
    
    def check_video_urls(self, requests: List[Dict]) -> List[VideoSource]:
        """Verifica URLs de vídeo nas requisições"""
        videos = []
        seen = set()
        
        for req in requests:
            url = req.get('url', '')
            url_lower = url.lower()
            
            is_video = any(p in url_lower for p in self.VIDEO_PATTERNS)
            
            if is_video and url not in seen and 'google' not in url_lower and 'analytics' not in url_lower:
                seen.add(url)
                
                source_type = 'm3u8' if '.m3u8' in url_lower else ('mp4' if '.mp4' in url_lower else 'stream')
                
                video = VideoSource(
                    url=url,
                    source_type=source_type,
                    host=self._get_host(url),
                    headers=req.get('headers', {}),
                    found_at=datetime.now().isoformat()
                )
                videos.append(video)
                self.log(f"VÍDEO: {url[:100]}...", "VIDEO")
        
        return videos
    
    def _get_host(self, url: str) -> str:
        url_lower = url.lower()
        if any(d in url_lower for d in self.DOODSTREAM_DOMAINS):
            return "doodstream"
        elif "megaembed" in url_lower:
            return "megaembed"
        elif "playerembedapi" in url_lower:
            return "playerembedapi"
        elif "playerthree" in url_lower:
            return "playerthree"
        elif "storage.googleapis" in url_lower:
            return "google_storage"
        elif "akamai" in url_lower:
            return "akamai"
        else:
            try:
                from urllib.parse import urlparse
                return urlparse(url).netloc
            except:
                return "unknown"
    
    def extract_iframes(self) -> List[str]:
        """Extrai URLs de iframes"""
        iframes = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for el in elements:
                src = el.get_attribute('src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    iframes.append(src)
                    self.log(f"Iframe: {src[:60]}...", "DEBUG")
        except Exception as e:
            self.log(f"Erro iframes: {e}", "ERROR")
        return iframes
    
    def get_player_sources(self) -> List[Dict]:
        """Extrai botões de fonte do player"""
        sources = []
        try:
            # Múltiplos seletores para diferentes layouts
            selectors = [
                'button[data-source]',
                'li[data-source] button',
                'li[data-source]',
                'a[data-source]',
                '.server-item[data-source]',
                '[data-video]',
                '.source-btn',
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        src = (el.get_attribute('data-source') or 
                               el.get_attribute('data-video') or
                               el.get_attribute('href'))
                        text = el.text.strip() or el.get_attribute('title') or 'Unknown'
                        
                        if src and src.startswith('http') and 'youtube' not in src.lower():
                            sources.append({'url': src, 'name': text, 'element': el})
                            self.log(f"Fonte: {text} - {src[:50]}...", "DEBUG")
                except:
                    pass
                    
        except Exception as e:
            self.log(f"Erro fontes: {e}", "ERROR")
        
        # Remover duplicatas
        seen = set()
        unique = []
        for s in sources:
            if s['url'] not in seen:
                seen.add(s['url'])
                unique.append(s)
        
        return unique
    
    def click_source_button(self, source: Dict) -> bool:
        """Clica em um botão de fonte"""
        try:
            el = source.get('element')
            if el:
                self.log(f"Clicando: {source['name']}", "CLICK")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                self.human_delay(0.3, 0.7)
                el.click()
                self.human_delay(2, 4)
                return True
        except Exception as e:
            self.log(f"Erro clique: {e}", "ERROR")
        return False
    
    def wait_and_capture(self, seconds: int = 15) -> List[VideoSource]:
        """Aguarda e captura requisições"""
        self.log(f"Aguardando {seconds}s para capturar...")
        time.sleep(seconds)
        
        requests = self.capture_network()
        self.all_network.extend(requests)
        
        return self.check_video_urls(requests)
    
    def check_video_element(self) -> List[str]:
        """Verifica elementos <video>"""
        videos = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'video')
            for v in elements:
                src = v.get_attribute('src')
                if src:
                    videos.append(src)
                    self.log(f"Video element: {src[:60]}...", "VIDEO")
                
                # currentSrc pode ser diferente após JS
                try:
                    cs = self.driver.execute_script("return arguments[0].currentSrc", v)
                    if cs and cs != src:
                        videos.append(cs)
                        self.log(f"currentSrc: {cs[:60]}...", "VIDEO")
                except:
                    pass
                    
                # Verificar sources
                for s in v.find_elements(By.TAG_NAME, 'source'):
                    src = s.get_attribute('src')
                    if src:
                        videos.append(src)
        except:
            pass
        return list(set(videos))
    
    def switch_to_iframe_and_capture(self, iframe_url: str) -> List[VideoSource]:
        """Navega para iframe e captura"""
        videos = []
        
        try:
            self.log(f"Navegando: {iframe_url[:60]}...")
            self.driver.get(iframe_url)
            self.human_delay(3, 5)
            
            # Capturar inicialmente
            videos.extend(self.wait_and_capture(10))
            
            # Verificar elementos de vídeo
            for url in self.check_video_element():
                if not any(v.url == url for v in videos):
                    videos.append(VideoSource(
                        url=url,
                        source_type='m3u8' if '.m3u8' in url else 'mp4',
                        host=self._get_host(url),
                        headers={},
                        found_at=datetime.now().isoformat()
                    ))
            
            # Verificar iframes aninhados
            nested = self.extract_iframes()
            for nf in nested[:2]:
                if nf != iframe_url and any(h in nf for h in self.HARD_HOSTS + self.DOODSTREAM_DOMAINS):
                    self.log(f"Iframe aninhado: {nf[:50]}...")
                    self.driver.get(nf)
                    self.human_delay(3, 5)
                    videos.extend(self.wait_and_capture(10))
                    
        except Exception as e:
            self.log(f"Erro iframe: {e}", "ERROR")
            
        return videos
    
    def process_player_page(self, player_url: str) -> List[VideoSource]:
        """Processa página de player com múltiplas fontes"""
        all_videos = []
        
        try:
            self.log(f"Processando player: {player_url[:60]}...")
            self.driver.get(player_url)
            self.human_delay(3, 5)
            
            # Primeiro, capturar o que já está carregado
            all_videos.extend(self.wait_and_capture(5))
            
            # Pegar todas as fontes disponíveis
            sources = self.get_player_sources()
            self.log(f"Encontradas {len(sources)} fontes")
            
            # Clicar em cada fonte e capturar
            for source in sources[:6]:  # Limitar a 6 fontes
                self.log(f"Testando fonte: {source['name']}", "INFO")
                
                # Tentar clicar no botão
                if self.click_source_button(source):
                    # Aguardar carregar e capturar
                    videos = self.wait_and_capture(8)
                    all_videos.extend(videos)
                    
                    # Verificar se há iframe carregado
                    iframes = self.extract_iframes()
                    for iframe in iframes[:2]:
                        if any(h in iframe for h in self.HARD_HOSTS + self.DOODSTREAM_DOMAINS):
                            # Navegar para o iframe
                            sub_videos = self.switch_to_iframe_and_capture(iframe)
                            all_videos.extend(sub_videos)
                            
                            # Voltar para o player
                            self.driver.get(player_url)
                            self.human_delay(2, 3)
                else:
                    # Se não conseguiu clicar, tentar navegar diretamente
                    sub_videos = self.switch_to_iframe_and_capture(source['url'])
                    all_videos.extend(sub_videos)
            
        except Exception as e:
            self.log(f"Erro player: {e}", "ERROR")
            
        return all_videos
    
    def capture_from_maxseries(self, url: str) -> List[VideoSource]:
        """Captura de episódio do MaxSeries"""
        all_videos = []
        
        self.log(f"=== MaxSeries: {url} ===")
        
        try:
            # Acessar página
            self.driver.get(url)
            self.human_delay(3, 5)
            
            # Extrair iframes
            iframes = self.extract_iframes()
            
            # Encontrar player iframe
            player_iframes = [i for i in iframes if any(h in i for h in self.HARD_HOSTS)]
            
            if not player_iframes:
                self.log("Nenhum player encontrado na página", "ERROR")
                return all_videos
            
            for player_url in player_iframes[:2]:
                videos = self.process_player_page(player_url)
                all_videos.extend(videos)
                
        except Exception as e:
            self.log(f"Erro MaxSeries: {e}", "ERROR")
            
        return all_videos
    
    def run(self, url: str) -> Dict:
        """Executa captura completa"""
        self.log("=" * 60)
        self.log("CAPTURA DE VÍDEO V2 - SELENIUM INDETECTÁVEL")
        self.log("=" * 60)
        
        results = {
            "input_url": url,
            "videos": [],
            "total_requests": 0,
            "started_at": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            self.driver = self.create_driver()
            self.log("Driver OK!", "SUCCESS")
            
            # Capturar baseado no tipo de URL
            if 'maxseries' in url.lower():
                videos = self.capture_from_maxseries(url)
            elif any(h in url.lower() for h in self.HARD_HOSTS):
                videos = self.process_player_page(url)
            else:
                videos = self.switch_to_iframe_and_capture(url)
            
            # Remover duplicatas
            unique = []
            seen = set()
            for v in videos:
                if v.url not in seen:
                    seen.add(v.url)
                    unique.append(v)
            
            self.found_videos = unique
            
            results["videos"] = [asdict(v) for v in unique]
            results["total_requests"] = len(self.all_network)
            results["success"] = len(unique) > 0
            results["finished_at"] = datetime.now().isoformat()
            
            # Resumo
            self.log("=" * 60)
            self.log("RESULTADOS")
            self.log("=" * 60)
            self.log(f"Requisições: {len(self.all_network)}")
            self.log(f"Vídeos: {len(unique)}")
            
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
            filename = f"video_capture_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"Salvo: {filename}", "SUCCESS")


def main():
    default_url = "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print("\n" + "=" * 70)
    print("  UNDETECTED VIDEO CAPTURE V2")
    print("  Com suporte a clique em botões e iframes aninhados")
    print("=" * 70)
    print(f"\n  URL: {url}\n")
    
    capturer = UndetectedVideoCaptureV2(headless=False, verbose=True)
    results = capturer.run(url)
    capturer.save(results)
    
    if results.get('videos'):
        print("\n" + "=" * 70)
        print("  ✅ VÍDEOS ENCONTRADOS")
        print("=" * 70)
        
        for i, v in enumerate(results['videos'], 1):
            print(f"\n  {i}. Host: {v['host']}")
            print(f"     Tipo: {v['source_type']}")
            print(f"     URL:  {v['url']}")
    else:
        print("\n  ❌ Nenhum vídeo encontrado.")
    
    print()
    return results


if __name__ == "__main__":
    main()
