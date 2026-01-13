import requests
import re
from bs4 import BeautifulSoup

def analyze_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # 1. Look for iframes and episode items
        print("\n--- ELEMENTS ---")
        soup = BeautifulSoup(html, 'html.parser')
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', 'No src')
            print(f"Iframe src: {src}")
            
        episodes = soup.find_all(attrs={"data-episode-id": True})
        if episodes:
            print(f"Episodes found: {len(episodes)}")
            for ep in episodes[:5]:
                ep_id = ep.get('data-episode-id')
                se_id = ep.get('data-season-id')
                print(f"  - Episode ID: {ep_id}, Season ID: {se_id}")

        seasons = soup.find_all(attrs={"data-season-id": True})
        # Deduplicate seasons if they are on the same elements as episodes
        season_ids = set(s.get('data-season-id') for s in seasons if s.name == 'li' or s.get('data-season-number'))
        if season_ids:
            print(f"Season IDs found: {list(season_ids)}")
            
        # 2. Look for playerthree, megaembed, playerembedapi patterns
        print("\n--- PATTERNS ---")
        patterns = [
            r'playerthree\.online/embed/[^"\'\s]+',
            r'megaembed\.link/[^"\'\s]+',
            r'playerembedapi\.link/[^"\'\s]+',
            r'marvellaholdings\.sbs[^"\'\s]+',
            r'data-source=["\']([^"\']+)["\']',
            r'data-src=["\']([^"\']+)["\']'
        ]
        
        for p in patterns:
            matches = re.findall(p, html)
            if matches:
                print(f"Matches for {p}: {len(matches)}")
                for m in matches[:5]:
                    print(f"  - {m}")
                    
        # 3. Look for script tags that might load players
        print("\n--- SCRIPTS ---")
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src')
            if src:
                if any(x in src for x in ['player', 'embed', 'main', 'app']):
                    print(f"Script src: {src}")
            else:
                content = script.string
                if content and any(x in content for x in ['player', 'embed', 'source']):
                    print(f"Inline script (starts with): {content[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_page("https://www.maxseries.one/series/assistir-terra-de-pecados-online")
    print("\n" + "="*50)
    print("STEP 2: ANALYZING PLAYERTHREE IFRAME")
    analyze_page("https://playerthree.online/embed/synden/")
