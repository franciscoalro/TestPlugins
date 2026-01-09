#!/usr/bin/env python3
"""
Teste com Selenium para extrair links de vídeo do MaxSeries
"""
import time
import re
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_PATH = r'D:\geckodriver.exe'
FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'

def setup_driver():
    """Configura Firefox com Selenium"""
    options = Options()
    options.binary_location = FIREFOX_PATH
    # options.add_argument('--headless')  # Comentado para ver o que acontece
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def extract_video_url(driver, player_url):
    """Tenta extrair URL de vídeo do player"""
    print(f'\n🔍 Carregando player: {player_url[:60]}...')
    
    try:
        driver.get(player_url)
        time.sleep(5)  # Esperar JavaScript carregar
        
        # Procurar elemento de vídeo
        video_elements = driver.find_elements(By.TAG_NAME, 'video')
        for video in video_elements:
            src = video.get_attribute('src')
            if src and ('m3u8' in src or 'mp4' in src):
                print(f'✅ Video src: {src[:80]}...')
                return src
        
        # Procurar source dentro de video
        sources = driver.find_elements(By.CSS_SELECTOR, 'video source')
        for source in sources:
            src = source.get_attribute('src')
            if src and ('m3u8' in src or 'mp4' in src):
                print(f'✅ Source src: {src[:80]}...')
                return src
        
        # Procurar no JavaScript da página
        page_source = driver.page_source
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Regex match: {m[:80]}...')
                    return m
        
        # Verificar network requests (se possível)
        print('  Nenhum vídeo encontrado no HTML')
        
        # Tentar clicar em play se existir
        try:
            play_btn = driver.find_element(By.CSS_SELECTOR, '.play-button, .vjs-big-play-button, [class*="play"]')
            play_btn.click()
            time.sleep(3)
            
            # Verificar novamente
            video_elements = driver.find_elements(By.TAG_NAME, 'video')
            for video in video_elements:
                src = video.get_attribute('src')
                if src and ('m3u8' in src or 'mp4' in src):
                    print(f'✅ Video após play: {src[:80]}...')
                    return src
        except:
            pass
            
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
    """Reproduz no VLC"""
    print(f'\n🎬 Abrindo VLC...')
    
    vlc_paths = [
        r'C:\Program Files\VideoLAN\VLC\vlc.exe',
        r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe',
    ]
    
    vlc_path = None
    for path in vlc_paths:
        try:
            subprocess.run([path, '--version'], capture_output=True, timeout=5)
            vlc_path = path
            break
        except:
            continue
    
    if not vlc_path:
        print('❌ VLC não encontrado!')
        print(f'\n📋 Copie e abra manualmente:')
        print(video_url)
        return False
    
    cmd = [vlc_path, video_url]
    if referer:
        cmd.extend(['--http-referrer', referer])
    
    subprocess.Popen(cmd)
    print('✅ VLC aberto!')
    return True

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC (Selenium)')
    print('=' * 60)
    
    # Players encontrados anteriormente
    players = [
        {'name': 'PlayerEmbedAPI', 'url': 'https://playerembedapi.link/?v=o_4s_DFJuL'},
        {'name': 'MegaEmbed', 'url': 'https://megaembed.link/#rckhv6'},
        {'name': 'Bysebuho', 'url': 'https://bysebuho.com/e/cnox47bzdraa'},
    ]
    
    print('\n🚀 Iniciando Firefox...')
    driver = setup_driver()
    
    video_url = None
    
    try:
        for player in players:
            video_url = extract_video_url(driver, player['url'])
            if video_url:
                print(f'\n✅ Vídeo encontrado via {player["name"]}!')
                break
        
        if video_url:
            print('\n' + '=' * 60)
            print('✅ SUCESSO!')
            print(f'URL: {video_url}')
            print('=' * 60)
            
            # Fechar browser antes de abrir VLC
            driver.quit()
            play_in_vlc(video_url)
        else:
            print('\n' + '=' * 60)
            print('❌ Não foi possível extrair link direto')
            print('Os players usam proteção anti-scraping')
            print('=' * 60)
            driver.quit()
            
    except Exception as e:
        print(f'❌ Erro: {e}')
        driver.quit()

if __name__ == '__main__':
    main()
