#!/usr/bin/env python3
"""
Teste usando embed_frame_url descoberto
"""
import requests
import re
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': '*/*',
}

GECKO_PATH = r'D:\geckodriver.exe'
FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'

def try_g9r6_direct(url):
    """Tenta acessar g9r6.com diretamente"""
    print(f'\n🔍 Tentando g9r6: {url}')
    
    headers = {
        **HEADERS,
        'Referer': 'https://bysebuho.com/',
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f'  Status: {r.status_code}')
        print(f'  URL final: {r.url}')
        print(f'  Tamanho: {len(r.text)} bytes')
        
        # Procurar URLs de vídeo
        patterns = [
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'"([^"]+\.m3u8[^"]*)"',
            r"'([^']+\.m3u8[^']*)'",
            r'source\s*:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'"([^"]+\.mp4[^"]*)"',
        ]
        
        for p in patterns:
            matches = re.findall(p, r.text)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Encontrado: {m[:100]}')
                    return m
        
        # Procurar pass_md5 (Doodstream)
        pass_match = re.search(r"'/pass_md5/([^']+)'", r.text)
        if pass_match:
            pass_path = '/pass_md5/' + pass_match.group(1)
            print(f'  Pass path: {pass_path}')
            
            # Extrair domínio
            domain_match = re.match(r'(https?://[^/]+)', r.url)
            if domain_match:
                pass_url = domain_match.group(1) + pass_path
                print(f'  Pass URL: {pass_url}')
                
                r2 = requests.get(pass_url, headers={**headers, 'Referer': r.url}, timeout=30)
                print(f'  Pass response: {r2.text[:200]}')
                
                if r2.text.startswith('http'):
                    # Procurar token
                    token_match = re.search(r"token=([^&'\"]+)", r.text)
                    if token_match:
                        video_url = f"{r2.text.strip()}?token={token_match.group(1)}&expiry={int(time.time()*1000)}"
                    else:
                        video_url = r2.text.strip()
                    print(f'✅ Video URL: {video_url[:100]}')
                    return video_url
        
        # Mostrar parte do HTML para debug
        print(f'\n  HTML preview:')
        print(r.text[:1000])
        
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_with_selenium(url):
    """Tenta com Selenium para executar JS"""
    print(f'\n🔍 Tentando com Selenium: {url}')
    
    options = Options()
    options.binary_location = FIREFOX_PATH
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(10)  # Esperar JS carregar
        
        # Verificar video element
        videos = driver.find_elements(By.TAG_NAME, 'video')
        for v in videos:
            src = v.get_attribute('src')
            if src:
                print(f'  Video src: {src}')
                if '.m3u8' in src or '.mp4' in src:
                    return src
        
        # Verificar source elements
        sources = driver.find_elements(By.CSS_SELECTOR, 'video source')
        for s in sources:
            src = s.get_attribute('src')
            if src:
                print(f'  Source src: {src}')
                if '.m3u8' in src or '.mp4' in src:
                    return src
        
        # Procurar no page source
        page = driver.page_source
        patterns = [
            r'"([^"]+\.m3u8[^"]*)"',
            r"'([^']+\.m3u8[^']*)'",
        ]
        
        for p in patterns:
            matches = re.findall(p, page)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Encontrado no JS: {m[:100]}')
                    return m
        
        # Tentar clicar em play
        try:
            play_btns = driver.find_elements(By.CSS_SELECTOR, '[class*="play"], button')
            for btn in play_btns[:5]:
                try:
                    btn.click()
                    time.sleep(3)
                except:
                    pass
            
            # Verificar novamente
            videos = driver.find_elements(By.TAG_NAME, 'video')
            for v in videos:
                src = v.get_attribute('src')
                if src and ('.m3u8' in src or '.mp4' in src):
                    print(f'✅ Video após click: {src[:100]}')
                    return src
        except:
            pass
            
    except Exception as e:
        print(f'❌ Erro: {e}')
    finally:
        driver.quit()
    
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
        print(f'📋 URL: {video_url}')
        return False

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC (g9r6.com)')
    print('=' * 60)
    
    # URL descoberta na API
    embed_url = 'https://g9r6.com/3buub/cnox47bzdraa'
    
    video_url = try_g9r6_direct(embed_url)
    
    if not video_url:
        video_url = try_with_selenium(embed_url)
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        print(f'URL: {video_url}')
        play_in_vlc(video_url, embed_url)
    else:
        print('❌ Não foi possível extrair')
    print('=' * 60)

if __name__ == '__main__':
    main()
