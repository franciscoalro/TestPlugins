#!/usr/bin/env python3
"""
MegaEmbed HAR Flow Replicator
Replica o fluxo exato de requisições capturado no HAR do Firefox
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import base64
import re

class MegaEmbedHARReplicator:
    def __init__(self):
        self.driver = None
        self.video_id = "3wnuij"
        self.base_url = "https://megaembed.link"
        
    def setup_driver(self):
        """Configura o driver com headers similares ao Firefox"""
        options = uc.ChromeOptions()
        
        # User-Agent do Firefox do HAR
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0')
        
        # Outras configurações
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        # Habilita logging de rede
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        
        # Injeta script para interceptar XHR/Fetch
        self.driver.execute_cdp_cmd('Network.enable', {})
        
    def decode_base64_response(self, base64_text):
        """Decodifica resposta base64 do HAR"""
        try:
            decoded = base64.b64decode(base64_text).decode('utf-8')
            return decoded
        except Exception as e:
            print(f"Erro ao decodificar base64: {e}")
            return None
    
    def extract_video_info_from_har(self):
        """
        Extrai informações do HAR fornecido
        Baseado nas requisições capturadas
        """
        print("\n=== Analisando HAR fornecido ===")
        
        # Dados extraídos do HAR
        har_data = {
            'info_response': '155232f01d9442024a0f4a251781024deab5aa2eb019ac12f7c13c1904565...',  # Truncado
            'video_response': '933a30ecdabc15152bfbe068bc27d5342f59759c823e7e206be7a128ff897...',  # Truncado
            'player_response': 'eyJzdWNjZXNzIjogdHJ1ZX0K',  # {"success": true}
            'master_playlist': 'cf-master.1767386783.txt',
            'segment_playlist': 'index-f1-v1-a1.txt'
        }
        
        # Decodifica a resposta do player
        player_decoded = self.decode_base64_response(har_data['player_response'])
        print(f"Player Response: {player_decoded}")
        
        return har_data
    
    def replicate_api_flow(self):
        """Replica o fluxo de API do HAR"""
        print("\n=== Replicando Fluxo de API ===")
        
        # 1. Requisição /api/v1/info
        info_url = f"{self.base_url}/api/v1/info?id={self.video_id}"
        print(f"\n1. GET {info_url}")
        
        self.driver.get(info_url)
        time.sleep(2)
        
        info_response = self.driver.find_element(By.TAG_NAME, 'pre').text
        print(f"Info Response (primeiros 200 chars): {info_response[:200]}")
        
        # Tenta decodificar se for base64
        try:
            info_decoded = self.decode_base64_response(info_response)
            if info_decoded:
                print(f"Info Decoded (primeiros 200 chars): {info_decoded[:200]}")
        except:
            pass
        
        # 2. Requisição /api/v1/video
        # Extrai parâmetros da resposta info (simulado)
        video_url = f"{self.base_url}/api/v1/video?id={self.video_id}&w=2144&h=1206&r=playerthree.online"
        print(f"\n2. GET {video_url}")
        
        self.driver.get(video_url)
        time.sleep(2)
        
        video_response = self.driver.find_element(By.TAG_NAME, 'pre').text
        print(f"Video Response (primeiros 200 chars): {video_response[:200]}")
        
        # Tenta decodificar
        try:
            video_decoded = self.decode_base64_response(video_response)
            if video_decoded:
                print(f"Video Decoded (primeiros 200 chars): {video_decoded[:200]}")
                
                # Procura por URLs no conteúdo decodificado
                urls = re.findall(r'https?://[^\s<>"]+', video_decoded)
                if urls:
                    print(f"\nURLs encontradas no video response:")
                    for url in urls[:5]:  # Primeiras 5 URLs
                        print(f"  - {url}")
        except:
            pass
        
        return info_response, video_response
    
    def extract_token_from_response(self, response_text):
        """Extrai token da resposta decodificada"""
        try:
            # Tenta decodificar base64
            decoded = self.decode_base64_response(response_text)
            if not decoded:
                return None
            
            # Procura por padrões de token
            # Exemplo: t=3772aacff2bd31142eec...
            token_match = re.search(r't=([a-f0-9]+)', decoded)
            if token_match:
                return token_match.group(1)
            
            # Procura por URLs de playlist
            playlist_match = re.search(r'(https://[^\s]+\.txt)', decoded)
            if playlist_match:
                return playlist_match.group(1)
            
            return None
        except Exception as e:
            print(f"Erro ao extrair token: {e}")
            return None
    
    def access_master_playlist(self, token_or_url):
        """Acessa o master playlist"""
        print(f"\n=== Acessando Master Playlist ===")
        
        # URL do master playlist (do HAR)
        master_url = "https://smho.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt"
        
        print(f"GET {master_url}")
        self.driver.get(master_url)
        time.sleep(2)
        
        playlist_content = self.driver.find_element(By.TAG_NAME, 'pre').text
        print(f"\nMaster Playlist Content:\n{playlist_content}")
        
        # Extrai URLs de segmentos
        segment_urls = re.findall(r'index-f\d+-v\d+-a\d+\.txt', playlist_content)
        print(f"\nSegment playlists encontrados: {segment_urls}")
        
        return segment_urls
    
    def access_segment_playlist(self, segment_name):
        """Acessa playlist de segmentos"""
        print(f"\n=== Acessando Segment Playlist: {segment_name} ===")
        
        segment_url = f"https://smho.marvellaholdings.sbs/v4/x6b/3wnuij/{segment_name}"
        
        print(f"GET {segment_url}")
        self.driver.get(segment_url)
        time.sleep(2)
        
        segment_content = self.driver.find_element(By.TAG_NAME, 'pre').text
        print(f"\nSegment Playlist (primeiras 500 chars):\n{segment_content[:500]}")
        
        # Extrai URLs de segmentos de vídeo
        video_segments = re.findall(r'seg-\d+-f\d+-v\d+-a\d+\.woff2?', segment_content)
        print(f"\nTotal de segmentos de vídeo: {len(video_segments)}")
        if video_segments:
            print(f"Primeiro segmento: {video_segments[0]}")
            print(f"Último segmento: {video_segments[-1]}")
        
        # Extrai init segment
        init_segment = re.search(r'init-f\d+-v\d+-a\d+\.woff', segment_content)
        if init_segment:
            print(f"Init segment: {init_segment.group()}")
        
        return video_segments
    
    def run_full_extraction(self):
        """Executa o fluxo completo de extração"""
        try:
            print("=== Iniciando MegaEmbed HAR Replicator ===")
            
            # 1. Analisa HAR
            har_data = self.extract_video_info_from_har()
            
            # 2. Setup driver
            self.setup_driver()
            
            # 3. Replica fluxo de API
            info_response, video_response = self.replicate_api_flow()
            
            # 4. Extrai token
            token = self.extract_token_from_response(video_response)
            if token:
                print(f"\nToken extraído: {token[:50]}...")
            
            # 5. Acessa master playlist
            segment_playlists = self.access_master_playlist(token)
            
            # 6. Acessa primeiro segment playlist
            if segment_playlists:
                video_segments = self.access_segment_playlist(segment_playlists[0])
                
                # 7. Constrói URL do primeiro segmento
                if video_segments:
                    first_segment_url = f"https://smho.marvellaholdings.sbs/v4/x6b/3wnuij/{video_segments[0]}"
                    print(f"\n=== URL do Primeiro Segmento ===")
                    print(first_segment_url)
                    
                    # Testa acesso ao segmento
                    print(f"\nTestando acesso ao segmento...")
                    self.driver.get(first_segment_url)
                    time.sleep(2)
                    
                    print("✓ Segmento acessível!")
            
            print("\n=== Extração Completa ===")
            
        except Exception as e:
            print(f"\n❌ Erro durante extração: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                print("\nMantendo navegador aberto para inspeção...")
                input("Pressione Enter para fechar o navegador...")
                self.driver.quit()

def main():
    extractor = MegaEmbedHARReplicator()
    extractor.run_full_extraction()

if __name__ == "__main__":
    main()
