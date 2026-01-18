#!/usr/bin/env python3
"""
Extract the exact decryption logic from core.bundle.js
"""
import re
import json

def extract_decrypt_logic():
    """Extract decryption logic"""
    
    print("[*] Reading core_bundle_new.js...")
    
    with open("core_bundle_new.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"[+] File size: {len(content)} bytes")
    
    # Found: AES-CTR encryption
    print("\n[+] ENCRYPTION ALGORITHM: AES-CTR")
    
    # Search for the class/function that handles decryption
    print("\n[*] Searching for decryption class...")
    
    # Look for the pattern we found: algorithm, key, keyUsages, encoder
    pattern = r'(this\[[\'"]\w+[\'"]\]\s*=\s*null[^}]{0,500}AES-CTR[^}]{0,500}TextEncoder[^}]{0,500})'
    
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        print("\n[+] Found decryption initialization:")
        print("=" * 80)
        print(match.group())
        print("=" * 80)
        
        # Get more context (the whole class/function)
        start = match.start()
        # Go back to find function/class start
        context_start = max(0, start - 2000)
        context_end = min(len(content), start + 5000)
        context = content[context_start:context_end]
        
        print("\n[+] Full context:")
        print("=" * 80)
        print(context)
        print("=" * 80)
    
    # Search for where media is processed
    print("\n[*] Searching for media processing...")
    
    # Found: media']=JSON[...](...)
    media_json_pattern = r'media[\'"]\]\s*=\s*JSON\[[^\]]+\]\([^)]+\)'
    
    matches = re.finditer(media_json_pattern, content)
    for match in matches:
        start = match.start()
        context_start = max(0, start - 500)
        context_end = min(len(content), start + 1000)
        context = content[context_start:context_end]
        
        print("\n[+] Found media JSON processing:")
        print("=" * 80)
        print(context)
        print("=" * 80)
    
    # Search for the decrypt call with media
    print("\n[*] Searching for decrypt calls...")
    
    decrypt_pattern = r'crypto\[[^\]]+\]\[[^\]]+\]\([^)]+this\[[^\]]+\][^)]+\)'
    
    matches = re.finditer(decrypt_pattern, content)
    for idx, match in enumerate(matches):
        if idx < 5:
            start = match.start()
            context_start = max(0, start - 800)
            context_end = min(len(content), start + 800)
            context = content[context_start:context_end]
            
            print(f"\n[+] Found decrypt call {idx + 1}:")
            print("=" * 80)
            print(context)
            print("=" * 80)
    
    # Search for file URL construction
    print("\n[*] Searching for file URL construction...")
    
    # Found: file':...+'n.iamcdn.n'+...+'/'+...+'/'+...+'.'+...
    file_pattern = r'file[\'"]\s*:\s*[^,]{100,300}'
    
    matches = re.finditer(file_pattern, content)
    for idx, match in enumerate(matches):
        if idx < 5:
            print(f"\n[+] Found file URL pattern {idx + 1}:")
            print(match.group())
    
    # Try to find the complete flow
    print("\n[*] Searching for complete decryption flow...")
    
    # Look for functions that take the datas parameter
    datas_pattern = r'function[^(]*\([^)]*\)\s*{[^}]{0,2000}media[^}]{0,2000}decrypt[^}]{0,2000}}'
    
    matches = re.finditer(datas_pattern, content, re.DOTALL)
    for idx, match in enumerate(matches):
        if idx < 3:
            print(f"\n[+] Found potential main function {idx + 1}:")
            print("=" * 80)
            print(match.group()[:1000])  # First 1000 chars
            print("=" * 80)

if __name__ == '__main__':
    extract_decrypt_logic()
