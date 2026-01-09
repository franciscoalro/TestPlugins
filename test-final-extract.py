#!/usr/bin/env python3
"""
Extração final usando todas as técnicas combinadas
"""
import requests
import re
import subprocess
import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_PATH = r'D:\geckodriver.exe'
FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': '*/*',
}

def get_bysebuho_embed_url(video_id):
    """Obtém URL de embed do Bysebuho via API"""
    print(f'\n📡 API Bysebuho: {video_id}')
    
    api_url = f'https://bysebuho.com/api/videos/{video_id}/embed/details'
    
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            embed_url = data.get('embed_frame_url')
            print(f'  embed_frame_url: {embed_url}')
            return embed_url
    except Exception as e:
        print(f'  Erro: {e}')
    
    return None

def extract_with_selenium_wait(url):
    """Extrai vídeo esperando o player carregar completamente"""
    print(f'\n🔍 Selenium com espera: {url[:60]}...')
    
    options = Options()
    options.binary_location = FIREFOX_PATH
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(60)
    
    video_url = None
    
    try:
        driver.get(url)
        
        # Esperar página carregar
        print('  Aguardando 15s...')
        time.sleep(15)
        
        # Injetar interceptador ANTES de clicar
        driver.execute_script("""
            window._videoUrls = [];
            
            // Interceptar src de video
            Object.defineProperty(HTMLMediaElement.prototype, 'src', {
                set: function(value) {
                    if (value && !value.startsWith('blob:')) {
                        window._videoUrls.push(value);
                        console.log('VIDEO_SRC:', value);
                    }
                    this.setAttribute('src', value);
                },
                get: function() {
                    return this.getAttribute('src');
                }
            });
            
            // Interceptar source.src
            const origSetAttr = Element.prototype.setAttribute;
            Element.prototype.setAttribute = function(name, value) {
                if (name === 'src' && value && (value.includes('.m3u8') || value.includes('.mp4'))) {
                    window._videoUrls.push(value);
                    console.log('ATTR_SRC:', value);
                }
                return origSetAttr.call(this, name, value);
            };
        """)
        
        # Tentar clicar em play
        print('  Clicando em play...')
        try:
            # Esperar elemento clicável
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'video, [class*="play"], button'))
            )
            
            # Clicar no centro da página (onde geralmente está o play)
            driver.execute_script("""
                var event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: window.innerWidth / 2,
                    clientY: window.innerHeight / 2
                });
                document.elementFromPoint(window.innerWidth/2, window.innerHeight/2).dispatchEvent(event);
            """)
            
            time.sleep(3)
            
            # Clicar em elementos específicos
            for selector in ['video', '.vjs-big-play-button', '[class*="play"]', 'button']:
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in els[:3]:
                        try:
                            el.click()
                            time.sleep(2)
                        except:
                            pass
                except:
                    pass
                    
        except Exception as e:
            print(f'  Erro click: {e}')
        
        # Esperar vídeo carregar
        print('  Aguardando vídeo carregar...')
        time.sleep(15)
        
        # Verificar URLs interceptadas
        try:
            intercepted = driver.execute_script("return window._videoUrls || [];")
            print(f'  URLs interceptadas: {intercepted}')
            for u in intercepted:
                if u.startswith('http') and ('.m3u8' in u or '.mp4' in u):
                    video_url = u
                    break
        except:
            pass
        
        # Verificar video elements
        videos = driver.find_elements(By.TAG_NAME, 'video')
        print(f'  Videos encontrados: {len(videos)}')
        
        for v in videos:
            # Tentar várias formas de obter src
            src = v.get_attribute('src')
            current_src = driver.execute_script("return arguments[0].currentSrc;", v)
            
            print(f'    src: {src}')
            print(f'    currentSrc: {current_src}')
            
            for s in [src, current_src]:
                if s and not s.startswith('blob:') and ('m3u8' in s or 'mp4' in s):
                    video_url = s
                    break
            
            if video_url:
                break
        
        # Verificar source elements
        if not video_url:
            sources = driver.find_elements(By.CSS_SELECTOR, 'video source')
            for s in sources:
                src = s.get_attribute('src')
                print(f'    source: {src}')
                if src and not src.startswith('blob:') and ('m3u8' in src or 'mp4' in src):
                    video_url = src
                    break
        
        # Verificar network via Performance API
        if not video_url:
            try:
                resources = driver.execute_script("""
                    return performance.getEntriesByType('resource')
                        .map(e => e.name)
                        .filter(n => n.includes('.m3u8') || n.includes('.mp4') || n.includes('/video/') || n.includes('/stream/'));
                """)
                print(f'  Resources: {resources}')
                for r in resources:
                    if '.m3u8' in r or '.mp4' in r:
                        video_url = r
                        break
            except:
                pass
        
        # Procurar no page source
        if not video_url:
            page = driver.page_source
            patterns = [
                r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
                r'"source"\s*:\s*"([^"]+\.m3u8[^"]*)"',
                r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            ]
            
            for p in patterns:
                matches = re.findall(p, page)
                for m in matches:
                    if m.startswith('http') and 'logo' not in m.lower():
                        print(f'  Regex match: {m[:80]}')
                        video_url = m
                        break
                if video_url:
                    break
                    
    except Exception as e:
        print(f'  Erro: {e}')
    finally:
        driver.quit()
    
    return video_url

def try_direct_dood_api(video_id):
    """Tenta API direta do Doodstream"""
    print(f'\n📡 Doodstream API: {video_id}')
    
    # Diferentes domínios Doodstream
    domains = ['bysebuho.com', 'g9r6.com', 'dood.wf', 'dood.pm', 'dood.so']
    
    for domain in domains:
        try:
            # Tentar endpoint de download
            url = f'https://{domain}/d/{video_id}'
            r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
            
            if r.status_code == 200:
                # Procurar link de download
                match = re.search(r'href="([^"]+)"[^>]*>Download', r.text)
                if match:
                    dl_url = match.group(1)
                    print(f'  Download: {dl_url[:80]}')
                    
                    # Seguir redirect
                    r2 = requests.head(dl_url, headers=HEADERS, timeout=30, allow_redirects=True)
                    if '.mp4' in r2.url or '.m3u8' in r2.url:
                        print(f'✅ Final: {r2.url[:80]}')
                        return r2.url
                        
        except Exception as e:
            pass
    
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
    print('🎬 EXTRAÇÃO FINAL - MaxSeries → VLC')
    print('=' * 60)
    
    video_id = 'cnox47bzdraa'
    video_url = None
    
    # 1. Obter embed URL via API
    embed_url = get_bysebuho_embed_url(video_id)
    
    # 2. Tentar API direta Doodstream
    if not video_url:
        video_url = try_direct_dood_api(video_id)
    
    # 3. Tentar Selenium no embed URL
    if not video_url and embed_url:
        video_url = extract_with_selenium_wait(embed_url)
    
    # 4. Tentar Selenium no URL original
    if not video_url:
        video_url = extract_with_selenium_wait(f'https://bysebuho.com/e/{video_id}')
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        play_in_vlc(video_url, 'https://bysebuho.com/')
    else:
        print('❌ Não foi possível extrair')
        print('\nO player usa Blob URLs gerados via JavaScript.')
        print('Isso significa que o vídeo é decodificado no navegador')
        print('e não existe uma URL direta acessível.')
    print('=' * 60)

if __name__ == '__main__':
    main()
