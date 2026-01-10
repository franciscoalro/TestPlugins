"""
MaxSeries Advanced Video Capture
Captura APIs de vídeo player e URLs de conteúdo usando Chrome DevTools Protocol
"""

import undetected_chromedriver as uc
import time
import json
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs


class MaxSeriesAdvancedCapture:
    def __init__(self):
        """Inicializa com undetected-chromedriver + CDP"""
        
        print("[INIT] Configurando navegador com CDP...")
        
        # Configurar Chrome com logging de performance
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--enable-logging')
        options.add_argument('--v=1')
        
        # Habilitar CDP (Chrome DevTools Protocol)
        options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        self.driver = uc.Chrome(
            options=options,
            version_main=None
        )
        
        # Habilitar Network tracking via CDP
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        print("[OK] Navegador iniciado com CDP ativado\n")
        
        # Armazenar requisições capturadas
        self.captured_requests = []
        
    def extract_video_content(self, series_url, episode_index=0, wait_time=30):
        """
        Extrai URLs de vídeo e APIs de player
        
        Args:
            series_url: URL da série
            episode_index: Índice do episódio
            wait_time: Tempo de espera para captura (segundos)
        """
        print(f"{'='*80}")
        print(f"[*] MAXSERIES ADVANCED VIDEO CAPTURE")
        print(f"{'='*80}\n")
        
        video_data = {
            'video_urls': [],
            'player_apis': [],
            'iframes': [],
            'all_requests': []
        }
        
        try:
            # PASSO 1: Acessar maxseries.one
            print("[1/9] Acessando maxseries.one...")
            self.driver.get(series_url)
            time.sleep(5)
            
            # PASSO 2: Clicar no episódio
            print(f"[2/9] Clicando no episodio #{episode_index + 1}...")
            self._click_episode(episode_index)
            time.sleep(4)
            
            # PASSO 3: Capturar todos os iframes
            print("[3/9] Capturando todos os iframes...")
            iframes = self._get_all_iframes()
            video_data['iframes'] = iframes
            
            for i, iframe in enumerate(iframes, 1):
                print(f"  [{i}] {iframe}")
            
            # PASSO 4: Acessar playerthree.online
            print("\n[4/9] Procurando playerthree.online...")
            playerthree_url = self._extract_iframe_url('playerthree')
            
            if playerthree_url:
                print(f"[+] Encontrado: {playerthree_url}")
                print("[5/9] Acessando playerthree.online...")
                self.driver.get(playerthree_url)
                time.sleep(5)
                
                # Selecionar Player #1
                print("[6/9] Selecionando Player #1...")
                self._select_player()
                time.sleep(5)
            else:
                print("[!] playerthree.online nao encontrado, continuando...")
            
            # PASSO 5: Procurar megaembed ou playerembedapi
            print("\n[7/9] Procurando iframes de video player...")
            
            # Tentar megaembed
            megaembed_url = self._extract_iframe_url('megaembed')
            if megaembed_url:
                print(f"[+] MEGAEMBED encontrado: {megaembed_url}")
                print("[8/9] Acessando megaembed...")
                self.driver.get(megaembed_url)
                time.sleep(5)
            else:
                # Tentar playerembedapi
                playerembed_url = self._extract_iframe_url('playerembed')
                if playerembed_url:
                    print(f"[+] PLAYEREMBED encontrado: {playerembed_url}")
                    print("[8/9] Acessando playerembed...")
                    self.driver.get(playerembed_url)
                    time.sleep(5)
                else:
                    print("[!] Nenhum iframe de player encontrado")
            
            # PASSO 6: Injetar popup blocker
            print("\n[9/9] Injetando bloqueador de popups...")
            self._inject_popup_blocker()
            
            # Tentar clicar no play
            print("\n[PLAY] Tentando iniciar video...")
            for attempt in range(3):
                print(f"  Tentativa {attempt + 1}/3...")
                self._click_play()
                time.sleep(3)
            
            # PASSO 7: Aguardar e capturar requisições
            print(f"\n[CAPTURE] Capturando requisicoes por {wait_time} segundos...")
            print("[INFO] Aguarde enquanto o video carrega...\n")
            
            start_time = time.time()
            while (time.time() - start_time) < wait_time:
                elapsed = int(time.time() - start_time)
                remaining = wait_time - elapsed
                print(f"\r[TIMER] {elapsed}s / {wait_time}s (restam {remaining}s)", end='', flush=True)
                time.sleep(1)
            
            print("\n\n[ANALYZE] Analisando dados capturados...")
            
            # Analisar Performance Logs
            video_data['all_requests'] = self._capture_all_network_requests()
            
            # Filtrar URLs de vídeo
            video_data['video_urls'] = self._filter_video_urls(video_data['all_requests'])
            
            # Procurar APIs de player
            video_data['player_apis'] = self._find_player_apis()
            
            # Extrair do JavaScript
            js_urls = self._extract_from_javascript()
            video_data['video_urls'].extend(js_urls)
            
            # Extrair do DOM
            dom_urls = self._extract_from_dom()
            video_data['video_urls'].extend(dom_urls)
            
            # Remover duplicatas
            video_data['video_urls'] = list(set(video_data['video_urls']))
            
            # Exibir resultados
            self._print_results(video_data)
            
        except Exception as e:
            print(f"\n[!] ERRO: {e}")
            import traceback
            traceback.print_exc()
        
        return video_data
    
    def _get_all_iframes(self):
        """Captura todos os iframes da página"""
        try:
            iframes = self.driver.execute_script("""
                const iframes = Array.from(document.querySelectorAll('iframe'));
                return iframes.map(i => ({
                    src: i.src,
                    id: i.id,
                    class: i.className
                }));
            """)
            return [f"{i['src']} (id={i['id']}, class={i['class']})" for i in iframes if i['src']]
        except:
            return []
    
    def _click_episode(self, index):
        """Clica no episódio"""
        try:
            # Tentar múltiplas estratégias
            self.driver.execute_script("""
                // Estratégia 1: Procurar por texto
                const elements = Array.from(document.querySelectorAll('*'));
                let target = elements.find(el => 
                    (el.textContent.includes("You") && el.textContent.includes("Been")) &&
                    el.offsetWidth > 0
                );
                
                // Estratégia 2: Procurar por classe/atributo de episódio
                if (!target) {
                    target = document.querySelector('[class*="episode"], [class*="ep-"], .episodio, .capitulo');
                }
                
                if (target) {
                    target.click();
                    return true;
                }
                return false;
            """)
        except Exception as e:
            print(f"[!] Erro ao clicar no episodio: {e}")
    
    def _extract_iframe_url(self, domain_filter):
        """Extrai URL de iframe"""
        try:
            iframe_url = self.driver.execute_script(f"""
                const iframes = Array.from(document.querySelectorAll('iframe'));
                const target = iframes.find(i => i.src.includes('{domain_filter}'));
                return target ? target.src : null;
            """)
            return iframe_url
        except:
            return None
    
    def _select_player(self):
        """Seleciona Player #1"""
        try:
            self.driver.execute_script("""
                const elements = Array.from(document.querySelectorAll('*'));
                const player1 = elements.find(el => 
                    el.textContent.includes('Player #1') &&
                    el.offsetWidth > 0
                );
                if (player1) player1.click();
            """)
        except Exception as e:
            print(f"[!] Erro ao selecionar player: {e}")
    
    def _inject_popup_blocker(self):
        """Injeta bloqueador de popups"""
        try:
            self.driver.execute_script("""
                // Bloquear window.open
                window.open = function() {
                    console.log('[BLOQUEADO] Popup bloqueado');
                    return null;
                };
                
                // Bloquear target="_blank"
                document.addEventListener('click', function(e) {
                    if (e.target.target === '_blank') {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }, true);
            """)
        except:
            pass
    
    def _click_play(self):
        """Clica no play"""
        try:
            self.driver.execute_script("""
                // Estratégia 1: Elemento <video>
                const video = document.querySelector('video');
                if (video) {
                    video.click();
                    video.play();
                }
                
                // Estratégia 2: Botão play
                const playBtn = document.querySelector('[class*="play"], [aria-label*="play"], .vjs-big-play-button');
                if (playBtn) playBtn.click();
                
                // Estratégia 3: Centro da tela
                const centerX = window.innerWidth / 2;
                const centerY = window.innerHeight / 2;
                const element = document.elementFromPoint(centerX, centerY);
                if (element) element.click();
            """)
        except:
            pass
    
    def _capture_all_network_requests(self):
        """Captura todas as requisições de rede via Performance Logs"""
        all_requests = []
        
        try:
            logs = self.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    
                    if log['method'] == 'Network.requestWillBeSent':
                        request = log['params']['request']
                        url = request['url']
                        
                        all_requests.append({
                            'url': url,
                            'method': request.get('method', 'GET'),
                            'type': log['params'].get('type', 'Unknown')
                        })
                        
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] Erro ao capturar requisições: {e}")
        
        return all_requests
    
    def _filter_video_urls(self, requests):
        """Filtra URLs de vídeo das requisições"""
        video_urls = []
        
        # Extensões e padrões de vídeo
        video_patterns = [
            '.m3u8', '.mpd', '.mp4', '.webm', '.ts',
            'playlist', 'manifest', 'master.m3u8',
            'index.m3u8', 'stream', 'video'
        ]
        
        # Domínios conhecidos de CDN de vídeo
        video_domains = [
            'cloudflare', 'akamai', 'fastly', 'cdn',
            'stream', 'video', 'media', 'vod',
            'megaembed', 'playerembed', 'abyss.to'
        ]
        
        for req in requests:
            url = req['url'].lower()
            
            # Verificar extensões
            if any(pattern in url for pattern in video_patterns):
                video_urls.append(req['url'])
                print(f"[+] VIDEO (pattern): {req['url'][:100]}...")
                continue
            
            # Verificar domínios
            if any(domain in url for domain in video_domains):
                if req['type'] in ['Media', 'XHR', 'Fetch']:
                    video_urls.append(req['url'])
                    print(f"[+] VIDEO (domain): {req['url'][:100]}...")
        
        return video_urls
    
    def _find_player_apis(self):
        """Procura APIs de player de vídeo"""
        try:
            apis = self.driver.execute_script("""
                const apis = [];
                
                // Vidstack
                if (window.vidstack) apis.push({name: 'Vidstack', obj: 'window.vidstack'});
                
                // Video.js
                if (window.videojs) apis.push({name: 'Video.js', obj: 'window.videojs'});
                
                // JW Player
                if (window.jwplayer) apis.push({name: 'JW Player', obj: 'window.jwplayer'});
                
                // Plyr
                if (window.Plyr) apis.push({name: 'Plyr', obj: 'window.Plyr'});
                
                // Clappr
                if (window.Clappr) apis.push({name: 'Clappr', obj: 'window.Clappr'});
                
                // Shaka Player
                if (window.shaka) apis.push({name: 'Shaka Player', obj: 'window.shaka'});
                
                // HLS.js
                if (window.Hls) apis.push({name: 'HLS.js', obj: 'window.Hls'});
                
                // Dash.js
                if (window.dashjs) apis.push({name: 'Dash.js', obj: 'window.dashjs'});
                
                // Procurar elementos <video>
                const videos = Array.from(document.querySelectorAll('video'));
                videos.forEach((v, i) => {
                    apis.push({
                        name: `Video Element #${i+1}`,
                        src: v.src || v.currentSrc,
                        duration: v.duration,
                        readyState: v.readyState
                    });
                });
                
                return apis;
            """)
            
            return apis
        except:
            return []
    
    def _extract_from_javascript(self):
        """Extrai URLs do JavaScript"""
        try:
            page_source = self.driver.page_source
            urls = []
            
            # Padrões de URL
            patterns = [
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+\.mpd[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/playlist[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/manifest[^\s"\'<>]*'
            ]
            
            for pattern in patterns:
                found = re.findall(pattern, page_source, re.IGNORECASE)
                urls.extend(found)
            
            if urls:
                print(f"[+] Encontrado {len(urls)} URLs no JavaScript")
            
            return urls
        except:
            return []
    
    def _extract_from_dom(self):
        """Extrai URLs de elementos <video> e <source>"""
        try:
            urls = self.driver.execute_script("""
                const urls = [];
                
                // Elementos <video>
                document.querySelectorAll('video').forEach(v => {
                    if (v.src) urls.push(v.src);
                    if (v.currentSrc) urls.push(v.currentSrc);
                    
                    // Atributos data-*
                    for (let attr of v.attributes) {
                        if (attr.name.startsWith('data-') && attr.value.includes('http')) {
                            urls.push(attr.value);
                        }
                    }
                });
                
                // Elementos <source>
                document.querySelectorAll('source').forEach(s => {
                    if (s.src) urls.push(s.src);
                });
                
                return urls;
            """)
            
            if urls:
                print(f"[+] Encontrado {len(urls)} URLs no DOM")
            
            return urls
        except:
            return []
    
    def _print_results(self, video_data):
        """Imprime resultados"""
        print(f"\n{'='*80}")
        print("[RESULTADOS FINAIS]")
        print(f"{'='*80}\n")
        
        # Player APIs
        if video_data['player_apis']:
            print(f"[PLAYER APIs] Encontrados {len(video_data['player_apis'])} players:\n")
            for api in video_data['player_apis']:
                print(f"  • {api.get('name', 'Unknown')}")
                if 'src' in api:
                    print(f"    SRC: {api['src']}")
                if 'obj' in api:
                    print(f"    Object: {api['obj']}")
                print()
        
        # URLs de vídeo
        if video_data['video_urls']:
            print(f"[VIDEO URLs] Encontradas {len(video_data['video_urls'])} URLs:\n")
            for i, url in enumerate(video_data['video_urls'], 1):
                print(f"[{i}] {url}\n")
        else:
            print("[!] NENHUMA URL DE VIDEO ENCONTRADA\n")
        
        # Iframes
        if video_data['iframes']:
            print(f"[IFRAMES] Encontrados {len(video_data['iframes'])} iframes:\n")
            for iframe in video_data['iframes']:
                print(f"  • {iframe}")
        
        # Estatísticas
        print(f"\n{'='*80}")
        print("[ESTATISTICAS]")
        print(f"{'='*80}")
        print(f"Total de requisições: {len(video_data['all_requests'])}")
        print(f"URLs de vídeo: {len(video_data['video_urls'])}")
        print(f"Player APIs: {len(video_data['player_apis'])}")
        print(f"Iframes: {len(video_data['iframes'])}")
        print(f"{'='*80}\n")
    
    def save_results(self, video_data, filename='maxseries_advanced_results.json'):
        """Salva resultados"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'video_urls': video_data['video_urls'],
            'player_apis': video_data['player_apis'],
            'iframes': video_data['iframes'],
            'total_requests': len(video_data['all_requests']),
            'statistics': {
                'video_urls_count': len(video_data['video_urls']),
                'player_apis_count': len(video_data['player_apis']),
                'iframes_count': len(video_data['iframes'])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] Resultados salvos em: {filename}")
    
    def close(self):
        """Fecha navegador"""
        self.driver.quit()


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    extractor = MaxSeriesAdvancedCapture()
    
    try:
        # Extrair conteúdo de vídeo
        video_data = extractor.extract_video_content(
            series_url="https://www.maxseries.one/series/assistir-terra-de-pecados-online",
            episode_index=0,
            wait_time=40  # Aguardar 40 segundos capturando
        )
        
        # Salvar resultados
        extractor.save_results(video_data)
        
    finally:
        input("\n[PAUSE] Pressione ENTER para fechar o navegador...")
        extractor.close()
