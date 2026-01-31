import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

# Testar MegaEmbed
megaembed_url = 'https://megaembed.link/#3wnuij'
video_id = '3wnuij'

print("=" * 60)
print("TESTE DO EXTRACTOR MEGAEMBED")
print("=" * 60)

# 1. Testar API
print("\n[1] TESTANDO API...")
api_url = f'https://megaembed.link/api/v1/info?id={video_id}'
print(f"URL: {api_url}")

r = requests.get(api_url, headers={
    **headers,
    'Referer': megaembed_url,
    'Accept': 'application/json',
    'Origin': 'https://megaembed.link'
}, timeout=15)

print(f"[OK] Status da API: {r.status_code}")
print(f"[OK] Content-Type: {r.headers.get('Content-Type', 'N/A')}")

# Verificar se eh JSON ou dados criptografados
try:
    json_data = r.json()
    print(f"[OK] Tipo: JSON valido")
    print(f"  Chaves: {list(json_data.keys())[:5]}")
except:
    print(f"[CRIPTOGRAFADO] Tipo: Dados criptografados (nao eh JSON)")
    print(f"  Tamanho: {len(r.text)} caracteres")
    print(f"  Primeiros 100 chars: {r.text[:100]}")

# 2. Testar pagina HTML
print("\n[2] TESTANDO HTML...")
print(f"URL: {megaembed_url}")

r2 = requests.get(megaembed_url, headers=headers, timeout=15)
print(f"[OK] Status HTML: {r2.status_code}")
print(f"[OK] Tamanho da pagina: {len(r2.text)} caracteres")

# Procurar video URLs
print("\n[3] PROCURANDO URLS DE VIDEO NO HTML...")
patterns = [
    (r'file:\s*["\']([^"\']+)["\']', 'file:'),
    (r'source:\s*["\']([^"\']+)["\']', 'source:'),
    (r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)', 'm3u8'),
    (r'(https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*)', 'mp4'),
    (r'(https?://[^"\'<>\s]+\.html[^"\'<>\s]*)', 'html'),
]

found_video = False
for pattern, name in patterns:
    matches = re.findall(pattern, r2.text, re.IGNORECASE)
    if matches:
        found_video = True
        print(f"[OK] Padrao '{name}' encontrado: {matches[:3]}")

if not found_video:
    print("[NAO] Nenhuma URL de video encontrada no HTML")

# Verificar necessidade de JavaScript
print("\n[4] ANALISANDO NECESSIDADE DE WEBVIEW...")
js_indicators = [
    r'<script[^>]*src="[^"]*player',
    r'eval\(function',
    r'CryptoJS',
    r'window\.location',
    r'document\.write',
]

js_found = []
for pattern in js_indicators:
    if re.search(pattern, r2.text, re.IGNORECASE):
        js_found.append(pattern)

if js_found:
    print(f"[!] Indicadores de JavaScript dinamico encontrados:")
    for ind in js_found:
        print(f"  - {ind}")
    print("-> Provavelmente PRECISA de WebView")
else:
    print("[OK] Sem indicadores fortes de JavaScript dinamico")
    print("-> Pode funcionar com HTTP simples")

# Verificar framework/player usado
print("\n[5] TECNOLOGIAS DETECTADAS...")
tech_patterns = {
    'JW Player': r'jwplayer',
    'Video.js': r'video\.js',
    'Plyr': r'plyr',
    'Hls.js': r'hls\.js',
    'CryptoJS': r'crypto-js',
    'jQuery': r'jquery',
}

tech_found = []
for tech, pattern in tech_patterns.items():
    if re.search(pattern, r2.text, re.IGNORECASE):
        tech_found.append(tech)

if tech_found:
    print(f"[OK] Tecnologias: {', '.join(tech_found)}")
else:
    print("[?] Nenhuma tecnologia especifica detectada")

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)
print(f"* API respondeu: Sim (Status {r.status_code})")
print(f"* Formato: {'JSON' if r.headers.get('Content-Type', '').startswith('application/json') else 'Criptografado/texto'}")
print(f"* URL video no HTML: {'Sim' if found_video else 'Nao'}")
print(f"* Requer WebView: {'Sim' if js_found else 'Provavelmente nao'}")
