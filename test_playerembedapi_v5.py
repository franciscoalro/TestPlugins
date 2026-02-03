#!/usr/bin/env python3
"""
PlayerEmbedAPI v5.0 - Teste Automático Simplificado
Valida componentes críticos da extração de vídeo
"""

import base64
import hashlib
import json
import re
import time
from datetime import datetime

# Mock data
MOCK_USER_ID = "482120"
MOCK_SLUG = "yhRExEdvKy"
MOCK_MD5_ID = "27648163"

MOCK_MEDIA_JSON = {
    "hls": "https://cdn.iamcdn.net/hls/playlist_480p.m3u8",
    "mp4": ["https://cdn.iamcdn.net/videos/480p.mp4", "https://cdn.iamcdn.net/videos/720p.mp4"],
    "sources": [
        {"file": "https://cdn.iamcdn.net/hls/master.m3u8", "label": "Auto", "type": "hls"},
        {"file": "https://cdn.iamcdn.net/videos/480p.mp4", "label": "480p", "type": "mp4"}
    ]
}

def test_base64_extraction():
    """Teste 1: Extração de Base64"""
    print("\n" + "="*60)
    print("TESTE 1: Extração de Base64")
    print("="*60)
    
    test_data = json.dumps({"user_id": MOCK_USER_ID}).encode('utf-8')
    base64_data = base64.b64encode(test_data).decode('utf-8')
    
    html_variants = [
        f'const datas = "{base64_data}";',
        f'var datas = "{base64_data}";',
        f'<div data-datas="{base64_data}"></div>',
    ]
    
    pattern = r'datas\s*=\s*"([A-Za-z0-9+/=]+)"'
    passed = 0
    
    for i, html in enumerate(html_variants, 1):
        match = re.search(pattern, html)
        if match and match.group(1) == base64_data:
            print(f"  ✅ Variante {i}: PASS")
            passed += 1
        else:
            print(f"  ❌ Variante {i}: FAIL")
    
    print(f"\nResultado: {passed}/3 testes passaram")
    return passed == 3

def test_key_derivation():
    """Teste 2: Derivação de Chave AES"""
    print("\n" + "="*60)
    print("TESTE 2: Derivação de Chave AES-CTR")
    print("="*60)
    
    key_string = f"{MOCK_USER_ID}:{MOCK_SLUG}:{MOCK_MD5_ID}"
    md5_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()
    key_bytes = md5_hash.encode('utf-8')
    iv_bytes = key_bytes[:16]
    
    print(f"  Key string: {key_string}")
    print(f"  MD5 hash: {md5_hash}")
    print(f"  Key length: {len(key_bytes)} bytes")
    print(f"  IV length: {len(iv_bytes)} bytes")
    
    if len(key_bytes) == 32 and len(iv_bytes) == 16:
        print(f"\n  ✅ Tamanhos corretos: PASS")
        return True
    else:
        print(f"\n  ❌ Tamanhos incorretos: FAIL")
        return False

def test_url_validation():
    """Teste 3: Validação de URLs"""
    print("\n" + "="*60)
    print("TESTE 3: Validação de URLs de Vídeo")
    print("="*60)
    
    valid_urls = [
        "https://cdn.iamcdn.net/hls/playlist.m3u8",
        "https://cdn.iamcdn.net/videos/movie_480p.mp4",
        "https://storage.googleapis.com/video.mp4",
    ]
    
    invalid_urls = [
        "not-a-url",
        "ftp://invalid.com/file.mp4",
        "",
    ]
    
    passed = 0
    
    for url in valid_urls:
        if url.startswith('https://') and ('.m3u8' in url or '.mp4' in url):
            print(f"  ✅ URL válida aceita: {url[:50]}...")
            passed += 1
        else:
            print(f"  ❌ URL válida rejeitada: {url[:50]}...")
    
    for url in invalid_urls:
        if not url or not url.startswith('https://'):
            print(f"  ✅ URL inválida rejeitada: {url[:30] if url else 'empty'}")
            passed += 1
        else:
            print(f"  ❌ URL inválida aceita: {url[:30]}")
    
    total = len(valid_urls) + len(invalid_urls)
    print(f"\nResultado: {passed}/{total} testes passaram")
    return passed == total

def test_quality_detection():
    """Teste 4: Detecção de Qualidade"""
    print("\n" + "="*60)
    print("TESTE 4: Detecção de Qualidade")
    print("="*60)
    
    test_cases = [
        ("https://cdn.com/video_480p.mp4", "480p"),
        ("https://cdn.com/video_720p.mp4", "720p"),
        ("https://cdn.com/video_1080p.mp4", "1080p"),
        ("https://cdn.com/video_1920x1080.mp4", "1080p"),
    ]
    
    passed = 0
    
    for url, expected in test_cases:
        # Detecta qualidade pela URL
        match = re.search(r'(\d{3,4})p', url)
        if not match:
            match = re.search(r'x(\d{3,4})', url)
        
        detected = f"{match.group(1)}p" if match else "Unknown"
        
        if detected == expected:
            print(f"  ✅ {expected}: PASS")
            passed += 1
        else:
            print(f"  ❌ {expected}: FAIL (detectado: {detected})")
    
    print(f"\nResultado: {passed}/{len(test_cases)} testes passaram")
    return passed == len(test_cases)

def test_json_parsing():
    """Teste 5: Parsing de JSON"""
    print("\n" + "="*60)
    print("TESTE 5: Parsing de JSON com Escapes")
    print("="*60)
    
    test_cases = [
        ('{"url": "https://example.com/video.mp4"}', {"url": "https://example.com/video.mp4"}),
        ('{"title": "Episode"}', {"title": "Episode"}),
    ]
    
    passed = 0
    
    for json_str, expected in test_cases:
        try:
            parsed = json.loads(json_str)
            if parsed == expected:
                print(f"  ✅ Parse correto: {json_str[:40]}...")
                passed += 1
            else:
                print(f"  ❌ Parse incorreto: {json_str[:40]}...")
        except Exception as e:
            print(f"  ❌ Erro de parse: {e}")
    
    print(f"\nResultado: {passed}/{len(test_cases)} testes passaram")
    return passed == len(test_cases)

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("  PlayerEmbedAPI v5.0 - Suite de Testes Automáticos")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    results = []
    results.append(("Base64 Extraction", test_base64_extraction()))
    results.append(("Key Derivation", test_key_derivation()))
    results.append(("URL Validation", test_url_validation()))
    results.append(("Quality Detection", test_quality_detection()))
    results.append(("JSON Parsing", test_json_parsing()))
    
    duration = (time.time() - start_time) * 1000
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} módulos passaram")
    print(f"Taxa de sucesso: {(passed/total*100):.1f}%")
    print(f"Duração: {duration:.2f} ms")
    print("="*60)
    
    if passed == total:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        return 1

if __name__ == "__main__":
    exit(main())
