"""
MaxSeries Undetectable Extractor - FIXED VERSION
Usando apenas undetected-chromedriver (sem Selenium Wire)

Este script evita detecção de automação e captura URLs de vídeo reais
"""

import undetected_chromedriver as uc
import time
import json
import re
from datetime import datetime


class MaxSeriesUndetectableExtractor:
    def __init__(self):
        """Inicializa com undetected-chromedriver"""
        
        print("[INIT] Configurando navegador indetectavel...")
        
        # Criar driver indetectável
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-popup-blocking')
        
        # Habilitar logs de performance para capturar requisições de rede
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = uc.Chrome(
            options=options,
            version_main=None  # Auto-detect Chrome version
        )
        
        print("[OK] Navegador iniciado com sucesso\n")
        
    def extract_video_urls(self, series_url, episode_index=0):
        """
        Extrai URLs de vídeo do MaxSeries
        
        Args:
            series_url: URL da série
            episode_index: Índice do episódio (0 = primeiro)
        
        Returns:
            Lista de URLs de vídeo
        """
        print(f"{'='*80}")
        print(f"[*] MAXSERIES UNDETECTABLE EXTRACTOR")
        print(f"{'='*80}\n")
        
        video_urls = []
        
        try:
            # PASSO 1: Acessar maxseries.one
            print("[1/8] Acessando maxseries.one...")
            self.driver.get(series_url)
            time.sleep(5)  # Aguardar mais tempo para evitar detecção
            
            # PASSO 2: Clicar no episódio
            print(f"[2/8] Clicando no episodio #{episode_index + 1}...")
            self._click_episode(episode_index)
            time.sleep(4)
            
            # PASSO 3: Extrair URL do playerthree.online
            print("[3/8] Extraindo URL do playerthree.online...")
            playerthree_url = self._extract_iframe_url('playerthree')
            
            if not playerthree_url:
                print("[!] ERRO: Iframe playerthree.online nao encontrado")
                return []
            
            print(f"[+] Encontrado: {playerthree_url}")
            
            # PASSO 4: Acessar playerthree.online
            print("[4/8] Acessando playerthree.online...")
            self.driver.get(playerthree_url)
            time.sleep(5)
            
            # PASSO 5: Selecionar Player #1
            print("[5/8] Selecionando Player #1...")
            self._select_player()
            time.sleep(5)  # Aguardar iframe carregar
            
            # PASSO 6: Extrair URL do playerembedapi.link
            print("[6/8] Procurando iframe playerembedapi.link...")
            playerembed_url = self._extract_iframe_url('playerembed')
            
            if playerembed_url:
                print(f"[+] Encontrado: {playerembed_url}")
                
                print("[7/8] Acessando playerembedapi.link...")
                self.driver.execute_script(f'window.location.href = "{playerembed_url}";')
                time.sleep(5)
            else:
                print("[!] AVISO: Iframe playerembedapi nao encontrado")
                print("[!] Continuando na pagina atual...")
            
            # PASSO 7: Injetar bloqueador de popups
            print("[8/8] Injetando bloqueador de popups...")
            self._inject_popup_blocker()
            
            # Clicar no play (2 vezes)
            print("\n[PLAY] Clicando no play (1a vez - popup trap)...")
            self._click_play()
            time.sleep(3)
            
            print("[PLAY] Clicando no play (2a vez - video real)...")
            self._click_play()
            time.sleep(3)
            
            # Aguardar vídeo carregar
            print("[WAIT] Aguardando video carregar (20 segundos)...")
            time.sleep(20)
            
            # ANÁLISE: Capturar URLs de vídeo via Performance Logs
            print("\n[ANALISE] Analisando requisicoes via Performance Logs...")
            video_urls = self._analyze_performance_logs()
            
            # Também extrair do JavaScript
            print("[ANALISE] Extraindo URLs do JavaScript da pagina...")
            js_urls = self._extract_from_javascript()
            video_urls.extend(js_urls)
            
            # Extrair do DOM (elementos video/source)
            print("[ANALISE] Extraindo URLs do DOM (elementos video)...")
            dom_urls = self._extract_from_dom()
            video_urls.extend(dom_urls)
            
            # Remover duplicatas
            video_urls = list(set(video_urls))
            
            # Exibir resultados
            self._print_results(video_urls)
            
        except Exception as e:
            print(f"\n[!] ERRO: {e}")
            import traceback
            traceback.print_exc()
        
        return video_urls
    
    def _click_episode(self, index):
        """Clica no episódio"""
        try:
            self.driver.execute_script("""
                const elements = Array.from(document.querySelectorAll('*'));
                const target = elements.find(el => 
                    el.textContent.includes("You") && 
                    el.textContent.includes("Been") &&
                    el.offsetWidth > 0
                );
                if (target) target.click();
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
                window.open = function() {
                    console.log('[BLOQUEADO] Popup bloqueado');
                    return null;
                };
            """)
        except:
            pass
    
    def _click_play(self):
        """Clica no play"""
        try:
            self.driver.execute_script("""
                // Tentar clicar no vídeo
                const video = document.querySelector('video');
                if (video) {
                    video.click();
                    return;
                }
                
                // Clicar no centro
                const centerX = window.innerWidth / 2;
                const centerY = window.innerHeight / 2;
                const element = document.elementFromPoint(centerX, centerY);
                if (element) element.click();
            """)
        except:
            pass
    
    def _analyze_performance_logs(self):
        """Analisa Performance Logs para capturar requisições de rede"""
        video_urls = []
        
        try:
            logs = self.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    
                    # Procurar requisições de rede
                    if log['method'] == 'Network.requestWillBeSent':
                        url = log['params']['request']['url']
                        
                        # Procurar extensões de vídeo
                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.ts', 'playlist', 'manifest']):
                            video_urls.append(url)
                            print(f"[+] VIDEO URL (Performance): {url[:80]}...")
                            
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] Erro ao analisar Performance Logs: {e}")
        
        return video_urls
    
    def _extract_from_javascript(self):
        """Extrai URLs do JavaScript"""
        try:
            page_source = self.driver.page_source
            urls = []
            
            # Regex para .m3u8
            m3u8_pattern = r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*'
            m3u8_urls = re.findall(m3u8_pattern, page_source)
            urls.extend(m3u8_urls)
            
            # Regex para .mp4
            mp4_pattern = r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*'
            mp4_urls = re.findall(mp4_pattern, page_source)
            urls.extend(mp4_urls)
            
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
    
    def _print_results(self, video_urls):
        """Imprime resultados"""
        print(f"\n{'='*80}")
        print("[RESULTADOS]")
        print(f"{'='*80}\n")
        
        if video_urls:
            print(f"[SUCCESS] Encontradas {len(video_urls)} URLs de video:\n")
            for i, url in enumerate(video_urls, 1):
                print(f"[{i}] {url}\n")
        else:
            print("[!] NENHUMA URL DE VIDEO ENCONTRADA")
            print("\n[DICA] O site pode estar usando:")
            print("  - WebRTC/P2P (nao usa HTTP)")
            print("  - Lazy loading extremo")
            print("  - Protecao anti-bot muito avancada")
        
        print(f"{'='*80}\n")
    
    def save_results(self, video_urls, filename='maxseries_undetectable_results.json'):
        """Salva resultados"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'video_urls': video_urls,
            'total': len(video_urls)
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
    extractor = MaxSeriesUndetectableExtractor()
    
    try:
        # Extrair URLs
        video_urls = extractor.extract_video_urls(
            series_url="https://www.maxseries.one/series/assistir-terra-de-pecados-online",
            episode_index=0
        )
        
        # Salvar
        if video_urls:
            extractor.save_results(video_urls)
        
    finally:
        input("\n[PAUSE] Pressione ENTER para fechar...")
        extractor.close()
