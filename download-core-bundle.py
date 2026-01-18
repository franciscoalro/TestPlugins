#!/usr/bin/env python3
"""
Download and analyze core.bundle.js from PlayerEmbedAPI
"""
import requests
import re
import json

def download_bundle():
    """Download the core.bundle.js file"""
    url = "https://iamcdn.net/player-v2/core.bundle.js"
    
    print(f"[*] Downloading {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        print(f"[+] Downloaded {len(content)} bytes")
        
        # Save to file
        with open("core_bundle_new.js", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Saved to core_bundle_new.js")
        
        # Search for SoTrym function
        print("\n[*] Searching for SoTrym function...")
        
        # Look for function definitions
        patterns = [
            r'function\s+SoTrym\s*\([^)]*\)\s*{',
            r'SoTrym\s*=\s*function\s*\([^)]*\)\s*{',
            r'SoTrym:\s*function\s*\([^)]*\)\s*{',
            r'window\.SoTrym\s*=\s*function\s*\([^)]*\)\s*{',
            r'const\s+SoTrym\s*=\s*\([^)]*\)\s*=>',
            r'var\s+SoTrym\s*=\s*function\s*\([^)]*\)\s*{',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = match.start()
                # Extract surrounding context (500 chars before and after)
                context_start = max(0, start - 500)
                context_end = min(len(content), start + 2000)
                context = content[context_start:context_end]
                
                print(f"\n[+] Found SoTrym at position {start}:")
                print("=" * 80)
                print(context)
                print("=" * 80)
        
        # Search for media decoding
        print("\n[*] Searching for media decoding logic...")
        
        decode_patterns = [
            r'\.media[^;]{0,200}',
            r'atob\([^)]+\)',
            r'JSON\.parse\([^)]+\)',
            r'decrypt[^;]{0,200}',
            r'decode[^;]{0,200}',
        ]
        
        for pattern in decode_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                print(f"\n[+] Found {len(matches)} matches for pattern: {pattern}")
                # Show first 3 matches
                for match in matches[:3]:
                    print(f"    {match.group()}")
        
        # Search for jwplayer setup
        print("\n[*] Searching for jwplayer setup...")
        
        jwplayer_patterns = [
            r'jwplayer\([^)]*\)\.setup\([^)]+\)',
            r'\.setup\(\{[^}]{0,500}\}\)',
        ]
        
        for pattern in jwplayer_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                print(f"\n[+] Found {len(matches)} matches for pattern: {pattern}")
                for match in matches[:3]:
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(content), match.end() + 200)
                    context = content[context_start:context_end]
                    print(f"\n{context}")
        
        # Look for URL patterns
        print("\n[*] Searching for URL patterns...")
        
        url_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'/sora/\d+/[A-Za-z0-9+/=]+',
            r'sssrr\.org',
        ]
        
        for pattern in url_patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                print(f"\n[+] Found {len(matches)} matches for pattern: {pattern}")
                for match in list(set([m.group() for m in matches]))[:5]:
                    print(f"    {match}")
        
        return content
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

if __name__ == '__main__':
    download_bundle()
