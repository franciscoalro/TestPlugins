import re

# Ler JavaScript
with open(r'd:\TestPlugins-master\megaembed_player.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Tamanho total: {len(content)} chars\n')

# Procurar por padrões de API
api_patterns = [
    r'/api/v1/\w+',
    r'https?://[^"\']+\.txt',
    r'https?://[^"\']+\.m3u8',
    r'cf-master',
    r'marvellaholdings',
    r'veritasholdings',
    r'valenium'
]

print('=== Buscando padrões de API ===')
for pattern in api_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f'\n{pattern}:')
        for match in set(matches[:5]):  # Primeiros 5 únicos
            print(f'  - {match}')

# Procurar por funções de conversão hex
print('\n\n=== Funções de conversão ===')
hex_patterns = [
    r'parseInt\([^,]+,\s*16\)',
    r'toString\(16\)',
    r'fromCharCode',
    r'charCodeAt'
]

for pattern in hex_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f'{pattern}: {len(matches)} ocorrências')

# Procurar por fetch/XMLHttpRequest
print('\n\n=== Requisições HTTP ===')
if 'fetch(' in content:
    print('✅ Usa fetch()')
if 'XMLHttpRequest' in content:
    print('✅ Usa XMLHttpRequest')
if 'axios' in content:
    print('✅ Usa axios')

# Procurar por variáveis relacionadas a vídeo
print('\n\n=== Variáveis de vídeo ===')
video_vars = ['videoId', 'playlistUrl', 'streamUrl', 'source', 'token']
for var in video_vars:
    if var in content:
        print(f'✅ Contém: {var}')
