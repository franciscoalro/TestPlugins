#!/usr/bin/env python3
"""
MITM Capture Tool - MaxSeries Reverse Engineering
Captures all video-related HTTP traffic using mitmproxy

Usage:
    mitmproxy -s mitm_capture.py --listen-port 8080
    
Then configure Android device to use proxy:
    adb shell settings put global http_proxy 192.168.1.100:8080
"""

from mitmproxy import http
import json
import re

class VideoExtractor:
    def __init__(self):
        self.captured = []
        self.video_patterns = [
            '.m3u8', '.mp4', '.mkv', '.webm',
            'cloudatacdn', 'megaembed', 'playerembedapi',
            'googleapis', 'valenium', 'sssrr'
        ]
    
    def request(self, flow: http.HTTPFlow):
        """Capture video-related requests"""
        url = flow.request.url
        
        # Check if URL matches video patterns
        if any(pattern in url.lower() for pattern in self.video_patterns):
            request_data = {
                'timestamp': flow.request.timestamp_start,
                'url': url,
                'method': flow.request.method,
                'headers': dict(flow.request.headers),
                'body': flow.request.text if flow.request.text else None
            }
            
            self.captured.append(request_data)
            print(f"[CAPTURED] {flow.request.method} {url[:80]}...")
    
    def response(self, flow: http.HTTPFlow):
        """Capture responses with tokens or video URLs"""
        url = flow.request.url
        
        if any(pattern in url.lower() for pattern in self.video_patterns):
            try:
                # Try to parse as JSON
                if 'application/json' in flow.response.headers.get('content-type', ''):
                    data = json.loads(flow.response.text)
                    
                    # Look for video URLs or tokens in JSON
                    json_str = json.dumps(data)
                    if any(x in json_str for x in ['token', 'url', 'file', 'source', '.m3u8', '.mp4']):
                        print(f"\n[TOKEN/URL FOUND] {url}")
                        print(f"Response: {json.dumps(data, indent=2)[:500]}...\n")
                        
                        # Save to separate file for analysis
                        with open(f'api_response_{len(self.captured)}.json', 'w') as f:
                            json.dump(data, f, indent=2)
                
                # Check for M3U8 playlists
                elif flow.response.text and flow.response.text.startswith('#EXTM3U'):
                    print(f"\n[M3U8 FOUND] {url}")
                    print(f"Playlist preview:\n{flow.response.text[:200]}...\n")
                    
            except Exception as e:
                pass
    
    def done(self):
        """Save all captured requests on exit"""
        output_file = 'captured_requests.json'
        with open(output_file, 'w') as f:
            json.dump(self.captured, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"[SAVED] {len(self.captured)} requests to {output_file}")
        print(f"{'='*60}")
        
        # Print summary
        domains = {}
        for req in self.captured:
            domain = re.search(r'https?://([^/]+)', req['url'])
            if domain:
                domain = domain.group(1)
                domains[domain] = domains.get(domain, 0) + 1
        
        print("\nDomain Summary:")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            print(f"  {domain}: {count} requests")

addons = [VideoExtractor()]
