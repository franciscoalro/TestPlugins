#!/usr/bin/env python3
"""
MegaEmbed API Extractor - Usa as APIs reais descobertas no JS
"""

import requests
import json
import re

class MegaEmbedAPI:
    BASE_URL = "https://megaembed.link"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Referer': 'https://megaembed.link/',
            'Origin': 'https://megaembed.link'
        })
    
    def extract(self, url_or_id):
        """Extrai m3u8 do megaembed"""
        
        # Extrair ID
        video_id = self._extract_id(url_or_id)
        print(f"\n🎬 MegaEmbed Extractor")
        print(f"🆔 Video ID: {video_id}")
        print("=" * 80)
        
        # Tentar API v1/player
        print("\n📡 Tentando: /api/v1/player?t={id}")
        result = self._try_player_api(video_id)
        if result:
            return result
        
        # Tentar API v1/video
        print("\n📡 Tentando: /api/v1/video?id={id}")
        result = self._try_video_api(video_id)
        if result:
            return result
        
        # Tentar API v1/info
        print("\n📡 Tentando: /api/v1/info?id={id}")
        result = self._try_info_api(video_id)
        if result:
            return result
        
        print("\n❌ Nenhuma API funcionou")
        return None
    
    def _extract_id(self, url_or_id):
        """Extrai ID da URL ou retorna o ID direto"""
        if 'http' in url_or_id:
            # megaembed.link/#xez5rx
            if '#' in url_or_id:
                return url_or_id.split('#')[-1]
            # megaembed.link/xez5rx
            parts = url_or_id.rstrip('/').split('/')
            return parts[-1]
        return url_or_id
    
    def _try_player_api(self, video_id):
        """Tenta API /api/v1/player?t={id}"""
        try:
            url = f"{self.BASE_URL}/api/v1/player?t={video_id}"
            response = self.session.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                return self._parse_response(response)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        return None
    
    def _try_video_api(self, video_id):
        """Tenta API /api/v1/video?id={id}"""
        try:
            url = f"{self.BASE_URL}/api/v1/video?id={video_id}"
            response = self.session.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                return self._parse_response(response)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        return None
    
    def _try_info_api(self, video_id):
        """Tenta API /api/v1/info?id={id}"""
        try:
            url = f"{self.BASE_URL}/api/v1/info?id={video_id}"
            response = self.session.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                return self._parse_response(response)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        return None
    
    def _parse_response(self, response):
        """Parse resposta da API"""
        content = response.text
        
        # Se for m3u8 direto
        if '#EXTM3U' in content:
            print("   ✅ M3U8 direto encontrado!")
            return content
        
        # Se for JSON
        try:
            data = json.loads(content)
            print(f"   📦 JSON recebido:")
            print(f"   {json.dumps(data, indent=2)[:300]}")
            
            # Procurar campos comuns
            for key in ['url', 'source', 'file', 'video', 'stream', 'hls', 'm3u8', 'sources', 'data']:
                if key in data:
                    value = data[key]
                    
                    # Se for string com URL
                    if isinstance(value, str):
                        if 'http' in value:
                            print(f"   🎯 URL encontrada em '{key}': {value}")
                            return self._fetch_url(value)
                    
                    # Se for lista
                    elif isinstance(value, list) and len(value) > 0:
                        first = value[0]
                        if isinstance(first, dict):
                            # Procurar 'file' ou 'src' no primeiro item
                            for subkey in ['file', 'src', 'url']:
                                if subkey in first:
                                    url = first[subkey]
                                    print(f"   🎯 URL encontrada em '{key}[0].{subkey}': {url}")
                                    return self._fetch_url(url)
                        elif isinstance(first, str) and 'http' in first:
                            print(f"   🎯 URL encontrada em '{key}[0]': {first}")
                            return self._fetch_url(first)
            
            # Busca recursiva
            result = self._find_url_recursive(data)
            if result:
                print(f"   🎯 URL encontrada recursivamente: {result}")
                return self._fetch_url(result)
            
        except json.JSONDecodeError:
            pass
        
        # Se for URL direta
        if content.startswith('http'):
            print(f"   🎯 URL direta: {content}")
            return self._fetch_url(content.strip())
        
        return None
    
    def _find_url_recursive(self, obj, depth=0):
        """Busca recursiva por URLs"""
        if depth > 5:  # Limite de profundidade
            return None
        
        if isinstance(obj, dict):
            for value in obj.values():
                result = self._find_url_recursive(value, depth + 1)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self._find_url_recursive(item, depth + 1)
                if result:
                    return result
        elif isinstance(obj, str):
            if 'http' in obj and ('.m3u8' in obj or '.txt' in obj or '.mp4' in obj):
                return obj
        
        return None
    
    def _fetch_url(self, url):
        """Baixa conteúdo de uma URL"""
        try:
            print(f"   📥 Baixando: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Se for m3u8
                if '#EXTM3U' in content:
                    print("   ✅ M3U8 válido!")
                    return content
                
                # Se for outra URL (redirecionamento)
                if content.startswith('http'):
                    print(f"   🔄 Redirecionamento: {content}")
                    return self._fetch_url(content.strip())
                
                # Retornar conteúdo mesmo que não seja m3u8
                return content
            
        except Exception as e:
            print(f"   ❌ Erro ao baixar: {e}")
        
        return None

def main():
    import sys
    
    extractor = MegaEmbedAPI()
    
    # URLs de teste do Burp Suite
    test_urls = [
        "https://megaembed.link/#xez5rx",
        "xez5rx",  # ID direto
    ]
    
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    for url in test_urls:
        result = extractor.extract(url)
        
        if result:
            print("\n" + "=" * 80)
            print("✅ SUCESSO! Conteúdo extraído:")
            print("=" * 80)
            print(result[:500])
            
            # Salvar
            filename = f"megaembed_extracted_{extractor._extract_id(url)}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n💾 Salvo em: {filename}")
            break
        else:
            print("\n❌ Falhou")
        
        print("\n" + "-" * 80 + "\n")

if __name__ == "__main__":
    main()
