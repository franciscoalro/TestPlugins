#!/usr/bin/env python3
"""
Captura de URLs de Vídeo - V4 FINAL
Foco em capturar URLs FINAIS de vídeo (.m3u8, .mp4) após decriptação JS

Uso: python undetected-video-capture-v4.py [URL_DO_PLAYER]
"""

import json
import time
import random
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


@dataclass
class VideoURL:
    url: str
    source_type: str
    quality: Optional[str] = None
    headers: Dict = None


class FinalVideoCapture:
    """Captura URLs finais de vídeo (.m3u8, .mp4)"""
    
    # Padrões específicos de URL de vídeo FINAL
    FINAL_VIDEO_PATTERNS = [
        '.m3u8',
        '.mp4',
        '/hls/',
        'master.m3u8',
        '/video/',
        'index.m3u8',
        'playlist.m3u8',
        '.ts',
        'googlevideo.com',
        'akamaized.net',
        'cloudfront.net',
        'storage.googleapis.com',
    ]
    
    # Padrões a ignorar
    IGNORE_PATTERNS = [
        'google-analytics',
        'analytics',
        'facebook',
        'ad.',
        'ads.',
        'tracking',
        '.css',
        '.js',
        '.png',
        '.jpg',
        '.gif',
        '.ico',
        '.woff',
        'mc.yandex',
        'cdn-cgi/rum',
    ]
    
    def __init__(self, headless: bool = False, verbose: bool = True):
        self.headless = headless
        self.verbose = verbose
        self.driver = None
        self.captured_videos: List[VideoURL] = []
        
    def log(self, msg: str, level: str = "INFO"):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "VIDEO": "🎬", 
                     "WAIT": "⏳", "DEBUG": "🔍"}.get(level, "")
            print(f"[{ts}] {emoji} {msg}")
    
    def create_driver(self) -> uc.Chrome:
        options = uc.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=pt-BR')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.log("Iniciando Chrome indetectável...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_page_load_timeout(60)
        
        return driver
    
    def is_final_video_url(self, url: str) -> bool:
        """Verifica se é uma URL de vídeo FINAL (não de player/page)"""
        url_lower = url.lower()
        
        # Ignorar padrões indesejados
        if any(p in url_lower for p in self.IGNORE_PATTERNS):
            return False
        
        # Verificar se é URL final de vídeo
        return any(p in url_lower for p in self.FINAL_VIDEO_PATTERNS)
    
    def get_quality(self, url: str) -> Optional[str]:
        """Extrai qualidade da URL"""
        import re
        patterns = [r'(\d{3,4})p', r'/(\d{3,4})/', r'_(\d{3,4})\.']
        for p in patterns:
            match = re.search(p, url)
            if match:
                return f"{match.group(1)}p"
        return None
    
    def capture_network_videos(self, wait_seconds: int = 20) -> List[VideoURL]:
        """Captura URLs de vídeo das requisições de rede"""
        videos = []
        seen = set()
        
        self.log(f"Aguardando {wait_seconds}s para capturar requisições de vídeo...", "WAIT")
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
                            headers = req.get('headers', {})
                        else:
                            resp = msg.get('params', {}).get('response', {})
                            url = resp.get('url', '')
                            headers = resp.get('headers', {})
                        
                        if url and self.is_final_video_url(url) and url not in seen:
                            seen.add(url)
                            
                            source_type = 'm3u8' if '.m3u8' in url.lower() else 'mp4'
                            quality = self.get_quality(url)
                            
                            video = VideoURL(
                                url=url,
                                source_type=source_type,
                                quality=quality,
                                headers=dict(headers) if headers else {}
                            )
                            videos.append(video)
                            self.log(f"VÍDEO FINAL: {url[:100]}", "VIDEO")
                            
                except Exception:
                    pass
                    
        except Exception as e:
            self.log(f"Erro captura: {e}", "ERROR")
            
        return videos
    
    def capture_from_player(self, player_url: str, wait_seconds: int = 25) -> List[VideoURL]:
        """Navega para player e captura URLs finais"""
        videos = []
        
        try:
            self.log(f"Acessando player: {player_url[:60]}...")
            self.driver.get(player_url)
            time.sleep(random.uniform(3, 5))
            
            # Primeira captura
            videos.extend(self.capture_network_videos(wait_seconds))
            
            # Verificar elementos video
            try:
                video_els = self.driver.find_elements(By.TAG_NAME, 'video')
                for vel in video_els:
                    src = vel.get_attribute('src') or ''
                    if src and self.is_final_video_url(src):
                        videos.append(VideoURL(url=src, source_type='direct'))
                        self.log(f"Video element: {src[:80]}", "VIDEO")
                    
                    # currentSrc
                    try:
                        cs = self.driver.execute_script("return arguments[0].currentSrc", vel)
                        if cs and self.is_final_video_url(cs) and cs != src:
                            videos.append(VideoURL(url=cs, source_type='currentSrc'))
                            self.log(f"currentSrc: {cs[:80]}", "VIDEO")
                    except:
                        pass
            except:
                pass
            
            # Tentar capturar via jwplayer/player JS
            try:
                js_url = self.driver.execute_script("""
                    // Tentar jwplayer
                    if (typeof jwplayer !== 'undefined' && jwplayer().getPlaylistItem) {
                        var item = jwplayer().getPlaylistItem();
                        if (item && item.file) return item.file;
                    }
                    // Tentar player genérico
                    if (window.player && window.player.source) {
                        return window.player.source;
                    }
                    // Tentar variáveis globais
                    if (window.videoSource) return window.videoSource;
                    if (window.hlsUrl) return window.hlsUrl;
                    if (window.videoUrl) return window.videoUrl;
                    return null;
                """)
                if js_url and self.is_final_video_url(js_url):
                    videos.append(VideoURL(url=js_url, source_type='js'))
                    self.log(f"JS variable: {js_url[:80]}", "VIDEO")
            except:
                pass
                
        except Exception as e:
            self.log(f"Erro no player: {e}", "ERROR")
            
        return videos
    
    def run(self, url: str) -> Dict:
        """Executa captura"""
        print("\n" + "=" * 70)
        print("  FINAL VIDEO CAPTURE V4")
        print("  Captura URLs finais .m3u8 e .mp4")
        print("=" * 70)
        print(f"\n  URL: {url}\n")
        
        self.log("=" * 60)
        self.log("INICIANDO CAPTURA V4")
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
            
            # Capturar vídeos
            videos = self.capture_from_player(url, wait_seconds=30)
            
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
            self.log(f"URLs de vídeo capturadas: {len(unique)}")
            
            for i, v in enumerate(unique, 1):
                quality_str = f" ({v.quality})" if v.quality else ""
                self.log(f"{i}. [{v.source_type}]{quality_str} {v.url}", "VIDEO")
                
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
            filename = f"final_video_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.log(f"Salvo: {filename}", "SUCCESS")


def main():
    # URLs de teste - players diretos
    test_urls = {
        "playerembedapi": "https://playerembedapi.link/?v=tx3jQLbTT",
        "megaembed": "https://megaembed.link/#dqd1uk"
    }
    
    # URL do argumento ou primeira disponível
    url = sys.argv[1] if len(sys.argv) > 1 else test_urls["megaembed"]
    
    capturer = FinalVideoCapture(headless=False, verbose=True)
    results = capturer.run(url)
    capturer.save(results)
    
    if results.get('videos'):
        print("\n" + "=" * 70)
        print("  ✅ URLs FINAIS DE VÍDEO")
        print("=" * 70)
        
        for i, v in enumerate(results['videos'], 1):
            print(f"\n  {i}. Tipo: {v['source_type']}")
            if v.get('quality'):
                print(f"     Qualidade: {v['quality']}")
            print(f"     URL: {v['url']}")
            
        print("\n  💡 Use estas URLs diretamente no player do Cloudstream!")
    else:
        print("\n  ❌ Nenhuma URL final de vídeo capturada.")
        print("     O site pode usar proteção adicional ou o vídeo pode estar indisponível.")
    
    print()
    return results


if __name__ == "__main__":
    main()
