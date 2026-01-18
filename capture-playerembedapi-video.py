#!/usr/bin/env python3
"""
Capture video URL from PlayerEmbedAPI using Playwright
"""
from playwright.sync_api import sync_playwright
import json
import time

def capture_playerembedapi_video(player_url):
    """
    Capture video URL from PlayerEmbedAPI
    
    Args:
        player_url: PlayerEmbedAPI URL (e.g., https://playerembedapi.link/?v=kBJLtxCD3)
    
    Returns:
        dict with video URLs and metadata
    """
    print(f"[*] Capturing video from: {player_url}")
    
    results = {
        'player_url': player_url,
        'video_urls': [],
        'network_requests': [],
        'jwplayer_config': None,
        'errors': []
    }
    
    with sync_playwright() as p:
        # Launch browser
        print("[*] Launching browser...")
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Track network requests
        def handle_request(request):
            url = request.url
            # Capture video-related requests
            if any(ext in url for ext in ['.m3u8', '.mp4', '.ts', '/sora/', 'sssrr.org']):
                print(f"[+] Network request: {url}")
                results['network_requests'].append({
                    'url': url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })
        
        def handle_response(response):
            url = response.url
            # Capture video URLs from responses
            if any(ext in url for ext in ['.m3u8', '.mp4', '.ts']):
                print(f"[+] Video response: {url} (status: {response.status})")
                if response.status in [200, 206]:  # 206 = Partial Content (video streaming)
                    results['video_urls'].append(url)
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # Navigate to player
        print("[*] Loading player page...")
        try:
            page.goto(player_url, wait_until='networkidle', timeout=30000)
        except Exception as e:
            print(f"[-] Error loading page: {e}")
            results['errors'].append(f"Page load error: {e}")
        
        # Wait for player to initialize
        print("[*] Waiting for player to initialize...")
        time.sleep(5)
        
        # Try to extract JWPlayer config
        print("[*] Extracting JWPlayer config...")
        try:
            jwplayer_config = page.evaluate("""
                () => {
                    try {
                        // Try to get JWPlayer instance
                        if (typeof jwplayer !== 'undefined') {
                            var player = jwplayer();
                            if (player && typeof player.getConfig === 'function') {
                                var config = player.getConfig();
                                return {
                                    file: config.file || null,
                                    sources: config.sources || [],
                                    playlist: config.playlist || [],
                                    playlistItem: config.playlistItem || null
                                };
                            }
                        }
                        return null;
                    } catch(e) {
                        return { error: e.toString() };
                    }
                }
            """)
            
            if jwplayer_config:
                print(f"[+] JWPlayer config extracted:")
                print(json.dumps(jwplayer_config, indent=2))
                results['jwplayer_config'] = jwplayer_config
                
                # Extract video URL from config
                if jwplayer_config.get('file'):
                    results['video_urls'].append(jwplayer_config['file'])
                    print(f"[+] Video URL from config: {jwplayer_config['file']}")
                
                if jwplayer_config.get('sources'):
                    for source in jwplayer_config['sources']:
                        if isinstance(source, dict) and source.get('file'):
                            results['video_urls'].append(source['file'])
                            print(f"[+] Video URL from sources: {source['file']}")
            else:
                print("[-] Could not extract JWPlayer config")
                results['errors'].append("JWPlayer config not found")
                
        except Exception as e:
            print(f"[-] Error extracting JWPlayer config: {e}")
            results['errors'].append(f"JWPlayer extraction error: {e}")
        
        # Try alternative methods to find video URL
        print("[*] Trying alternative extraction methods...")
        
        # Method 1: Check for video elements
        try:
            video_src = page.evaluate("""
                () => {
                    var videos = document.querySelectorAll('video');
                    if (videos.length > 0) {
                        return videos[0].src || videos[0].currentSrc;
                    }
                    return null;
                }
            """)
            if video_src:
                print(f"[+] Video element src: {video_src}")
                results['video_urls'].append(video_src)
        except Exception as e:
            print(f"[-] Error checking video elements: {e}")
        
        # Method 2: Check localStorage/sessionStorage
        try:
            storage_data = page.evaluate("""
                () => {
                    var data = {};
                    // Check localStorage
                    for (var i = 0; i < localStorage.length; i++) {
                        var key = localStorage.key(i);
                        var value = localStorage.getItem(key);
                        if (value && (value.includes('.m3u8') || value.includes('.mp4'))) {
                            data[key] = value;
                        }
                    }
                    return data;
                }
            """)
            if storage_data:
                print(f"[+] Storage data: {json.dumps(storage_data, indent=2)}")
                results['storage_data'] = storage_data
        except Exception as e:
            print(f"[-] Error checking storage: {e}")
        
        # Take screenshot
        screenshot_path = f"playerembedapi_screenshot_{int(time.time())}.png"
        page.screenshot(path=screenshot_path)
        print(f"[+] Screenshot saved: {screenshot_path}")
        results['screenshot'] = screenshot_path
        
        # Wait a bit more to capture any delayed requests
        print("[*] Waiting for additional requests...")
        time.sleep(3)
        
        # Close browser
        browser.close()
    
    # Remove duplicates from video_urls
    results['video_urls'] = list(set(results['video_urls']))
    
    # Save results
    output_file = f"playerembedapi_capture_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Player URL: {player_url}")
    print(f"Video URLs found: {len(results['video_urls'])}")
    for url in results['video_urls']:
        print(f"  - {url}")
    print(f"Network requests: {len(results['network_requests'])}")
    print(f"Errors: {len(results['errors'])}")
    for error in results['errors']:
        print(f"  - {error}")
    print("="*80)
    
    return results

if __name__ == '__main__':
    # Test with the PlayerEmbedAPI URL from Burp Suite
    player_url = "https://playerembedapi.link/?v=kBJLtxCD3"
    
    print("="*80)
    print("PlayerEmbedAPI Video Capture")
    print("="*80)
    print()
    
    results = capture_playerembedapi_video(player_url)
    
    if results['video_urls']:
        print("\n[+] SUCCESS! Video URLs captured:")
        for url in results['video_urls']:
            print(f"    {url}")
    else:
        print("\n[-] No video URLs found. Check the JSON output for details.")
