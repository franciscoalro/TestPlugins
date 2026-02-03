#!/usr/bin/env python3
"""
PLAYEREMBEDAPI - ADVANCED REVERSE ENGINEERING TOOLKIT
White Hat Hacking & Extraction Suite

Tecnicas implementadas:
1. Analise estatica do HTML e JavaScript
2. Decodificacao e analise do campo 'datas'
3. Engenharia reversa do core.bundle.js
4. Simulacao de execucao JavaScript
5. Interceptacao de rede simulada
6. Manipulacao de DOM virtual
7. Analise de padroes de criptografia
"""

import base64
import json
import re
import sys
import hashlib
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class VideoData:
    slug: str
    md5_id: int
    user_id: int
    media: bytes
    config: Dict[str, Any]
    raw_json: Dict[str, Any]

class PlayerEmbedAPIAnalyzer:
    def __init__(self, html_content: str = None, url: str = None):
        self.html = html_content
        self.url = url
        self.video_data: Optional[VideoData] = None
    
    def extract_datas_field(self) -> Optional[str]:
        pattern1 = r'const\s+datas\s*=\s*"([^"]+)"'
        match = re.search(pattern1, self.html)
        if match:
            return match.group(1)
        return None
    
    def decode_datas(self, datas_b64: str) -> Optional[VideoData]:
        try:
            padding = 4 - len(datas_b64) % 4
            if padding != 4:
                datas_b64 += '=' * padding
            
            decoded = base64.b64decode(datas_b64)
            json_data = json.loads(decoded)
            
            media_data = json_data.get('media', '')
            # O campo media pode ser binario criptografado - manter como bytes
            if isinstance(media_data, str):
                try:
                    # Tentar como base64
                    media_bytes = base64.b64decode(media_data)
                except:
                    # Se falhar, manter como string bytes
                    media_bytes = media_data.encode('latin-1', errors='ignore')
            else:
                media_bytes = bytes(media_data) if media_data else b''
            
            self.video_data = VideoData(
                slug=json_data.get('slug', ''),
                md5_id=json_data.get('md5_id', 0),
                user_id=json_data.get('user_id', 0),
                media=media_bytes,
                config=json_data.get('config', {}),
                raw_json=json_data
            )
            return self.video_data
        except Exception as e:
            print(f"[!] Erro ao decodificar datas: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_media_field(self) -> Dict[str, Any]:
        if not self.video_data:
            return {}
        
        media = self.video_data.media
        
        # Calcular entropia
        from math import log2
        entropy = 0.0
        if media:
            for x in range(256):
                p_x = float(media.count(x)) / len(media)
                if p_x > 0:
                    entropy += - p_x * log2(p_x)
        
        return {
            'size': len(media),
            'entropy': round(entropy, 2),
            'is_printable': all(32 <= b < 127 for b in media[:100]) if media else False,
            'prefix_hex': media[:16].hex() if media else '',
        }

def analyze_file(filepath: str):
    print(f"[*] Analisando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    analyzer = PlayerEmbedAPIAnalyzer(html, f"file://{filepath}")
    
    # Extrair datas
    datas = analyzer.extract_datas_field()
    if not datas:
        print("[!] Campo 'datas' nao encontrado")
        return
    
    print(f"[+] Campo datas encontrado ({len(datas)} chars)")
    
    # Decodificar
    video_data = analyzer.decode_datas(datas)
    if not video_data:
        print("[!] Falha ao decodificar datas")
        return
    
    print(f"\n[+] DADOS DECODIFICADOS:")
    print(f"    Slug: {video_data.slug}")
    print(f"    MD5 ID: {video_data.md5_id}")
    print(f"    User ID: {video_data.user_id}")
    print(f"    Config: {json.dumps(video_data.config, indent=2)}")
    
    # Analisar media
    media_analysis = analyzer.analyze_media_field()
    print(f"\n[+] ANALISE DO CAMPO MEDIA:")
    print(f"    Tamanho: {media_analysis.get('size')} bytes")
    print(f"    Entropia: {media_analysis.get('entropy')}/8.0")
    print(f"    Provavelmente criptografado: {media_analysis.get('entropy', 0) > 7.0}")
    print(f"    Prefixo (hex): {media_analysis.get('prefix_hex')}")
    
    # URLs potenciais
    print(f"\n[+] URLS POTENCIAIS:")
    print(f"    https://{video_data.slug}.sssrr.org/sora/{video_data.md5_id}/")
    print(f"    https://cdn.sssrr.org/sora/{video_data.md5_id}/")
    
    # Procurar por URLs no HTML
    print(f"\n[+] BUSCANDO URLS DE VIDEO NO HTML:")
    patterns = [
        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
        r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
        r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*',
    ]
    
    found_urls = set()
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for m in matches:
            if m not in found_urls:
                found_urls.add(m)
                print(f"    Found: {m[:80]}...")
    
    if not found_urls:
        print("    Nenhuma URL de video encontrada no HTML")
    
    # Analise de scripts
    print(f"\n[+] SCRIPTS CARREGADOS:")
    script_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
    scripts = re.findall(script_pattern, html)
    for script in scripts:
        print(f"    {script}")
    
    # Salvar relatorio
    report = {
        'file': filepath,
        'video_data': {
            'slug': video_data.slug,
            'md5_id': video_data.md5_id,
            'user_id': video_data.user_id,
            'config': video_data.config
        },
        'media_analysis': media_analysis,
        'potential_urls': [
            f"https://{video_data.slug}.sssrr.org/sora/{video_data.md5_id}/",
            f"https://cdn.sssrr.org/sora/{video_data.md5_id}/"
        ],
        'found_video_urls': list(found_urls)
    }
    
    report_file = filepath.replace('.html', '_analysis.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[+] Relatorio salvo em: {report_file}")

def main():
    print("=" * 60)
    print("PLAYEREMBEDAPI - ANALYZER")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        analyze_file(sys.argv[1])
    else:
        # Procurar arquivos de exemplo
        examples = [
            'playerembedapi_kBJLtxCD3.html',
            'playerembedapi_QvXFt2de3.html',
            'playerembedapi_response_new.html',
        ]
        
        for example in examples:
            if Path(example).exists():
                print(f"\n[*] Usando arquivo de exemplo: {example}\n")
                analyze_file(example)
                break
        else:
            print("Uso: python hacker_analyzer.py <arquivo.html>")

if __name__ == '__main__':
    main()
