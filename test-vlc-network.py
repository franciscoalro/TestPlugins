#!/usr/bin/env python3
"""
Teste com interceptação de rede para capturar m3u8
"""
import time
import json
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

GECKO_PATH = r'D:\geckodriver.exe'
FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'

def setup_driver_with_logging():
    """Configura Firefox com logging de rede"""
    options = Options()
    options.binary_location = FIREFOX_PATH
    
    # Habilitar logging
    options.set_preference('devtools.netmonitor.enabled', True)
    options.set_preference('devtools.console.stdout.content', True)
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def capture_network_with_js(driver, player_url):
    """Usa JavaScript para interceptar requisições"""
    print(f'\n🔍 Carregando: {player_url[:60]}...')
    
    # Injetar script para capturar fetch/XHR
    intercept_script = """
    window.capturedUrls = [];
    
    // Interceptar fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string') {
            window.capturedUrls.push(url);
        }
        return originalFetch.apply(this, args);
    };
    
    // Interceptar XHR
    const originalXHR = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function(method, url) {
        window.capturedUrls.push(url);
        return originalXHR.apply(this, arguments);
    };
    """
    
    try:
        driver.get(player_url)
        time.sleep(2)
        
        # Injetar interceptador
        driver.execute_script(intercept_script)
        
        # Esperar carregamento
        time.sleep(8)
        
        # Tentar clicar em play
        try:
            play_buttons = driver.find_elements(By.CSS_SELECTOR, 
                '.play-button, .vjs-big-play-button, [class*="play"], button')
            for btn in play_buttons[:3]:
                try:
                    btn.click()
                    time.sleep(2)
                except:
                    pass
        except:
            pass
        
        time.sleep(5)
        
        # Capturar URLs
        captured = driver.execute_script("return window.capturedUrls || [];")
        
        print(f'  URLs capturadas: {len(captured)}')
        
        for url in captured:
            if '.m3u8' in url or '.mp4' in url:
                print(f'✅ Vídeo: {url[:80]}...')
                return url
            if 'video' in url.lower() or 'stream' in url.lower():
                print(f'  Possível: {url[:60]}...')
        
        # Verificar elemento video
        videos = driver.find_elements(By.TAG_NAME, 'video')
        for v in videos:
            src = v.get_attribute('src')
            if src:
                print(f'  Video src: {src[:60]}...')
                if '.m3u8' in src or '.mp4' in src:
                    return src
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_direct_bysebuho():
    """Tenta método direto para Bysebuho/Doodstream"""
    import requests
    
    print('\n🔍 Tentando método direto Bysebuho...')
    
    url = 'https://bysebuho.com/e/cnox47bzdraa'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
        'Accept': '*/*',
        'Referer': url,
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        # Procurar pass_md5
        import re
        
        # Padrão Doodstream
        match = re.search(r"\$\.get\('(/pass_md5/[^']+)'", r.text)
        if match:
            pass_url = 'https://bysebuho.com' + match.group(1)
            print(f'  Pass URL: {pass_url}')
            
            r2 = requests.get(pass_url, headers=headers, timeout=30)
            if r2.status_code == 200:
                # O response é a base da URL
                base = r2.text
                
                # Procurar token
                token_match = re.search(r"token=([^&'\"]+)", r.text)
                if token_match:
                    token = token_match.group(1)
                    video_url = f'{base}?token={token}&expiry='
                    print(f'✅ Dood URL: {video_url[:80]}...')
                    return video_url
        
        # Procurar direto
        patterns = [
            r'"([^"]+\.m3u8[^"]*)"',
            r"'([^']+\.m3u8[^']*)'",
        ]
        
        for p in patterns:
            matches = re.findall(p, r.text)
            for m in matches:
                if m.startswith('http'):
                    print(f'✅ Encontrado: {m[:80]}...')
                    return m
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
    """Reproduz no VLC"""
    print(f'\n🎬 Abrindo VLC...')
    
    vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
    
    try:
        cmd = [vlc_path, video_url]
        if referer:
            cmd.extend(['--http-referrer', referer])
        subprocess.Popen(cmd)
        print('✅ VLC aberto!')
        return True
    except:
        print('❌ VLC não encontrado')
        print(f'\n📋 URL: {video_url}')
        return False

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC (Network Capture)')
    print('=' * 60)
    
    # Tentar método direto primeiro
    video_url = try_direct_bysebuho()
    
    if not video_url:
        # Tentar com Selenium
        players = [
            'https://bysebuho.com/e/cnox47bzdraa',
            'https://megaembed.link/#rckhv6',
            'https://playerembedapi.link/?v=o_4s_DFJuL',
        ]
        
        print('\n🚀 Iniciando Firefox...')
        driver = setup_driver_with_logging()
        
        try:
            for player_url in players:
                video_url = capture_network_with_js(driver, player_url)
                if video_url:
                    break
        finally:
            driver.quit()
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        print(f'URL: {video_url}')
        play_in_vlc(video_url, 'https://bysebuho.com/')
    else:
        print('❌ Não foi possível extrair link direto')
        print('\nEsses players usam proteção avançada:')
        print('- JavaScript ofuscado')
        print('- Tokens dinâmicos')
        print('- Verificação de referrer')
    print('=' * 60)

if __name__ == '__main__':
    main()
