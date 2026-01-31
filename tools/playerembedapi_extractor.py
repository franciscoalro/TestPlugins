#!/usr/bin/env python3
"""
PlayerEmbedAPI Pure HTTP Extractor - Python Prototype
Tests extraction logic before porting to Kotlin

Usage:
    python playerembedapi_extractor.py <video_id>
    python playerembedapi_extractor.py ABC123
"""

import requests
import re
import json
import sys

class PlayerEmbedAPIExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://playerembedapi.link/',
            'Origin': 'https://playerembedapi.link',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def extract(self, video_id):
        """Extract video URL without WebView"""
        url = f'https://playerembedapi.link/?v={video_id}'
        
        print(f"[1] Fetching: {url}")
        try:
            response = self.session.get(url, timeout=10)
            html = response.text
        except Exception as e:
            print(f"[ERROR] Failed to fetch: {e}")
            return None
        
        print(f"[2] HTML size: {len(html)} bytes")
        
        # Method 1: JWPlayer setup
        print("\n[3] Trying Method 1: JWPlayer setup...")
        result = self._extract_from_jwplayer_setup(html)
        if result:
            return result
        
        # Method 2: Direct regex
        print("[4] Trying Method 2: Direct regex...")
        result = self._extract_via_regex(html)
        if result:
            return result
        
        # Method 3: API endpoints
        print("[5] Trying Method 3: API endpoints...")
        result = self._extract_via_api(html)
        if result:
            return result
        
        print("\n[FAIL] All methods failed")
        
        # Debug: Save HTML for manual analysis
        with open('playerembedapi_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[DEBUG] Saved HTML to playerembedapi_debug.html")
        
        return None
    
    def _extract_from_jwplayer_setup(self, html):
        """Extract from jwplayer().setup({...})"""
        # Pattern: jwplayer('player').setup({...})
        pattern = r'jwplayer\(["\'].*?["\']\)\.setup\s*\((\{.*?\})\s*\);'
        match = re.search(pattern, html, re.DOTALL)
        
        if not match:
            print("  ✗ No JWPlayer setup found")
            return None
        
        try:
            setup_json = match.group(1)
            
            # Clean up for JSON parsing
            setup_json = re.sub(r'//.*?\n', '', setup_json)  # Remove comments
            setup_json = re.sub(r',\s*}', '}', setup_json)   # Remove trailing commas
            setup_json = re.sub(r',\s*]', ']', setup_json)
            
            # Try to parse as JSON
            config = json.loads(setup_json)
            
            # Check for 'file' key
            if 'file' in config:
                url = config['file']
                print(f"  ✓ Found 'file': {url}")
                return url
            
            # Check for 'sources' array
            if 'sources' in config and isinstance(config['sources'], list):
                for source in config['sources']:
                    if isinstance(source, dict) and 'file' in source:
                        url = source['file']
                        print(f"  ✓ Found in 'sources': {url}")
                        return url
        
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parse failed: {e}")
            # Fallback: regex for file URL
            file_match = re.search(r'["\']file["\']\s*:\s*["\']([^"\']+)["\']', match.group(1))
            if file_match:
                url = file_match.group(1)
                print(f"  ✓ Found via regex fallback: {url}")
                return url
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        return None
    
    def _extract_via_regex(self, html):
        """Extract via regex patterns"""
        patterns = [
            (r'https?://[^"\s]+\.m3u8[^"\s]*', 'M3U8'),
            (r'https?://[^"\s]*cloudatacdn[^"\s]+', 'CloudataCDN'),
            (r'https?://[^"\s]*googleapis[^"\s]+\.mp4', 'GoogleAPIs'),
            (r'https?://[^"\s]*sssrr[^"\s]+', 'SSSRR'),
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, html)
            if matches:
                url = matches[0]
                print(f"  ✓ Found {name}: {url}")
                return url
        
        print("  ✗ No video URLs found")
        return None
    
    def _extract_via_api(self, html):
        """Discover and call API endpoints"""
        # Find potential API URLs
        api_patterns = [
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
        ]
        
        api_urls = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if any(x in match for x in ['api', 'playlist', 'source', 'video']):
                    api_urls.add(match)
        
        if not api_urls:
            print("  ✗ No API endpoints found")
            return None
        
        print(f"  Found {len(api_urls)} potential API endpoints")
        
        for api_url in api_urls:
            # Build full URL
            if not api_url.startswith('http'):
                api_url = 'https://playerembedapi.link' + api_url
            
            try:
                print(f"  Trying: {api_url[:60]}...")
                response = self.session.get(api_url, timeout=5)
                
                # Try JSON
                try:
                    data = response.json()
                    video_url = self._find_video_url_in_json(data)
                    if video_url:
                        print(f"  ✓ Found in API response: {video_url}")
                        return video_url
                except:
                    pass
                
                # Try plain text
                if '.m3u8' in response.text or '.mp4' in response.text:
                    url_match = re.search(r'https?://[^\s"\']+\.(m3u8|mp4)', response.text)
                    if url_match:
                        url = url_match.group(0)
                        print(f"  ✓ Found in text response: {url}")
                        return url
            
            except Exception as e:
                continue
        
        print("  ✗ No video URLs in API responses")
        return None
    
    def _find_video_url_in_json(self, data, depth=0):
        """Recursive search for video URL in JSON"""
        if depth > 5:
            return None
        
        if isinstance(data, dict):
            # Common keys
            for key in ['file', 'url', 'source', 'src', 'stream', 'video', 'playlist']:
                if key in data and isinstance(data[key], str):
                    if '.m3u8' in data[key] or '.mp4' in data[key]:
                        return data[key]
            
            # Recursive search
            for value in data.values():
                result = self._find_video_url_in_json(value, depth + 1)
                if result:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = self._find_video_url_in_json(item, depth + 1)
                if result:
                    return result
        
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python playerembedapi_extractor.py <video_id>")
        print("Example: python playerembedapi_extractor.py ABC123")
        sys.exit(1)
    
    video_id = sys.argv[1]
    
    extractor = PlayerEmbedAPIExtractor()
    video_url = extractor.extract(video_id)
    
    if video_url:
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS")
        print(f"{'='*70}")
        print(f"Video URL: {video_url}")
        print(f"\nTest in VLC:")
        print(f"  vlc \"{video_url}\"")
    else:
        print(f"\n{'='*70}")
        print(f"❌ FAILED")
        print(f"{'='*70}")
        print("Check playerembedapi_debug.html for manual analysis")

if __name__ == '__main__':
    main()
