#!/usr/bin/env python3
"""
Interceptar requisições de rede com mitmproxy ou similar
"""
import time
import subprocess
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import socket

# Vamos tentar uma abordagem diferente:
# Usar o Firefox com extensão para capturar m3u8

def try_with_firefox_console():
    """Usa Firefox e monitora console para m3u8"""
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    
    GECKO_PATH = r'D:\geckodriver.exe'
    FIREFOX_PATH = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    
    options = Options()
    options.binary_location = FIREFOX_PATH
    
    # Configurar para logar requisições
    options.set_preference('devtools.console.stdout.content', True)
    options.set_preference('devtools.netmonitor.persistlog', True)
    
    service = Service(executable_path=GECKO_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    
    found_urls = []
    
    # Injetar script para interceptar
    intercept_script = """
    // Interceptar fetch
    const origFetch = window.fetch;
    window.fetch = async function(...args) {
        const url = typeof args[0] === 'string' ? args[0] : args[0].url;
        if (url && (url.includes('.m3u8') || url.includes('.mp4'))) {
            console.log('INTERCEPTED_URL:' + url);
            window.interceptedUrls = window.interceptedUrls || [];
            window.interceptedUrls.push(url);
        }
        return origFetch.apply(this, args);
    };
    
    // Interceptar XHR
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (url && (url.includes('.m3u8') || url.includes('.mp4'))) {
            console.log('INTERCEPTED_URL:' + url);
            window.interceptedUrls = window.interceptedUrls || [];
            window.interceptedUrls.push(url);
        }
        return origOpen.apply(this, arguments);
    };
    
    // Interceptar createElement para video/source
    const origCreate = document.createElement;
    document.createElement = function(tag) {
        const el = origCreate.call(document, tag);
        if (tag.toLowerCase() === 'video' || tag.toLowerCase() === 'source') {
            const origSetAttr = el.setAttribute;
            el.setAttribute = function(name, value) {
                if (name === 'src' && value && (value.includes('.m3u8') || value.includes('.mp4'))) {
                    console.log('INTERCEPTED_URL:' + value);
                    window.interceptedUrls = window.interceptedUrls || [];
                    window.interceptedUrls.push(value);
                }
                return origSetAttr.call(this, name, value);
            };
        }
        return el;
    };
    
    // Observer para novos elementos
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.tagName === 'VIDEO' || node.tagName === 'SOURCE') {
                    const src = node.src || node.getAttribute('src');
                    if (src && (src.includes('.m3u8') || src.includes('.mp4'))) {
                        console.log('INTERCEPTED_URL:' + src);
                        window.interceptedUrls = window.interceptedUrls || [];
                        window.interceptedUrls.push(src);
                    }
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    window.interceptedUrls = [];
    console.log('Interceptors installed');
    """
    
    urls_to_test = [
        'https://bysebuho.com/e/cnox47bzdraa',
        'https://megaembed.link/#rckhv6',
    ]
    
    for url in urls_to_test:
        print(f'\n🔍 Testando: {url}')
        
        try:
            driver.get(url)
            time.sleep(3)
            
            # Injetar interceptadores
            driver.execute_script(intercept_script)
            
            # Esperar carregamento
            time.sleep(10)
            
            # Tentar clicar em play
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, 
                    'video, button, [class*="play"], .vjs-big-play-button, .jw-icon-display')
                for el in elements[:5]:
                    try:
                        driver.execute_script("arguments[0].click();", el)
                        time.sleep(2)
                    except:
                        pass
            except:
                pass
            
            time.sleep(10)
            
            # Verificar URLs interceptadas
            try:
                intercepted = driver.execute_script("return window.interceptedUrls || [];")
                print(f'  Interceptadas: {len(intercepted)}')
                for u in intercepted:
                    print(f'  → {u[:80]}')
                    if '.m3u8' in u or '.mp4' in u:
                        found_urls.append(u)
            except:
                pass
            
            # Verificar video elements
            videos = driver.find_elements(By.TAG_NAME, 'video')
            for v in videos:
                src = v.get_attribute('src')
                current = driver.execute_script("return arguments[0].currentSrc;", v)
                
                if src and not src.startswith('blob:'):
                    print(f'  Video src: {src[:80]}')
                    found_urls.append(src)
                if current and not current.startswith('blob:'):
                    print(f'  currentSrc: {current[:80]}')
                    found_urls.append(current)
            
            # Verificar performance entries
            try:
                entries = driver.execute_script("""
                    return performance.getEntriesByType('resource')
                        .map(e => e.name)
                        .filter(n => n.includes('.m3u8') || n.includes('.mp4') || n.includes('video') || n.includes('stream'));
                """)
                for e in entries:
                    print(f'  Resource: {e[:80]}')
                    if '.m3u8' in e or '.mp4' in e:
                        found_urls.append(e)
            except:
                pass
            
            if found_urls:
                break
                
        except Exception as e:
            print(f'  Erro: {e}')
    
    driver.quit()
    return found_urls

def main():
    print('=' * 60)
    print('🎬 TESTE com Interceptação de Rede')
    print('=' * 60)
    
    urls = try_with_firefox_console()
    
    print('\n' + '=' * 60)
    if urls:
        # Filtrar URLs válidas
        valid_urls = [u for u in urls if u.startswith('http') and ('m3u8' in u or 'mp4' in u)]
        
        if valid_urls:
            print('✅ URLs ENCONTRADAS:')
            for u in set(valid_urls):
                print(f'  {u}')
            
            # Abrir primeira no VLC
            video_url = valid_urls[0]
            print(f'\n🎬 Abrindo no VLC: {video_url[:80]}...')
            
            vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
            try:
                subprocess.Popen([vlc_path, video_url])
                print('✅ VLC aberto!')
            except:
                print(f'📋 Copie: {video_url}')
        else:
            print('❌ Nenhuma URL de vídeo válida encontrada')
    else:
        print('❌ Nenhuma URL interceptada')
        print('\nOs players usam Blob URLs que não podem ser extraídos.')
    print('=' * 60)

if __name__ == '__main__':
    main()
