#!/usr/bin/env python3
"""
Extract PlayerEmbedAPI HTML response from Burp Suite XML export
"""
import re
import base64
from pathlib import Path

def extract_playerembedapi_html(xml_file):
    """Extract the actual HTML response from Burp Suite XML"""
    print(f"[*] Reading {xml_file}...")
    
    # Read file in chunks to handle large size
    with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"[*] File size: {len(content)} bytes")
    
    # Find all <item> tags
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    print(f"[*] Found {len(items)} items")
    
    for idx, item in enumerate(items):
        # Check if this is PlayerEmbedAPI
        if 'playerembedapi.link' in item:
            print(f"\n[+] Found PlayerEmbedAPI in item {idx}")
            
            # Extract URL
            url_match = re.search(r'<url>(.*?)</url>', item)
            if url_match:
                url = url_match.group(1)
                # Decode HTML entities
                url = url.replace('&amp;', '&')
                print(f"[+] URL: {url}")
            
            # Extract response (base64 encoded)
            response_match = re.search(r'<response base64="true">(.*?)</response>', item, re.DOTALL)
            if response_match:
                response_b64 = response_match.group(1).strip()
                # Remove CDATA tags if present
                response_b64 = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', response_b64, flags=re.DOTALL)
                response_b64 = response_b64.strip()
                print(f"[+] Response base64 length: {len(response_b64)}")
                
                try:
                    # Decode base64 (add padding if needed)
                    response_b64_clean = response_b64.replace('\n', '').replace('\r', '')
                    # Add padding if needed
                    missing_padding = len(response_b64_clean) % 4
                    if missing_padding:
                        response_b64_clean += '=' * (4 - missing_padding)
                    
                    response_bytes = base64.b64decode(response_b64_clean)
                    print(f"[+] Decoded response length: {len(response_bytes)} bytes")
                    
                    # Try to decode as text
                    try:
                        response_text = response_bytes.decode('utf-8')
                    except:
                        response_text = response_bytes.decode('latin-1')
                    
                    # Save to file
                    output_file = 'playerembedapi_full.html'
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(response_text)
                    print(f"[+] Saved to {output_file}")
                    
                    # Search for video URLs
                    print("\n[*] Searching for video URLs...")
                    
                    # Look for .m3u8
                    m3u8_urls = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', response_text)
                    if m3u8_urls:
                        print(f"\n[+] Found {len(m3u8_urls)} .m3u8 URLs:")
                        for url in set(m3u8_urls):
                            print(f"    {url}")
                    
                    # Look for .mp4
                    mp4_urls = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', response_text)
                    if mp4_urls:
                        print(f"\n[+] Found {len(mp4_urls)} .mp4 URLs:")
                        for url in set(mp4_urls):
                            print(f"    {url}")
                    
                    # Look for sora/ URLs
                    sora_urls = re.findall(r'/sora/\d+/[A-Za-z0-9+/=]+', response_text)
                    if sora_urls:
                        print(f"\n[+] Found {len(sora_urls)} sora/ URLs:")
                        for url in set(sora_urls):
                            print(f"    {url}")
                            # Try to decode base64
                            try:
                                parts = url.split('/')
                                if len(parts) >= 4:
                                    b64_part = parts[3]
                                    decoded = base64.b64decode(b64_part).decode('utf-8', errors='ignore')
                                    print(f"      Decoded: {decoded}")
                            except:
                                pass
                    
                    # Look for sssrr.org domains
                    sssrr_urls = re.findall(r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*', response_text)
                    if sssrr_urls:
                        print(f"\n[+] Found {len(sssrr_urls)} sssrr.org URLs:")
                        for url in set(sssrr_urls):
                            print(f"    {url}")
                    
                    # Look for trycloudflare.com
                    cloudflare_urls = re.findall(r'https?://[^\s"\'<>]*trycloudflare\.com[^\s"\'<>]*', response_text)
                    if cloudflare_urls:
                        print(f"\n[+] Found {len(cloudflare_urls)} trycloudflare.com URLs:")
                        for url in set(cloudflare_urls):
                            print(f"    {url}")
                    
                    # Look for JavaScript files
                    js_urls = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', response_text)
                    if js_urls:
                        print(f"\n[+] Found {len(js_urls)} JavaScript files:")
                        for url in js_urls[:10]:  # Show first 10
                            print(f"    {url}")
                    
                    # Look for any video-related patterns
                    video_patterns = [
                        r'"file":\s*"([^"]+)"',
                        r'"url":\s*"([^"]+)"',
                        r'"source":\s*"([^"]+)"',
                        r'"src":\s*"([^"]+)"',
                        r'videoUrl\s*=\s*["\']([^"\']+)["\']',
                        r'streamUrl\s*=\s*["\']([^"\']+)["\']',
                    ]
                    
                    for pattern in video_patterns:
                        matches = re.findall(pattern, response_text)
                        if matches:
                            print(f"\n[+] Found pattern {pattern}:")
                            for match in set(matches)[:5]:  # Show first 5
                                print(f"    {match}")
                    
                    return response_text
                    
                except Exception as e:
                    print(f"[-] Error decoding response: {e}")
    
    print("\n[-] PlayerEmbedAPI not found in XML")
    return None

if __name__ == '__main__':
    xml_file = 'playerembedapi_response.html'
    extract_playerembedapi_html(xml_file)
