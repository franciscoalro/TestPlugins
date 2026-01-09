#!/usr/bin/env python3
"""
Teste com Playwright - interceptação de rede real
"""
import asyncio
import subprocess
from playwright.async_api import async_playwright

async def extract_video():
    print('=' * 60)
    print('🎬 TESTE com Playwright')
    print('=' * 60)
    
    video_urls = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Interceptar todas as requisições
        async def handle_request(request):
            url = request.url
            if '.m3u8' in url or '.mp4' in url:
                if 'logo' not in url.lower() and 'thumb' not in url.lower():
                    print(f'✅ INTERCEPTADO: {url[:100]}')
                    video_urls.append(url)
        
        page.on('request', handle_request)
        
        # Também interceptar responses
        async def handle_response(response):
            url = response.url
            content_type = response.headers.get('content-type', '')
            if 'mpegurl' in content_type or 'video' in content_type:
                print(f'✅ RESPONSE VIDEO: {url[:100]}')
                video_urls.append(url)
        
        page.on('response', handle_response)
        
        urls_to_test = [
            'https://bysebuho.com/e/cnox47bzdraa',
            'https://g9r6.com/6uwcp/cnox47bzdraa',
        ]
        
        for url in urls_to_test:
            print(f'\n🔍 Carregando: {url}')
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Esperar um pouco
                await asyncio.sleep(5)
                
                # Tentar clicar em play
                try:
                    # Clicar no centro da página
                    await page.mouse.click(640, 360)
                    await asyncio.sleep(3)
                    
                    # Tentar clicar em elementos específicos
                    for selector in ['video', '[class*="play"]', 'button']:
                        try:
                            el = await page.query_selector(selector)
                            if el:
                                await el.click()
                                await asyncio.sleep(2)
                        except:
                            pass
                except:
                    pass
                
                # Esperar mais para carregar vídeo
                await asyncio.sleep(10)
                
                if video_urls:
                    break
                    
            except Exception as e:
                print(f'  Erro: {e}')
        
        # Verificar video elements
        videos = await page.query_selector_all('video')
        for v in videos:
            src = await v.get_attribute('src')
            if src and not src.startswith('blob:'):
                print(f'  Video src: {src}')
                video_urls.append(src)
        
        input('\nPressione ENTER para fechar...')
        await browser.close()
    
    return video_urls

def main():
    urls = asyncio.run(extract_video())
    
    print('\n' + '=' * 60)
    if urls:
        # Filtrar URLs válidas
        valid = [u for u in urls if u.startswith('http') and ('m3u8' in u or 'mp4' in u)]
        
        if valid:
            print('✅ URLs ENCONTRADAS:')
            for u in set(valid):
                print(f'  {u}')
            
            # Abrir no VLC
            vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
            try:
                subprocess.Popen([vlc_path, valid[0]])
                print('\n✅ VLC aberto!')
            except:
                print(f'\n📋 Copie: {valid[0]}')
        else:
            print('❌ Nenhuma URL de vídeo válida')
    else:
        print('❌ Nenhuma URL interceptada')
    print('=' * 60)

if __name__ == '__main__':
    main()
