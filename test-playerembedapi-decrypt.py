#!/usr/bin/env python3
"""
Test PlayerEmbedAPI decryption with real data
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
    
    # Decode base64 to JSON
    print("\n[*] Decoding base64...")
    try:
        datas_decoded = base64.b64decode(datas_b64)
        # The JSON contains binary data in media field, so we need to handle it carefully
        datas_str = datas_decoded.decode('utf-8', errors='replace')
        datas_json = json.loads(datas_str)
        
        print("[+] Decoded JSON:")
        print(f"    slug: {datas_json.get('slug')}")
        print(f"    md5_id: {datas_json.get('md5_id')}")
        print(f"    user_id: {datas_json.get('user_id')}")
        print(f"    media length: {len(datas_json.get('media', ''))} chars")
        print(f"    config: {datas_json.get('config')}")
        
        slug = datas_json['slug']
        md5_id = datas_json['md5_id']
        user_id = datas_json['user_id']
        media_encrypted = datas_json['media']
        
    except Exception as e:
        print(f"[-] Error decoding: {e}")
        return
    
    # Generate key
    print("\n[*] Generating decryption key...")
    key_string = f"{user_id}:{md5_id}:{slug}"
    print(f"[+] Key string: {key_string}")
    
    key_bytes = key_string.encode('utf-8')
    print(f"[+] Key bytes length: {len(key_bytes)}")
    
    # Try different key derivation methods
    print("\n[*] Trying different decryption methods...")
    
    # Method 1: Direct key bytes with first 16 as counter
    print("\n[1] Method 1: Direct key bytes, first 16 as counter")
    try:
        counter_bytes = key_bytes[:16]
        print(f"    Counter: {counter_bytes.hex()}")
        
        # Pad or hash key to 32 bytes for AES-256
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
        media_bytes = media_encrypted.encode('latin-1')
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    First 100 bytes: {decrypted[:100]}")
        
        # Try to parse as JSON
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON: {json.dumps(media_json, indent=2)}")
            return media_json
        except:
            print(f"    [-] Not valid JSON")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
    
    # Method 2: SHA256 hash of key string
    print("\n[2] Method 2: SHA256 hash of key string")
    try:
        key_hash = hashlib.sha256(key_string.encode('utf-8')).digest()
        print(f"    Key hash: {key_hash.hex()}")
        
        counter_bytes = key_hash[:16]
        cipher = AES.new(key_hash, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(counter_bytes, 'big')))
        
        media_bytes = media_encrypted.encode('latin-1')
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    First 100 bytes: {decrypted[:100]}")
        
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON: {json.dumps(media_json, indent=2)}")
            return media_json
        except:
            print(f"    [-] Not valid JSON")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
    
    # Method 3: Try with different counter initialization
    print("\n[3] Method 3: Zero counter")
    try:
        if len(key_bytes) < 32:
            key_padded = key_bytes + b'\x00' * (32 - len(key_bytes))
        else:
            key_padded = key_bytes[:32]
        
        counter = Counter.new(128, initial_value=0)
        cipher = AES.new(key_padded, AES.MODE_CTR, counter=counter)
        
        media_bytes = media_encrypted.encode('latin-1')
        decrypted = cipher.decrypt(media_bytes)
        
        print(f"    Decrypted length: {len(decrypted)}")
        print(f"    First 100 bytes: {decrypted[:100]}")
        
        try:
            media_json = json.loads(decrypted.decode('utf-8'))
            print(f"    [+] SUCCESS! Decrypted JSON: {json.dumps(media_json, indent=2)}")
            return media_json
        except:
            print(f"    [-] Not valid JSON")
            
    except Exception as e:
        print(f"    [-] Error: {e}")
    
    # Method 4: Check if media is already decrypted (just encoded)
    print("\n[4] Method 4: Check if media is just encoded (no encryption)")
    try:
        # Try direct JSON parse
        media_json = json.loads(media_encrypted)
        print(f"    [+] SUCCESS! Media is not encrypted, just JSON: {json.dumps(media_json, indent=2)}")
        return media_json
    except:
        print(f"    [-] Not plain JSON")
    
    # Method 5: Try base64 decode of media
    print("\n[5] Method 5: Try base64 decode of media")
    try:
        media_decoded = base64.b64decode(media_encrypted)
        print(f"    Decoded length: {len(media_decoded)}")
        print(f"    First 100 bytes: {media_decoded[:100]}")
        
        try:
            media_json = json.loads(media_decoded.decode('utf-8'))
            print(f"    [+] SUCCESS! Media was base64 encoded: {json.dumps(media_json, indent=2)}")
            return media_json
        except:
            print(f"    [-] Not valid JSON after base64 decode")
    except:
        print(f"    [-] Not valid base64")
    
    print("\n[-] All decryption methods failed")
    print("[*] Media might use a different encryption or encoding")
    
    # Show media sample for analysis
    print(f"\n[*] Media sample (first 200 chars):")
    print(f"    {media_encrypted[:200]}")
    print(f"\n[*] Media sample (hex, first 100 bytes):")
    print(f"    {media_encrypted.encode('latin-1')[:100].hex()}")

if __name__ == '__main__':
    test_decrypt()
