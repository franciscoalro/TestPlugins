import requests
import re
import json

def inspect_api():
    # Target: https://playerthree.online/embed/girl-taken/#13069_258444
    url = "https://playerthree.online/embed/girl-taken/#13069_258444"
    print(f"Target URL: {url}")
    
    # Extract ID
    match = re.search(r"#\d+_(\d+)", url)
    if not match:
        print("Could not extract ID from URL.")
        return

    ep_id = match.group(1)
    print(f"Extracted ID: {ep_id}")
    
    api_url = f"https://playerthree.online/episodio/{ep_id}"
    print(f"API URL: {api_url}")
    
    headers = {
        "Referer": url,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response Content:")
            # Just print the first 500 chars to avoid spam, but mostly look for obvious links
            print(response.text[:1000])
            
            # Simple link extraction check
            if ".m3u8" in response.text:
                 print("\n✅ Found .m3u8 in response!")
            if ".mp4" in response.text:
                 print("\n✅ Found .mp4 in response!")
            
            # Check for data-source attribute as mentioned in provider
            if 'data-source="' in response.text:
                print("\n✅ Found data-source attribute!")
        else:
            print("API request failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_api()
