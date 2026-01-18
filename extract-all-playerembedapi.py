#!/usr/bin/env python3
"""
Extract ALL PlayerEmbedAPI responses from Burp Suite XML export
"""
import re
import base64
from pathlib import Path

def extract_all_playerembedapi(xml_file):
    """Extract all PlayerEmbedAPI responses from Burp Suite XML"""
    print(f"[*] Reading {xml_file}...")
    
    with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"[*] File size: {len(content)} bytes")
    
    # Find all <item> tags
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    print(f"[*] Found {len(items)} items")
    
    saved_count = 0
    
    for idx, item in enumerate(items):
        # Check if this is PlayerEmbedAPI main page (not sw.import.js)
        if 'playerembedapi.link/?v=' in item:
            print(f"\n[+] Found PlayerEmbedAPI in item {idx}")
            
            # Extract URL
            url_match = re.search(r'<url><!\[CDATA\[(.*?)\]\]></url>', item)
            if url_match:
                url = url_match.group(1)
                print(f"[+] URL: {url}")
                
                # Extract video ID from URL
                video_id_match = re.search(r'\?v=([^&]+)', url)
                video_id = video_id_match.group(1) if video_id_match else f"unknown_{idx}"
            else:
                video_id = f"unknown_{idx}"
            
            # Extract response (base64 encoded)
            response_match = re.search(r'<response base64="true"><!\[CDATA\[(.*?)\]\]></response>', item, re.DOTALL)
            if response_match:
                response_b64 = response_match.group(1).strip()
                response_b64 = response_b64.replace('\n', '').replace('\r', '')
                
                # Add padding if needed
                missing_padding = len(response_b64) % 4
                if missing_padding:
                    response_b64 += '=' * (4 - missing_padding)
                
                print(f"[+] Response base64 length: {len(response_b64)}")
                
                try:
                    # Decode base64
                    response_bytes = base64.b64decode(response_b64)
                    print(f"[+] Decoded response length: {len(response_bytes)} bytes")
                    
                    # Try to decode as text
                    try:
                        response_text = response_bytes.decode('utf-8')
                    except:
                        response_text = response_bytes.decode('latin-1')
                    
                    # Check if it's HTML (not just headers)
                    if '<html' in response_text.lower() or '<body' in response_text.lower():
                        # Save to file
                        output_file = f'playerembedapi_{video_id}.html'
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        print(f"[+] Saved HTML to {output_file}")
                        saved_count += 1
                        
                        # Search for video URLs
                        print("\n[*] Analyzing content...")
                        
                        # Look for .m3u8
                        m3u8_urls = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', response_text)
                        if m3u8_urls:
                            print(f"  [+] Found {len(m3u8_urls)} .m3u8 URLs")
                        
                        # Look for .mp4
                        mp4_urls = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', response_text)
                        if mp4_urls:
                            print(f"  [+] Found {len(mp4_urls)} .mp4 URLs")
                        
                        # Look for sora/ URLs
                        sora_urls = re.findall(r'/sora/\d+/[A-Za-z0-9+/=]+', response_text)
                        if sora_urls:
                            print(f"  [+] Found {len(sora_urls)} sora/ URLs")
                        
                        # Look for video-related JSON
                        if '"file"' in response_text or '"url"' in response_text or '"source"' in response_text:
                            print(f"  [+] Contains video-related JSON properties")
                        
                        # Look for JavaScript variables
                        if 'var ' in response_text or 'const ' in response_text or 'let ' in response_text:
                            print(f"  [+] Contains JavaScript variables")
                    else:
                        print(f"[-] Response is not HTML (just headers)")
                    
                except Exception as e:
                    print(f"[-] Error decoding response: {e}")
    
    print(f"\n[*] Saved {saved_count} HTML files")

if __name__ == '__main__':
    xml_file = 'playerembedapi_response.html'
    extract_all_playerembedapi(xml_file)
