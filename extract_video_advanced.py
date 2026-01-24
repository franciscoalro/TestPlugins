#!/usr/bin/env python3
"""
Script Avançado para Extração de Vídeos - MaxSeries (com Selenium)
Uso: python extract_video_advanced.py <URL_DO_EPISODIO>
Requer: pip install selenium webdriver-manager
"""

import sys
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MaxSeriesVideoExtractor:
    def __init__(self):
        self.driver = None
        self.captured_urls = []
        
    def setup_driver(self):
        """Configura o Chrome com captura de rede"""
        print("🔧 Configurando navegador...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Modo invisível
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Habilitar logs de rede
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-detecção
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
        print("✅ Navegador configurado\n")
    
    def capture_network_traffic(self):
        """Captura requisições de rede"""
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                if log['method'] == 'Network.responseReceived':
                    url = log['params']['response']['url']
                    
                    # Filtrar URLs de vídeo
                    if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.ts', '.woff2']):
                        if url not in self.captured_urls:
                            self.captured_urls.append(url)
                            print(f"  📡 Capturado: {url}")
                            
            except Exception:
                pass
    
    def extract_from_episode(self, episode_url):
        """Extrai vídeos de um episódio"""
        print(f"🔍 Analisando: {episode_url}\n")
        
        try:
            # 1. Acessar página do episódio
            print("📥 Carregando página do episódio...")
            self.driver.get(episode_url)
            time.sleep(3)
            
            # 2. Encontrar iframes
            print("🎬 Procurando players...")
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            
            print(f"   Encontrados {len(iframes)} players\n")
            
            results = []
            
            for idx, iframe in enumerate(iframes, 1):
                src = iframe.get_attribute('src')
                if not src:
                    continue
                
                print(f"🎥 Player {idx}: {src}")
                
                # Identificar tipo
                player_type = "Desconhecido"
                if 'megaembed' in src.lower():
                    player_type = "MegaEmbed"
                elif 'playerembedapi' in src.lower() or 'playerthree' in src.lower():
                    player_type = "PlayerEmbedAPI"
                elif 'doodstream' in src.lower():
                    player_type = "DoodStream"
                
                print(f"   Tipo: {player_type}")
                
                # 3. Acessar iframe e capturar tráfego
                print(f"   🔄 Acessando player...")
                
                original_window = self.driver.current_window_handle
                
                try:
                    # Abrir em nova aba
                    self.driver.execute_script(f"window.open('{src}', '_blank');")
                    time.sleep(2)
                    
                    # Mudar para nova aba
                    windows = self.driver.window_handles
                    self.driver.switch_to.window(windows[-1])
                    
                    # Aguardar carregamento
                    print(f"   ⏳ Aguardando vídeo carregar...")
                    time.sleep(8)
                    
                    # Capturar tráfego
                    self.capture_network_traffic()
                    
                    # Fechar aba
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    
                    print(f"   ✅ Player {idx} processado\n")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao processar player: {str(e)}\n")
                    self.driver.switch_to.window(original_window)
                
                results.append({
                    'index': idx,
                    'url': src,
                    'type': player_type
                })
            
            # 4. Resumo
            print("\n" + "="*60)
            print("📊 RESUMO DA EXTRAÇÃO")
            print("="*60)
            
            if self.captured_urls:
                print(f"\n✅ {len(self.captured_urls)} URLs de vídeo capturadas:\n")
                for url in self.captured_urls:
                    print(f"   🎬 {url}")
            else:
                print("\n⚠️  Nenhuma URL de vídeo capturada diretamente")
                print("   Possíveis causas:")
                print("   - Vídeo requer interação manual (clique no play)")
                print("   - Player usa criptografia avançada")
                print("   - Necessário aguardar mais tempo")
            
            print("\n" + "="*60)
            
            return results
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return []
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python extract_video_advanced.py <URL_DO_EPISODIO>")
        print("   Exemplo: python extract_video_advanced.py https://maxseries.one/episodio/12345")
        sys.exit(1)
    
    episode_url = sys.argv[1]
    
    if not episode_url.startswith('http'):
        print("❌ URL inválida. Deve começar com http:// ou https://")
        sys.exit(1)
    
    extractor = MaxSeriesVideoExtractor()
    
    try:
        extractor.setup_driver()
        results = extractor.extract_from_episode(episode_url)
        
        if results:
            print("\n✅ Extração concluída!")
        else:
            print("\n❌ Nenhum resultado obtido")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
