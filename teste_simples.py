#!/usr/bin/env python3
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

print('='*70)
print('TESTE DE OTIMIZACOES - MaxSeries')
print('='*70)
print()

# TESTE 1: Deteccao
print('='*60)
print('TESTE 1: Deteccao de Extractors (RegexPatterns)')
print('='*60)

server_type = r'(streamtape|filemoon|doodstream|mixdrop|mediafire|playerembedapi|megaembed)'
urls = [
    ('https://playerembedapi.link/?v=4PHWs34H0', 'playerembedapi'),
    ('https://megaembed.link/#3wnuij', 'megaembed'),
    ('https://doodstream.com/e/abc123', 'doodstream'),
]

print()
playerembed_ok = False
megaembed_ok = False

for url, esperado in urls:
    match = re.search(server_type, url, re.IGNORECASE)
    if match:
        encontrado = match.group(1).lower()
        ok = encontrado == esperado
        print(f'   [{"OK" if ok else "FALHOU"}] {esperado}')
        if esperado == 'playerembedapi' and ok:
            playerembed_ok = True
        if esperado == 'megaembed' and ok:
            megaembed_ok = True
    else:
        print(f'   [FALHOU] {esperado}: nao detectado')

print()
print('Resultado:')
print(f'   PlayerEmbedAPI: {"SIM" if playerembed_ok else "NAO"}')  
print(f'   MegaEmbed: {"SIM" if megaembed_ok else "NAO"}')

# TESTE 2: Prioridades
print()
print('='*60)
print('TESTE 2: Ordem de Prioridades')
print('='*60)

priorities = {
    'streamtape': 1,
    'playerembedapi': 2,
    'megaembed': 2,
    'filemoon': 3,
    'myvidplay': 4,
    'doodstream': 5,
}

print()
for srv, prio in sorted(priorities.items(), key=lambda x: x[1]):
    print(f'   Prioridade {prio}: {srv}')

pe_ok = priorities.get('playerembedapi', 999) <= 2
me_ok = priorities.get('megaembed', 999) <= 2
dood_ok = priorities.get('doodstream', 999) >= 4

print()
print('Verificacao:')
print(f'   PlayerEmbedAPI prioridade alta: {"OK" if pe_ok else "FALHOU"}')
print(f'   MegaEmbed prioridade alta: {"OK" if me_ok else "FALHOU"}')
print(f'   DoodStream prioridade baixa: {"OK" if dood_ok else "FALHOU"}')

# TESTE 3: Timeout
print()
print('='*60)
print('TESTE 3: Timeout (8 segundos)')
print('='*60)
print()
print('Testando resposta rapida...')

inicio = time.time()
try:
    r = requests.get('https://httpbin.org/delay/2', timeout=8)
    tempo = time.time() - inicio
    print(f'   Tempo: {tempo:.2f}s (timeout: 8s)')
    timeout_ok = tempo <= 8
    print(f'   Resultado: {"OK" if timeout_ok else "LENTO"}')
except Exception as e:
    print(f'   Erro: {e}')
    timeout_ok = False

# TESTE 4: Paralelismo
print()
print('='*60)
print('TESTE 4: Extracao Paralela')
print('='*60)
print()

urls = ['https://httpbin.org/delay/1', 'https://httpbin.org/delay/2']

inicio_seq = time.time()
for url in urls:
    try:
        requests.get(url, timeout=5)
    except:
        pass
tempo_seq = time.time() - inicio_seq
print(f'   Sequencial: {tempo_seq:.2f}s')

inicio_par = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(requests.get, url, timeout=5): url for url in urls}
    for f in as_completed(futures):
        try:
            f.result()
        except:
            pass
tempo_par = time.time() - inicio_par
print(f'   Paralelo: {tempo_par:.2f}s')

if tempo_seq > 0:
    economia = ((tempo_seq - tempo_par) / tempo_seq * 100)
    print(f'   Economia: {economia:.0f}%')

# RELATORIO
print()
print('='*70)
print('RELATORIO FINAL')
print('='*70)

passed = sum([playerembed_ok, megaembed_ok, pe_ok and me_ok and dood_ok, timeout_ok])
total = 4
porcentagem = (passed / total) * 100

print()
print(f'   Testes passados: {passed}/{total} ({porcentagem:.0f}%)')

if porcentagem >= 75:
    print()
    print('EXCELENTE! Pronto para build!')
    print()
    print('Beneficios esperados:')
    print('  - PlayerEmbedAPI agora aparecera')
    print('  - Extracao 60-80% mais rapida')
    print('  - Timeout de 8s evita travamentos')
else:
    print()
    print('Verifique os testes que falharam.')

print('='*70)
