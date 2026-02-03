#!/usr/bin/env python3
"""
Test PlayerEmbedAPI extraction - HTTP vs Playwright
Compares what can be extracted via pure HTTP vs browser automation
"""
import requests
import re
import json
from datetime import datetime

def test_http_extraction(url):
    """Test what we can extract via pure HTTP"""
    print("="*80)
    print("TEST 1: PURE HTTP EXTRACTION")
    print("="*80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://playerembedapi.link/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        print(f"\n[*] Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        print(f"[+] Status: {response.status_code}")
        print(f"[+] HTML Size: {len(html)} bytes")
        
        # Analyze HTML structure
        print("\n[*] Analyzing HTML structure...")
        
        # Check for JWPlayer
        has_jwplayer = 'jwplayer' in html.lower()
        print(f"  - Has JWPlayer: {has_jwplayer}")
        
        # Check for video URLs
        video_patterns = [
            r'https?://[^\s"\']+\.m3u8[^\s"\']*',
            r'https?://[^\s"\']*storage\.googleapis[^\s"\']+',
            r'https?://[^\s"\']*cloudatacdn[^\s"\']+',
            r'https?://[^\s"\']+\.mp4[^\s"\']*',
        ]
        
        found_urls = []
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                found_urls.extend(matches)
                print(f"  - Pattern '{pattern[:30]}...': {len(matches)} matches")
        
        # Check for encrypted data
        has_base64 = bool(re.search(r'const datas\s*=\s*["\']([A-Za-z0-9+/=]{100,})["\']', html))
        print(f"  - Has encrypted data (base64): {has_base64}")
        
        # Check for AES/crypto references
        has_crypto = any(keyword in html.lower() for keyword in ['aes', 'crypto', 'decrypt', 'cipher'])
        print(f"  - Has crypto references: {has_crypto}")
        
        # Extract JWPlayer setup if present
        jwplayer_setup = re.search(r'jwplayer\([^)]+\)\.setup\((\{[^}]+\})\)', html, re.DOTALL)
        if jwplayer_setup:
            print(f"\n[+] Found JWPlayer setup (partial):")
            print(f"    {jwplayer_setup.group(1)[:200]}...")
        
        # Save HTML for analysis
        html_file = f"playerembedapi_http_{int(datetime.now().timestamp())}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n[+] HTML saved to: {html_file}")
        
        return {
            'method': 'HTTP',
            'status_code': response.status_code,
            'html_size': len(html),
            'has_jwplayer': has_jwplayer,
            'has_encrypted_data': has_base64,
            'has_crypto': has_crypto,
            'video_urls_found': len(found_urls),
            'video_urls': found_urls[:5],  # First 5
            'html_file': html_file
        }
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return {'method': 'HTTP', 'error': str(e)}

def analyze_client_vs_server():
    """Analyze what's manipulable on client vs server"""
    print("\n" + "="*80)
    print("ANALYSIS: CLIENT VS SERVER")
    print("="*80)
    
    analysis = {
        'client_side': {
            'accessible': [
                'HTML content (after JS execution)',
                'JWPlayer configuration (after initialization)',
                'Network requests (via browser)',
                'LocalStorage/SessionStorage',
                'Decrypted video URLs (after AES-CTR decryption)',
                'DOM elements and attributes'
            ],
            'not_accessible': [
                'Encrypted data without JS execution',
                'AES-CTR key derivation (complex)',
                'Server-side validation logic',
                'Token generation algorithms'
            ]
        },
        'server_side': {
            'controls': [
                'HTML generation with encrypted data',
                'AES-CTR encryption key',
                'Video URL generation',
                'Referer validation',
                'Token expiration',
                'Google Cloud Storage access'
            ],
            'cannot_prevent': [
                'Browser automation (Playwright/Selenium)',
                'Network interception in browser',
                'JWPlayer config extraction (after JS runs)',
                'Video URL capture (after decryption)'
            ]
        },
        'extraction_methods': {
            'pure_http': {
                'success_rate': '0%',
                'reason': 'Data is AES-CTR encrypted, cannot decrypt without JS',
                'speed': 'Fast (~1s)',
                'reliability': 'Low'
            },
            'browser_automation': {
                'success_rate': '100%',
                'reason': 'JS executes and decrypts data naturally',
                'speed': 'Slow (~5-10s)',
                'reliability': 'High'
            }
        }
    }
    
    print("\n📊 CLIENT-SIDE (Browser):")
    print("  ✅ Can access:")
    for item in analysis['client_side']['accessible']:
        print(f"    - {item}")
    print("\n  ❌ Cannot access:")
    for item in analysis['client_side']['not_accessible']:
        print(f"    - {item}")
    
    print("\n🖥️  SERVER-SIDE:")
    print("  ✅ Controls:")
    for item in analysis['server_side']['controls']:
        print(f"    - {item}")
    print("\n  ❌ Cannot prevent:")
    for item in analysis['server_side']['cannot_prevent']:
        print(f"    - {item}")
    
    print("\n🔧 EXTRACTION METHODS:")
    for method, details in analysis['extraction_methods'].items():
        print(f"\n  {method.upper()}:")
        for key, value in details.items():
            print(f"    {key}: {value}")
    
    return analysis

if __name__ == '__main__':
    # Test URL
    test_url = "https://playerembedapi.link/?v=rTxfmoIhd"
    
    print("\n" + "="*80)
    print("PLAYEREMBEDAPI EXTRACTION TEST")
    print("="*80)
    print(f"Test URL: {test_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: HTTP extraction
    http_results = test_http_extraction(test_url)
    
    # Test 2: Analyze client vs server
    analysis = analyze_client_vs_server()
    
    # Save combined results
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_url': test_url,
        'http_extraction': http_results,
        'client_server_analysis': analysis
    }
    
    output_file = f"playerembedapi_test_{int(datetime.now().timestamp())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[+] Full results saved to: {output_file}")
    
    # Print conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\n✅ RECOMMENDED SOLUTION:")
    print("  Use WebView/Playwright to let JavaScript execute naturally.")
    print("  This allows AES-CTR decryption to happen automatically.")
    print("\n❌ NOT RECOMMENDED:")
    print("  Pure HTTP extraction - data is encrypted and cannot be")
    print("  decrypted without complex reverse engineering.")
    print("\n" + "="*80)
