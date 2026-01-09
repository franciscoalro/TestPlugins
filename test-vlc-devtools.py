#!/usr/bin/env python3
"""
Teste usando DevTools Protocol para interceptar m3u8
"""
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import json

def setup_chrome_with_devtools():
    """Configura Chrome com DevTools Protocol"""
    options = ChromeOptions()
    options.add_argument('--auto-open-devtools-for-tabs')
    
    # Habilitar logging de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    return driver

def extract_m3u8_from_logs(driver):
    """Extrai URLs m3u8 dos logs de performance"""
    logs = driver.get_log('performance')
    
    m3u8_urls = []
    
    for entry in logs:
        try:
            message = json.loads(entry['message'])
            method = message.get('message', {}).get('method', '')
            
            if method in ['Network.requestWillBeSent', 'Network.responseReceived']:
                params = message.get('message', {}).get('params', {})
                
                # Verificar request
                request = params.get('request', {})
                url = request.get('url', '')
                
                if not url:
                    # Verificar response
                    response = params.get('response', {})
                    url = response.get('url', '')
                
                if url and ('.m3u8' in url or '.mp4' in url):
                    if url not in m3u8_urls:
                        m3u8_urls.append(url)
                        print(f'✅ Encontrado: {url[:100]}')
                        
        except:
            pass
    
    return m3u8_urls

def main():
    print('=' * 60)
    print('🎬 TESTE com Chrome DevTools')
    print('=' * 60)
    
    urls = [
        'https://megaembed.link/#rckhv6',
        'https://bysebuho.com/e/cnox47bzdraa',
    ]
    
    print('\n🚀 Iniciando Chrome...')
    
    try:
        driver = setup_chrome_with_devtools()
    except Exception as e:
        print(f'❌ Chrome não disponível: {e}')
        print('\nTentando método alternativo...')
        
        # Fallback: usar requests para tentar APIs conhecidas
        import requests
        
        # Tentar Filemoon/Doodstream API pattern
        print('\n🔍 Tentando padrões conhecidos...')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://bysebuho.com/',
        }
        
        # Filemoon pattern
        try:
            r = requests.get('https://bysebuho.com/e/cnox47bzdraa', headers=headers, timeout=30)
            
            import re
            
            # Procurar eval/packed JS
            packed = re.search(r"eval\(function\(p,a,c,k,e,d\).*?\)\)", r.text, re.DOTALL)
            if packed:
                print('  Encontrado JS packed (precisa desofuscar)')
            
            # Procurar sources array
            sources = re.search(r'sources\s*:\s*\[(.*?)\]', r.text, re.DOTALL)
            if sources:
                print(f'  Sources: {sources.group(1)[:200]}')
                
        except Exception as e:
            print(f'  Erro: {e}')
        
        print('\n' + '=' * 60)
        print('CONCLUSÃO:')
        print('=' * 60)
        print('''
Os players do MaxSeries (MegaEmbed, PlayerEmbedAPI, Bysebuho) usam:

1. JavaScript ofuscado/packed
2. Blob URLs gerados dinamicamente
3. Tokens temporários
4. Verificação de referrer

Para extrair os links seria necessário:
- Executar o JavaScript completo
- Interceptar as requisições de rede em tempo real
- Ou usar um browser automation mais avançado

O CloudStream consegue reproduzir alguns desses players porque:
- Tem extractors específicos para cada serviço
- Executa em ambiente Android com WebView
- Alguns extractors fazem engenharia reversa do JS

Para teste manual, você pode:
1. Abrir o player no navegador
2. Pressionar F12 → Network
3. Filtrar por "m3u8" ou "mp4"
4. Copiar a URL quando aparecer
5. Abrir no VLC com: vlc <url> --http-referrer=<player_url>
''')
        return
    
    try:
        for url in urls:
            print(f'\n🔍 Carregando: {url}')
            driver.get(url)
            time.sleep(15)
            
            # Tentar clicar em play
            try:
                plays = driver.find_elements(By.CSS_SELECTOR, '[class*="play"], video, button')
                for p in plays[:3]:
                    try:
                        p.click()
                        time.sleep(3)
                    except:
                        pass
            except:
                pass
            
            time.sleep(10)
            
            # Extrair URLs dos logs
            m3u8_urls = extract_m3u8_from_logs(driver)
            
            if m3u8_urls:
                print(f'\n✅ URLs encontradas: {len(m3u8_urls)}')
                for u in m3u8_urls:
                    print(f'  {u}')
                
                # Abrir no VLC
                vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
                try:
                    subprocess.Popen([vlc_path, m3u8_urls[0], '--http-referrer', url])
                    print('✅ VLC aberto!')
                except:
                    print(f'📋 URL: {m3u8_urls[0]}')
                break
                
    finally:
        input('\nPressione ENTER para fechar...')
        driver.quit()

if __name__ == '__main__':
    main()
