#!/usr/bin/env python3
"""
Extrator Real do MegaEmbed
Simula comportamento do browser para extrair m3u8
"""

import requests
import re
import json
import time
from urllib.parse import urlparse, urljoin

class MegaEmbedExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://megaembed.link/',
            'Origin': 'https://megaembed.link'
        })
    
    def extract(self, url):
        """Extrai m3u8 do megaembed"""
        print(f"\n🎬 Extraindo: {url}")
        print("=" * 80)
        
        # Extrair ID do hash
        video_id = self._extract_id(url)
        if not video_id:
            print("❌ ID não encontrado na URL")
            return None
        
        print(f"🆔 Video ID: {video_id}")
        
        # Tentar diferentes endpoints da API
        api_endpoints = [
            f"https://megaembed.link/api/video/{video_id}",
            f"https://megaembed.link/api/source/{video_id}",
            f"https://megaembed.link/api/player/{video_id}",
            f"https://megaembed.link/embed/{video_id}",
        ]
        
        for endpoint in api_endpoints:
            print(f"\n🔍 Tentando: {endpoint}")
            result = self._try_endpoint(endpoint, video_id)
            if result:
                return result
        
        # Se nada funcionou, tentar carregar a página e extrair do JavaScript
        print(f"\n🌐 Carregando página principal...")
        return self._extract_from_page(url, video_id)
    
    def _extract_id(self, url):
        """Extrai ID do vídeo da URL"""
        # megaembed.link/#xez5rx
        if '#' in url:
            return url.split('#')[-1]
        # megaembed.link/xez5rx
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else None
    
    def _try_endpoint(self, endpoint, video_id):
        """Tenta um endpoint específico"""
        try:
            response = self.session.get(endpoint, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code != 200:
                return None
            
            content = response.text
            
            # Se for JSON
            if response.headers.get('Content-Type', '').startswith('application/json'):
                return self._parse_json_response(content)
            
            # Se for texto com m3u8
            if '#EXTM3U' in content:
                print("   ✅ M3U8 encontrado!")
                return content
            
            # Se for URL direta
            if content.startswith('http') and ('.m3u8' in content or '.txt' in content):
                print(f"   🎯 URL encontrada: {content}")
                return self._fetch_m3u8_from_url(content)
            
            # Procurar URLs no conteúdo
            urls = re.findall(r'https?://[^\s\'"<>]+\.(?:m3u8|txt)[^\s\'"<>]*', content)
            if urls:
                print(f"   🎯 {len(urls)} URL(s) encontrada(s)")
                for url in urls:
                    result = self._fetch_m3u8_from_url(url)
                    if result:
                        return result
            
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return None
    
    def _parse_json_response(self, content):
        """Parse resposta JSON"""
        try:
            data = json.loads(content)
            print(f"   📦 JSON: {json.dumps(data, indent=2)[:200]}")
            
            # Procurar campos comuns
            for key in ['url', 'source', 'file', 'video', 'stream', 'hls', 'm3u8']:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and ('http' in value or '.m3u8' in value):
                        print(f"   🎯 Encontrado em '{key}': {value}")
                        return self._fetch_m3u8_from_url(value)
            
            # Procurar recursivamente
            def find_urls(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        result = find_urls(v)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_urls(item)
                        if result:
                            return result
                elif isinstance(obj, str):
                    if 'http' in obj and ('.m3u8' in obj or '.txt' in obj):
                        return obj
                return None
            
            url = find_urls(data)
            if url:
                print(f"   🎯 URL encontrada recursivamente: {url}")
                return self._fetch_m3u8_from_url(url)
            
        except json.JSONDecodeError:
            print("   ⚠️  Não é JSON válido")
        
        return None
    
    def _fetch_m3u8_from_url(self, url):
        """Baixa m3u8 de uma URL"""
        try:
            print(f"   📥 Baixando: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if '#EXTM3U' in content:
                    print("   ✅ M3U8 válido!")
                    return content
                elif content.startswith('http'):
                    # Pode ser outra URL
                    print(f"   🔄 Redirecionamento: {content}")
                    return self._fetch_m3u8_from_url(content.strip())
            
        except Exception as e:
            print(f"   ❌ Erro ao baixar: {e}")
        
        return None
    
    def _extract_from_page(self, url, video_id):
        """Extrai m3u8 da página HTML"""
        try:
            response = self.session.get(url, timeout=10)
            content = response.text
            
            print(f"   📄 Tamanho da página: {len(content)} bytes")
            
            # Procurar scripts inline
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            print(f"   📜 {len(scripts)} script(s) encontrado(s)")
            
            for i, script in enumerate(scripts):
                # Procurar variáveis com URLs
                var_matches = re.findall(r'(?:var|const|let)\s+(\w+)\s*=\s*["\']([^"\']+)["\']', script)
                for var_name, value in var_matches:
                    if 'http' in value and ('.m3u8' in value or '.txt' in value or 'api' in value):
                        print(f"   🎯 Script {i}: {var_name} = {value}")
                        result = self._fetch_m3u8_from_url(value)
                        if result:
                            return result
                
                # Procurar chamadas fetch/ajax
                fetch_matches = re.findall(r'fetch\(["\']([^"\']+)["\']', script)
                for fetch_url in fetch_matches:
                    if video_id in fetch_url or 'api' in fetch_url:
                        print(f"   🎯 Fetch encontrado: {fetch_url}")
                        full_url = urljoin(url, fetch_url)
                        result = self._try_endpoint(full_url, video_id)
                        if result:
                            return result
            
            # Procurar data attributes
            data_attrs = re.findall(r'data-[a-z-]+=["\']([^"\']+)["\']', content)
            for attr_value in data_attrs:
                if 'http' in attr_value and ('.m3u8' in attr_value or '.txt' in attr_value):
                    print(f"   🎯 Data attribute: {attr_value}")
                    result = self._fetch_m3u8_from_url(attr_value)
                    if result:
                        return result
            
        except Exception as e:
            print(f"   ❌ Erro ao processar página: {e}")
        
        return None

def main():
    import sys
    
    extractor = MegaEmbedExtractor()
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = extractor.extract(url)
        
        if result:
            print("\n" + "=" * 80)
            print("✅ SUCESSO! M3U8 extraído:")
            print("=" * 80)
            print(result[:500])
            print("\n💾 Salvando em megaembed_extracted.m3u8...")
            with open('megaembed_extracted.m3u8', 'w') as f:
                f.write(result)
            print("✅ Salvo!")
        else:
            print("\n❌ Não foi possível extrair o m3u8")
    else:
        print("💡 Uso: python extract-megaembed-real.py <URL>")
        print("\n📝 Exemplo:")
        print("   python extract-megaembed-real.py 'https://megaembed.link/#xez5rx'")

if __name__ == "__main__":
    main()
