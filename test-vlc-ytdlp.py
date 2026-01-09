#!/usr/bin/env python3
"""
Teste usando yt-dlp para extrair vídeos
"""
import subprocess
import json
import re

def try_ytdlp(url, name):
    """Tenta extrair com yt-dlp"""
    print(f'\n🔍 yt-dlp: {name}')
    print(f'   URL: {url[:60]}...')
    
    try:
        # Primeiro tentar obter info
        result = subprocess.run(
            ['yt-dlp', '-j', '--no-warnings', url],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            
            # Procurar URL do vídeo
            video_url = data.get('url')
            if not video_url:
                formats = data.get('formats', [])
                for f in formats:
                    if f.get('url'):
                        video_url = f['url']
                        break
            
            if video_url:
                print(f'✅ Encontrado: {video_url[:100]}...')
                return video_url
        
        # Se falhou, mostrar erro
        if result.stderr:
            # Filtrar linhas relevantes
            for line in result.stderr.split('\n'):
                if 'ERROR' in line or 'error' in line.lower():
                    print(f'   {line[:80]}')
                    
    except subprocess.TimeoutExpired:
        print('   Timeout')
    except Exception as e:
        print(f'   Erro: {e}')
    
    return None

def try_ytdlp_extract(url, name):
    """Tenta extrair URL direta com yt-dlp"""
    print(f'\n🔍 yt-dlp extract: {name}')
    
    try:
        result = subprocess.run(
            ['yt-dlp', '-g', '--no-warnings', url],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout.strip():
            video_url = result.stdout.strip().split('\n')[0]
            print(f'✅ URL: {video_url[:100]}...')
            return video_url
            
    except Exception as e:
        print(f'   Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
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
    print('🎬 TESTE com yt-dlp')
    print('=' * 60)
    
    players = [
        ('Bysebuho', 'https://bysebuho.com/e/cnox47bzdraa'),
        ('G9R6', 'https://g9r6.com/3buub/cnox47bzdraa'),
        ('MegaEmbed', 'https://megaembed.link/#rckhv6'),
        ('PlayerEmbedAPI', 'https://playerembedapi.link/?v=o_4s_DFJuL'),
    ]
    
    video_url = None
    
    for name, url in players:
        # Tentar método -g (get URL)
        video_url = try_ytdlp_extract(url, name)
        if video_url:
            break
        
        # Tentar método -j (JSON info)
        video_url = try_ytdlp(url, name)
        if video_url:
            break
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        play_in_vlc(video_url)
    else:
        print('❌ yt-dlp não conseguiu extrair')
        print('\nTentando método alternativo com Selenium + Network...')
    print('=' * 60)
    
    return video_url

if __name__ == '__main__':
    result = main()
    
    if not result:
        # Tentar com Selenium capturando network
        print('\n' + '=' * 60)
        print('🔄 Tentando Selenium com HAR capture...')
        print('=' * 60)
        
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver.common.by import By
            import time
            
            GECKO_PATH = r'D:\geckodriver.exe'
            FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            
            options = Options()
            options.binary_location = FIREFOX_PATH
            
            # Habilitar devtools
            options.set_preference('devtools.netmonitor.enabled', True)
            
            service = Service(executable_path=GECKO_PATH)
            driver = webdriver.Firefox(service=service, options=options)
            
            url = 'https://bysebuho.com/e/cnox47bzdraa'
            print(f'\n🔍 Carregando: {url}')
            
            driver.get(url)
            
            # Esperar e clicar
            time.sleep(10)
            
            try:
                # Clicar em qualquer coisa clicável
                elements = driver.find_elements(By.CSS_SELECTOR, 'video, button, [class*="play"]')
                for el in elements[:5]:
                    try:
                        el.click()
                        time.sleep(2)
                    except:
                        pass
            except:
                pass
            
            time.sleep(10)
            
            # Verificar video src
            videos = driver.find_elements(By.TAG_NAME, 'video')
            for v in videos:
                src = v.get_attribute('src')
                current = v.get_attribute('currentSrc')
                print(f'  Video src: {src}')
                print(f'  currentSrc: {current}')
                
                if current and not current.startswith('blob:'):
                    print(f'\n✅ ENCONTRADO: {current}')
                    driver.quit()
                    
                    vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
                    subprocess.Popen([vlc_path, current, '--http-referrer', url])
                    exit(0)
            
            # Executar JS para pegar network requests
            try:
                urls = driver.execute_script("""
                    var entries = performance.getEntriesByType('resource');
                    return entries.map(e => e.name);
                """)
                
                for u in urls:
                    if '.m3u8' in u or '.mp4' in u:
                        print(f'\n✅ Network: {u}')
                        driver.quit()
                        
                        vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
                        subprocess.Popen([vlc_path, u, '--http-referrer', url])
                        exit(0)
            except:
                pass
            
            input('\nPressione ENTER para fechar...')
            driver.quit()
            
        except Exception as e:
            print(f'Erro Selenium: {e}')
