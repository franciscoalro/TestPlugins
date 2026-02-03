#!/usr/bin/env python3
"""
PLAYEREMBEDAPI - FINAL EXTRACTION SYSTEM
Ultima versao integrada de todas as tecnicas

Uso: python playerembedapi_final_extractor.py <arquivo.html|url>
"""

import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

class PlayerEmbedAPIFinalExtractor:
    """Extrator final unificado"""
    
    def __init__(self, html_content: str = None, url: str = None):
        self.html = html_content
        self.url = url or ""
        self.video_data = None
        self.extracted_urls = []
    
    def extract_datas(self):
        """Extrai e decodifica o campo datas"""
        match = re.search(r'const\s+datas\s*=\s*"([^"]+)"', self.html)
        if not match:
            return None
        
        datas_b64 = match.group(1)
        padding = 4 - len(datas_b64) % 4
        if padding != 4:
            datas_b64 += '=' * padding
        
        decoded = base64.b64decode(datas_b64)
        decoded_str = decoded.decode('utf-8', errors='replace')
        
        # Extrair campos com regex (campo media pode quebrar JSON parse)
        slug = re.search(r'"slug":"([^"]+)"', decoded_str)
        md5_id = re.search(r'"md5_id":(\d+)', decoded_str)
        user_id = re.search(r'"user_id":(\d+)', decoded_str)
        
        return {
            'slug': slug.group(1) if slug else None,
            'md5_id': int(md5_id.group(1)) if md5_id else None,
            'user_id': int(user_id.group(1)) if user_id else None,
            'raw': decoded_str[:200]  # Primeiros 200 chars
        }
    
    def find_video_urls(self):
        """Procura por URLs de video no HTML"""
        patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*',
            r'https?://[^\s"\'<>]*googleapis\.com/mediastorage[^\s"\'<>]*',
        ]
        
        found = set()
        for pattern in patterns:
            matches = re.findall(pattern, self.html)
            for m in matches:
                # Filtrar apenas URLs de video (nao scripts)
                if any(ext in m for ext in ['.m3u8', '.mp4', '/sora/', 'mediastorage']):
                    found.add(m)
        
        return list(found)
    
    def construct_cdn_urls(self, data):
        """Constroi URLs de CDN a partir dos dados"""
        if not data or not data['slug'] or not data['md5_id']:
            return []
        
        return [
            f"https://{data['slug']}.sssrr.org/sora/{data['md5_id']}/",
            f"https://cdn.sssrr.org/sora/{data['md5_id']}/",
            f"https://{data['slug']}.sssrr.org/future",
        ]
    
    def extract(self):
        """Executa extracao completa"""
        results = {
            'source_url': self.url,
            'datas': None,
            'video_urls_found': [],
            'cdn_urls_constructed': [],
            'scripts': [],
            'recommendation': None
        }
        
        # 1. Extrair datas
        results['datas'] = self.extract_datas()
        
        # 2. Procurar URLs no HTML
        results['video_urls_found'] = self.find_video_urls()
        
        # 3. Construir URLs CDN
        if results['datas']:
            results['cdn_urls_constructed'] = self.construct_cdn_urls(results['datas'])
        
        # 4. Listar scripts
        results['scripts'] = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', self.html)
        
        # 5. Recomendacao
        if results['video_urls_found']:
            results['recommendation'] = "URLs encontradas no HTML - usar diretamente"
        elif results['cdn_urls_constructed']:
            results['recommendation'] = "Usar WebView para acessar URLs CDN construidas"
        else:
            results['recommendation'] = "Requer analise dinamica com browser"
        
        return results

def print_report(results):
    """Imprime relatorio formatado"""
    print("=" * 60)
    print("PLAYEREMBEDAPI - EXTRACTION REPORT")
    print("=" * 60)
    
    # Dados
    if results['datas']:
        d = results['datas']
        print("\n[+] DADOS EXTRAIDOS:")
        print(f"    Slug: {d['slug']}")
        print(f"    MD5 ID: {d['md5_id']}")
        print(f"    User ID: {d['user_id']}")
    
    # URLs encontradas
    print(f"\n[+] URLS DE VIDEO ENCONTRADAS: {len(results['video_urls_found'])}")
    for url in results['video_urls_found'][:5]:  # Max 5
        print(f"    - {url[:70]}...")
    
    # URLs construidas
    print(f"\n[+] URLS CDN CONSTRUIDAS: {len(results['cdn_urls_constructed'])}")
    for url in results['cdn_urls_constructed']:
        print(f"    - {url}")
    
    # Scripts
    print(f"\n[+] SCRIPTS CARREGADOS: {len(results['scripts'])}")
    for script in results['scripts']:
        if 'sssrr' in script or 'jwplayer' in script:
            print(f"    * {script}")  # Destacar importantes
        else:
            print(f"      {script}")
    
    # Recomendacao
    print(f"\n[+] RECOMENDACAO:")
    print(f"    {results['recommendation']}")
    
    # Headers para reproducao
    print("\n[+] HEADERS PARA REPRODUCAO:")
    print('    {')
    print('      "Referer": "https://playerembedapi.link/",')
    print('      "Origin": "https://playerembedapi.link",')
    print('      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"')
    print('    }')
    
    print("\n" + "=" * 60)

def main():
    if len(sys.argv) < 2:
        # Testar com arquivo exemplo
        examples = [
            'playerembedapi_kBJLtxCD3.html',
            'playerembedapi_QvXFt2de3.html',
        ]
        
        for example in examples:
            if Path(example).exists():
                print(f"[*] Usando arquivo de exemplo: {example}\n")
                with open(example, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()
                
                extractor = PlayerEmbedAPIFinalExtractor(html, f"file://{example}")
                results = extractor.extract()
                print_report(results)
                
                # Salvar JSON
                json_file = example.replace('.html', '_extraction.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"[*] Resultado salvo em: {json_file}")
                return
        
        print("Uso: python playerembedapi_final_extractor.py <arquivo.html>")
        return
    
    input_file = sys.argv[1]
    
    if input_file.startswith('http'):
        import requests
        print(f"[*] Baixando: {input_file}")
        resp = requests.get(input_file, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        html = resp.text
        url = input_file
    else:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        url = f"file://{input_file}"
    
    extractor = PlayerEmbedAPIFinalExtractor(html, url)
    results = extractor.extract()
    print_report(results)

if __name__ == '__main__':
    main()
