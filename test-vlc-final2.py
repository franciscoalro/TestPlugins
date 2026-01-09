#!/usr/bin/env python3
"""
Teste final com espera longa e captura de rede
"""
import time
import re
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_PATH = r'D:\geckodriver.exe'
FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'

def setup_driver():
    options = Options()
    options.binary_location = FIREFOX_PATH
    # Não usar headless para ver o que acontece
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def extract_video(driver, url):
    """Extrai vídeo com espera longa"""
    print(f'\n🔍 Carregando: {url}')
    
    try:
        driver.get(url)
        
        # Esperar página carregar completamente
        print('  Aguardando carregamento...')
        time.sleep(15)
        
        # Verificar se há video
        videos = driver.find_elements(By.TAG_NAME, 'video')
        print(f'  Videos encontrados: {len(videos)}')
        
        for v in videos:
            src = v.get_attribute('src')
            print(f'  Video src: {src}')
            if src and ('m3u8' in src or 'mp4' in src or 'blob:' in src):
                if not src.startswith('blob:'):
                    return src
        
        # Verificar sources
        sources = driver.find_elements(By.CSS_SELECTOR, 'video source')
        for s in sources:
            src = s.get_attribute('src')
            print(f'  Source: {src}')
            if src and ('m3u8' in src or 'mp4' in src):
                return src
        
        # Tentar clicar em play
        print('  Tentando clicar em play...')
        try:
            # Esperar botão de play aparecer
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'video, [class*="play"], button'))
            )
            
            # Clicar no video ou botão
            clickables = driver.find_elements(By.CSS_SELECTOR, 'video, [class*="play"], .vjs-big-play-button')
            for el in clickables:
                try:
                    el.click()
                    print('  Clicou!')
                    time.sleep(5)
                    break
                except:
                    pass
        except:
            pass
        
        # Verificar novamente após click
        videos = driver.find_elements(By.TAG_NAME, 'video')
        for v in videos:
            src = v.get_attribute('src')
            if src and ('m3u8' in src or 'mp4' in src) and not src.startswith('blob:'):
                print(f'✅ Video após click: {src}')
                return src
        
        # Procurar no JavaScript
        print('  Procurando no page source...')
        page = driver.page_source
        
        patterns = [
            r'"file"\s*:\s*"([^"]+)"',
            r'"source"\s*:\s*"([^"]+)"',
            r'"url"\s*:\s*"([^"]+)"',
            r'"src"\s*:\s*"([^"]+)"',
            r'([^"\']+\.m3u8[^"\']*)',
        ]
        
        for p in patterns:
            matches = re.findall(p, page)
            for m in matches:
                if ('m3u8' in m or 'mp4' in m) and m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Encontrado: {m[:100]}')
                    return m
        
        # Executar JS para pegar currentSrc
        try:
            current_src = driver.execute_script("""
                var videos = document.querySelectorAll('video');
                for (var v of videos) {
                    if (v.currentSrc) return v.currentSrc;
                    if (v.src) return v.src;
                }
                return null;
            """)
            if current_src and ('m3u8' in current_src or 'mp4' in current_src):
                print(f'✅ currentSrc: {current_src}')
                return current_src
        except:
            pass
        
        # Verificar network requests via Performance API
        try:
            entries = driver.execute_script("""
                var entries = performance.getEntriesByType('resource');
                return entries.map(e => e.name).filter(n => n.includes('m3u8') || n.includes('mp4'));
            """)
            if entries:
                print(f'  Network entries: {entries}')
                for e in entries:
                    if e.startswith('http'):
                        return e
        except:
            pass
            
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
    print(f'\n🎬 Abrindo VLC...')
    print(f'URL: {video_url}')
    
    vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
    
    try:
        cmd = [vlc_path, video_url]
        if referer:
            cmd.extend(['--http-referrer', referer])
        subprocess.Popen(cmd)
        print('✅ VLC aberto!')
        return True
    except:
        print(f'📋 Copie: {video_url}')
        return False

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC (Final)')
    print('=' * 60)
    
    # URLs para testar
    urls = [
        'https://g9r6.com/3buub/cnox47bzdraa',
        'https://bysebuho.com/e/cnox47bzdraa',
        'https://megaembed.link/#rckhv6',
    ]
    
    print('\n🚀 Iniciando Firefox...')
    driver = setup_driver()
    
    video_url = None
    
    try:
        for url in urls:
            video_url = extract_video(driver, url)
            if video_url:
                break
    finally:
        input('\nPressione ENTER para fechar o Firefox...')
        driver.quit()
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        play_in_vlc(video_url)
    else:
        print('❌ Não foi possível extrair automaticamente')
        print('\nOs players usam:')
        print('- Blob URLs (não extraíveis)')
        print('- JavaScript ofuscado')
        print('- Proteção anti-bot')
    print('=' * 60)

if __name__ == '__main__':
    main()
