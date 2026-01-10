from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def get_test_url():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Accessing homepage...")
        driver.get("https://www.maxseries.one")
        time.sleep(3)
        
        # 1. Find a Series
        item = driver.find_element(By.CSS_SELECTOR, "article.item .data h3 a")
        series_link = item.get_attribute("href")
        print(f"Found series: {series_link}")
        
        driver.get(series_link)
        time.sleep(3)
        
        # 2. Check for Iframe (Standard MaxSeries structure)
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe")
        if iframes:
            iframe_src = iframes[0].get_attribute("src")
            if iframe_src.startswith("//"):
                iframe_src = "https:" + iframe_src
            
            print(f"Found iframe: {iframe_src}")
            driver.get(iframe_src)
            time.sleep(3)
            
            # 3. Find Episode in Iframe
            episodes = driver.find_elements(By.CSS_SELECTOR, "li[data-episode-id] a")
            if episodes:
                # The href usually is relative or partial, we need to handle it.
                # MaxSeriesProvider: valid href logic.
                ep_link = episodes[0].get_attribute("href")
                
                # If path starts with #, prepend current url
                if ep_link.startswith("#"): # internal anchor
                     # Actually MaxSeriesProvider says: if (href.startsWith("#")) "$iframeSrc$href" else href
                     # Selenium get_attribute("href") usually returns absolute matching the browser view.
                     pass 
                
                print(f"Found episode in iframe: {ep_link}")
                return ep_link
            else:
                 print("No episodes found inside iframe.")
                 return iframe_src # Maybe the iframe itself is a player?

        else:
             print("No iframe found. checking for direct episode links or movie.")
             return series_link

    except Exception as e:
        print(f"Error finding link: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    url = get_test_url()
    if url:
        print(f"TEST_URL={url}")
