#!/usr/bin/env python3
"""
Analyze core.bundle.js to find SoTrym and decryption logic
"""
import re
import base64

def analyze_bundle():
    """Analyze the core.bundle.js file"""
    
    print("[*] Reading core_bundle_new.js...")
    
    with open("core_bundle_new.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"[+] File size: {len(content)} bytes")
    
    # Search for window.SoTrym assignment
    print("\n[*] Searching for window.SoTrym...")
    
    # Look for window.SoTrym or window['SoTrym']
    patterns = [
        r'window\[[\'"](SoTrym|sotrym)[\'"]]\s*=\s*([^;]+)',
        r'window\.(SoTrym|sotrym)\s*=\s*([^;]+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            print(f"\n[+] Found: {match.group()}")
            
            # Get more context
            start = match.start()
            context_start = max(0, start - 1000)
            context_end = min(len(content), start + 3000)
            context = content[context_start:context_end]
            
            print("\n" + "=" * 80)
            print("CONTEXT:")
            print("=" * 80)
            print(context)
            print("=" * 80)
    
    # Search for decrypt function
    print("\n[*] Searching for decrypt function...")
    
    decrypt_matches = re.finditer(r'function\s+(\w+)\s*\([^)]*\)\s*{[^}]{0,500}decrypt[^}]{0,500}}', content, re.IGNORECASE)
    for match in decrypt_matches:
        print(f"\n[+] Found decrypt function: {match.group(1)}")
        print(match.group())
    
    # Search for media processing
    print("\n[*] Searching for media field processing...")
    
    media_patterns = [
        r'\.media[^;]{0,300}',
        r'media[\'"][^;]{0,300}',
    ]
    
    for pattern in media_patterns:
        matches = list(re.finditer(pattern, content))
        if matches:
            print(f"\n[+] Found {len(matches)} matches for media processing")
            # Show unique matches
            unique_matches = list(set([m.group() for m in matches]))
            for match in unique_matches[:10]:
                print(f"    {match}")
    
    # Search for base64 decode
    print("\n[*] Searching for base64 decode...")
    
    atob_matches = re.finditer(r'atob\([^)]+\)[^;]{0,200}', content)
    for idx, match in enumerate(atob_matches):
        if idx < 10:  # Show first 10
            print(f"    {match.group()}")
    
    # Search for AES or crypto
    print("\n[*] Searching for crypto/AES...")
    
    crypto_patterns = [
        r'AES[^;]{0,200}',
        r'CryptoJS[^;]{0,200}',
        r'crypto[^;]{0,200}',
    ]
    
    for pattern in crypto_patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if matches:
            print(f"\n[+] Found {len(matches)} matches for {pattern}")
            for match in matches[:5]:
                print(f"    {match.group()}")
    
    # Try to find the actual decryption key or algorithm
    print("\n[*] Searching for decryption keys/algorithms...")
    
    # Look for hex strings (potential keys)
    hex_pattern = r'["\']([0-9a-fA-F]{32,})["\']'
    hex_matches = re.finditer(hex_pattern, content)
    hex_strings = list(set([m.group(1) for m in hex_matches]))
    
    if hex_strings:
        print(f"\n[+] Found {len(hex_strings)} potential hex keys")
        for hex_str in hex_strings[:5]:
            print(f"    {hex_str} (length: {len(hex_str)})")
    
    # Search for TextDecoder (used for decoding)
    print("\n[*] Searching for TextDecoder usage...")
    
    decoder_matches = re.finditer(r'TextDecoder[^;]{0,300}', content)
    for idx, match in enumerate(decoder_matches):
        if idx < 5:
            print(f"    {match.group()}")
    
    # Look for the actual video URL extraction
    print("\n[*] Searching for video URL extraction...")
    
    url_extract_patterns = [
        r'file[\'"]?\s*:\s*[^,]+',
        r'sources[\'"]?\s*:\s*\[[^\]]+\]',
        r'\.m3u8[^;]{0,100}',
    ]
    
    for pattern in url_extract_patterns:
        matches = list(re.finditer(pattern, content))
        if matches:
            print(f"\n[+] Found {len(matches)} matches for {pattern}")
            for match in matches[:5]:
                print(f"    {match.group()}")

if __name__ == '__main__':
    analyze_bundle()
