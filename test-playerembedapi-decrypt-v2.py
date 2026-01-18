#!/usr/bin/env python3
"""
Test PlayerEmbedAPI decryption with real data - Version 2
Properly handle binary data in JSON
"""
import base64
import json
import re
from Crypto.Cipher import AES
from Crypto.Util import Counter
import hashlib

def test_decrypt():
    """Test decryption with real PlayerEmbedAPI data"""
    
    print("[*] Reading playerembedapi_kBJLtxCD3.html...")
    
    with open("playerembedapi_kBJLtxCD3.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Extract base64 data
    print("\n[*] Extracting base64 data...")
    match = re.search(r'const datas = "([^"]+)"', html)
    if not match:
        print("[-] Could not find datas variable")
        return
    
    datas_b64 = match.group(1)
    print(f"[+] Found base64 data: {len(datas_b64)} chars")
    
    # Decode base64
    print("\n[*] Decoding base64...")
    try:
        datas_decoded = base64.b64decode(datas_b64)
        print(f"[+] Decoded {len(datas_decoded)} bytes")
        
        # Parse JSON manually to preserve binary data
        # Find the media field boundaries
        json_str = datas_decoded.decode('utf-8', errors='surrogateescape')
        
        # Extract fields using regex
        slug_match = re.search(r'"slug":"([^"]+)"', json_str)
        md5_match = re.search(r'"md5_id":(\d+)', json_str)
        user_match = re.search(r'"user_id":(\d+)', json_str)
        
        if not (slug_match and md5_match and user_match):
            print("[-] Could not extract fields from JSON")
            return
        
        slug = slug_match.group(1)
        md5_id = int(md5_match.group(1))
        user_id = int(user_match.group(1))
        
        print(f"[+] Extracted fields:")
        print(f"    slug: {slug}")
        print(f"    md5_id: {md5_id}")
        print(f"    user_id: {user_id}")
        
        # Extract media field (between "media":" and ","config")
        media_start = json_str.find('"media":"') + len('"media":"')
        media_end = json_str.find('","config"', media_start)
        
        if media_start == -1 or media_end == -1:
            print("[-] Could not find media field")
            return
        
        # Get the raw bytes for media
        media_start_byte = json_str[:media_start].encode('utf-8', errors='surrogateescape')
        media_end_byte = json_str[:media_end].encode('utf-8', errors='surrogateescape')
        
        media_bytes = datas_decoded[len(media_start_byte):len(media_end_byte)]
        print(f"[+] Media field: {len(media_bytes)} bytes")
        print(f"[+] Media hex (first 50 bytes): {media_bytes[:50].hex()}")
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate key
    print("\n[*] Generating decryption key...")
    key_string = f"{user_id}:{md5_id}:{slug}"
    print(f"[+] Key string: {key_string}")
    
    key_bytes = key_string.encode('utf-8')
    print(f"[+] Key bytes length: {len(key_bytes)}")
    print(f"[+] Key hex: {key_bytes.hex()}")
    
    # Try different decryption methods
    print("\n[*] Trying different decryption methods...")
    
    # Method 1: Direct key bytes with first 16 as counter
    print("\n[1] Method 1: Direct key bytes, first 16 as counter")
    try:
        counter_bytes = key_bytes[:16]
        print(f"    Counter: {counter_bytes.hex()}")
        
        # Pad key to 32 bytes for AES-256
        if len(key_bytes) < 32:
            key_padded = key_bytes + b'\x00' * (32 - len(key_bytes))
        else:
            key_padded = key_bytes[:32]
        
        print(f"    Key (padded): {key_padded.hex()}")
        
        # Create counter
        counter_int = int.from_bytes(counter_bytes, 'big')
        counter = Counter.new(128, initial_value=counter_int)
        
        cipher = AES.new(key_padded, AES.MODE_CTR, counter=counter)
        
        # Decrypt
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    Decrypted hex (first 50 bytes): {decrypted[:50].hex()}")
        print(f"    Decrypted text (first 100 chars): {decrypted[:100]}")
        
        # Try to parse as JSON
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON:")
            print(json.dumps(media_json, indent=2))
            return media_json
        except Exception as e:
            print(f"    [-] Not valid JSON: {e}")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Method 2: SHA256 hash of key string
    print("\n[2] Method 2: SHA256 hash of key string")
    try:
        key_hash = hashlib.sha256(key_string.encode('utf-8')).digest()
        print(f"    Key hash: {key_hash.hex()}")
        
        counter_bytes = key_hash[:16]
        cipher = AES.new(key_hash, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(counter_bytes, 'big')))
        
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    Decrypted hex (first 50 bytes): {decrypted[:50].hex()}")
        
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON:")
            print(json.dumps(media_json, indent=2))
            return media_json
        except Exception as e:
            print(f"    [-] Not valid JSON: {e}")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
    
    # Method 3: Zero counter
    print("\n[3] Method 3: Zero counter")
    try:
        if len(key_bytes) < 32:
            key_padded = key_bytes + b'\x00' * (32 - len(key_bytes))
        else:
            key_padded = key_bytes[:32]
        
        counter = Counter.new(128, initial_value=0)
        cipher = AES.new(key_padded, AES.MODE_CTR, counter=counter)
        
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    Decrypted hex (first 50 bytes): {decrypted[:50].hex()}")
        
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON:")
            print(json.dumps(media_json, indent=2))
            return media_json
        except Exception as e:
            print(f"    [-] Not valid JSON: {e}")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
    
    print("\n[-] All decryption methods failed")

if __name__ == '__main__':
    test_decrypt()
