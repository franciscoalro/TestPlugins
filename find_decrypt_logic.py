import re

# Ler JavaScript minificado
with open(r'd:\TestPlugins-master\megaembed_player.js', 'r', encoding='utf-8') as f:
    js = f.read()

print('=== Procurando lógica de descriptografia ===\n')

# Procurar por padrões de descriptografia
patterns = {
    'Conversão hex para string': r'parseInt\([^,]+,\s*16\)',
    'fromCharCode (decodificação)': r'String\.fromCharCode',
    'XOR operations': r'\^\s*\d+|\d+\s*\^',
    'Substring/slice': r'\.substring\(|\.slice\(',
    'Split operations': r'\.split\(',
}

for name, pattern in patterns.items():
    matches = re.findall(pattern, js)
    if matches:
        print(f'{name}: {len(matches)} ocorrências')
        print(f'  Exemplo: {matches[0]}')

# Procurar por construção de URL
print('\n=== Procurando construção de URL ===\n')

# Procurar por template strings ou concatenações com /v4/
url_patterns = [
    r'["`\']https?://[^"`\']+/v4/[^"`\']+["`\']',
    r'/v4/[^"`\']+\.txt',
    r'\.txt["`\']',
]

for pattern in url_patterns:
    matches = re.findall(pattern, js, re.IGNORECASE)
    if matches:
        print(f'Padrão {pattern}:')
        for m in set(matches[:3]):
            print(f'  - {m}')

# Procurar por referências a domínios CDN
print('\n=== Procurando domínios CDN ===\n')

cdn_patterns = [
    r'marvellaholdings',
    r'veritasholdings',
    r'valenium',
    r'\.sbs',
    r'\.cyou',
    r'\.shop',
]

for pattern in cdn_patterns:
    if re.search(pattern, js, re.IGNORECASE):
        print(f'✅ Encontrado: {pattern}')
        # Mostrar contexto
        match = re.search(r'.{0,100}' + pattern + r'.{0,100}', js, re.IGNORECASE)
        if match:
            print(f'   Contexto: {match.group()[:200]}...')

# Procurar por função que processa resposta de /api/v1/video
print('\n=== Procurando processamento de resposta ===\n')

# Procurar por fetch seguido de processamento
fetch_pattern = r'fetch\([^)]+/api/v1/video[^)]*\)[^;]{0,500}'
matches = re.findall(fetch_pattern, js, re.IGNORECASE)
if matches:
    print(f'Encontradas {len(matches)} chamadas fetch para /api/v1/video:')
    for i, m in enumerate(matches[:2]):
        print(f'\n{i+1}. {m[:300]}...')
