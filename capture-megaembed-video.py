#!/usr/bin/env python3
"""
Captura de vídeo MegaEmbed - Baseado na análise do Burp Suite
Descoberta: O vídeo M3U8 está em sd8g.gametech.cfd
"""

import requests
import re
import json
from urllib.parse import urljoin

# Headers baseados no Burp Suite
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://megaembed.link/',
    'Origin': 'https://megaembed.link',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

def extract_video_from_megaembed(embed_url):
    """
    Extrai o link M3U8 do MegaEmbed
    
    Fluxo descoberto:
    1. megaembed.link/e/ID -> página do player
    2. API /api/v1/video retorna dados encriptados
    3. Decodifica para encontrar URL gametech.cfd
    4. URL .txt é na verdade M3U8 master playlist
    """
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    print(f"[1] Acessando: {embed_url}")
    
    # Passo 1: Acessar página do embed
    resp = session.get(embed_url)
    print(f"    Status: {resp.status_code}")
    
    # Passo 2: Procurar por padrões conhecidos
    html = resp.text
    
    # Procurar URLs gametech.cfd diretamente
    gametech_pattern = r'https?://[a-z0-9]+\.gametech\.cfd/[^\s"\']+'
    gametech_urls = re.findall(gametech_pattern, html)
    
    if gametech_urls:
        print(f"[2] URLs gametech.cfd encontradas: {gametech_urls}")
        return gametech_urls
    
    # Procurar API endpoint
    api_pattern = r'/api/v1/video[^\s"\']*'
    api_matches = re.findall(api_pattern, html)
    
    if api_matches:
        print(f"[2] API endpoints encontrados: {api_matches}")
        
        for api_path in api_matches:
            api_url = urljoin(embed_url, api_path)
            print(f"[3] Chamando API: {api_url}")
            
            try:
                api_resp = session.get(api_url)
                print(f"    Status: {api_resp.status_code}")
                print(f"    Resposta: {api_resp.text[:500]}")
                
                # Procurar URLs na resposta da API
                urls_in_api = re.findall(gametech_pattern, api_resp.text)
                if urls_in_api:
                    print(f"[4] URLs encontradas na API: {urls_in_api}")
                    return urls_in_api
                    
            except Exception as e:
                print(f"    Erro: {e}")
    
    # Procurar qualquer URL .txt que possa ser M3U8
    txt_pattern = r'https?://[^\s"\']+\.txt'
    txt_urls = re.findall(txt_pattern, html)
    
    if txt_urls:
        print(f"[2] URLs .txt encontradas: {txt_urls}")
        return txt_urls
    
    print("[!] Nenhuma URL de vídeo encontrada diretamente")
    print("[!] Pode ser necessário executar JavaScript para decodificar")
    
    return None


def get_m3u8_content(m3u8_url, referer="https://megaembed.link/"):
    """
    Baixa o conteúdo do M3U8 master playlist
    """
    headers = HEADERS.copy()
    headers['Referer'] = referer
    
    print(f"\n[M3U8] Baixando: {m3u8_url}")
    
    resp = requests.get(m3u8_url, headers=headers)
    print(f"       Status: {resp.status_code}")
    print(f"       Content-Type: {resp.headers.get('Content-Type')}")
    
    if resp.status_code == 200:
        content = resp.text
        print(f"\n--- Conteúdo M3U8 ---")
        print(content)
        print(f"--- Fim ---\n")
        
        # Extrair variantes de qualidade
        if '#EXTM3U' in content:
            print("[✓] Confirmado: É um M3U8 válido!")
            
            # Extrair streams
            streams = re.findall(r'#EXT-X-STREAM-INF:.*?RESOLUTION=(\d+x\d+).*?\n([^\n]+)', content)
            
            if streams:
                print("\nQualidades disponíveis:")
                base_url = m3u8_url.rsplit('/', 1)[0]
                
                for resolution, stream_file in streams:
                    full_url = f"{base_url}/{stream_file}"
                    print(f"  {resolution}: {full_url}")
                
                return content, streams
        
        return content, None
    
    return None, None


def test_known_url():
    """
    Testa a URL conhecida do Burp Suite
    """
    # URL descoberta no Burp Suite
    known_url = "https://sd8g.gametech.cfd/v4/db/6pyw3v/cf-master.1767387529.txt"
    
    print("=" * 60)
    print("TESTE COM URL CONHECIDA DO BURP SUITE")
    print("=" * 60)
    
    content, streams = get_m3u8_content(known_url)
    
    if content and streams:
        print("\n[✓] SUCESSO! Links de vídeo extraídos!")
        
        # Construir URLs completas das variantes
        base_url = known_url.rsplit('/', 1)[0]
        
        result = {
            "master_playlist": known_url,
            "base_url": base_url,
            "streams": []
        }
        
        for resolution, stream_file in streams:
            stream_url = f"{base_url}/{stream_file}"
            result["streams"].append({
                "resolution": resolution,
                "url": stream_url
            })
        
        # Salvar resultado
        with open("megaembed_video_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nResultado salvo em: megaembed_video_result.json")
        
        return result
    
    return None


if __name__ == "__main__":
    # Primeiro, testar com a URL conhecida
    result = test_known_url()
    
    if result:
        print("\n" + "=" * 60)
        print("LINKS FINAIS PARA REPRODUÇÃO")
        print("=" * 60)
        print(f"\nMaster Playlist: {result['master_playlist']}")
        print("\nStreams por qualidade:")
        for stream in result['streams']:
            print(f"  {stream['resolution']}: {stream['url']}")
        
        print("\n[DICA] Para reproduzir no VLC:")
        print(f'  vlc "{result["master_playlist"]}" --http-referrer="https://megaembed.link/"')
