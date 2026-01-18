#!/usr/bin/env python3
"""
Analisador de resposta JS do MegaEmbed
Extrai m3u8 camuflado de arquivos .txt ou .js
"""

import requests
import re
import base64
import json
from urllib.parse import urlparse, parse_qs

def analyze_megaembed_response(url):
    """Analisa resposta do megaembed e extrai m3u8"""
    
    print(f"\n🔍 Analisando: {url}")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://megaembed.link/',
        'Origin': 'https://megaembed.link'
    }
    
    try:
        response = requests.get(url, headers=headers, allow_redirects=True)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Tamanho: {len(response.content)} bytes")
        print(f"🔗 URL Final: {response.url}")
        
        content = response.text
        
        # Detectar tipo de resposta
        print("\n🔎 Tipo de Resposta:")
        
        # 1. Verificar se é JavaScript
        if 'function' in content or 'var ' in content or 'const ' in content:
            print("   ⚠️  JAVASCRIPT detectado!")
            analyze_javascript(content)
        
        # 2. Verificar se é m3u8 direto
        elif '#EXTM3U' in content:
            print("   ✅ M3U8 DIRETO encontrado!")
            print("\n📺 Conteúdo M3U8:")
            print(content[:500])
            return content
        
        # 3. Verificar se é JSON
        elif content.strip().startswith('{'):
            print("   📦 JSON detectado!")
            analyze_json(content)
        
        # 4. Verificar se é HTML
        elif '<html' in content.lower() or '<!doctype' in content.lower():
            print("   🌐 HTML detectado!")
            analyze_html(content)
        
        # 5. Verificar se é texto puro (m3u8 camuflado)
        else:
            print("   📝 TEXTO PURO - possível m3u8 camuflado")
            if content.startswith('http'):
                print(f"   🎯 URL encontrada: {content[:200]}")
                return content
        
        # Buscar padrões comuns
        print("\n🔍 Buscando padrões:")
        
        # URLs m3u8
        m3u8_urls = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', content)
        if m3u8_urls:
            print(f"   ✅ {len(m3u8_urls)} URL(s) m3u8 encontrada(s):")
            for m3u8 in m3u8_urls[:3]:
                print(f"      - {m3u8}")
        
        # URLs .txt
        txt_urls = re.findall(r'https?://[^\s\'"]+\.txt[^\s\'"]*', content)
        if txt_urls:
            print(f"   📄 {len(txt_urls)} URL(s) .txt encontrada(s):")
            for txt in txt_urls[:3]:
                print(f"      - {txt}")
                # Tentar baixar o .txt
                try:
                    txt_response = requests.get(txt, headers=headers)
                    if '#EXTM3U' in txt_response.text:
                        print(f"      ✅ M3U8 encontrado em {txt}!")
                        return txt_response.text
                except:
                    pass
        
        # Base64
        b64_matches = re.findall(r'[A-Za-z0-9+/]{40,}={0,2}', content)
        if b64_matches:
            print(f"   🔐 {len(b64_matches)} string(s) Base64 encontrada(s)")
            for b64 in b64_matches[:2]:
                try:
                    decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                    if 'http' in decoded or 'm3u8' in decoded:
                        print(f"      ✅ Decodificado: {decoded[:100]}")
                except:
                    pass
        
        return None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def analyze_javascript(content):
    """Analisa código JavaScript"""
    print("\n📜 Análise JavaScript:")
    
    # Procurar variáveis com URLs
    var_patterns = [
        r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
        r'const\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
        r'let\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in var_patterns:
        matches = re.findall(pattern, content)
        for var_name, value in matches:
            if 'http' in value or 'm3u8' in value or '.txt' in value:
                print(f"   📌 {var_name} = {value}")
    
    # Procurar funções de decodificação
    if 'atob' in content:
        print("   🔐 Função atob() (Base64) detectada")
    if 'decode' in content.lower():
        print("   🔐 Função decode detectada")
    if 'decrypt' in content.lower():
        print("   🔐 Função decrypt detectada")

def analyze_json(content):
    """Analisa JSON"""
    try:
        data = json.loads(content)
        print("\n📦 Estrutura JSON:")
        print(json.dumps(data, indent=2)[:500])
        
        # Procurar URLs recursivamente
        def find_urls(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    find_urls(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_urls(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                if 'http' in obj or 'm3u8' in obj:
                    print(f"   🎯 {path}: {obj}")
        
        find_urls(data)
    except:
        print("   ⚠️  JSON inválido")

def analyze_html(content):
    """Analisa HTML"""
    print("\n🌐 Análise HTML:")
    
    # Procurar iframes
    iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', content)
    if iframes:
        print(f"   🖼️  {len(iframes)} iframe(s) encontrado(s):")
        for iframe in iframes[:3]:
            print(f"      - {iframe}")
    
    # Procurar scripts
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if scripts:
        print(f"   📜 {len(scripts)} script(s) encontrado(s)")
        for script in scripts[:2]:
            if 'm3u8' in script or 'video' in script.lower():
                print(f"      ⚠️  Script com referência a vídeo encontrado")

def test_common_megaembed_patterns():
    """Testa padrões comuns do megaembed"""
    
    print("\n🧪 TESTANDO PADRÕES COMUNS DO MEGAEMBED")
    print("=" * 80)
    
    # Padrões de URL do megaembed
    test_urls = [
        "https://megaembed.link/#xez5rx",  # Do Burp Suite
        "https://megaembed.link/api/video/xez5rx",
        "https://megaembed.link/api/source/xez5rx",
    ]
    
    for url in test_urls:
        analyze_megaembed_response(url)
        print("\n" + "-" * 80 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        analyze_megaembed_response(url)
    else:
        print("💡 Uso: python analyze-js-response.py <URL>")
        print("\n🧪 Executando testes com URLs do Burp Suite...")
        test_common_megaembed_patterns()
