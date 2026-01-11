import json
import sys
import base64

# Ler HAR
har_path = r'C:\Users\KYTHOURS\Desktop\www.maxseries.one_Archive [26-01-10 21-29-33].har'

with open(har_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data['log']['entries']
print(f'Total de requisições: {len(entries)}')

# Filtrar arquivos JavaScript
js_files = []
for entry in entries:
    url = entry['request']['url']
    if '.js' in url and 'megaembed' in url.lower():
        js_files.append(entry)

print(f'\nArquivos JS do MegaEmbed: {len(js_files)}')

# Listar arquivos JS encontrados
for i, entry in enumerate(js_files[:20]):
    url = entry['request']['url']
    size = entry['response'].get('bodySize', 0)
    print(f'{i+1}. {url.split("/")[-1][:60]} ({size} bytes)')

# Extrair conteúdo do maior arquivo JS
if js_files:
    largest = max(js_files, key=lambda e: e['response'].get('bodySize', 0))
    print(f'\n=== Maior arquivo JS ===')
    print(f'URL: {largest["request"]["url"]}')
    print(f'Tamanho: {largest["response"].get("bodySize", 0)} bytes')
    
    # Tentar extrair conteúdo
    response = largest['response']
    content = None
    
    if 'content' in response:
        if 'text' in response['content']:
            text = response['content']['text']
            encoding = response['content'].get('encoding', '')
            
            print(f'Encoding: {encoding}')
            
            # Se estiver em base64, decodificar
            if encoding == 'base64':
                try:
                    content = base64.b64decode(text).decode('utf-8', errors='ignore')
                    print('✅ Decodificado de base64')
                except Exception as e:
                    print(f'❌ Erro ao decodificar: {e}')
                    content = text
            else:
                content = text
    
    if content:
        # Salvar em arquivo
        output_path = r'd:\TestPlugins-master\megaembed_player.js'
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(content)
        
        print(f'✅ Salvo em: {output_path}')
        print(f'Tamanho real: {len(content)} chars')
        print(f'\nPrimeiras 500 chars:')
        print(content[:500])
    else:
        print('❌ Não foi possível extrair conteúdo')
