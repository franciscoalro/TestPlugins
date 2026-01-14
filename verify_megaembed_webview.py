from playwright.sync_api import sync_playwright
import time
import sys
import re

# Same User-Agent as in key Kotlin file to ensure identical behavior
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

# The JavaScript payload exactly as implemented in the Kotlin Extractor
# This forces play and searches for video URLs
JS_PAYLOAD = """
(function() {
    return new Promise(function(resolve) {
        var attempts = 0;
        var maxAttempts = 100; // 10 seconds
        
        // Function to force play on video elements
        function tryPlayVideo() {
            var vids = document.getElementsByTagName('video');
            for(var i=0; i<vids.length; i++){
                var v = vids[i];
                if(v.paused) {
                    v.muted = true; // Required for autoplay
                    v.play().catch(function(e){ console.log("Play error: " + e); });
                }
            }
            
            // Try clicking play overlays
            var overlays = document.querySelectorAll('.play-button, .vjs-big-play-button, .jw-display-icon-container, [class*="play"]');
            for(var j=0; j<overlays.length; j++) {
                try { overlays[j].click(); } catch(e) {}
            }
        }

        var interval = setInterval(function() {
            attempts++;
            tryPlayVideo(); // Force interaction
            
            var result = '';
            
            // 1. Search in video elements
            var videos = document.querySelectorAll('video');
            console.log("Found " + videos.length + " video elements");
            
            for (var i = 0; i < videos.length; i++) {
                var video = videos[i];
                if (video.src && video.src.startsWith('http')) {
                    result = video.src;
                    break;
                }
                if (video.currentSrc && video.currentSrc.startsWith('http')) {
                    result = video.currentSrc;
                    break;
                }
            }
            
            // 2. Search in source elements
            if (!result) {
                var sources = document.querySelectorAll('source[src]');
                for (var j = 0; j < sources.length; j++) {
                    var src = sources[j].src;
                    if (src && (src.includes('.m3u8') || src.includes('.mp4'))) {
                        result = src;
                        break;
                    }
                }
            }
            
            // 3. Global variables
            if (!result) {
                var globals = ['videoUrl', 'playlistUrl', 'source', 'file', 'src', 'url', 'config', 'playerConfig'];
                for (var k = 0; k < globals.length; k++) {
                    var varName = globals[k];
                    if (window[varName]) {
                        var val = window[varName];
                        if (typeof val === 'string' && val.startsWith('http')) {
                            result = val;
                            break;
                        }
                        if (typeof val === 'object' && val.file) {
                            result = val.file;
                            break;
                        }
                    }
                }
            }
            
            // 4. JWPlayer
            if (!result) {
                if (window.jwplayer) {
                    try {
                        var jw = window.jwplayer();
                        if (jw && jw.getPlaylistItem) {
                            var item = jw.getPlaylistItem();
                            if (item && item.file) result = item.file;
                        }
                    } catch(e) {}
                }
            }
            
            // 5. HTML Patterns
            if (!result) {
                var html = document.documentElement.innerHTML;
                var patterns = [
                    /https?:\\/\\/[^"'\s]+\\/v4\\/[^"'\s]+\\.txt/g,
                    /https?:\\/\\/[^"'\s]+\\.m3u8[^"'\s]*/g,
                    /https?:\\/\\/[^"'\s]+\\.mp4[^"'\s]*/g
                ];
                
                for (var p = 0; p < patterns.length; p++) {
                    var matches = html.match(patterns[p]);
                    if (matches && matches.length > 0) {
                        result = matches[0];
                        break;
                    }
                }
            }
            
            if (result && result.length > 0) {
                clearInterval(interval);
                resolve("SUCCESS: " + result);
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                resolve('TIMEOUT: Found ' + videos.length + ' video tags but no URL'); 
            }
        }, 100);
    });
})()
"""

def test_megaembed(url):
    print(f"🚀 Starting test for: {url}")
    
    with sync_playwright() as p:
        # Launch browser (change headless=False to see it in action)
        browser = p.chromium.launch(headless=True) 
        
        # Create context with Android User-Agent
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 412, 'height': 915}, # Mobile viewport
            is_mobile=True,
            has_touch=True
        )
        
        page = context.new_page()
        
        # Network monitoring
        request_log = []
        
        def log_request(request):
            if request.resource_type in ["media", "xhr", "fetch"]:
                url_str = request.url
                # Filter for interesting video extensions
                if any(x in url_str for x in [".m3u8", ".mp4", "master.txt", "cloudatacdn"]):
                    print(f"📡 Network Trap: {url_str}")
                    request_log.append(url_str)

        page.on("request", log_request)
        
        # Navigate
        print("🌐 Navigating...")
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            print("✅ Page loaded. Injecting analysis script...")
            
            # Run the same JS as the Kotlin app
            result = page.evaluate(JS_PAYLOAD)
            print(f"\n🧪 JS Analysis Result: {result}")
            
            if "SUCCESS" in result:
                print("✅ TEST PASSED: JavaScript extracted the video URL.")
            elif len(request_log) > 0:
                print("⚠️ TEST PARTIAL: JS timed out, but Network Trap caught links (WebView interceptor would likely work).")
            else:
                print("❌ TEST FAILED: Neither JS nor Network Interceptor found video links.")
                
        except Exception as e:
            print(f"❌ Error during execution: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_megaembed_webview.py <URL>")
        print("Example: python verify_megaembed_webview.py https://megaembed.link/...")
    else:
        target_url = sys.argv[1]
        test_megaembed(target_url)
