#!/usr/bin/env python3
"""
Captura de vídeo com fingerprint real de navegador
Headers e dados de navegação reais para evitar detecção
"""

import json
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Headers reais capturados de Chrome 120
REAL_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Fingerprint real de navegador
BROWSER_FINGERPRINT = '''
// Fingerprint completo de Chrome real
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
            {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}
        ];
        plugins.item = (i) => plugins[i];
        plugins.namedItem = (n) => plugins.find(p => p.name === n);
        plugins.refresh = () => {};
        return plugins;
    }
});
'''

BROWSER_FINGERPRINT += '''
Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});

// Chrome object
window.chrome = {
    app: {isInstalled: false, InstallState: {DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed'}, RunningState: {CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running'}},
    runtime: {OnInstalledReason: {CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update'}, OnRestartRequiredReason: {APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic'}, PlatformArch: {ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64'}, PlatformNaclArch: {ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64'}, PlatformOs: {ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win'}, RequestUpdateCheckStatus: {NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available'}},
    csi: function(){return {}},
    loadTimes: function(){return {}}
};

// Permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

// WebGL fingerprint real
const getParameterProxyHandler = {
    apply: function(target, thisArg, args) {
        const param = args[0];
        if (param === 37445) return 'Google Inc. (Intel)';
        if (param === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)';
        return Reflect.apply(target, thisArg, args);
    }
};
WebGLRenderingContext.prototype.getParameter = new Proxy(WebGLRenderingContext.prototype.getParameter, getParameterProxyHandler);

// Canvas fingerprint
HTMLCanvasElement.prototype.toDataURL = (function(original) {
    return function() {
        return original.apply(this, arguments);
    };
})(HTMLCanvasElement.prototype.toDataURL);

// Screen properties
Object.defineProperty(screen, 'width', {get: () => 1920});
Object.defineProperty(screen, 'height', {get: () => 1080});
Object.defineProperty(screen, 'availWidth', {get: () => 1920});
Object.defineProperty(screen, 'availHeight', {get: () => 1040});
Object.defineProperty(screen, 'colorDepth', {get: () => 24});
Object.defineProperty(screen, 'pixelDepth', {get: () => 24});

// Timezone
Date.prototype.getTimezoneOffset = function() { return 180; }; // GMT-3 Brasil
'''

def create_real_browser():
    """Cria navegador com fingerprint real"""
    options = uc.ChromeOptions()
    
    # Configurações de navegador real
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--lang=pt-BR')
    options.add_argument('--disable-extensions')
    
    # Preferências reais
    prefs = {
        'intl.accept_languages': 'pt-BR,pt,en-US,en',
        'profile.default_content_setting_values.notifications': 2,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.default_content_settings.popups': 0,
        'download.prompt_for_download': False,
    }
    options.add_experimental_option('prefs', prefs)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options, version_main=None)
    
    # Aplicar fingerprint
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': BROWSER_FINGERPRINT})
    
    # Headers reais via CDP
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': REAL_HEADERS})
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        'userAgent': REAL_HEADERS['User-Agent'],
        'platform': 'Win32',
        'acceptLanguage': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    })
    
    return driver

def human_move(driver, element):
    """Move mouse de forma humana até elemento"""
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.pause(random.uniform(0.1, 0.3))
    actions.perform()

def human_click(driver, element):
    """Clica de forma humana"""
    human_move(driver, element)
    time.sleep(random.uniform(0.1, 0.2))
    element.click()

def human_wait(min_s=1, max_s=3):
    """Espera aleatória humana"""
    time.sleep(random.uniform(min_s, max_s))

def capture_video(episode_url):
    """Captura vídeo simulando navegação real"""
    print("="*60)
    print("CAPTURA COM BROWSER REAL")
    print("="*60)
    
    driver = create_real_browser()
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Navegar para página
        print(f"\n1. Navegando: {episode_url}")
        driver.get(episode_url)
        human_wait(3, 5)
        
        # Scroll natural
        for _ in range(random.randint(1, 3)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
            human_wait(0.3, 0.8)
        
        # 2. Encontrar players
        print("\n2. Buscando players...")
        human_wait(1, 2)
        
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
        for btn in buttons:
            src = btn.get_attribute('data-source')
            txt = btn.text.strip()
            if src:
                results['players'].append({'name': txt, 'url': src})
                print(f"   ✓ {txt}: {src[:50]}...")
        
        # 3. Testar primeiro player
        if results['players']:
            player = results['players'][0]
            print(f"\n3. Testando: {player['name']}")
            
            # Encontrar e clicar no botão
            btn = driver.find_element(By.CSS_SELECTOR, f'button[data-source="{player["url"]}"]')
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
            human_wait(0.5, 1)
            human_click(driver, btn)
            human_wait(3, 5)
            
            # Verificar iframe
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes: {len(iframes)}")
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if any(x in src for x in ['player', 'embed', 'abyss', 'mega']):
                    print(f"   → Entrando iframe: {src[:50]}...")
                    driver.switch_to.frame(iframe)
                    human_wait(5, 8)
                    
                    # Capturar rede
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            msg = json.loads(log['message'])['message']
                            if msg.get('method') == 'Network.requestWillBeSent':
                                url = msg['params']['request']['url']
                                if any(x in url for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                                    print(f"\n   🎬 VÍDEO: {url[:70]}...")
                                    results['videos'].append({'url': url, 'player': player['name']})
                        except:
                            pass
                    
                    driver.switch_to.default_content()
                    break
        
        print(f"\n\nResultado: {len(results['videos'])} vídeos encontrados")
        with open('real_browser_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_video("https://www.maxseries.one/episodio/terra-de-pecados-1x1/")
