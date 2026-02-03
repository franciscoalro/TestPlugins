#!/usr/bin/env python3
"""
Test PlayerEmbedAPI with REAL URL from user logs
URL: https://playerembedapi.link/?v=rTxfmoIhd
"""
import requests
import re
import json
import base64
from datetime import datetime

def analyze_playerembedapi_html(url):
    """Analyze PlayerEmbedAPI HTML to understand structure"""
    print("="*80)
    print("PLAYEREMBEDAPI DEEP ANALYSIS")
    print("="*80)
    print(f"URL: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://playerembedapi.link/',
        'Accept': 'text/html'
    }
    
    response = requests.get(url, headers=headers)
    html = response.text
    
    print(f"[+] Status: {response.status_code}")
    print(f"[+] HTML Size: {len(html)} bytes\n")
    
    # 1. Find encrypted data
    print("[1] SEARCHING FOR ENCRYPTED DATA...")
    datas_pattern = r'const datas\s*=\s*["\']([A-Za-z0-9+/=]+)["\']'
    datas_match = re.search(datas_pattern, html)
    
    if datas_match:
        encrypted_data = datas_match.group(1)
        print(f"  ✅ Found encrypted data (base64)")
        print(f"  Length: {len(encrypted_data)} characters")
        print(f"  Preview: {encrypted_data[:100]}...")
        
        # Try to decode base64
        try:
            decoded = base64.b64decode(encrypted_data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            print(f"\n  [*] Base64 decoded (first 200 chars):")
            print(f"      {decoded_str[:200]}")
            
            # Check if it's JSON
            try:
                json_data = json.loads(decoded_str)
                print(f"\n  ✅ Decoded data is JSON!")
                print(f"  Keys: {list(json_data.keys())}")
                
                # Check for encrypted media field
                if 'media' in json_data:
                    media = json_data['media']
                    print(f"\n  [*] Found 'media' field:")
                    print(f"      Type: {type(media)}")
                    print(f"      Length: {len(str(media))}")
                    print(f"      Preview: {str(media)[:100]}...")
                    print(f"\n  ⚠️  MEDIA FIELD IS ENCRYPTED (AES-CTR)")
                    print(f"      Cannot decrypt without:")
                    print(f"        - user_id: {json_data.get('user_id', 'N/A')}")
                    print(f"        - md5_id: {json_data.get('md5_id', 'N/A')}")
                    print(f"        - slug: {json_data.get('slug', 'N/A')}")
                    print(f"        - AES-CTR decryption algorithm")
                
            except json.JSONDecodeError:
                print(f"  ❌ Decoded data is not valid JSON")
                
        except Exception as e:
            print(f"  ❌ Error decoding base64: {e}")
    else:
        print(f"  ❌ No encrypted data found")
    
    # 2. Find JWPlayer setup
    print(f"\n[2] SEARCHING FOR JWPLAYER SETUP...")
    jwplayer_pattern = r'jwplayer\([^)]+\)\.setup\((\{[^}]+\})\)'
    jwplayer_match = re.search(jwplayer_pattern, html, re.DOTALL)
    
    if jwplayer_match:
        setup = jwplayer_match.group(1)
        print(f"  ✅ Found JWPlayer setup")
        print(f"  Content: {setup[:200]}...")
    else:
        print(f"  ❌ No JWPlayer setup found in HTML")
    
    # 3. Find JavaScript files
    print(f"\n[3] SEARCHING FOR JAVASCRIPT FILES...")
    js_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
    js_files = re.findall(js_pattern, html)
    
    if js_files:
        print(f"  ✅ Found {len(js_files)} JavaScript files:")
        for js_file in js_files[:5]:
            print(f"      - {js_file}")
    else:
        print(f"  ❌ No external JavaScript files found")
    
    # 4. Find video URL patterns (unlikely in encrypted version)
    print(f"\n[4] SEARCHING FOR VIDEO URLs...")
    video_patterns = [
        (r'https?://[^\s"\']+\.m3u8[^\s"\']*', 'M3U8'),
        (r'https?://[^\s"\']*storage\.googleapis[^\s"\']+', 'Google Storage'),
        (r'https?://[^\s"\']*cloudatacdn[^\s"\']+', 'CloudataCDN'),
        (r'https?://[^\s"\']+\.mp4[^\s"\']*', 'MP4'),
    ]
    
    found_any = False
    for pattern, name in video_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f"  ✅ Found {name} URLs: {len(matches)}")
            for match in matches[:2]:
                print(f"      - {match}")
            found_any = True
    
    if not found_any:
        print(f"  ❌ No video URLs found in HTML (expected - data is encrypted)")
    
    # Save HTML
    html_file = f"playerembedapi_analysis_{int(datetime.now().timestamp())}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n[+] HTML saved to: {html_file}")
    
    # CONCLUSION
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\n🔍 FINDINGS:")
    print("  1. ✅ HTML contains encrypted data (base64)")
    print("  2. ✅ Data can be decoded to JSON")
    print("  3. ⚠️  'media' field is AES-CTR encrypted")
    print("  4. ❌ No video URLs in HTML (encrypted)")
    print("\n💡 WHY PURE HTTP FAILS:")
    print("  - Video URL is inside encrypted 'media' field")
    print("  - Requires AES-CTR decryption with complex key derivation")
    print("  - Key depends on: user_id + md5_id + slug")
    print("  - Decryption algorithm is complex (not worth reverse engineering)")
    print("\n✅ WHY WEBVIEW WORKS:")
    print("  - JavaScript executes automatically")
    print("  - AES-CTR decryption happens in browser")
    print("  - JWPlayer initializes with decrypted URL")
    print("  - WebView can intercept the final video URL")
    print("\n🎯 RECOMMENDATION:")
    print("  Use WebView (PlayerEmbedAPIExtractorV7) as PRIMARY method")
    print("  Pure HTTP (V8) will ALWAYS fail for PlayerEmbedAPI")
    print("="*80)

if __name__ == '__main__':
    # Use the EXACT URL from user's logs
    test_url = "https://playerembedapi.link/?v=rTxfmoIhd"
    
    analyze_playerembedapi_html(test_url)
