#!/usr/bin/env python3
"""
Teste de extração do MyVidPlay - Similar ao Filemoon
"""

import requests
import re
import json
from urllib.parse import unquote

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def test_myvidplay(url):
    """Testa extração do MyVidPlay"""
    print(f'\n{"="*60}')
    print(f'🔍 Testando MyVidPlay: {url}')
    print('='*60)
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(f'Status: {r.status_code}')
        print(f'Content-Length: {len(r.text)}')
        
        html = r.text
        
        # Salvar HTML para análise
        with open('myvidplay_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('📄 HTML salvo em myvidplay_response.html')
        
        # 1. Procurar por eval/packed JavaScript (comum em Filemoon)
        print('\n📦 Procurando JavaScript packed/eval...')
        eval_match = re.search(r"eval\(function\(p,a,c,k,e,d\).*?\)\)", html, re.DOTALL)
        if eval_match:
            print(f'  ✅ Encontrado eval packed! ({len(eval_match.group())} chars)')
            packed = eval_match.group()
            
            # Tentar extrair dados do packed
            # Padrão: split('|') no final
            split_match = re.search(r"'([^']+)'\.split\('\|'\)", packed)
            if split_match:
                words = split_match.group(1).split('|')
                print(f'  📝 Palavras no packed: {len(words)}')
                
                # Procurar por URLs de vídeo nas palavras
                for word in words:
                    if 'm3u8' in word.lower() or 'mp4' in word.lower():
                        print(f'  🎬 Possível vídeo: {word}')
        else:
            print('  ❌ Não encontrado eval packed')
        
        # 2. Procurar por URLs de vídeo diretas
        print('\n🎬 Procurando URLs de vídeo...')
        
        # M3U8
        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
        if m3u8_matches:
            print(f'  ✅ M3U8 encontrados: {len(m3u8_matches)}')
            for m in m3u8_matches[:5]:
                print(f'    → {m}')
        
        # MP4
        mp4_matches = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html)
        if mp4_matches:
            print(f'  ✅ MP4 encontrados: {len(mp4_matches)}')
            for m in mp4_matches[:5]:
                print(f'    → {m}')
        
        # 3. Procurar por configuração de player (JWPlayer, Plyr, etc.)
        print('\n⚙️ Procurando configuração de player...')
        
        # JWPlayer
        jwplayer_match = re.search(r'jwplayer\(["\']([^"\']+)["\']\)\.setup\((\{.*?\})\)', html, re.DOTALL)
        if jwplayer_match:
            print(f'  ✅ JWPlayer encontrado!')
            config = jwplayer_match.group(2)
            print(f'  Config: {config[:200]}...')
        
        # sources: [...]
        sources_match = re.search(r'sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if sources_match:
            print(f'  ✅ Sources encontrado!')
            sources = sources_match.group(1)
            print(f'  Sources: {sources[:300]}...')
            
            # Extrair URLs das sources
            file_matches = re.findall(r'file\s*:\s*["\']([^"\']+)["\']', sources)
            for f in file_matches:
                print(f'    🎬 File: {f}')
        
        # 4. Procurar por variáveis JavaScript com URLs
        print('\n📝 Procurando variáveis JavaScript...')
        
        # var file = "..."
        var_file = re.search(r'var\s+(?:file|source|video|src)\s*=\s*["\']([^"\']+)["\']', html)
        if var_file:
            print(f'  ✅ Variável encontrada: {var_file.group(1)}')
        
        # file: "..."
        file_prop = re.findall(r'["\']?file["\']?\s*:\s*["\']([^"\']+)["\']', html)
        if file_prop:
            print(f'  ✅ Propriedade file: {file_prop}')
        
        # 5. Procurar por iframes internos
        print('\n🖼️ Procurando iframes...')
        iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
        if iframes:
            print(f'  ✅ Iframes encontrados: {len(iframes)}')
            for iframe in iframes:
                print(f'    → {iframe}')
        
        # 6. Procurar por scripts externos
        print('\n📜 Scripts externos...')
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
        for s in scripts[:10]:
            print(f'  → {s}')
        
        # 7. Análise específica do Filemoon pattern
        print('\n🌙 Análise padrão Filemoon...')
        
        # Filemoon usa: atob() para decodificar
        atob_match = re.search(r'atob\(["\']([^"\']+)["\']\)', html)
        if atob_match:
            import base64
            encoded = atob_match.group(1)
            try:
                decoded = base64.b64decode(encoded).decode('utf-8')
                print(f'  ✅ atob decodificado: {decoded[:200]}')
            except:
                print(f'  ⚠️ atob encontrado mas não decodificável')
        
        # Filemoon usa: JSON.parse
        json_parse = re.search(r'JSON\.parse\(["\']([^"\']+)["\']\)', html)
        if json_parse:
            try:
                data = json.loads(json_parse.group(1).replace('\\"', '"'))
                print(f'  ✅ JSON.parse: {data}')
            except:
                print(f'  ⚠️ JSON.parse encontrado mas não parseável')
        
        return True
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    # URLs do MyVidPlay encontradas na análise
    urls = [
        'https://myvidplay.com/e/kieb85xhpkf3',
        'https://myvidplay.com/e/lsp5ozsw6zc9',
    ]
    
    for url in urls:
        test_myvidplay(url)
        print('\n')


if __name__ == '__main__':
    main()
