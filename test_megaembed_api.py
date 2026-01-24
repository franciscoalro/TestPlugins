#!/usr/bin/env python3
"""
Test MegaEmbed API - MaxSeries Debugging
=========================================

Testa a API do MegaEmbed para extrair links de vídeo diretamente.

Uso:
    python test_megaembed_api.py
"""

import requests
import json
import re
from urllib.parse import urlparse, parse_qs

# Headers padrão (simulando navegador)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://megaembed.link/",
    "Origin": "https://megaembed.link",
    "Accept": "application/json, text/plain, */*",
}

def test_megaembed_api(video_id):
    """
    Testa a API do MegaEmbed com um videoId
    
    Args:
        video_id: ID do vídeo (ex: "rcok1i")
    
    Returns:
        dict com os dados da API ou None se falhar
    """
    print(f"\n{'='*60}")
    print(f"🔍 Testando MegaEmbed API")
    print(f"{'='*60}")
    print(f"Video ID: {video_id}")
    
    # Tentar diferentes endpoints da API
    api_urls = [
        f"https://megaembed.link/api/v1/info?id={video_id}",
        f"https://megaembed.link/api/info?id={video_id}",
        f"https://megaembed.link/api/v1/video/{video_id}",
        f"https://megaembed.link/api/video/{video_id}",
    ]
    
    for api_url in api_urls:
        print(f"\n📡 Tentando: {api_url}")
        
        try:
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON válido recebido!")
                    print(f"\n📦 Dados da API:")
                    print(json.dumps(data, indent=2))
                    return data
                except json.JSONDecodeError:
                    print(f"   ⚠️ Resposta não é JSON")
                    print(f"   Conteúdo: {response.text[:200]}")
            else:
                print(f"   ❌ Falhou")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro: {e}")
    
    return None

def scrape_megaembed_page(video_id):
    """
    Raspa a página HTML do MegaEmbed para extrair URLs de vídeo
    
    Args:
        video_id: ID do vídeo (ex: "rcok1i")
    
    Returns:
        list de URLs encontradas
    """
    print(f"\n{'='*60}")
    print(f"🌐 Raspando Página HTML do MegaEmbed")
    print(f"{'='*60}")
    
    url = f"https://megaembed.link/#{video_id}"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"HTML Size: {len(html)} bytes")
            
            # Regex para encontrar URLs de vídeo
            patterns = [
                # Padrão /v4/
                r'https?://[^/\s"\'<>]+/v4/[a-z0-9]{1,3}/[a-z0-9]{6}/[^\s"\'<>]+',
                # Arquivos .m3u8
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                # Arquivos .txt (playlists disfarçadas)
                r'https?://[^\s"\'<>]+\.txt[^\s"\'<>]*',
                # Arquivos .woff2 (segmentos disfarçados)
                r'https?://[^\s"\'<>]+\.woff2[^\s"\'<>]*',
            ]
            
            found_urls = []
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    print(f"\n✅ Encontrado com padrão: {pattern}")
                    for match in matches:
                        print(f"   - {match}")
                        found_urls.append(match)
            
            if not found_urls:
                print("\n❌ Nenhuma URL de vídeo encontrada no HTML")
                
                # Procurar por scripts que possam conter dados
                script_pattern = r'<script[^>]*>(.*?)</script>'
                scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
                
                print(f"\n📜 Scripts encontrados: {len(scripts)}")
                
                for i, script in enumerate(scripts[:5]):  # Primeiros 5 scripts
                    if 'http' in script or 'file' in script or 'source' in script:
                        print(f"\n   Script #{i+1} (primeiros 200 chars):")
                        print(f"   {script[:200]}")
            
            return list(set(found_urls))  # Remove duplicatas
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")
    
    return []

def test_video_url(url):
    """
    Testa se uma URL de vídeo é válida (retorna 200 OK)
    
    Args:
        url: URL para testar
    
    Returns:
        bool indicando se a URL é válida
    """
    print(f"\n🧪 Testando URL: {url}")
    
    try:
        response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 206]:  # 206 = Partial Content (vídeo)
            print(f"   ✅ URL VÁLIDA!")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
            return True
        else:
            print(f"   ❌ URL inválida")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    
    # Video ID extraído do navegador
    video_id = "rcok1i"  # de https://megaembed.link/#rcok1i
    
    print(f"""
{'='*60}
    MegaEmbed API Tester - MaxSeries Debug
{'='*60}

Video ID: {video_id}
URL Original: https://megaembed.link/#{video_id}
    """)
    
    # Teste 1: API direta
    api_data = test_megaembed_api(video_id)
    
    if api_data:
        # Procurar por URLs de vídeo nos dados da API
        print(f"\n🔍 Procurando URLs de vídeo nos dados da API...")
        
        def find_urls_in_dict(d, path=""):
            """Busca recursiva por URLs em dicionários"""
            urls = []
            if isinstance(d, dict):
                for key, value in d.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and value.startswith("http"):
                        print(f"   Encontrado em '{new_path}': {value}")
                        urls.append(value)
                    elif isinstance(value, (dict, list)):
                        urls.extend(find_urls_in_dict(value, new_path))
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    urls.extend(find_urls_in_dict(item, f"{path}[{i}]"))
            return urls
        
        api_urls = find_urls_in_dict(api_data)
        
        if api_urls:
            print(f"\n✅ {len(api_urls)} URL(s) encontrada(s) na API!")
            for url in api_urls:
                test_video_url(url)
        else:
            print(f"\n⚠️ Nenhuma URL encontrada nos dados da API")
    
    # Teste 2: Scraping da página HTML
    html_urls = scrape_megaembed_page(video_id)
    
    if html_urls:
        print(f"\n✅ {len(html_urls)} URL(s) encontrada(s) no HTML!")
        
        # Testar cada URL encontrada
        for url in html_urls[:5]:  # Testar apenas as primeiras 5
            test_video_url(url)
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO")
    print(f"{'='*60}")
    print(f"API retornou dados: {'✅ SIM' if api_data else '❌ NÃO'}")
    print(f"URLs encontradas no HTML: {len(html_urls)}")
    print(f"\n💡 Próximos Passos:")
    print(f"   1. Se API funcionou: Implementar no MegaEmbedExtractorV8.kt")
    print(f"   2. Se HTML funcionou: Melhorar regex de parsing")
    print(f"   3. Se nada funcionou: Usar PlayerEmbedAPI ou MyVidPlay como fallback")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
