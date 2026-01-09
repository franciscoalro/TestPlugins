#!/usr/bin/env python3
"""
Captura de URLs de Vídeo com Selenium Indetectável
Usa undetected-chromedriver para bypass de anti-bot
Intercepta requisições de rede quando detecta frames de vídeo

Uso: python undetected-video-capture.py [URL_DO_EPISODIO_OU_FILME]
"""

import json
import time
import random
import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Selenium indetectável
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@dataclass
class VideoSource:
    """Estrutura para armazenar fonte de vídeo encontrada"""
    url: str
    source_type: str  # m3u8, mp4, direct
    host: str         # megaembed, playerembedapi, doodstream, etc
    headers: Dict[str, str]
    found_at: str
    quality: Optional[str] = None


class UndetectedVideoCapture:
    """Captura URLs de vídeo usando Selenium indetectável"""
    
    # Domínios de vídeo conhecidos (DoodStream clones)
    DOODSTREAM_DOMAINS = [
        'myvidplay.com', 'bysebuho.com', 'g9r6.com',
        'doodstream.com', 'dood.to', 'dood.watch', 'dood.pm',
        'dood.wf', 'dood.re', 'dood.so', 'dood.cx',
        'dood.la', 'dood.ws', 'dood.sh', 'doodstream.co',
        'd0000d.com', 'd000d.com', 'dooood.com', 'ds2play.com'
    ]
    
    # Hosts "difíceis" que precisam de WebView/Selenium
    HARD_HOSTS = ['megaembed.link', 'playerembedapi.link', 'playerthree.online']
    
    # Padrões de URL de vídeo
    VIDEO_PATTERNS = ['.m3u8', '.mp4', '.ts', '/hls/', 'master.txt', '/video/', 'stream']
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        self.headless = headless
        self.verbose = verbose
        self.driver: Optional[uc.Chrome] = None
        self.found_videos: List[VideoSource] = []
        self.network_requests: List[Dict] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "VIDEO": "🎬", "DEBUG": "🔍"}.get(level, "")
            print(f"[{timestamp}] {emoji} {message}")
    
    def create_driver(self) -> uc.Chrome:
        """Cria driver Chrome indetectável com logging de rede"""
        options = uc.ChromeOptions()
        
        # Configurações básicas
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=pt-BR')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--ignore-certificate-errors')
        
        # Headless mode (se configurado)
        if self.headless:
            options.add_argument('--headless=new')
        
        # IMPORTANTE: Habilitar logging de performance para capturar requisições de rede
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.log("Iniciando Chrome indetectável...")
        driver = uc.Chrome(options=options, version_main=None)
        
        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        return driver
    
    def human_delay(self, min_sec: float = 1, max_sec: float = 3):
        """Delay humanizado para evitar detecção"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def capture_network_logs(self) -> List[Dict]:
        """Captura todas as requisições de rede do browser"""
        if not self.driver:
            return []
            
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
                        headers = req.get('headers', {})
                        
                        requests.append({
                            'url': url,
                            'headers': headers,
                            'type': 'request'
                        })
                        
                    elif method == 'Network.responseReceived':
                        resp = msg.get('params', {}).get('response', {})
                        url = resp.get('url', '')
                        headers = resp.get('headers', {})
                        
                        requests.append({
                            'url': url,
                            'headers': headers,
                            'type': 'response'
                        })
                        
                except Exception:
                    pass
        except Exception as e:
            self.log(f"Erro ao capturar logs de rede: {e}", "ERROR")
            
        return requests
    
    def filter_video_urls(self, requests: List[Dict]) -> List[VideoSource]:
        """Filtra requisições para encontrar URLs de vídeo"""
        videos = []
        seen_urls = set()
        
        for req in requests:
            url = req.get('url', '')
            
            # Verificar se é URL de vídeo
            is_video = any(pattern in url.lower() for pattern in self.VIDEO_PATTERNS)
            
            if is_video and url not in seen_urls:
                seen_urls.add(url)
                
                # Determinar tipo
                if '.m3u8' in url.lower():
                    source_type = 'm3u8'
                elif '.mp4' in url.lower():
                    source_type = 'mp4'
                else:
                    source_type = 'stream'
                
                # Determinar host
                host = self._identify_host(url)
                
                # Extrair qualidade se disponível
                quality = self._extract_quality(url)
                
                video = VideoSource(
                    url=url,
                    source_type=source_type,
                    host=host,
                    headers=req.get('headers', {}),
                    found_at=datetime.now().isoformat(),
                    quality=quality
                )
                
                videos.append(video)
                self.log(f"VÍDEO ENCONTRADO: {url[:80]}...", "VIDEO")
        
        return videos
    
    def _identify_host(self, url: str) -> str:
        """Identifica o host de streaming"""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in self.DOODSTREAM_DOMAINS):
            return "doodstream"
        elif "megaembed" in url_lower:
            return "megaembed"
        elif "playerembedapi" in url_lower:
            return "playerembedapi"
        elif "playerthree" in url_lower:
            return "playerthree"
        elif "storage.googleapis" in url_lower or "gcs" in url_lower:
            return "google_storage"
        elif "akamai" in url_lower:
            return "akamai"
        elif "cloudfront" in url_lower:
            return "cloudfront"
        else:
            # Extrair domínio
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc or "unknown"
    
    def _extract_quality(self, url: str) -> Optional[str]:
        """Extrai qualidade do URL se disponível"""
        patterns = [
            r'(\d{3,4})p',      # 720p, 1080p
            r'/(\d{3,4})/',     # /720/
            r'_(\d{3,4})\.',    # _720.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"{match.group(1)}p"
        
        return None
    
    def extract_iframes(self) -> List[str]:
        """Extrai URLs de iframes da página"""
        iframes = []
        
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in elements:
                src = iframe.get_attribute('src')
                if src and src.strip():
                    # Normalizar URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    iframes.append(src)
                    self.log(f"Iframe encontrado: {src[:60]}...", "DEBUG")
        except Exception as e:
            self.log(f"Erro ao extrair iframes: {e}", "ERROR")
        
        return iframes
    
    def extract_video_elements(self) -> List[str]:
        """Extrai URLs de elementos <video>"""
        videos = []
        
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'video')
            for video in elements:
                # Verificar src direto
                src = video.get_attribute('src')
                if src:
                    videos.append(src)
                
                # Verificar currentSrc (pode ser diferente após JS)
                try:
                    current_src = self.driver.execute_script("return arguments[0].currentSrc", video)
                    if current_src and current_src != src:
                        videos.append(current_src)
                except:
                    pass
                
                # Verificar elementos <source>
                sources = video.find_elements(By.TAG_NAME, 'source')
                for source in sources:
                    src = source.get_attribute('src')
                    if src:
                        videos.append(src)
                        
        except Exception as e:
            self.log(f"Erro ao extrair elementos video: {e}", "ERROR")
        
        return list(set(videos))
    
    def extract_player_sources(self) -> List[str]:
        """Extrai URLs de botões de fonte (data-source, data-video, etc)"""
        sources = []
        
        try:
            # Vários seletores de botões de fonte
            selectors = [
                'button[data-source]',
                'li[data-source]',
                'a[data-source]',
                '[data-video]',
                '[data-url]',
                '.player-source',
                '.video-source',
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    src = (el.get_attribute('data-source') or 
                           el.get_attribute('data-video') or 
                           el.get_attribute('data-url'))
                    if src and src.startswith('http'):
                        # Ignorar YouTube (trailers)
                        if 'youtube' not in src.lower() and 'youtu.be' not in src.lower():
                            sources.append(src)
                            self.log(f"Fonte encontrada: {src[:60]}...", "DEBUG")
                            
        except Exception as e:
            self.log(f"Erro ao extrair fontes do player: {e}", "ERROR")
        
        return list(set(sources))
    
    def navigate_to_iframe_and_capture(self, iframe_url: str, wait_time: int = 15) -> List[VideoSource]:
        """Navega para iframe e captura requisições de vídeo"""
        videos = []
        
        self.log(f"Navegando para iframe: {iframe_url[:60]}...")
        
        try:
            self.driver.get(iframe_url)
            self.human_delay(3, 5)
            
            # Esperar player carregar
            self.log(f"Aguardando {wait_time}s para capturar requisições...")
            time.sleep(wait_time)
            
            # Capturar requisições de rede
            requests = self.capture_network_logs()
            self.network_requests.extend(requests)
            
            # Filtrar vídeos
            videos = self.filter_video_urls(requests)
            
            # Também verificar elementos de vídeo
            video_elements = self.extract_video_elements()
            for url in video_elements:
                if url and not any(v.url == url for v in videos):
                    videos.append(VideoSource(
                        url=url,
                        source_type='m3u8' if '.m3u8' in url else 'mp4',
                        host=self._identify_host(url),
                        headers={},
                        found_at=datetime.now().isoformat()
                    ))
                    
        except Exception as e:
            self.log(f"Erro ao navegar para iframe: {e}", "ERROR")
        
        return videos
    
    def click_and_capture(self, selector: str, wait_time: int = 10) -> List[VideoSource]:
        """Clica em um elemento e captura requisições resultantes"""
        videos = []
        
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            self.log(f"Clicando em: {selector}")
            element.click()
            
            self.human_delay(2, 4)
            time.sleep(wait_time)
            
            # Capturar requisições
            requests = self.capture_network_logs()
            videos = self.filter_video_urls(requests)
            
        except TimeoutException:
            self.log(f"Timeout ao aguardar elemento: {selector}", "ERROR")
        except Exception as e:
            self.log(f"Erro ao clicar: {e}", "ERROR")
        
        return videos
    
    def capture_episode_from_maxseries(self, episode_url: str) -> List[VideoSource]:
        """Captura fontes de vídeo de um episódio do MaxSeries"""
        self.log(f"=== Capturando episódio: {episode_url} ===", "INFO")
        
        all_videos = []
        
        try:
            # 1. Acessar página do episódio
            self.driver.get(episode_url)
            self.human_delay(3, 5)
            
            # 2. Extrair iframes
            iframes = self.extract_iframes()
            
            # 3. Encontrar iframe do player (playerthree, etc)
            player_iframes = [url for url in iframes if any(host in url for host in self.HARD_HOSTS)]
            
            if not player_iframes:
                self.log("Nenhum player iframe encontrado, tentando iframes genéricos...")
                player_iframes = [url for url in iframes if 'player' in url.lower()]
            
            for iframe_url in player_iframes[:2]:  # Limitar a 2 iframes
                self.log(f"Processando player: {iframe_url[:60]}...")
                
                # Navegar para o iframe
                self.driver.get(iframe_url)
                self.human_delay(3, 5)
                
                # Extrair fontes do player
                sources = self.extract_player_sources()
                
                # Para cada fonte, navegar e capturar
                for source_url in sources[:5]:  # Limitar a 5 fontes
                    self.log(f"Testando fonte: {source_url[:60]}...")
                    
                    videos = self.navigate_to_iframe_and_capture(source_url, wait_time=12)
                    all_videos.extend(videos)
                    
                    if videos:
                        self.log(f"Encontrados {len(videos)} vídeos nesta fonte!", "SUCCESS")
            
            # Se não encontrou nenhum, tentar método alternativo
            if not all_videos and iframes:
                self.log("Tentando método alternativo com todos os iframes...")
                for iframe in iframes[:3]:
                    videos = self.navigate_to_iframe_and_capture(iframe)
                    all_videos.extend(videos)
            
        except Exception as e:
            self.log(f"Erro na captura: {e}", "ERROR")
        
        return all_videos
    
    def capture_from_player_url(self, player_url: str, wait_time: int = 20) -> List[VideoSource]:
        """Captura diretamente de uma URL de player"""
        self.log(f"=== Capturando de player direto: {player_url} ===", "INFO")
        
        all_videos = []
        
        try:
            videos = self.navigate_to_iframe_and_capture(player_url, wait_time)
            all_videos.extend(videos)
            
            # Se é um player com múltiplas fontes, tentar cada uma
            sources = self.extract_player_sources()
            
            for source_url in sources[:5]:
                self.log(f"Testando fonte adicional: {source_url[:60]}...")
                videos = self.navigate_to_iframe_and_capture(source_url, wait_time=12)
                all_videos.extend(videos)
                
        except Exception as e:
            self.log(f"Erro: {e}", "ERROR")
        
        return all_videos
    
    def run(self, url: str) -> Dict:
        """Executa captura completa"""
        self.log("=" * 60)
        self.log("CAPTURA DE VÍDEO COM SELENIUM INDETECTÁVEL")
        self.log("=" * 60)
        
        results = {
            "input_url": url,
            "videos": [],
            "total_requests": 0,
            "started_at": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            # Iniciar driver
            self.driver = self.create_driver()
            self.log("Driver iniciado com sucesso!", "SUCCESS")
            
            # Determinar tipo de URL e capturar
            if 'maxseries' in url.lower():
                videos = self.capture_episode_from_maxseries(url)
            elif any(host in url.lower() for host in self.HARD_HOSTS):
                videos = self.capture_from_player_url(url)
            else:
                # Genérico
                videos = self.navigate_to_iframe_and_capture(url, wait_time=20)
            
            # Remover duplicatas
            unique_videos = []
            seen = set()
            for v in videos:
                if v.url not in seen:
                    seen.add(v.url)
                    unique_videos.append(v)
            
            self.found_videos = unique_videos
            
            # Preparar resultados
            results["videos"] = [asdict(v) for v in unique_videos]
            results["total_requests"] = len(self.network_requests)
            results["success"] = len(unique_videos) > 0
            results["finished_at"] = datetime.now().isoformat()
            
            # Log resumo
            self.log("=" * 60)
            self.log("RESULTADOS")
            self.log("=" * 60)
            self.log(f"Total de requisições capturadas: {len(self.network_requests)}")
            self.log(f"Vídeos encontrados: {len(unique_videos)}")
            
            for i, video in enumerate(unique_videos, 1):
                self.log(f"{i}. [{video.host}] {video.url}", "VIDEO")
                
        except Exception as e:
            self.log(f"Erro fatal: {e}", "ERROR")
            results["error"] = str(e)
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.log("Driver encerrado", "INFO")
                except:
                    pass
        
        return results
    
    def save_results(self, results: Dict, filename: str = None):
        """Salva resultados em arquivo JSON"""
        if not filename:
            filename = f"video_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"Resultados salvos em: {filename}", "SUCCESS")


def main():
    """Função principal"""
    # URL padrão para teste
    default_url = "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"
    
    # Verificar argumentos
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print("\n" + "=" * 70)
    print("  UNDETECTED VIDEO CAPTURE - Selenium Anti-Bot Bypass")
    print("  Para uso com Cloudstream plugins")
    print("=" * 70)
    print(f"\n  URL: {url}\n")
    
    # Criar capturador
    capturer = UndetectedVideoCapture(
        headless=False,  # Mude para True para rodar sem janela
        verbose=True
    )
    
    # Executar captura
    results = capturer.run(url)
    
    # Salvar resultados
    capturer.save_results(results)
    
    # Mostrar vídeos encontrados
    if results.get('videos'):
        print("\n" + "=" * 70)
        print("  VÍDEOS ENCONTRADOS - Use estas URLs no Cloudstream")
        print("=" * 70)
        
        for i, video in enumerate(results['videos'], 1):
            print(f"\n  {i}. Host: {video['host']}")
            print(f"     Tipo: {video['source_type']}")
            print(f"     URL:  {video['url']}")
            if video.get('quality'):
                print(f"     Qualidade: {video['quality']}")
    else:
        print("\n  ❌ Nenhum vídeo encontrado.")
        print("     Tente com uma URL diferente ou verifique se o site está online.")
    
    print("\n")
    return results


if __name__ == "__main__":
    main()
