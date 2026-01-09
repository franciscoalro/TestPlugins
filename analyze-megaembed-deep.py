#!/usr/bin/env python3
"""
Análise profunda do MegaEmbed para extrair URL do vídeo
"""

import json
import time
import re
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-web-security")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_all_network_requests(driver):
    """Extrai todas as requisições de rede"""
    logs = driver.get_log("performance")
    requests = []
    
    for log in logs:
        try:
            msg = json.loads(log["message"])["message"]
            if msg["method"] == "Network.requestWillBeSent":
                req = msg["params"]["request"]
                requests.append({
                    "url": req["url"],
                    "method": req.get("method", "GET"),
                    "headers": req.get("headers", {})
                })
            elif msg["method"] == "Network.responseReceived":
                resp = msg["params"]["response"]
                requests.append({
                    "url": resp["url"],
                    "status": resp.get("status", 0),
                    "mimeType": resp.get("mimeType", "")
                })
        except:
            pass
    
    return requests

def analyze_megaembed(driver, url):
    """Analisa MegaEmbed em detalhes"""
    print(f"\n{'='*80}")
    print(f"Analisando MegaEmbed: {url}")
    print('='*80)
    
    result = {
        "url": url,
        "video_urls": [],
        "api_calls": [],
        "scripts": [],
        "errors": []
    }
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # Capturar requisições
        requests = get_all_network_requests(driver)
        
        # Filtrar requisições interessantes
        for req in requests:
            req_url = req.get("url", "")
            
            # URLs de vídeo
            if any(ext in req_url.lower() for ext in [".m3u8", ".mp4", ".ts", 