
import requests
import re
import sys

def get_headers(referer=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    if referer:
        headers['Referer'] = referer
    return headers

def analyze_maxseries(url):
    print(f"Analyzing: {url}")
    session = requests.Session()
    
    # 1. Fetch Main Page
    try:
        response = session.get(url, headers=get_headers())
        html = response.text
        print(f"Main page status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching maxseries: {e}")
        return

    # 2. Extract PlayerThree URL
    # Look for iframe
    iframe_match = re.search(r'iframe[^>]+src=["\']([^"\']*playerthree[^"\']*)["\']', html)
    player_url = None
    
    if iframe_match:
        player_url = iframe_match.group(1)
        print(f"Found PlayerThree iframe: {player_url}")
    else:
        # Look for direct pattern in HTML logic (as seen in provider)
        # val pattern = Regex("""https?://playerthree\.online/embed/[^"'\s]+""")
        direct_match = re.search(r'https?://playerthree\.online/embed/[^"\'\s]+', html)
        if direct_match:
            player_url = direct_match.group(0)
            print(f"Found PlayerThree URL in text: {player_url}")
    
    if not player_url:
        print("No PlayerThree URL found.")
        # Check for season/episodes on main page (fallback)
        episodes = re.findall(r'<li[^>]*data-episode-id', html)
        print(f"Found {len(episodes)} episodes on main page (fallback structure).")
        return

    # 3. Analyze PlayerThree Page
    try:
        print(f"Fetching PlayerThree: {player_url}")
        p3_response = session.get(player_url, headers=get_headers(referer=url))
        p3_html = p3_response.text
        print(f"PlayerThree status: {p3_response.status_code}")
        
        # Look for Episodes
        # data-episode-id="..."
        episodes = re.findall(r'data-episode-id=["\']([^"\']+)["\']', p3_html)
        print(f"Found {len(episodes)} episodes in PlayerThree.")
        
        if episodes:
            first_ep_id = episodes[0]
            print(f"Testing first episode ID: {first_ep_id}")
            
            # Construct AJAX URL
            # Url used in provider: "$baseUrl/episodio/$episodeId"
            # baseUrl is playerthreeUrl.substringBefore("/embed/") -> usually https://playerthree.online
            
            base_p3 = "https://playerthree.online"
            if "playerthree.online" not in player_url:
                 # Handle cases where it might be different, but usually it is fixed
                 pass
            
            episode_url = f"{base_p3}/episodio/{first_ep_id}"
            print(f"Requesting Episode API: {episode_url}")
            
            ep_response = session.get(episode_url, headers=get_headers(referer=player_url))
            print(f"Episode API status: {ep_response.status_code}")
            print("Episode API Response start:")
            print(ep_response.text[:500])
            
            # Look for sources
            sources = re.findall(r'data-source=["\']([^"\']+)["\']', ep_response.text)
            print(f"Found sources: {sources}")
            
            # Look for megaembed or playerembedapi
            for source in sources:
                if "megaembed" in source:
                    print(f"MegaEmbed Source found: {source}")
                if "playerembedapi" in source:
                    print(f"PlayerEmbedAPI Source found: {source}")

    except Exception as e:
        print(f"Error fetching playerthree: {e}")

if __name__ == "__main__":
    analyze_maxseries("https://www.maxseries.one/series/assistir-dele-dela-online")
